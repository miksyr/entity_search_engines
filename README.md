# Entity Search Engines

This package provides classes that wrap the Google Knowledge Graph API and the Wikidata API.

It provides;  
* `search_for_entity` functions for both of these knowledge bases, for when you need to do a text search for entities with unknown Google/Wikidata ids.
* `get_entity` functions for both knowledge bases for when you know the IDs for an entity and want to pull more information.

## Installation
```pip install entity_search_engines```

## Usage

There are some slight differences when using either the Google or Wikidata engines.
* Both engines will attempt to retrieve both IDs for an entity.  For example, when using the Google search class, it'll also attempt to fill in the WikiID for the returned entity class.  However, sometimes this mapping isn't available and it would be up to the user to resolve this by using both engines.
* Descriptions will only be filled in for the engine type that has been used.  (i.e. the Google engine will only fill out the "googleDescription" for an entity and not the "wikidataDescription").
* The wikidata API currently returns many more surface forms than the Google API (as Google doesn't seem to provide that information).

Merging both classes into a single class that does everything would seem like a good idea, but entangling functionalities could create more problems than it solves.

### Google API
```
from entity_search_engines import GoogleEntityEngine

googleSearchEngine = GoogleEntityEngine(apiKey=API_KEY)

searchResults = googleSearchEngine.search_for_entity(
    query='Liverpool', 
    types=['SportsTeam'],
    limit=3
)

print(searchResults[0])  # this is an 'Entity' class


Entity("Liverpool F.C.", type: SportsTeam|Corporation|Organization|Thing, qid: Q1130849, googleId: /m/04ltf, entitySource: Google)
surfaceForms: ['Liverpool F.C.']
googleDescription: Liverpool Football Club is a professional football club in Liverpool, England, that competes in the Premier League, the top tier of English football. 
wikidataDescription: None
wikiUrl: https://wikidata.org/wiki/Q1130849
googleUrl: https://www.google.com/search?q=Liverpool%20F.C.
```

Similarly, the `googleSearchEngine.get_entity(googleId=GOOGLE_ID)` can be used to retrieve an Entity class containing relevant information.

### Wikidata API
```
from entity_search_engines import WikidataEntityEngine

wikidataSearchEngine = WikidataEntityEngine()

searchResults = wikidataSearchEngine.search_for_entity(
    query='Liverpool FC'
)

print(searchResults[0])  # this is an 'Entity' class


Entity("Liverpool F.C.", type: None, qid: Q1130849, googleId: /m/04ltf, entitySource: wikidata)
surfaceForms: ['Liverpool Football Club', 'Liverpool FC', 'Liverpool', 'The Reds', 'LFC']
googleDescription: None
wikidataDescription: association football club in Liverpool, England
wikiUrl: https://wikidata.org/wiki/Q1130849
googleUrl: https://www.google.com/search?q=Liverpool%20F.C.
```

Similarly, the `wikidataSearchEngine.get_entity(wikiId=WIKI_ID)` can be used to retrieve an Entity class containing relevant information.
