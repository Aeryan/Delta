# language = any

"""
Komponent töötajate nimede hägusaks eraldamiseks.
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
class EmployeeExtractor(GraphComponent, EntityExtractorMixin):

    # Vaikeväärtused
    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
                # töötaja nime ja teksti vastavuse lävendid
                "no_match_threshold": 20,
                "low_match_threshold": 50,
                "high_match_threshold": 80,
                # Töötajate nimede andmetabeli asukoht
                "employee_file_path": "data/employee.yml",
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
        self.employees = []
        for key in ["no_match_threshold", "low_match_threshold", "high_match_threshold"]:
            try:
                setattr(self, key, config[key])
            except KeyError:
                setattr(self, key, self.get_default_config()[key])

        # Töötajate nimede mällu lugemine
        with open(self.get_default_config()['employee_file_path'], "r") as f:
            for line in f.readlines()[4:]:
                self.employees.append(line.replace("      - ", "").replace("\n", ""))

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
        print(self.get_default_config())
        # Väärtuste ebavajaliku eraldamise vältimine kavatsuse kontrolli abil
        if message.get(INTENT)['name'] not in {"request_employee_office"}:
            return entities
        best_match = process.extractOne(remove_intent_words(message.get(TEXT), self.intent_words), self.employees)
        if best_match[1] >= self.no_match_threshold:
            entities.append({
                ENTITY_ATTRIBUTE_TYPE: "employee",
                ENTITY_ATTRIBUTE_VALUE: best_match[0],
                PREDICTED_CONFIDENCE_KEY: best_match[1]
            })
            entities.append({
                ENTITY_ATTRIBUTE_TYPE: "employee_confidence",
                ENTITY_ATTRIBUTE_VALUE: "high" if best_match[1] > self.high_match_threshold else "low" if best_match[1] > self.low_match_threshold else "none"
            })
        return entities

    def process(self, messages: List[Message], **kwargs: Any) -> List[Message]:
        for message in messages:
            extracted_entities = self._extract_entities(message)
            extracted_entities = self.add_extractor_name(extracted_entities)

            message.set(ENTITIES, message.get(ENTITIES, []) + extracted_entities, add_to_output=True)
        return messages

    def persist(self) -> None:
        pass
