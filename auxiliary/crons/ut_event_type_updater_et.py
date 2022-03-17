# language = any

# Kursusenimede ja sündmuseliikide andmetabelite uuendaja

import psycopg2
import os

# Andmebaasi seaded
from auxiliary.database_settings import *

from auxiliary.localisation import lang

# Kui see väärtus on tõene, lisanduvad andmetabelis mitteesinevad nimed selle lõppu,
# vastasel juhul luuakse värske andmetabel puhtalt andmebaasis oleva teabe põhjal.
APPEND_TO_EXISTING = True


def update_course_tables(keep_existing):
    # Leitud kursusesündmuste nimetuste hulk
    # Kuna sündmused korduvad (nt. on mitmel ainel loengud) ja olulised on unikaalsed nimetused, tuleb kordused eemaldada
    course_event_types = set()

    conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
    cur = conn.cursor()

    cur.execute(f"SELECT event_type_{lang} FROM course_events;")
    for i in cur.fetchall():
        course_event_types.add(i[0])

    existing_events = []
    if keep_existing:
        write_mode = "a"
        with open(os.path.join("data", "course_event.yml")) as course_event_file:
            for line in course_event_file.readlines():
                if line.startswith("      - "):
                    existing_events.append(line.replace("      - ", "").replace("\n", ""))
    else:
        write_mode = "w"

    with open(os.path.join("data", "course_event.yml"), write_mode) as course_event_file:
        if not keep_existing:
            course_event_file.write('version: "3.0"\nnlu:\n  - lookup: course_event\n    examples: |')
        for course_event in course_event_types:
            if course_event not in existing_events:
                if "/" in course_event:
                    course_event_file.write('\n      - ' + course_event.split("/")[0]
                                            + '\n      - ' + course_event.split("/")[1])
                else:
                    course_event_file.write('\n      - ' + course_event)

    # Kursustenimed
    # Andmebaasitabelis korduvad ka kursuste nimed (unikaalsed on ainult sündmused ise), seega tuleb taas kordused eemaldada

    course_titles = set()
    cur.execute(f"SELECT course_title_{lang} FROM course_events;")

    for i in cur.fetchall():
        course_titles.add(i[0].replace("''", "'"))

    existing_names = []
    if keep_existing:
        write_mode = "a"
        with open(os.path.join("data", "course.yml")) as course_file:
            for line in course_file.readlines():
                if line.startswith("      - "):
                    existing_names.append(line.replace("      - ", "").replace("\n", ""))
    else:
        write_mode = "w"

    # Kõigi unikaalsete kursusenimede andmetabelisse lisamine
    with open(os.path.join("data", "course.yml"), write_mode) as course_file:
        if not keep_existing:
            course_file.write('version: "3.0"\nnlu:\n  - lookup: course\n    examples: |')
        for course_name in course_titles:
            if course_name not in existing_names:
                course_file.write('\n      - ' + course_name)


if __name__ == '__main__':
    update_course_tables(APPEND_TO_EXISTING)
