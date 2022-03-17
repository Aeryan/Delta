# language = any

"""
Komponent ruuminumbrite eraldamiseks.
Loodud Rasa Open Source komponendi RegexEntityExtractor põhjal.
https://github.com/RasaHQ/rasa/blob/main/rasa/nlu/extractors/regex_entity_extractor.py
"""

from __future__ import annotations

import re
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
class RoomNumberExtractor(GraphComponent, EntityExtractorMixin):

    # Vaikeväärtused
    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
                # teksti ruuminumbriks sobivuse lävend
                "match_threshold": 100,
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
        if message.get(INTENT)['name'] not in {"request_room_guide"}:
            return entities
        result = re.search(r"\d\d\d\d", message.get(TEXT))
        if result is not None:
            entities.append({
                ENTITY_ATTRIBUTE_TYPE: "room_of_interest",
                ENTITY_ATTRIBUTE_VALUE: int(result.group()),
                PREDICTED_CONFIDENCE_KEY: 100
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
