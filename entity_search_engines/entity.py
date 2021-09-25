from typing import Sequence

GOOGLE_LINK = "https://www.google.com/search?q={}"
WIKIDATA_SEARCH_LINK = "https://www.wikidata.org/w/index.php?search={}"
WIKIDATA_GET_LINK = "https://wikidata.org/wiki/{}"


class Entity:
    def __init__(
        self,
        entityName: str,
        entityType: str = None,
        wikiId: str = None,
        wikidataDescription: str = None,
        googleId: str = None,
        googleDescription: str = None,
        surfaceForms: Sequence[str] = None,
    ):
        """
        General class that represents an entity.  Contains info for google and wikidata.

        :param entityName: str
        :param entityType: str
        :param wikiId: str
        :param wikidataDescription: str
        :param googleId: str
        :param googleDescription: str
        :param surfaceForms: List[str]
        """
        self.entityName = entityName
        self.entityType = entityType
        self.wikiId = wikiId
        self.wikidataDescription = wikidataDescription
        self.googleId = googleId
        self.googleDescription = googleDescription
        self.surfaceForms = surfaceForms or []
        self.entitySource = None

    def set_entity_source(self, entitySource: str) -> None:
        """
        Sets the source of an entity.  E.g. Google or Wikidata
        :param entitySource: str
        """
        self.entitySource = entitySource

    def __repr__(self):
        baseRepresentation = f'Entity("{self.entityName}", type: {self.entityType}, qid: {self.wikiId}, googleId: {self.googleId}, entitySource: {self.entitySource})'
        return f"{baseRepresentation}\nsurfaceForms: {self.surfaceForms}\ngoogleDescription: {self.googleDescription}\nwikidataDescription: {self.wikidataDescription}\nwikiUrl: {self.wikiUrl}\ngoogleUrl: {self.googleSearchUrl}"

    def __str__(self):
        return self.__repr__()

    @property
    def wikiUrl(self) -> str:
        return (
            WIKIDATA_GET_LINK.format(self.wikiId) if self.wikiId is not None else None
        )

    @property
    def googleSearchUrl(self) -> str:
        return GOOGLE_LINK.format(str(self.entityName).replace(" ", "%20"))
