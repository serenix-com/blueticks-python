from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.identity import Identity, IdentityBatchResponse


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


def _identity(**overrides):
    data = {
        "input": "120813554507870@lid",
        "resolved": True,
        "canonical": "14155551234@c.us",
        "phone": "14155551234",
        "lid": "120813554507870@lid",
        "aliases": ["14155551234@s.whatsapp.net"],
        "type": "user",
        "source": "engine",
    }
    data.update(overrides)
    return data


def test_retrieve_identity_url_encodes_id():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.raw_path == b"/v1/identity/120813554507870%40lid"
        return _ok(_identity())

    result = _client(handler).identity.retrieve("120813554507870@lid")
    assert isinstance(result, Identity)
    assert result.resolved is True
    assert result.phone == "14155551234"
    assert result.type == "user"
    assert result.source == "engine"


def test_retrieve_identity_unresolved():
    unresolved = _identity(
        resolved=False,
        canonical=None,
        phone=None,
        lid=None,
        aliases=[],
        type="unknown",
        source="unknown",
    )
    result = _client(lambda req: _ok(unresolved)).identity.retrieve("1@lid")
    assert result.resolved is False
    assert result.canonical is None
    assert result.aliases == []


def test_resolve_batch_identities():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/identity/resolve"
        return _ok([_identity(), _identity(input="x@g.us", type="group", source="cache")])

    result = _client(handler).identity.resolve_batch(["120813554507870@lid", "x@g.us"])
    assert isinstance(result, IdentityBatchResponse)
    assert [i.type for i in result.data] == ["user", "group"]
    assert result.data[1].source == "cache"
    assert body_seen == {"ids": ["120813554507870@lid", "x@g.us"]}


def test_identity_retrieve_raises_authentication_error_on_401():
    with pytest.raises(AuthenticationError) as exc_info:
        _client(lambda req: _unauth()).identity.retrieve("1@lid")
    assert exc_info.value.request_id == "req_x1"
    assert exc_info.value.code == "authentication_required"


def test_identity_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).identity.retrieve("1@lid")


def test_resolve_batch_accepts_bare_array_wire_shape():
    def handler(req: httpx.Request) -> httpx.Response:
        return _ok([_identity(input="1@lid", resolved=False, canonical=None, phone=None)])

    result = _client(handler).identity.resolve_batch(["1@lid"])
    assert result.data[0].resolved is False
    assert result.data[0].canonical is None
