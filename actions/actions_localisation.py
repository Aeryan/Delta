import sys
import datetime
import psycopg2
from estnltk.vabamorf.morf import synthesize

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction, AllSlotsReset

sys.path.append("../")
from components.tts_preprocess_et.convert import make_ordinal, convert_number
# Andmebaasi seaded
from auxiliary.database_settings import *

# Nädalapäevade nimetused
WEEKDAYS = {1: "esmaspäev", 2: "teispäev", 3: "kolmapäev", 4: "neljapäev", 5: "reede", 6: "laupäev", 7: "pühapäev"}


class ActionUtterGeneralHelp(Action):
    def name(self) -> Text:
        return "display_general_help"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text='See on üldine abisõnum.')
        dispatcher.utter_message(text='Minu võimekuste kohta saab infot päringuga "Mida sa teha oskad?".')
        dispatcher.utter_message(text='Abi töötajate kabinetinumbrite otsinguga seoses saab päringuga "Kuidas küsida töötajate kontorinumbreid?"')
        dispatcher.utter_message(text='Kursuste toimumiste kohta küsimise abi saab päringuga "Kuidas küsida infot kursuste toimumiste kohta?"')

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

        cur.execute("SELECT weekday, begin_time, end_time, location, notes_et, notes_en FROM course_events WHERE course_title_et = '"
                    + course_title.replace("'", "''")
                    + "' AND week = " + current_week
                    + " AND event_type_et = '" + course_event
                    + "';")

        results = cur.fetchall()

        if len(results) == 0:
            dispatcher.utter_message("Minu teada ei toimu aines " + course_title + " sel nädalal ühtki " + synthesize(course_event, "sg p")[0] + ".")
        else:
            result_count = len(results)
            dispatcher.utter_message("Aines " + course_title + " toimub sel nädalal "
                                     + convert_number(str(result_count), True)
                                     + " "
                                     + (course_event if result_count == 1 else synthesize(course_event, "sg p")[0])
                                     + ".\n")
            for i in range(len(results)):
                result = results[i]

                response_string = ""

                if result_count > 1:
                    lemma = make_ordinal(convert_number(str(i+1), True))[0]
                else:
                    lemma = "see"

                if result[3] is None:
                    response_string += synthesize(lemma, "sg ad")[0].title() + " ei ole toimumispaika märgitud. See toimub "
                elif "Narva mnt 18" not in result[3]:
                    response_string += synthesize(lemma, "sg g")[0].title() + " toimumiskoht on " + result[3] + ", "
                else:
                    response_string += lemma.title() + " toimub ruumis " + result[3].split(" - ")[1] + ", "
                # Time
                response_string += synthesize(WEEKDAYS[result[0]], "sg ad")[0] + " ajavahemikus " + str(result[1]).rsplit(":", 1)[0] + "-" + str(result[2]).rsplit(":", 1)[0] + "."

                if result[4] != 'NULL':
                    response_string += " Sellele on lisatud järgnev märkus: "
                    response_string += result[4]
                elif result[5] != 'NULL':
                    response_string += " Sellele on lisatud järgnev (tõenäoliselt ingliskeelne) märkus: "
                    response_string += result[5]
                dispatcher.utter_message(response_string)

        cur.close()
        conn.close()

        return [AllSlotsReset(),
                FollowupAction("utter_offer_additional_help")]
