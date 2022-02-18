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

        cur.execute(f"SELECT room_nr FROM offices WHERE name = '{name}';")
        result = cur.fetchone()

        cur.close()
        conn.close()
        if result[0] is None:
            return []
        return [SlotSet("office_search_result", result[0])]


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
