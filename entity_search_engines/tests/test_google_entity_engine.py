import os

from unittest import TestCase

from entity_search_engines.google_entity_engine import GoogleEntityEngine
from entity_search_engines.tests.example_entity import EXAMPLE_ENTITY


class TestGoogleEntityEngine(TestCase):

    def __init__(self, methodName='runTest'):
        super(TestGoogleEntityEngine, self).__init__(methodName=methodName)

    def setUp(self):
        super().setUp()
        self.googleEngine = GoogleEntityEngine(apiKey=os.environ['GOOGLE_SEARCH_API_KEY'])

    def test_get_entity(self):
        returnEntity = self.googleEngine.get_entity(googleId=EXAMPLE_ENTITY.googleId)
        self.assertEqual(EXAMPLE_ENTITY.googleId, returnEntity.googleId)
        self.assertEqual(EXAMPLE_ENTITY.wikiId, returnEntity.wikiId)
        # not exact matches here in case of updates on Google end
        self.assertTrue(EXAMPLE_ENTITY.entityName in returnEntity.entityName)
        self.assertTrue(EXAMPLE_ENTITY.entityType in returnEntity.entityType)

    def test_search_entity(self):
        returnEntities = self.googleEngine.search_for_entity(query=EXAMPLE_ENTITY.entityName, types=[EXAMPLE_ENTITY.entityType])
        topEntity = returnEntities[0]
        self.assertEqual(EXAMPLE_ENTITY.googleId, topEntity.googleId)
        self.assertEqual(EXAMPLE_ENTITY.wikiId, topEntity.wikiId)
        self.assertTrue(EXAMPLE_ENTITY.entityName in topEntity.entityName)
        self.assertTrue(EXAMPLE_ENTITY.entityType in topEntity.entityType)

    def test_get_entity_invalid(self):
        self.assertRaises(ValueError, self.googleEngine.get_entity, 1)

    def test_search_entity_invalid(self):
        noResults = self.googleEngine.search_for_entity(query='jfhsgjfdgjfdbvjghsbvfknsbdfgshgiur')
        self.assertEqual(len(noResults), 0)
