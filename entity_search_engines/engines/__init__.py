"""Knowledge-base backends (Google Knowledge Graph, Wikidata)."""

from .base import EntityEngineBase
from .google import GoogleEntityEngine
from .wikidata import WikidataEntityEngine

__all__ = [
    "EntityEngineBase",
    "GoogleEntityEngine",
    "WikidataEntityEngine",
]
