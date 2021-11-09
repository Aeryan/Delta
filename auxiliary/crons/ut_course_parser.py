# Kursuste teabe pärija
# Andmete allikas on ÕIS2 API
# Tööaeg on ATI sülearvutil ~20 minutit

import requests
import psycopg2
import re

from components.helper_functions import stringify
# Andmebaasi seaded
from database_settings import *

# Otsitav aasta, näiteks "2021"
YEAR_CODE = "2021"
# Otsitav semester, kas "spring" või "autumn"
SEMESTER_CODE = "autumn"


# Funktsioon kõigi sobivate kursuste tagastamiseks
# Sobiv kursus peab omama ingliskeelset pealkirja, mis sisaldab vähemalt üht sõna
def get_courses(course_titles_backup):
    counter = 1
    while True:
        r = requests.get("https://ois2.ut.ee/api/courses?start={}&take=1".format(counter)).json()
        if not r:
            break
        r = r[0]
        if r and re.match(r"\w+", r["title"]["et"]):
            print("\n", counter)
            print(r["title"]["en"] + "/" + r["title"]["et"])
            print("Course ", r["uuid"])

            # Pealkirjade varundamine
            course_titles_backup["en"] = r["title"]["en"]
            course_titles_backup["et"] = r["title"]["et"]

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


# Funktsioon kõigi sobivate sündmuste andmebaasi salvestamiseks
# Sobiv sündmus peab omama staatust "confirmed"
def save_course_version_data(course_version_id, course_titles_backup, cur):
    # Päring ja kõigi saadud vastete läbivaatus
    r = requests.get("https://ois2.ut.ee/api/timetable/courses/{}".format(course_version_id)).json()
    if "events" in r.keys():
        info = r["info"]

        for event in r["events"]:
            print("\t\tEvent ", event["uuid"])
            for week in week_generator(event["time"]["academic_weeks"]):
                # Sündmuse sobivuse kontroll
                if event["state"]["code"] == "confirmed":

                    # Salvestan kirjeldatuist kõige täpsema välja sisu
                    if "study_work_type" in event.keys():
                        event_type_en = event["study_work_type"]["en"]
                        event_type_et = event["study_work_type"]["et"]
                    else:
                        event_type_en = event["event_type"]["en"]
                        event_type_et = event["event_type"]["et"]

                    # Salvestan olemasolevad märkused
                    notes = {"en": "NULL", "et": "NULL"}
                    for keycode in ["en", "et"]:
                        if keycode in event["notes"].keys():
                            notes[keycode] = event["notes"][keycode]
                        if "notes" in event["location"].keys():
                            notes[keycode] = ("" if notes[keycode] == 'NULL' else notes[keycode] + " ") + event["location"]["notes"]

                    # Andmete sisestus andmebaasi
                    cur.execute("INSERT INTO course_events (event_uuid, course_uuid, course_title_en, course_title_et, "
                                + "course_language_code, course_version_uuid, event_type_en, event_type_et, "
                                + "week, weekday, begin_time, end_time, location, notes_en, notes_et) VALUES ("
                                + stringify(event["uuid"]) + ", "
                                + stringify(info["course_uuid"]) + ", "
                                + (stringify(info["title"]["en"].replace("'", "''")) if "en" in info["title"].keys() else stringify(course_titles_backup["en"].replace("'", "''"))) + ", "
                                + (stringify(info["title"]["et"].replace("'", "''")) if "et" in info["title"].keys() else stringify(course_titles_backup["et"].replace("'", "''"))) + ", "
                                + stringify(info["language"]["code"]) + ", "
                                + stringify(info["course_version_uuid"]) + ", "
                                + stringify(event_type_en) + ", "
                                + stringify(event_type_et) + ", "
                                + str(week) + ", "
                                + (stringify(event["time"]["weekday"]["code"]) if "weekday" in event["time"].keys() else "NULL") + ", "
                                + (stringify(event["time"]["begin_time"]) if "begin_time" in event["time"].keys() else "NULL") + ", "
                                + (stringify(event["time"]["end_time"]) if "end_time" in event["time"].keys() else "NULL") + ", "
                                + (stringify(event["location"]["address"]) if "address" in event["location"].keys() else "NULL") + ", "
                                + stringify(notes["en"].replace("'", "''")) + ", "
                                + stringify(notes["et"].replace("'", "''"))
                                + ");")


# Funktsioon kursuste teabe uuendamiseks
def update_course_data():
    # Vanade andmete eemaldus
    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE course_events RESTART IDENTITY;")

    # Kursuste genereerimisel jäävad mällu kursuse pealkirjad juhuks, kui versioonides need puuduvad
    course_titles_backup = {"en": "NULL", "et": "NULL"}
    # Kõigi asjakohase kursuseversioonide salvestamine
    for course in get_courses(course_titles_backup):
        for course_version in get_course_versions(course):
            print("\tVersion ", course_version)
            save_course_version_data(course_version, course_titles_backup, cur)

    cur.close()
    conn.commit()
    conn.close()


update_course_data()
