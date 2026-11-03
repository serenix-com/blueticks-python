from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.realtime import RealtimeToken


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _unauth():
    return httpx.Response(
        401,
        json={
            "success": False,
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "request_id": "req_x1",
            },
        },
    )


def test_create_realtime_token():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/realtime/token"
        return _ok(
            {
                "brokerUrl": "wss://mqtt.example.test:8084/mqtt",
                "username": "api_u1",
                "password": "s3cret",
                "expiresAt": "2036-04-23T00:00:00Z",
                "expiresInSeconds": 315360000,
                "topics": {"messages": "api/u1/messages"},
            },
            status=201,
        )

    token = _client(handler).realtime.create_token()
    assert isinstance(token, RealtimeToken)
    assert token.broker_url == "wss://mqtt.example.test:8084/mqtt"
    assert token.username == "api_u1"
    assert token.expires_in_seconds == 315360000
    assert token.expires_at.year == 2036
    assert token.topics.messages == "api/u1/messages"


def test_realtime_raises_authentication_error_on_401():
    with pytest.raises(AuthenticationError) as exc_info:
        _client(lambda req: _unauth()).realtime.create_token()
    assert exc_info.value.request_id == "req_x1"
    assert exc_info.value.code == "authentication_required"


def test_realtime_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({}, status=201)).realtime.create_token()
