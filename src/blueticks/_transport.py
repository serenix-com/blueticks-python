from __future__ import annotations

import json
import random
import time
from typing import Any

import httpx

from blueticks._errors import (
    APIConnectionError,
    from_envelope,
)

_RETRIABLE_STATUS = {429, 502, 503, 504}
_IDEMPOTENT_METHODS = {"GET", "HEAD", "OPTIONS", "DELETE", "PATCH", "PUT"}
# Note: PATCH is not strictly idempotent per RFC 5789 but most REST APIs treat
# partial updates as idempotent in practice. Matches Stripe/OpenAI convention.
_BACKOFF_BASE_SECONDS = 0.5
_BACKOFF_CAP_SECONDS = 8.0


class Transport:
    """HTTP transport for the Blueticks API. Wraps httpx.Client with retries."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
        max_retries: int,
        user_agent_suffix: str | None,
        version: str,
        http_transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._version = version
        self._user_agent = f"blueticks-python/{version}"
        if user_agent_suffix:
            self._user_agent = f"{self._user_agent} {user_agent_suffix}"
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
            transport=http_transport,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None,
        body: dict[str, Any] | None,
        idempotency_key: str | None = None,
    ) -> Any:
        method = method.upper()
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": self._user_agent,
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        is_idempotent = method in _IDEMPOTENT_METHODS or idempotency_key is not None

        attempt = 0
        while True:
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    content=json.dumps(body).encode() if body is not None else None,
                    headers=headers,
                )
            except httpx.TransportError as exc:
                if attempt < self._max_retries:
                    self._sleep_backoff(attempt, retry_after=None)
                    attempt += 1
                    continue
                raise APIConnectionError(
                    status_code=None,
                    code=None,
                    message=f"connection error: {exc}",
                    request_id=None,
                    response=None,
                ) from exc

            if 200 <= response.status_code < 300:
                if not response.content:
                    return None
                return response.json()

            parsed_body: Any
            try:
                parsed_body = response.json()
            except (json.JSONDecodeError, ValueError):
                parsed_body = response.text

            retry_after = self._parse_retry_after(response) if response.status_code == 429 else None

            retriable_status = response.status_code in _RETRIABLE_STATUS
            if retriable_status and is_idempotent and attempt < self._max_retries:
                self._sleep_backoff(attempt, retry_after=retry_after)
                attempt += 1
                continue

            raise from_envelope(
                status_code=response.status_code,
                body=parsed_body,
                response=response,
                retry_after=retry_after,
            )

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> float | None:
        raw = response.headers.get("retry-after")
        if raw is None:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    @staticmethod
    def _sleep_backoff(attempt: int, *, retry_after: float | None) -> None:
        if retry_after is not None:
            time.sleep(retry_after)
            return
        backoff = min(_BACKOFF_BASE_SECONDS * (2**attempt), _BACKOFF_CAP_SECONDS)
        jitter = random.uniform(0, _BACKOFF_BASE_SECONDS)
        time.sleep(backoff + jitter)
