"""Default HTTP headers for outbound API requests (Wikimedia requires User-Agent)."""

from typing import Dict

DEFAULT_USER_AGENT = "EntitySearchEngines/0.2 (anonymous client)"


def default_http_headers() -> Dict[str, str]:
    return {"User-Agent": DEFAULT_USER_AGENT}
