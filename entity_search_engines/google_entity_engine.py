import json
from typing import Any, Dict, List, Optional

import requests

from .entity import Entity
from .entity_engine_base import EntityEngineBase
from .wikidata_entity_engine import WikidataEntityEngine


class GoogleEntityEngine(EntityEngineBase):

    API_URL = (
        "https://kgsearch.googleapis.com/v1/entities:search?&key={API_KEY}&indent=True"
    )

    def __init__(self, apiKey: str):
        self.apiKey = apiKey
        self.apiUrl = self.API_URL.format(API_KEY=apiKey)

    @staticmethod
    def _get_entity_from_source(source: Dict[str, Any]) -> Entity:
        detailedDescription = source.get("detailedDescription", {}).get("articleBody")
        descriptionUrl = source.get("detailedDescription", {}).get("url")
        matchingQid = (
            "|".join(
                WikidataEntityEngine().get_qids_from_wikipedia_url(url=descriptionUrl)
            )
            if descriptionUrl is not None
            else None
        )
        entity = Entity(
            entityName=source.get("name"),
            entityType="|".join(source.get("@type", "")),
            wikiId=matchingQid if matchingQid != "" else None,
            wikidataDescription=None,
            googleId=source.get("@id").replace("kg:", ""),
            googleDescription=detailedDescription or source.get("description", ""),
            surfaceForms=[source.get("name")],
        )
        entity.set_entity_source(entitySource="Google")
        return entity

    def _search(self, params: Dict[str, Any]) -> List[Entity]:
        results = json.loads(requests.get(self.apiUrl, params=params).text).get(
            "itemListElement", []
        )
        return [
            self._get_entity_from_source(source=result["result"]) for result in results
        ]

    def search_for_entity(
        self, query: str, types: Optional[List[str]] = None, limit: Optional[int] = 3
    ) -> List[Entity]:
        params = {"query": query}
        if types is not None:
            params["types"] = types
        if limit is not None:
            params["limit"] = limit
        return self._search(params=params)

    def get_entity(self, googleId: str) -> Entity:
        googleId = str(googleId).replace("kg:", "")
        try:
            return self._search(params={"ids": googleId})[0]
        except IndexError:
            raise ValueError("googleId not found")
