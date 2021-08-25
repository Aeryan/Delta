# Kursuste teabe pärija
# Andmete allikas on ÕIS2 API
# Tööaeg on ATI sülearvutil ~20 minutit

import requests
import psycopg2
import re
import os

# Otsitav aasta, näiteks "2021"
YEAR_CODE = "2020"
# Otsitav semester, kas "spring" või "autumn"
SEMESTER_CODE = "spring"
# Leitud kursusenimede hulk
course_names = set()

# Andmebaasi seaded
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432
DATABASE_NAME = "delta"
DATABASE_USER = "postgres"
DATABASE_PASSWORD = "postgres"


# Funktsioon kõigi sobivate kursuste tagastamiseks
# Sobiv kursus peab omama ingliskeelset pealkirja, mis sisaldab vähemalt üht sõna
def get_courses():
    counter = 1
    while True:
        r = requests.get("https://ois2.ut.ee/api/courses?start={}&take=1".format(counter)).json()
        if not r:
            break
        r = r[0]
        if r and re.match(r"\w+", r["title"]["en"]):
            print("Course ", r["uuid"])
            yield r["uuid"]
            counter += 1
        else:
            break


# Funktsioon sisendkursuse sobivate versioonide leidmiseks
# Sobiv versioon peab toimuma aastal YEAR_CODE ja semestril SEMESTER_CODE ning omama staatust "confirmed
def get_course_versions(course_id):
    r = requests.get("https://ois2.ut.ee/api/courses/{}/versions/".format(course_id)).json()
    if type(r) == dict:
        return
    for version in r:
        if version["target"]["year"]["code"] == YEAR_CODE and version["target"]["semester"]["code"] == SEMESTER_CODE and version["state"]["code"] == "confirmed":
            yield version["uuid"]
    return


# Täisarvude generaator sõnede (näiteks "n-m") järjenditeks muundamiseks
def week_generator(week_string):
    # Võimalike koopiate välja praakimiseks kasutan sõnastikku
    weeks = {}
    for substring in week_string.split(","):
        if "-" in substring:
            for week in range(int(substring.split("-")[0]), int(substring.split("-")[1])+1):
                weeks[week] = ""
        else:
            weeks[int(substring)] = ""

    return list(dict.fromkeys(weeks))


# Funktsioon SQLisõbralike sõnede loomiseks
def stringify(string):
    return "'" + string + "'"


# Funktsioon kõigi sobivate sündmuste andmebaasi salvestamiseks
# Sobiv sündmus peab omama staatust "confirmed"
def save_course_version_data(course_version_id):
    # Andmebaasiga ühendumine
    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()

    # Päring ja kõigi saadud vastete läbivaatus
    r = requests.get("https://ois2.ut.ee/api/timetable/courses/{}".format(course_version_id)).json()
    if "events" in r.keys():
        info = r["info"]
        tabled = False

        for event in r["events"]:
            print("\t\tEvent ", event["uuid"])
            for week in week_generator(event["time"]["academic_weeks"]):
                # Sündmuse sobivuse kontroll
                if event["state"]["code"] == "confirmed":

                    # Kui kursus on senini läbinud kõik kontrollid, lisan selle juturoboti keeletuvastuse andmetabelisse
                    # Mõned nimed võivad korduda, selle vältimiseks hoiustan nimesid hulgas
                    if not tabled:
                        course_names.add(info["title"]["en"])
                        print(info["title"]["en"])
                        tabled = True

                    # Salvestan kirjeldatuist kõige täpsema välja sisu
                    if "study_work_type" in event.keys():
                        event_type = event["study_work_type"]["en"]
                    else:
                        event_type = event["event_type"]["en"]

                    # Salvestan olemasolevad märkused
                    notes = {"et": "NULL", "en": "NULL"}
                    for keycode in ["et", "en"]:
                        if keycode in event["notes"].keys():
                            notes[keycode] = event["notes"][keycode]
                        if "notes" in event["location"].keys():
                            notes[keycode] = ("" if notes[keycode] == 'NULL' else notes[keycode] + " ") + event["location"]["notes"]

                    # Andmete sisestus andmebaasi
                    cur.execute("INSERT INTO course_events (event_uuid, course_uuid, course_title, course_language_code, course_version_uuid, event_type, week, weekday, begin_time, end_time, location, notes_et, notes_en) VALUES ("
                                + stringify(event["uuid"]) + ", "
                                + stringify(info["course_uuid"]) + ", "
                                + stringify(info["title"]["en"].replace("'", "''")) + ", "
                                + stringify(info["language"]["code"]) + ", "
                                + stringify(info["course_version_uuid"]) + ", "
                                + stringify(event_type) + ", "
                                + str(week) + ", "
                                + (stringify(event["time"]["weekday"]["code"]) if "weekday" in event["time"].keys() else "NULL") + ", "
                                + (stringify(event["time"]["begin_time"]) if "begin_time" in event["time"].keys() else "NULL") + ", "
                                + (stringify(event["time"]["end_time"]) if "end_time" in event["time"].keys() else "NULL") + ", "
                                + (stringify(event["location"]["address"]) if "address" in event["location"].keys() else "NULL") + ", "
                                + stringify(notes["et"].replace("'", "''")) + ", "
                                + stringify(notes["en"].replace("'", "''"))
                                + ");")

    cur.close()
    conn.commit()
    conn.close()


# Funktsioon kursuste teabe uuendamiseks
def update_course_data():
    # Vanade andmete eemaldus
    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE course_events RESTART IDENTITY;")
    cur.close()
    conn.commit()
    conn.close()

    # Kõigi asjakohase kursuseversioonide salvestamine
    for course in get_courses():
        for course_version in get_course_versions(course):
            print("\tVersion ", course_version)
            save_course_version_data(course_version)

    # Juturoboti andmetabeli tühjendus ja korrektse päise lisamine
    with open(os.path.join("..", "..", "data", "course.yml"), 'w') as course_file:
        course_file.write('version: "2.0"\nnlu:\n  - lookup: course\n    examples: |')

    # Kõigi unikaalsete kursusenimede andmetabelisse lisamine
    with open(os.path.join("..", "..", "data", "course.yml"), 'a') as course_file:
        for course_name in course_names:
            course_file.write('\n      - ' + course_name)

    # Kursusesündmuste tabeli uuendus
    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT event_type FROM course_events;")

    with open(os.path.join("..", "..", "data", "course_event.yml"), 'w') as course_event_file:
        course_event_file.write('version: "2.0"\nnlu:\n  - lookup: course_event\n    examples: |')
        for course_event in map(lambda x: x[0], cur.fetchall()):
            course_event_file.write('\n      - ' + course_event)

    cur.close()
    conn.commit()
    conn.close()


update_course_data()
