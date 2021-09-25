from abc import ABC, abstractmethod
from typing import List

from .entity import Entity


class EntityEngineBase(ABC):
    @abstractmethod
    def search_for_entity(self, query: str) -> List[Entity]:
        raise NotImplementedError(
            f"Error: {self.__class__.__name__} must implement `search_entity` function"
        )

    @abstractmethod
    def get_entity(self, entityId: str) -> Entity:
        raise NotImplementedError(
            f"Error: {self.__class__.__name__} must implement `get_entity` function"
        )
