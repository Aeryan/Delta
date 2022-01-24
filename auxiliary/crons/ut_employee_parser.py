# ATI ning matemaatika ja statistikainstituudi töötajate ja nende kabinettide numbrite parser
# Allikateks on veebilehed, mis on toodud välja muutujas 'pages'
# Tööaeg ATI sülearvutil ~1 minut

from bs4 import BeautifulSoup
import requests
import re
import psycopg2
import os
from components.helper_functions import stringify
# Andmebaasi seaded
from auxiliary.database_settings import *


# Kui see väärtus on tõene, lisanduvad andmetabelis mitteesinevad nimed selle lõppu,
# vastasel juhul luuakse värske andmetabel puhtalt andmebaasis oleva teabe põhjal.
APPEND_TO_EXISTING = True

# Majandusteaduskonna töötajate lehel on siintoodutest erinev kujundus, mille töötlust antud skript ei võimalda
PAGES = [
    # ATI
    requests.get("https://www.cs.ut.ee/et/kontakt/arvutiteaduse-instituut"),
    # Matemaatika ja Statistika instituut
    requests.get("https://www.math.ut.ee/et/kontakt/matemaatika-statistika-instituut")]


def update_employees(pages, keep_existing=True):
    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()

    updated = {}
    cur.execute("SELECT name FROM offices;")
    for hit in cur.fetchall():
        updated[hit[0]] = False

    for page in pages:
        soup = BeautifulSoup(page.content, 'html.parser')
        data = []

        src = soup.find_all("tr", {"class": "odd"}) + soup.find_all("tr", {"class": "even"})
        for i in src:
            name = re.sub(r"  +", "", re.sub(r"\r", "",  re.sub(r"\n", "", i.find("td", {"class": "views-field-field-ut-employee-lname"}).text))).replace(" -", "")
            room_info = re.findall(r"r \d+", i.find("td", {"class": "views-field-field-ut-employee-phone"}).text)
            if len(room_info) > 0:
                room_nr = room_info[0].replace("r ", "")
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
