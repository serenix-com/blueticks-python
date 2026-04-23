from __future__ import annotations

import json
from datetime import datetime

import httpx
import pytest
from pydantic import ValidationError

from blueticks import AuthenticationError
from blueticks.types.account import Account


def test_account_retrieve_returns_typed_model(mock_client) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/account"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "id": "acc_1",
                    "name": "Acme",
                    "timezone": "America/New_York",
                    "created_at": "2026-04-22T10:00:00Z",
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.account.retrieve()
    assert isinstance(result, Account)
    assert result.id == "acc_1"
    assert result.name == "Acme"
    assert result.timezone == "America/New_York"
    assert isinstance(result.created_at, datetime)


def test_account_retrieve_accepts_null_timezone(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "id": "acc_2",
                    "name": "Nobody",
                    "timezone": None,
                    "created_at": "2026-01-01T00:00:00Z",
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.account.retrieve()
    assert result.timezone is None


def test_account_retrieve_propagates_authentication_error(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        body = {
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "request_id": "req_a",
            }
        }
        return httpx.Response(
            401,
            content=json.dumps(body).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        with pytest.raises(AuthenticationError) as info:
            client.account.retrieve()
    assert info.value.code == "authentication_required"
    assert info.value.message == "bad key"
    assert info.value.request_id == "req_a"


def test_account_retrieve_missing_required_field_raises_validation_error(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{}", headers={"content-type": "application/json"})

    with mock_client(handler) as client:
        with pytest.raises(ValidationError):
            client.account.retrieve()
