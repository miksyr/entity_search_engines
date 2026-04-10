from unittest import TestCase

from entity_search_engines import Entity


class TestEntity(TestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName=methodName)
        self.testSource = "testSource"

    def setUp(self):
        super().setUp()
        self.exampleEntity = Entity(entityName="TestEntity")

    def test_set_entity_source(self):
        self.assertIsNone(self.exampleEntity.entitySource)
        self.exampleEntity.set_entity_source(entitySource=self.testSource)
        self.assertEqual(self.exampleEntity.entitySource, self.testSource)
