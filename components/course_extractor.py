# language = any

"""
Komponent kursusenimede hägusaks eraldamiseks.
Loodud Rasa Open Source komponendi RegexEntityExtractor põhjal.
https://github.com/RasaHQ/rasa/blob/main/rasa/nlu/extractors/regex_entity_extractor.py
"""

from __future__ import annotations

from fuzzywuzzy import process
from components.helper_functions import parse_nlu, remove_intent_words

from typing import Any, Optional, Text, Dict, List

from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.storage.resource import Resource
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData

from rasa.shared.nlu.constants import (
    ENTITIES,
    ENTITY_ATTRIBUTE_VALUE,
    TEXT,
    ENTITY_ATTRIBUTE_TYPE,
    INTENT,
    PREDICTED_CONFIDENCE_KEY
)


@DefaultV1Recipe.register(DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=False)
class CourseTitleExtractor(GraphComponent, EntityExtractorMixin):

    # Vaikeväärtused
    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
                # Kursusenime ja teksti vastavuse lävend
                "match_threshold": 90,
                # Kursusenimede andmetabeli asukoht
                "file_path": "data/course.yml",
                }

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        return cls(model_storage, resource, config, training_artifact=None)

    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> GraphComponent:
        return cls(model_storage, resource, config, training_artifact=None)

    def __init__(
        self,
        model_storage: ModelStorage,
        resource: Resource,
        config: Dict[Text, Any],
        training_artifact: Optional[Dict],
    ) -> None:
        self.course_titles = []
        try:
            self.match_threshold = config["match_threshold"]
        except KeyError:
            self.match_threshold = self.get_default_config()["match_threshold"]

        # Kursusenimede mällu lugemine
        with open(self.get_default_config()['file_path'], "r") as f:
            for line in f.readlines()[4:]:
                self.course_titles.append(line.replace("      - ", "").replace("\n", ""))

        # Kavatsustes esinevate sõnade mällu lugemine
        self.intent_words = parse_nlu(["- intent: request_employee_office\n"])

        self._model_storage = model_storage
        self._resource = resource

    def train(
        self,
        training_data: TrainingData
    ) -> Resource:
        self.persist()
        return self._resource

    def _extract_entities(self, message: Message) -> List[Dict[Text, Any]]:
        entities = []
        # Väärtuste ebavajaliku eraldamise vältimine kavatsuse kontrolli abil
        if message.get(INTENT)['name'] not in {"inform_course", "request_course_event_data"}:
            return entities
        best_match = process.extractOne(remove_intent_words(message.get(TEXT), self.intent_words), self.course_titles)
        if best_match[1] >= self.match_threshold:
            entities.append({
                ENTITY_ATTRIBUTE_TYPE: "course",
                ENTITY_ATTRIBUTE_VALUE: best_match[0],
                PREDICTED_CONFIDENCE_KEY: best_match[1]
            })

        return entities

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            extracted_entities = self._extract_entities(message)
            extracted_entities = self.add_extractor_name(extracted_entities)

            message.set(ENTITIES, message.get(ENTITIES, []) + extracted_entities, add_to_output=True)
        return messages

    def persist(self) -> None:
        pass
