from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.ping import Ping


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def test_ping_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/ping"
        return _ok(
            {
                "api": "ok",
                "accountId": "acc_abc",
                "whatsappConnections": [
                    {"id": "eng_1", "type": "gateway", "connected": True},
                ],
                "message": "1 engine connected",
            }
        )

    result = _client(handler).ping()
    assert isinstance(result, Ping)
    assert result.api == "ok"
    assert result.account_id == "acc_abc"
    assert len(result.whatsapp_connections) == 1
    assert result.whatsapp_connections[0].id == "eng_1"
    assert result.whatsapp_connections[0].type == "gateway"
    assert result.message == "1 engine connected"


def test_ping_empty_connections_when_no_engine():
    def handler(req: httpx.Request) -> httpx.Response:
        return _ok({"api": "ok", "accountId": "acc_abc", "whatsappConnections": []})

    result = _client(handler).ping()
    assert result.whatsapp_connections == []


def test_ping_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_ping_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).ping()
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_ping_1"


def test_ping_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).ping()
