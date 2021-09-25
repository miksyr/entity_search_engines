from unittest import TestCase

from entity_search_engines.wikidata_entity_engine import WikidataEntityEngine
from entity_search_engines.tests.example_entity import EXAMPLE_ENTITY


class TestGoogleEntityEngine(TestCase):
    def __init__(self, methodName="runTest"):
        super(TestGoogleEntityEngine, self).__init__(methodName=methodName)

    def setUp(self):
        super().setUp()
        self.wikidataEngine = WikidataEntityEngine()

    def test_get_entity(self):
        returnEntity = self.wikidataEngine.get_entity(wikiId=EXAMPLE_ENTITY.wikiId)
        self.assertEqual(EXAMPLE_ENTITY.googleId, returnEntity.googleId)
        self.assertEqual(EXAMPLE_ENTITY.wikiId, returnEntity.wikiId)
        # not exact matches here in case of updates on Wikidata end
        self.assertTrue(EXAMPLE_ENTITY.entityName in returnEntity.entityName)
        self.assertIsNone(returnEntity.entityType)

    def test_search_entity(self):
        returnEntities = self.wikidataEngine.search_for_entity(
            query=f"{EXAMPLE_ENTITY.entityName} FC"
        )
        topEntity = returnEntities[0]
        self.assertEqual(EXAMPLE_ENTITY.googleId, topEntity.googleId)
        self.assertEqual(EXAMPLE_ENTITY.wikiId, topEntity.wikiId)
        self.assertTrue(EXAMPLE_ENTITY.entityName in topEntity.entityName)
        self.assertIsNone(topEntity.entityType)

    def test_get_entity_invalid(self):
        self.assertRaises(Exception, self.wikidataEngine.get_entity, 1)

    def test_search_entity_invalid(self):
        noResults = self.wikidataEngine.search_for_entity(
            query="jfhsgjfdgjfdbvjghsbvfknsbdfgshgiur"
        )
        self.assertEqual(len(noResults), 0)
