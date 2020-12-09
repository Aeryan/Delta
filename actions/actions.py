# Symlink test
import psycopg2
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset


def search_transparent_rooms(cursor, room_capacity, preferred=True):
    cursor.execute("SELECT room_number FROM rooms WHERE available = true AND room_capacity >= {0} ORDER BY room_capacity ASC, transparent DESC;".format(room_capacity))
    q = cursor.fetchone()
    if q is not None:
        result = [preferred, q]
    else:
        result = [False, None]

    return result


class ActionCheckRooms(Action):
    def name(self) -> Text:
        return "room_search"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        num_people = tracker.get_slot('num_people')
        glass_walls = tracker.get_slot('glass_walls')
        print(type(num_people), num_people)
        if type(num_people) == list:
            num_people = num_people[1]

        conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
        cur = conn.cursor()
        if glass_walls:
            result = search_transparent_rooms(cur, num_people)
        else:
            cur.execute("SELECT room_number FROM rooms WHERE available = true AND room_capacity >= {0} AND transparent = false ORDER BY room_capacity ASC;".format(num_people))
            q = cur.fetchone()
            if q is not None:
                result = [True, q]

            else:
                result = search_transparent_rooms(cur, num_people, preferred=False)

        cur.close()
        conn.close()

        if result[1] is not None:
            partial_match = True
        else:
            partial_match = False

        return [SlotSet("room_search_perfect_match", result[0]),
                SlotSet("room_search_partial_match", partial_match),
                SlotSet("room_search_result", result[1])
                ]


class ActionUtterRoomSearchResults(Action):
    def name(self) -> Text:
        return "room_search_results"
    
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        room_num = tracker.get_slot('room_search_result')
        if tracker.get_slot('room_search_perfect_match'):
            dispatcher.utter_message(text="Room " + str(room_num) + " is available.")
            return [FollowupAction(name="room_accept_form")]
        elif tracker.get_slot('room_search_partial_match'):
            dispatcher.utter_message(text="No available rooms with opaque walls and sufficient space were found. Room " + str(room_num) + " is available, but has transparent walls.")
            return [FollowupAction(name="room_accept_form")]
        else:
            dispatcher.utter_message(text="No available rooms were found.")
            return []


class ActionFinalizeRoomSearch(Action):
    def name(self) -> Text:
        return "room_search_finalize"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_slot("room_search_feedback"):
            room_num = tracker.get_slot("room_search_result")[0]
            conn = psycopg2.connect(host="localhost", port=5432, database="delta", user="postgres", password="postgres")
            cur = conn.cursor()
            cur.execute("UPDATE rooms SET available=false WHERE room_number = " + str(room_num))
            conn.commit()
            cur.close()
            conn.close()

        return []


class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "reset_all_slots"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]

#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
