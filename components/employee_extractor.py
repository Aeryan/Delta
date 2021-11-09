"""
Komponent töötajate nimede hägusaks eraldamiseks.
Loodud Rasa Open Source komponendi RegexEntityExtractor põhjal.
https://github.com/RasaHQ/rasa/blob/main/rasa/nlu/extractors/regex_entity_extractor.py
"""

import typing
from components.helper_functions import parse_nlu
from components.levenshtein import manual_levenshtein
from typing import Any, Optional, Text, Dict, List

from rasa.nlu.extractors.extractor import EntityExtractor
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import (
    ENTITIES,
    ENTITY_ATTRIBUTE_VALUE,
    TEXT,
    ENTITY_ATTRIBUTE_TYPE,
    INTENT,
    PREDICTED_CONFIDENCE_KEY
)
from fuzzywuzzy import process

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class EmployeeExtractor(EntityExtractor):

    # Vaikeväärtused
    defaults = {
        # töötaja nime ja teksti vastavuse lävend
        "match_threshold": 80,
        # Töötajate nimede andmetabeli asukoht
        "employee_file_path": "data/employee.yml",
    }

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None):
        super().__init__(component_config)
        self.employees = []
        self.match_threshold = self.component_config["match_threshold"]

        # Töötajate nimede mällu lugemine
        with open(self.defaults['employee_file_path'], "r") as f:
            for line in f.readlines()[4:]:
                self.employees.append(line.replace("      - ", "").replace("\n", ""))

        # Kavatsustes esinevate sõnade mällu lugemine
        self.intent_words = parse_nlu(["- intent: request_employee_office\n"])

    def remove_intent_words(self, text):
        text_list = text.split(" ")
        for word in text.split(" "):
            # best_match = process.extractOne(word, self.intent_words)
            best_match = manual_levenshtein(word, self.intent_words)
            if best_match[1] < 2:
                text_list.remove(word)
        return " ".join(text_list)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def _extract_entities(self, message: Message) -> List[Dict[Text, Any]]:
        entities = []
        # Väärtuste ebavajaliku eraldamise vältimine kavatsuse kontrolli abil
        if message.get(INTENT)['name'] not in {"request_employee_office"}:
            return entities
        best_match = process.extractOne(self.remove_intent_words(message.get(TEXT)), self.employees)
        if best_match[1] >= self.match_threshold:
            entities.append({
                ENTITY_ATTRIBUTE_TYPE: "employee",
                ENTITY_ATTRIBUTE_VALUE: best_match[0],
                PREDICTED_CONFIDENCE_KEY: best_match[1]
            })

        return entities

    def process(self, message: Message, **kwargs: Any) -> None:
        extracted_entities = self._extract_entities(message)
        extracted_entities = self.add_extractor_name(extracted_entities)

        message.set(ENTITIES, message.get(ENTITIES, []) + extracted_entities, add_to_output=True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadata"] = None,
        cached_component: Optional["EntityExtractor"] = None,
        **kwargs: Any,
    ) -> "EntityExtractor":

        if cached_component:
            return cached_component
        else:
            return cls(meta)

