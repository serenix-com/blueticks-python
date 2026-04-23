from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import AuthenticationError
from blueticks.types.ping import Ping


def test_ping_retrieve_returns_typed_model(mock_client) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/ping"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "account_id": "acc_abc",
                    "key_prefix": "xy12ab34",
                    "scopes": ["messages:read"],
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.ping()
    assert isinstance(result, Ping)
    assert result.account_id == "acc_abc"
    assert result.key_prefix == "xy12ab34"
    assert result.scopes == ["messages:read"]


def test_ping_propagates_authentication_error(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        body = {
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "request_id": "req_1",
            }
        }
        return httpx.Response(
            401,
            content=json.dumps(body).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        with pytest.raises(AuthenticationError) as info:
            client.ping()
    assert info.value.code == "authentication_required"
    assert info.value.request_id == "req_1"


def test_ping_missing_required_field_raises_validation_error(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{}", headers={"content-type": "application/json"})

    with mock_client(handler) as client:
        with pytest.raises(ValidationError):
            client.ping()
