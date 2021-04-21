import psycopg2
import datetime
from num2words import num2words
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "reset_all_slots"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]


class ActionSearchOffices(Action):
    def name(self) -> Text:
        return "office_search"

    def run(self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if type(tracker.get_slot('employee')) != str:
            return []
        name = tracker.get_slot('employee').title()
        conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
        cur = conn.cursor()

        # If exact matching fails, offer to repeat query with closest match
        # https://www.postgresql.org/docs/13/pgtrgm.html
        cur.execute("SELECT room_nr FROM offices WHERE name = '" + name + "';")
        result = cur.fetchone()
        if result is None:
            cur.execute("SELECT * FROM offices WHERE name % '" + name + "' ORDER BY name DESC;")
            result = cur.fetchone()
            cur.close()
            conn.close()
            return [SlotSet("office_search_result", result[1]),
                    FollowupAction(name="utter_name_not_found")]

        cur.close()
        conn.close()
        if result[0] is None:
            return [FollowupAction(name="utter_office_no_result")]
        return [SlotSet("office_search_result", result[0]),
                FollowupAction(name="utter_office_result")]


# TODO: Needs better naming
class ActionParseEmployeeSuggestionReply(Action):
    def name(self) -> Text:
        return "office_search_parse_suggestion_reply"

    def run(self,
            dispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("office_employee_suggestion_feedback"):
            conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
            cur = conn.cursor()
            cur.execute("SELECT room_nr FROM offices WHERE name = '" + tracker.get_slot("office_search_result") + "';")
            result = cur.fetchone()[0]
            cur.close()
            conn.close()
            return [SlotSet("office_search_result", result),
                    FollowupAction("utter_office_result")]

        else:
            dispatcher.utter_message(text="Alright.")
            return [AllSlotsReset(),
                    FollowupAction("utter_offer_additional_help")]


# TODO: Only limited course titles are added to the lookup table.
#  Memorize all unique course titles and add responses for irrelevant ones.
class ActionCourseEventResponse(Action):

    def name(self) -> Text:
        return "course_event_data_response"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course_title = tracker.get_slot("course")
        course_event = tracker.get_slot("course_event")

        conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
        cur = conn.cursor()

        cur.execute("SELECT week_nr FROM ut_weeks WHERE monday <= '" + str(datetime.date.today())
                    + "' AND sunday >= '" + str(datetime.date.today()) + "';")
        current_week = str(cur.fetchone()[0])

        cur.execute("SELECT weekday, begin_time, end_time, location, notes_et, notes_en FROM course_events WHERE course_title = '"
                    + course_title.replace("'", "''")
                    + "' AND week = " + current_week
                    + " AND event_type = '" + course_event
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

                # Sensible sentence starts
                if len(results) == 1:
                    primer = "It"
                else:
                    primer = "The " + num2words(i+1, to='ordinal')

                # Location
                if result[3] is None:
                    dispatcher.utter_message(primer + " has no designated location.")
                elif "Narva mnt 18" not in result[3]:
                    dispatcher.utter_message(primer + " takes place in " + result[3] + ".")
                else:
                    dispatcher.utter_message(primer + " takes place in room " + result[3].split(" - ")[1] + ".")
                # Time
                dispatcher.utter_message("It takes place on " + WEEKDAYS[result[0]] + " between " + str(result[1]) + " and " + str(result[2]) + ".")

                if result[4] != 'NULL':
                    dispatcher.utter_message("The following (probably Estonian) note is attached:")
                    dispatcher.utter_message(result[4])
                if result[5] != 'NULL':
                    dispatcher.utter_message("The following note is attached:")
                    dispatcher.utter_message(result[5])
                dispatcher.utter_message("\n")

        cur.close()
        conn.close()

        return [AllSlotsReset(),
                FollowupAction("utter_offer_additional_help")]


# def search_transparent_rooms(cursor, room_capacity, preferred=True):
#     cursor.execute("SELECT room_number FROM rooms WHERE available = true AND room_capacity >= {0} ORDER BY room_capacity ASC, transparent DESC;".format(room_capacity))
#     q = cursor.fetchone()
#     if q is not None:
#         result = [preferred, q]
#     else:
#         result = [False, None]
#
#     return result


# class ActionCheckRooms(Action):
#     def name(self) -> Text:
#         return "room_search"
#
#     def run(self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         num_people = tracker.get_slot('num_people')
#         glass_walls = tracker.get_slot('glass_walls')
#         print(type(num_people), num_people)
#         if type(num_people) == list:
#             num_people = num_people[1]
#
#         conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
#         cur = conn.cursor()
#         if glass_walls:
#             result = search_transparent_rooms(cur, num_people)
#         else:
#             cur.execute("SELECT room_number FROM rooms WHERE available = true AND room_capacity >= {0} AND transparent = false ORDER BY room_capacity ASC;".format(num_people))
#             q = cur.fetchone()
#             if q is not None:
#                 result = [True, q]
#
#             else:
#                 result = search_transparent_rooms(cur, num_people, preferred=False)
#
#         cur.close()
#         conn.close()
#
#         if result[1] is not None:
#             partial_match = True
#         else:
#             partial_match = False
#
#         return [SlotSet("room_search_perfect_match", result[0]),
#                 SlotSet("room_search_partial_match", partial_match),
#                 SlotSet("room_search_result", result[1])
#                 ]


# class ActionUtterRoomSearchResults(Action):
#     def name(self) -> Text:
#         return "room_search_results"
#
#     def run(self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         room_num = tracker.get_slot('room_search_result')
#         if tracker.get_slot('room_search_perfect_match'):
#             string = "Room " + str(room_num[0]) + " is available."
#             print(string)
#             dispatcher.utter_message(text=string)
#             return [FollowupAction(name="room_accept_form")]
#         elif tracker.get_slot('room_search_partial_match'):
#             dispatcher.utter_message(text="No available rooms with opaque walls and sufficient space were found. Room " + str(room_num) + " is available, but has transparent walls.")
#             return [FollowupAction(name="room_accept_form")]
#         else:
#             # dispatcher.utter_message(text="No available rooms were found.")
#             # return [FollowupAction(name="reset_all_slots")]
#             return [FollowupAction(name="utter_room_search_failure")]


# class ActionFinalizeRoomSearch(Action):
#     def name(self) -> Text:
#         return "room_search_finalize"
#
#     def run(self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         if tracker.get_slot("room_search_feedback"):
#             room_num = tracker.get_slot("room_search_result")[0]
#             conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
#             cur = conn.cursor()
#             cur.execute("UPDATE rooms SET available=false WHERE room_number = " + str(room_num))
#             conn.commit()
#             cur.close()
#             conn.close()
#
#             dispatcher.utter_message(text="Done.")
#         else:
#             dispatcher.utter_message(text="Alright.")
#
#         return []


# class ActionRoomCheck(Action):
#     def name(self) -> Text:
#         return "room_check"
#
#     def run(self,
#             dispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
#         cur = conn.cursor()
#         room_nr = tracker.get_slot('check_room')
#         cur.execute("SELECT available FROM rooms WHERE room_number = " + str(room_nr) + ";")
#         if cur.fetchone()[0]:
#             dispatcher.utter_message(str(room_nr) + " is currently available.")
#         else:
#             dispatcher.utter_message(str(room_nr) + " is currently not available.")
#
#         cur.close()
#         conn.close()
#         return []
