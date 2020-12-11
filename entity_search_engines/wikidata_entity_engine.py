import logging
import requests
import numpy as np

from itertools import groupby
from tqdm.auto import tqdm
from typing import List

from .entity import Entity
from .entity_engine_base import EntityEngineBase


class WikidataEntityEngine(EntityEngineBase):

    WIKIDATA_API_LINK = 'https://www.wikidata.org/w/api.php'
    WIKIPEDIA_API_LINK = 'https://www.wikipedia.org/w/api.php'
    GOOGLE_ID_PROPERTIES = ['P2671', 'P646']
    WIKI_ID_BATCH_SIZE = 50

    def get_properties_of_wiki_ids(self, wikiIds: List[str], propertyIds: List[str], languages='en'):
        numIds = len(wikiIds)
        if numIds > self.WIKI_ID_BATCH_SIZE:
            numBatches = np.ceil(numIds / self.WIKI_ID_BATCH_SIZE)
            batchIndexes = [list(v) for k, v in groupby(list(range(len(wikiIds))), key=lambda x: x // (len(wikiIds) / numBatches))]
            batchedWikiIds = [[wikiIds[index] for index in batchIndex] for batchIndex in batchIndexes]
        else:
            batchedWikiIds = [wikiIds]
        qidPropertyDictionary = {}
        for qidBatch in tqdm(batchedWikiIds, desc='Getting properties for batched wikiIds'):
            params = {'action': 'wbgetentities', 'format': 'json', 'ids': '|'.join(qidBatch), 'props': 'info|aliases|labels|descriptions|claims|datatype', 'languages': languages}
            results = requests.get(self.WIKIDATA_API_LINK, params=params).json()
            if 'error' in results:
                raise Exception(f'Something went wrong:\n{results["error"]}')
            for wikiId, source in results['entities'].items():
                qidPropertyDictionary.update({
                    wikiId: self._extract_property_from_entity_claims(wikiId=wikiId, entityClaims=source.get('claims', {}), propertyIds=propertyIds)
                })
        return qidPropertyDictionary

    @staticmethod
    def _extract_property_from_entity_claims(wikiId: str, entityClaims: dict, propertyIds):
        propertyDictionary = {}
        for propertyId in propertyIds:
            for x in entityClaims.get(propertyId, []):
                try:
                    propertyDictionary.update({propertyId: x['mainsnak']['datavalue']['value']})
                except KeyError:
                    logging.warning(msg=f"Couldn't find property {propertyId} for {wikiId}")
                    propertyDictionary.update({propertyId: None})
        return propertyDictionary

    @staticmethod
    def _process_result(result: dict):
        wikiId = list(result.keys())[0]
        source = result[wikiId]
        labels = source.get('labels', {})
        descriptions = source.get('descriptions', {})
        claims = source.get('claims', {})
        googleIds = [x['mainsnak']['datavalue']['value'] for propertyId in WikidataEntityEngine.GOOGLE_ID_PROPERTIES for x in claims.get(propertyId, [])]
        entity = Entity(
            entityName=labels['en'].get('value') if 'en' in labels else None,
            surfaceForms=[x['value'] for x in source.get('aliases', {}).get('en', [])],
            wikiId=source['id'],
            wikidataDescription=descriptions['en'].get('value') if 'en' in descriptions else None,
            googleId=googleIds[0] if len(googleIds) == 1 else None
        )
        entity.set_entity_source(entitySource='wikidata')
        return entity

    def get_entity(self, wikiId: str, properties: str = None, languages: str = 'en'):
        defaultProperties = 'info|aliases|labels|descriptions|claims|datatype'
        params = {'action': 'wbgetentities', 'format': 'json', 'ids': wikiId, 'props': properties or defaultProperties, 'languages': languages}
        result = requests.get(self.WIKIDATA_API_LINK, params=params).json()
        if 'error' in result:
            raise Exception(f'Something went wrong:\n{result["error"]}')
        return self._process_result(result=result['entities'])

    def search_for_entity(self, query: str):
        entities = []
        params = {'action': 'wbsearchentities', 'format': 'json', 'language': 'en', 'search': query}
        for entity in requests.get(self.WIKIDATA_API_LINK, params=params).json()['search']:
            entities.append(self.get_entity(wikiId=entity['id']))
        return entities

    def get_qids_from_wikipedia_url(self, url: str):
        params = {'action': 'query', 'format': 'json', 'titles': url.split('/')[-1], 'prop': 'pageprops'}
        qids = [
            page.get('pageprops', {}).get('wikibase_item')
            for page in requests.get(self.WIKIPEDIA_API_LINK, params=params).json()['query']['pages'].values()
        ]
        return [qid for qid in qids if qid is not None]
