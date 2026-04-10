"""Errors raised by this library."""


class EntitySearchEnginesError(Exception):
    """Base class for library-specific failures."""


class WikidataApiError(EntitySearchEnginesError):
    """The Wikidata Action API returned an error payload or an unexpected response."""
