# ATI ning matemaatika ja statistikainstituudi töötajate ja nende kabinettide numbrite parser
# Allikateks on veebilehed, mis on toodud välja muutujas 'pages'
# Tööaeg ATI sülearvutil ~1 minut

import re
import os
import requests
import psycopg2

from bs4 import BeautifulSoup

# Kui import ei õnnestu, käivita järgnev käsk:
# export PYTHONPATH="${PYTHONPATH}:/teekond/kausta/Delta_ex/"
from auxiliary.database_settings import *
from components.helper_functions import stringify

# Kui see väärtus on tõene, lisanduvad andmetabelis mitteesinevad nimed selle lõppu,
# vastasel juhul luuakse värske andmetabel puhtalt andmebaasis oleva teabe põhjal.
APPEND_TO_EXISTING = True

PAGES = [
    # ATI
    "https://cs.ut.ee/et/arvutiteaduse-instituut",
    # Matemaatika ja Statistika Instituut
    "https://math.ut.ee/et/matemaatika-ja-statistika-instituut"]


def update_database_from_page(ut_soup, updatelist, database_cursor):
    for employee_box in ut_soup.find_all("article", {"class": "employee-item"}):
        name = employee_box.find_all("div", {"class": "contact-title column"})[0].text.replace("\n", "")
        if name == "Rauno Jaaska":
            print("lmao")
        room_nr_candidates = list(filter(lambda x: x.text.startswith("r "), employee_box.find_all("div", {
            "class": "d-flex flex-column contact-data column"})[0].find_all("div")))
        if len(room_nr_candidates) == 1:
            room_nr = int(re.match(r"^\d+", room_nr_candidates[0].text.replace("r ", ""))[0])
            if name in updatelist.keys():
                if not updatelist[name]:
                    database_cursor.execute(f"UPDATE offices SET room_nr = {room_nr} WHERE name = '" + name + "';")
                    updatelist[name] = True
            else:
                database_cursor.execute(f"INSERT INTO offices(name, room_nr) VALUES ({stringify(name)}, {room_nr});")
                updatelist[name] = True
        else:
            if name in updatelist.keys():
                if not updatelist[name]:
                    database_cursor.execute(f"UPDATE offices SET room_nr = NULL WHERE name = {stringify(name)};")
                    updatelist[name] = True
            else:
                database_cursor.execute(f"INSERT INTO offices(name, room_nr) VALUES ({stringify(name)}, NULL);")
                updatelist[name] = True


def update_employees(pages, keep_existing=True):
    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()

    updated = {}
    cur.execute("SELECT name FROM offices;")
    for hit in cur.fetchall():
        updated[hit[0]] = False

    for page in pages:
        soup = BeautifulSoup(requests.get(page).content, 'html.parser')
        update_database_from_page(soup, updated, cur)
        subpage_indices = list(map(lambda x: x.get("data-ajax"),
                                   soup.find_all("button", {"data-target": re.compile(r'#collapse-\d+'),
                                                            "data-ajax": re.compile(r"\d+")})))

        for index in subpage_indices:
            subpage = re.match(r'https://\w+.ut.ee/', page)[0] + "et/ut_stucture/employee-output/" + index
            update_database_from_page(BeautifulSoup(requests.get(subpage).content, 'html.parser'),
                                      updated, cur)

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
