from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

GOOGLE_LINK = "https://www.google.com/search?q={}"
WIKIDATA_GET_LINK = "https://wikidata.org/wiki/{}"


@dataclass(repr=False)
class Entity:
    """
    A grounded record that may include Google Knowledge Graph and Wikidata fields.

    Attribute names use camelCase for backward compatibility with earlier releases.
    """

    entityName: Optional[str]
    entityType: Optional[str] = None
    wikiId: Optional[str] = None
    wikidataDescription: Optional[str] = None
    googleId: Optional[str] = None
    googleDescription: Optional[str] = None
    surfaceForms: List[str] = field(default_factory=list)
    entitySource: Optional[str] = field(default=None, compare=False)

    def set_entity_source(self, entitySource: str) -> None:
        self.entitySource = entitySource

    def __repr__(self) -> str:
        base_representation = (
            f'Entity("{self.entityName}", type: {self.entityType}, '
            f"qid: {self.wikiId}, googleId: {self.googleId}, "
            f"entitySource: {self.entitySource})"
        )
        return (
            f"{base_representation}\n"
            f"surfaceForms: {self.surfaceForms}\n"
            f"googleDescription: {self.googleDescription}\n"
            f"wikidataDescription: {self.wikidataDescription}\n"
            f"wikiUrl: {self.wikiUrl}\n"
            f"googleUrl: {self.googleSearchUrl}"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def wikiUrl(self) -> Optional[str]:
        if self.wikiId is None:
            return None
        return WIKIDATA_GET_LINK.format(self.wikiId)

    @property
    def googleSearchUrl(self) -> Optional[str]:
        if self.entityName is None:
            return None
        return GOOGLE_LINK.format(str(self.entityName).replace(" ", "%20"))
