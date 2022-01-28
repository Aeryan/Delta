# ATI ning matemaatika ja statistikainstituudi töötajate ja nende kabinettide numbrite parser
# Allikateks on veebilehed, mis on toodud välja muutujas 'pages'
# Tööaeg ATI sülearvutil ~1 minut

import re
import os
import time
import psycopg2
import selenium.common.exceptions

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Kui import ei õnnestu, käivita järgnev käsk:
# export PYTHONPATH="${PYTHONPATH}:/teekond/kausta/Delta_et/"
from auxiliary.database_settings import *
from components.helper_functions import stringify

# Kui see väärtus on tõene, lisanduvad andmetabelis mitteesinevad nimed selle lõppu,
# vastasel juhul luuakse värske andmetabel puhtalt andmebaasis oleva teabe põhjal.
APPEND_TO_EXISTING = True

# Majandusteaduskonna töötajate lehel on siintoodutest erinev kujundus, mille töötlust antud skript ei võimalda
PAGES = [
    # ATI
    "https://www.cs.ut.ee/et/arvutiteaduse-instituut",
    # Matemaatika ja Statistika Instituut
    "https://www.math.ut.ee/et/matemaatika-statistika-instituut"]


def update_employees(pages, keep_existing=True):
    headlessoption = Options()
    headlessoption.add_argument('--headless')
    driver = webdriver.Chrome(options=headlessoption)

    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()

    updated = {}
    cur.execute("SELECT name FROM offices;")
    for hit in cur.fetchall():
        updated[hit[0]] = False

    for page in pages:
        driver.get(page)
        time.sleep(1)
        try:
            compliance_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/button[1]")
            compliance_button.click()
        except selenium.common.exceptions.NoSuchElementException as e:
            if not str(e).startswith(
                    'Message: no such element: Unable to locate element: {"method":"xpath","selector":"/html/body/div[4]/div/div/div[2]/button[2]"}'):
                raise e
        buttons = list(filter(lambda x: x.text == "Ava", driver.find_elements(By.TAG_NAME, "button")))
        for button in buttons:
            button.click()

        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        employee_boxes = soup.find_all("article", {"class": "employee-item"})

        for employee_box in employee_boxes:
            name = employee_box.find_all("div", {"class": "contact-title column"})[0].text.replace("\n", "")
            room_nr_candidates = list(filter(lambda x: x.text.startswith("r "), employee_box.find_all("div", {
                "class": "d-flex flex-column contact-data column"})[0].find_all("div")))
            if len(room_nr_candidates) == 1:
                room_nr = int(re.match(r"^\d+", room_nr_candidates[0].text.replace("r ", ""))[0])
                if name in updated.keys():
                    if not updated[name]:
                        cur.execute(f"UPDATE offices SET room_nr = {room_nr} WHERE name = '" + name + "';")
                        updated[name] = True
                else:
                    cur.execute(f"INSERT INTO offices(name, room_nr) VALUES ({stringify(name)}, {room_nr});")
                    updated[name] = True
            else:
                if name in updated.keys():
                    if not updated[name]:
                        cur.execute(f"UPDATE offices SET room_nr = NULL WHERE name = '{name}';")
                        updated[name] = True
                else:
                    cur.execute(f"INSERT INTO offices(name, room_nr) VALUES ('{name}', NULL);")
                    updated[name] = True

    existing_names = []
    if keep_existing:
        write_mode = "a"
        with open(os.path.join("data", "employee.yml")) as employee_file:
            for line in employee_file.readlines():
                if line.startswith("      - "):
                    existing_names.append(line.replace("      - ", "").replace("\n", ""))
    else:
        write_mode = "w"

    with open(os.path.join("data", "employee.yml"), write_mode) as employee_file:
        if not keep_existing:
            employee_file.write('version: "2.0"\nnlu:\n  - lookup: employee\n    examples: |')
        for name in updated.keys():
            if not updated[name]:
                cur.execute(f"DELETE FROM offices WHERE name = '{name}';")
            if name not in existing_names:
                employee_file.write('\n      - ' + name)

    employee_file.close()
    conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    update_employees(PAGES, keep_existing=APPEND_TO_EXISTING)
