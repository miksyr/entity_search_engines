"""Shared HTTP configuration: sessions, timeouts, and Wikimedia-compliant headers."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional

import requests

from .headers import default_http_headers


class HttpClient:
    """
    Thin wrapper around ``requests.Session`` with default headers and timeouts.

    Using a session improves performance when a caller makes many requests (connection reuse).
    """

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        default_timeout_seconds: float = 60.0,
        extra_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._session = session if session is not None else requests.Session()
        merged_headers: MutableMapping[str, str] = dict(default_http_headers())
        if extra_headers:
            merged_headers.update(extra_headers)
        self._session.headers.update(merged_headers)
        self._default_timeout_seconds = default_timeout_seconds

    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> requests.Response:
        return self._session.get(
            url,
            params=params,
            timeout=(
                timeout_seconds
                if timeout_seconds is not None
                else self._default_timeout_seconds
            ),
        )

    def get_json(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        response = self.get(
            url,
            params=params,
            timeout_seconds=timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
