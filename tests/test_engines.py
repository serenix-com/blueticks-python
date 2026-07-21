from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.engines import Engine


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def test_engines_list_returns_list_of_engines():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/engines"
        return httpx.Response(
            200,
            json={
                "success": True,
                "data": [
                    {
                        "id": "eng_1",
                        "type": "gateway",
                        "connected": True,
                        "state": "CONNECTED",
                        "stream": "CONNECTED",
                        "hasSynced": True,
                    },
                    {"id": "eng_2", "type": "regular", "connected": False},
                ],
            },
        )

    result = _client(handler).engines.list()
    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], Engine)
    assert result[0].id == "eng_1"
    assert result[0].type == "gateway"
    assert result[0].connected is True
    assert result[0].has_synced is True
    assert result[1].type == "regular"
    assert result[1].connected is False


def test_engines_list_empty_when_no_engine():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": True, "data": []})

    assert _client(handler).engines.list() == []


def test_optional_fields_accept_explicit_null_and_omission():
    """The API is inconsistent: a CONNECTED engine OMITS state/stream/hasSynced,
    a DISCONNECTED engine returns them as explicit ``null``. Both must parse.
    """

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "success": True,
                "data": [
                    # CONNECTED: optional fields omitted entirely.
                    {"id": "eng_connected", "type": "gateway", "connected": True},
                    # DISCONNECTED: optional fields present as explicit null.
                    {
                        "id": "eng_disconnected",
                        "type": "regular",
                        "connected": False,
                        "state": None,
                        "stream": None,
                        "hasSynced": None,
                    },
                ],
            },
        )

    engines = _client(handler).engines.list()
    assert engines[0].state is None and engines[0].has_synced is None
    assert engines[1].state is None and engines[1].stream is None
    assert engines[1].has_synced is None


def test_engines_list_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_eng_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).engines.list()
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_eng_1"


def test_engine_validation_fails_when_required_field_missing():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": True, "data": [{}]})

    with pytest.raises(ValidationError):
        _client(handler).engines.list()
