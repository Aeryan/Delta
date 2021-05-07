"""
Komponent kursusenimede hägusaks eraldamiseks.
Loodud Rasa Open Source komponendi RegexEntityExtractor põhjal.
https://github.com/RasaHQ/rasa/blob/main/rasa/nlu/extractors/regex_entity_extractor.py
"""

import typing
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


class CourseTitleExtractor(EntityExtractor):

    # Vaikeväärtused
    defaults = {
        # Kursusenime ja teksti vastavuse lävend
        "match_threshold": 90,
        # Kursusenimede andmetabeli asukoht
        "file_path": "data/course.yml",
    }

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None):
        super().__init__(component_config)
        with open(self.defaults['file_path'], "r") as f:
            lines = f.readlines()
        self.course_titles = []
        self.match_threshold = self.component_config["match_threshold"]
        for line in lines[4:]:
            self.course_titles.append(line.replace("      - ", "").replace("\n", ""))

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
        if message.get(INTENT)['name'] not in {"inform_course", "request_course_event_data"}:
            return entities

        best_match = process.extractOne(message.get(TEXT), self.course_titles)
        if best_match[1] >= self.match_threshold:
            entities.append({
                ENTITY_ATTRIBUTE_TYPE: "course",
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

