# Rasa Action Serveri käivitatavad käsud
import os
import json
from PIL import Image, ImageDraw
from rasa_sdk.events import SlotSet

from actions_localisation import *


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
            return [FollowupAction(name="utter_office_unrecognized_name")]
        name = tracker.get_slot('employee').title()
        conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
        cur = conn.cursor()

        # If exact matching fails, offer to repeat query with closest match
        # https://www.postgresql.org/docs/13/pgtrgm.html
        cur.execute(f"SELECT room_nr FROM offices WHERE name = '{name}';")
        result = cur.fetchone()
        if result is None:
            cur.execute(f"SELECT name FROM (SELECT *, similarity(name, {name}) from offices order by 3 desc) as similar_names;")
            result = cur.fetchone()
            cur.close()
            conn.close()
            return [SlotSet("office_search_result", result[1])]

        cur.close()
        conn.close()
        if result[0] is None:
            return []
        return [SlotSet("office_search_result", result[0])]


# class ActionParseEmployeeSuggestionReply(Action):
#     def name(self) -> Text:
#         return "office_search_parse_suggestion_reply"
#
#     def run(self,
#             dispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         if tracker.get_slot("office_employee_suggestion_feedback"):
#             conn = psycopg2.connect(host=DATABASE_HOST, port=DATABASE_PORT, database=DATABASE_NAME, user=DATABASE_USER, password=DATABASE_PASSWORD)
#             cur = conn.cursor()
#             cur.execute("SELECT room_nr FROM offices WHERE name = '" + tracker.get_slot("office_search_result") + "';")
#             result = cur.fetchone()[0]
#             cur.close()
#             conn.close()
#             return [SlotSet("office_search_result", result),
#                     FollowupAction("utter_office_result")
#                     ]
#
#         else:
#             dispatcher.utter_message(text="Alright.")
#             return [AllSlotsReset(),
#                     FollowupAction("utter_offer_additional_help")
#                     ]


class ActionDrawLocationMap(Action):
    def name(self) -> Text:
        return "draw_location_map"

    def run(self,
            dispatcher: "CollectingDispatcher",
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        room_nr = tracker.get_slot("office_search_result")
        if room_nr is None:
            room_nr = tracker.get_slot("room_of_interest")

        if str(room_nr) + ".png" not in os.listdir("../../media/location_images/"):
            with open("../../delta_map/delta_pixel_map.json") as f:
                pixel_map = json.load(f)
            center = pixel_map[str(room_nr)]
            img = Image.open(f"../../delta_map/delta_{room_nr // 1000}.png")
            ImageDraw.Draw(img).ellipse([center[0]-5, center[1]-5, center[0]+5, center[1]+5], fill=(255, 0, 0))
            img.save(f"../../media/location_images/{room_nr}.png")
        dispatcher.utter_message(f"!img /media/location_images/{room_nr}.png")

        return []


def room_has_mapping(room_nr):
    if str(room_nr) + ".png" not in os.listdir("../../media/location_images/"):
        with open("../../delta_map/delta_pixel_map.json") as f:
            pixel_map = json.load(f)
        if f"delta_{room_nr // 1000}.png" not in os.listdir("../../delta_map/") or str(room_nr) not in pixel_map.keys() or pixel_map[str(room_nr)] == []:
            return False
    return True


class ActionCheckRoomMapping(Action):
    def name(self) -> Text:
        return "check_room_mapping"

    def run(self,
            dispatcher: "CollectingDispatcher",
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        room_nr = tracker.get_slot("office_search_result")
        if room_nr is None:
            room_nr = tracker.get_slot("room_of_interest")

        return [SlotSet("room_is_mapped", room_has_mapping(room_nr))]
