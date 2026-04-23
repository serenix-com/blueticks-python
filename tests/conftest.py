from __future__ import annotations

import json
from typing import Any, Callable

import httpx
import pytest

from blueticks import Blueticks


@pytest.fixture
def mock_client() -> Callable[[Callable[[httpx.Request], httpx.Response]], Blueticks]:
    """Return a factory that builds a Blueticks client with an injected MockTransport."""

    def _factory(handler: Callable[[httpx.Request], httpx.Response]) -> Blueticks:
        transport = httpx.MockTransport(handler)
        return Blueticks(
            api_key="bt_test_fixture",
            base_url="https://example.test",
            _http_transport=transport,
        )

    return _factory


def json_response(status: int, body: Any) -> httpx.Response:
    return httpx.Response(
        status,
        content=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )
