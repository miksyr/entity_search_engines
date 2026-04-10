from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Sequence

from ..http import HttpClient
from ..models.entity import Entity
from .base import EntityEngineBase
from .wikidata import WikidataEntityEngine

logger = logging.getLogger(__name__)


class GoogleEntityEngine(EntityEngineBase):
    """Search and fetch entities via the public Google Knowledge Graph Search API."""

    _KNOWLEDGE_GRAPH_SEARCH_URL = (
        "https://kgsearch.googleapis.com/v1/entities:search"
    )

    def __init__(
        self,
        apiKey: str,
        *,
        http_client: Optional[HttpClient] = None,
        wikidata_entity_engine: Optional[WikidataEntityEngine] = None,
    ) -> None:
        self.apiKey = apiKey
        self._http_client = http_client if http_client is not None else HttpClient()
        self._wikidata_entity_engine = (
            wikidata_entity_engine
            if wikidata_entity_engine is not None
            else WikidataEntityEngine(http_client=self._http_client)
        )

    def _get_entity_from_source(self, source: Dict[str, Any]) -> Entity:
        detailed_description = source.get("detailedDescription", {}).get("articleBody")
        description_url = source.get("detailedDescription", {}).get("url")
        matching_qid: Optional[str]
        if description_url is not None:
            qids = self._wikidata_entity_engine.get_qids_from_wikipedia_url(
                url=description_url,
            )
            matching_qid = "|".join(qids) if qids else None
        else:
            matching_qid = None
        raw_schema_types = source.get("@type")
        if isinstance(raw_schema_types, list):
            entity_type = "|".join(raw_schema_types)
        elif raw_schema_types:
            entity_type = str(raw_schema_types)
        else:
            entity_type = ""
        raw_google_id = source.get("@id")
        google_id = (
            str(raw_google_id).replace("kg:", "")
            if raw_google_id is not None
            else None
        )
        entity = Entity(
            entityName=source.get("name"),
            entityType=entity_type,
            wikiId=matching_qid if matching_qid != "" else None,
            wikidataDescription=None,
            googleId=google_id,
            googleDescription=detailed_description or source.get("description", ""),
            surfaceForms=[source.get("name")],
        )
        entity.set_entity_source(entitySource="Google")
        return entity

    def _search(self, params: Dict[str, Any]) -> List[Entity]:
        request_params: Dict[str, Any] = {
            "key": self.apiKey,
            "indent": True,
        }
        request_params.update(params)
        response = self._http_client.get(
            self._KNOWLEDGE_GRAPH_SEARCH_URL,
            params=request_params,
            timeout_seconds=60.0,
        )
        if response.status_code != 200:
            logger.warning(
                "Google Knowledge Graph API returned %s: %s",
                response.status_code,
                response.text[:500],
            )
            return []
        try:
            payload = response.json()
        except json.JSONDecodeError as error:
            logger.warning("Google Knowledge Graph API returned non-JSON: %s", error)
            return []
        results = payload.get("itemListElement", [])
        entities: List[Entity] = []
        for element in results:
            result = element.get("result")
            if result is None:
                continue
            entities.append(self._get_entity_from_source(source=result))
        return entities

    def search_for_entity(
        self,
        query: str,
        types: Optional[Sequence[str]] = None,
        limit: Optional[int] = 3,
    ) -> List[Entity]:
        params: Dict[str, Any] = {"query": query}
        if types is not None:
            params["types"] = list(types)
        if limit is not None:
            params["limit"] = limit
        return self._search(params=params)

    def get_entity(self, googleId: str, **kwargs: Any) -> Entity:
        del kwargs
        normalized_google_id = str(googleId).replace("kg:", "")
        results = self._search(params={"ids": normalized_google_id})
        if not results:
            raise ValueError("googleId not found")
        return results[0]
