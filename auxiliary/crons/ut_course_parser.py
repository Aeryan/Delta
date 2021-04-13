# Course data extractor using the API of  Student Information System 2
# Runtime ~20 minutes on a CS laptop

import requests
import psycopg2
import re
import os

# Example: "2021"
YEAR_CODE = "2020"
# Options are "spring" and "autumn"
SEMESTER_CODE = "spring"
# Set of captured course names
course_names = set()


# Yield all courses with valid English titles
# Valid course must contain a word
def get_courses():
    counter = 1
    while True:
        r = requests.get("https://ois2.ut.ee/api/courses?start={}&take=1".format(counter+1)).json()[0]
        if r and re.match(r"\w+", r["title"]["en"]):
            print("Course ", r["uuid"])
            yield r["uuid"]
            counter += 1
        else:
            break


# Get all valid versions of given course
# Valid course must take place in year YEAR_CODE and semester SEMESTER_CODE, and be of status "confirmed
def get_course_versions(course_id):
    r = requests.get("https://ois2.ut.ee/api/courses/{}/versions/".format(course_id)).json()
    if type(r) == dict:
        return
    for version in r:
        if version["target"]["year"]["code"] == YEAR_CODE and version["target"]["semester"]["code"] == SEMESTER_CODE and version["state"]["code"] == "confirmed":
            yield version["uuid"]
    return


# Integer generator to convert strings such as "n-m" into individual values
def week_generator(week_string):
    # A dictionary is used to weed out possible duplicates
    # (weeks are used as part of the primary key in the database table)
    weeks = {}
    for substring in week_string.split(","):
        if "-" in substring:
            for week in range(int(substring.split("-")[0]), int(substring.split("-")[1])+1):
                weeks[week] = ""
        else:
            weeks[int(substring)] = ""

    return list(dict.fromkeys(weeks))


def stringify(string):
    return "'" + string + "'"


# Save all valid events of the given course to the database
# Valid event must take place in Delta and be of status "confirmed"
def save_course_version_data(course_version_id):
    # Connect to the database
    conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
    cur = conn.cursor()

    r = requests.get("https://ois2.ut.ee/api/timetable/courses/{}".format(course_version_id)).json()
    if "events" in r.keys():
        info = r["info"]
        tabled = False

        for event in r["events"]:
            print("\t\tEvent ", event["uuid"])
            for week in week_generator(event["time"]["academic_weeks"]):
                # Store all events regardless of their location

                # if event["state"]["code"] == "confirmed" and (event["location"] == {}
                #                                               or "notes" in event["location"].keys()
                #                                               or event["location"]["address"].split(" - ")[0] == "Narva mnt 18"):
                if event["state"]["code"] == "confirmed":

                    # If the course passes all checks, add it to the lookup table
                    # Some unique courses share names, necessitating duplicate removal via set insertion
                    if not tabled:
                        course_names.add(info["title"]["en"])
                        print(info["title"]["en"])
                        tabled = True

                    # Read most descriptive available event type
                    if "study_work_type" in event.keys():
                        event_type = event["study_work_type"]["en"]
                    else:
                        event_type = event["event_type"]["en"]

                    # Read available notes
                    notes = {"et": "NULL", "en": "NULL"}
                    for keycode in ["et", "en"]:
                        if keycode in event["notes"].keys():
                            notes[keycode] = event["notes"][keycode]
                        if "notes" in event["location"].keys():
                            notes[keycode] = ("" if notes[keycode] == 'NULL' else notes[keycode] + " ") + event["location"]["notes"]

                    # Insert data into the PSQL table
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


def update_course_data():
    # Empty the database of old data
    conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE course_events;")
    cur.close()
    conn.commit()
    conn.close()

    # Enter all relevant course versions into the database
    for course in get_courses():
        for course_version in get_course_versions(course):
            print("\tVersion ", course_version)
            save_course_version_data(course_version)

    # Empty the course lookup table of old data and add the header
    with open(os.path.join("..", "..", "data", "course.yml"), 'w') as course_file:
        course_file.write('version: "2.0"\nnlu:\n  - lookup: course\n    examples: |')

    # Add all unique course names to the lookup table
    with open(os.path.join("..", "..", "data", "course.yml"), 'a') as course_file:
        for course_name in course_names:
            course_file.write('\n      - ' + course_name)

    # Update course event lookup table
    conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT event_type FROM course_events;")

    with open(os.path.join("..", "..", "data", "course_event.yml"), 'w') as course_event_file:
        course_event_file.write('version: "2.0"\nnlu:\n  - lookup: course_event\n    examples: |')
        for course_event in map(lambda x: x[0], cur.fetchall()):
            course_event_file.write('\n      - ' + course_event)

    cur.close()
    conn.commit()
    conn.close()


# import datetime
# start = datetime.datetime.now()
update_course_data()
# print(datetime.datetime.now()-start)
