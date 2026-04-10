from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Sequence

from ..models.entity import Entity


class EntityEngineBase(ABC):
    """Contract for engines that resolve entities from an external knowledge base."""

    @abstractmethod
    def search_for_entity(
        self,
        query: str,
        types: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Entity]:
        ...

    @abstractmethod
    def get_entity(self, *args: Any, **kwargs: Any) -> Entity:
        ...
