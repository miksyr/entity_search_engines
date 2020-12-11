

class EntityEngineBase:

    def search_for_entity(self, query):
        raise NotImplementedError(f'Error: {self.__class__.__name__} must implement `search_entity` function')

    def get_entity(self, entityId):
        raise NotImplementedError(f'Error: {self.__class__.__name__} must implement `get_entity` function')
