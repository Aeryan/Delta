#
import sys
import datetime
import psycopg2
from num2words import num2words

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, AllSlotsReset

sys.path.append("../")
from auxiliary.database_settings import *

# Nädalapäevade nimetused
WEEKDAYS = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"}


class ActionUtterGeneralHelp(Action):
    def name(self) -> Text:
        return "display_general_help"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text='This is the general help message.')
        dispatcher.utter_message(text='To learn about my competencies, you can ask me "What can you do?".')
        dispatcher.utter_message(text='For help on employee office searches, you can ask me "How to search for employee offices?"')
        dispatcher.utter_message(text='For help on course event data searches, you can ask me "How to search for course events?"')

        return []


class ActionCourseEventResponse(Action):

    def name(self) -> Text:
        return "course_event_data_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_title = tracker.get_slot("course")
        course_event = tracker.get_slot("course_event")

        conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
        cur = conn.cursor()

        cur.execute("SELECT week_nr FROM ut_weeks WHERE monday <= '" + str(datetime.date.today())
                    + "' AND sunday >= '" + str(datetime.date.today()) + "';")
        current_week = str(cur.fetchone()[0])

        cur.execute("SELECT weekday, begin_time, end_time, location, notes_et, notes_en FROM course_events WHERE course_title_en = '"
                    + course_title.replace("'", "''")
                    + "' AND week = " + current_week
                    + " AND event_type_en = '" + course_event
                    + "';")

        results = cur.fetchall()

        if len(results) == 0:
            dispatcher.utter_message("I don't know of any " + course_title + " " + course_event + "s this week.")
        else:
            result_count = len(results)
            dispatcher.utter_message(course_title + " has " + str(result_count) + " " + course_event
                                     + ("s" if result_count > 1 else "") + " this week.")
            dispatcher.utter_message("\n")
            for i in range(len(results)):
                result = results[i]

                response_string = ""

                # Sensible sentence starts
                if len(results) == 1:
                    response_string += "It"
                else:
                    response_string += "The " + num2words(i+1, to='ordinal')

                # Location
                if result[3] is None:
                    response_string += " has no designated location. It takes place "
                elif "Narva mnt 18" not in result[3]:
                    response_string += " takes place in " + result[3] + ", "
                else:
                    response_string += " takes place in room " + result[3].split(" - ")[1] + ", "
                # Time
                response_string += "on " + WEEKDAYS[result[0]] + " between " + str(result[1]).rsplit(":", 1)[0] + " and " + str(result[2]).rsplit(":", 1)[0] + "."

                if result[4] != 'NULL':
                    response_string += " The following (probably Estonian) note is attached: "
                    response_string += result[4]
                if result[5] != 'NULL':
                    response_string += " The following note is attached: "
                    response_string += result[5]
                dispatcher.utter_message(response_string)

        cur.close()
        conn.close()

        return [AllSlotsReset(),
                FollowupAction("utter_offer_additional_help")]
