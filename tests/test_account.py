from __future__ import annotations

import datetime

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.account import Account


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _auth_error(request_id: str) -> httpx.Response:
    return httpx.Response(
        401,
        json={
            "success": False,
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "request_id": request_id,
            },
        },
    )


def test_account_retrieve_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/account"
        return _ok(
            {
                "id": "acc_1",
                "name": "Acme",
                "userEmail": "owner@acme.co",
                "timezone": "America/New_York",
                "createdAt": "2026-04-22T10:00:00Z",
            }
        )

    result = _client(handler).account.retrieve()
    assert isinstance(result, Account)
    assert result.id == "acc_1"
    assert result.name == "Acme"
    assert result.user_email == "owner@acme.co"
    assert result.timezone == "America/New_York"
    assert isinstance(result.created_at, datetime.datetime)
    assert result.created_at.year == 2026


def test_account_retrieve_raises_authentication_error_on_401():
    with pytest.raises(AuthenticationError) as exc_info:
        _client(lambda req: _auth_error("req_acc_1")).account.retrieve()
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_acc_1"


def test_account_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).account.retrieve()
