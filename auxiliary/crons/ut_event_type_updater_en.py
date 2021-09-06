import psycopg2
import os

# Andmebaasi seaded
from database_settings import *

# Kursusesündmuste nimetused

# Leitud kursusesündmuste nimetuste hulk
# Kuna sündmused korduvad (nt. on mitmel ainel loengud) ja olulised on unikaalsed nimetused, tuleb kordused eemaldada
course_event_types = set()

conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
cur = conn.cursor()

cur.execute("SELECT event_type_en FROM course_events;")
for i in cur.fetchall():
    course_event_types.add(i[0])

with open(os.path.join("..", "..", "data", "course_event.yml"), 'w') as course_event_file:
    course_event_file.write('version: "2.0"\nnlu:\n  - lookup: course_event\n    examples: |')
    for course_event in course_event_types:
        if "/" in course_event:
            course_event_file.write('\n      - ' + course_event.split("/")[0]
                                    + '\n      - ' + course_event.split("/")[1])
        else:
            course_event_file.write('\n      - ' + course_event)


# Kursustenimed
# Andmebaasitabelis korduvad ka kursuste nimed (unikaalsed on ainult sündmused ise), seega tuleb taas kordused eemaldada

course_titles = set()
cur.execute("SELECT course_title_en FROM course_events;")

for i in cur.fetchall():
    course_titles.add(i[0])

# Kõigi unikaalsete kursusenimede andmetabelisse lisamine
with open(os.path.join("..", "..", "data", "course.yml"), 'w') as course_file:
    course_file.write('version: "2.0"\nnlu:\n  - lookup: course\n    examples: |')
    for course_name in course_titles:
        course_file.write('\n      - ' + course_name)



