from bs4 import BeautifulSoup
import requests
import re
import psycopg2
import os

# TODO: Majandusteaduskonnal on teistsugune kujundus, see vajab eraldi töötlust

pages = [
    # CS
    requests.get("https://www.cs.ut.ee/et/kontakt/arvutiteaduse-instituut"),
    # MS
    requests.get("https://www.math.ut.ee/et/kontakt/matemaatika-statistika-instituut")]

conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
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
            # cur.execute("SELECT room_nr FROM offices WHERE name = '" + name + "';")
            if name in updated.keys():
                if not updated[name]:
                    cur.execute("UPDATE offices SET room_nr = " + room_nr + " WHERE name = '" + name + "';")
                    updated[name] = True
            else:
                cur.execute("INSERT INTO offices(name, room_nr) VALUES ('" + name + "', " + room_nr + ");")
                updated[name] = True
        else:
            if name in updated.keys():
                if not updated[name]:
                    cur.execute("UPDATE offices SET room_nr = NULL WHERE name = '" + name + "';")
                    updated[name] = True
            else:
                cur.execute("INSERT INTO offices(name, room_nr) VALUES ('" + name + "', NULL);")
                updated[name] = True

with open(os.path.join("..", "data", "employee.yml"), 'w') as employee_file:
    employee_file.write('version: "2.0"\nnlu:\n  - lookup: employee\n    examples: |')
    for name in updated.keys():
        if not updated[name]:
            cur.execute("DELETE FROM offices WHERE name = '" + name + "';")
        print(name)
        employee_file.write('\n      - ' + name)

employee_file.close()
conn.commit()

cur.close()
conn.close()
