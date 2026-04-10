from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union

from tqdm.auto import tqdm

from ..exceptions import WikidataApiError
from ..http import HttpClient
from ..models.entity import Entity
from .base import EntityEngineBase

logger = logging.getLogger(__name__)


def _chunk_list(items: List[str], chunk_size: int) -> Iterable[List[str]]:
    for index in range(0, len(items), chunk_size):
        yield items[index : index + chunk_size]


class WikidataEntityEngine(EntityEngineBase):
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    GOOGLE_ID_PROPERTIES = ("P2671", "P646")
    WIKI_ID_BATCH_SIZE = 50

    def __init__(self, *, http_client: Optional[HttpClient] = None) -> None:
        self._http_client = http_client if http_client is not None else HttpClient()

    def get_properties_of_wiki_ids(
        self,
        wiki_ids: List[str],
        property_ids: List[str],
        *,
        languages: Optional[str] = "en",
        show_progress: bool = False,
    ) -> Dict[str, Dict[str, Union[str, int, None]]]:
        qid_property_dictionary: Dict[str, Dict[str, Union[str, int, None]]] = {}
        batches = list(_chunk_list(wiki_ids, self.WIKI_ID_BATCH_SIZE))
        batch_iterator: Iterable[List[str]] = batches
        if show_progress:
            batch_iterator = tqdm(
                batches,
                desc="Getting properties for batched wiki_ids",
            )
        for qid_batch in batch_iterator:
            params = {
                "action": "wbgetentities",
                "format": "json",
                "ids": "|".join(qid_batch),
                "props": "info|aliases|labels|descriptions|claims|datatype",
                "languages": languages,
            }
            results = self._http_client.get_json(
                self.WIKIDATA_API_URL,
                params=params,
            )
            if "error" in results:
                raise WikidataApiError(str(results["error"]))
            for wiki_id, source in results["entities"].items():
                qid_property_dictionary[wiki_id] = (
                    self._extract_property_from_entity_claims(
                        wiki_id=wiki_id,
                        entity_claims=source.get("claims", {}),
                        property_ids=property_ids,
                    )
                )
        return qid_property_dictionary

    @staticmethod
    def _extract_property_from_entity_claims(
        wiki_id: str,
        entity_claims: Dict[str, List[Dict[str, Any]]],
        property_ids: List[str],
    ) -> Dict[str, Union[str, int, None]]:
        property_dictionary: Dict[str, Union[str, int, None]] = {}
        for property_id in property_ids:
            for claim in entity_claims.get(property_id, []):
                try:
                    property_dictionary[property_id] = claim["mainsnak"]["datavalue"][
                        "value"
                    ]
                except KeyError:
                    logger.warning(
                        "Could not read property %s for wiki_id %s",
                        property_id,
                        wiki_id,
                    )
                    property_dictionary[property_id] = None
        return property_dictionary

    @staticmethod
    def _process_result(result: Dict[str, Any]) -> Entity:
        wiki_id = next(iter(result.keys()))
        source = result[wiki_id]
        labels = source.get("labels", {})
        descriptions = source.get("descriptions", {})
        claims = source.get("claims", {})
        google_ids = [
            claim["mainsnak"]["datavalue"]["value"]
            for property_id in WikidataEntityEngine.GOOGLE_ID_PROPERTIES
            for claim in claims.get(property_id, [])
        ]
        entity = Entity(
            entityName=labels["en"].get("value") if "en" in labels else None,
            surfaceForms=[
                alias["value"]
                for alias in source.get("aliases", {}).get("en", [])
            ],
            wikiId=source["id"],
            wikidataDescription=descriptions["en"].get("value")
            if "en" in descriptions
            else None,
            googleId=google_ids[0] if len(google_ids) == 1 else None,
        )
        entity.set_entity_source(entitySource="wikidata")
        return entity

    def get_entity(
        self,
        wiki_id: str,
        *,
        properties: Optional[List[str]] = None,
        languages: Optional[str] = "en",
    ) -> Entity:
        default_properties = [
            "info",
            "aliases",
            "labels",
            "descriptions",
            "claims",
            "datatype",
        ]
        property_query_string = "|".join(properties or default_properties)
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": wiki_id,
            "props": property_query_string,
            "languages": languages,
        }
        result = self._http_client.get_json(self.WIKIDATA_API_URL, params=params)
        if "error" in result:
            raise WikidataApiError(str(result["error"]))
        return self._process_result(result=result["entities"])

    def search_for_entity(
        self,
        query: str,
        types: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Entity]:
        del types, limit  # Wikidata text search does not use these filters.
        params = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": query,
        }
        payload = self._http_client.get_json(self.WIKIDATA_API_URL, params=params)
        entities: List[Entity] = []
        for item in payload.get("search", []):
            entities.append(self.get_entity(wiki_id=item["id"]))
        return entities

    def get_qids_from_wikipedia_url(self, url: str) -> List[str]:
        from urllib.parse import unquote, urlparse

        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path or ""
        if "/wiki/" not in path:
            return []
        title_segment = unquote(path.split("/wiki/", 1)[1])
        if not title_segment:
            return []
        if hostname in ("www.wikipedia.org", "wikipedia.org"):
            wikipedia_api_host = "en.wikipedia.org"
        else:
            wikipedia_api_host = hostname
        wikipedia_api_url = f"https://{wikipedia_api_host}/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": title_segment,
            "prop": "pageprops",
        }
        response = self._http_client.get(
            wikipedia_api_url,
            params=params,
            timeout_seconds=30.0,
        )
        if response.status_code != 200:
            logger.warning(
                "Wikipedia API request failed (%s) for %s",
                response.status_code,
                wikipedia_api_url,
            )
            return []
        try:
            payload = response.json()
        except json.JSONDecodeError as error:
            logger.warning("Wikipedia API returned non-JSON for %s: %s", url, error)
            return []
        pages = payload.get("query", {}).get("pages", {})
        qids = [
            page.get("pageprops", {}).get("wikibase_item")
            for page in pages.values()
            if isinstance(page, dict)
        ]
        return [qid for qid in qids if qid is not None]
