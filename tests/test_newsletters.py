from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.newsletters import Newsletter
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _newsletter(nid: str = "120363201733549020@newsletter", **overrides) -> dict:
    data = {
        "id": nid,
        "name": "Acme Updates",
        "description": "Weekly product news",
        "owner": "15551234567@s.whatsapp.net",
        "createdAt": "2026-04-23T00:00:00Z",
        "subscribers": 1042,
        "invite": "XyZAbC123",
        "verification": "VERIFIED",
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# list() tests
# ---------------------------------------------------------------------------


def test_list_newsletters_returns_page(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/newsletters"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "data": [_newsletter()],
                    "has_more": False,
                    "next_cursor": None,
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with _client(handler) as client:
        result = client.newsletters.list()
    assert isinstance(result, Page)
    assert len(result.data) == 1
    assert isinstance(result.data[0], Newsletter)
    assert result.data[0].id == "120363201733549020@newsletter"
    assert result.data[0].name == "Acme Updates"
    assert result.data[0].subscribers == 1042
    assert result.data[0].verification == "VERIFIED"
    assert result.has_more is False
    assert result.next_cursor is None


def test_list_newsletters_passes_params(mock_client) -> None:
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        return httpx.Response(
            200,
            content=json.dumps({"data": [], "has_more": False, "next_cursor": None}).encode(),
            headers={"content-type": "application/json"},
        )

    with _client(handler) as client:
        client.newsletters.list(limit=10, cursor="tok_abc")
    assert params_seen.get("limit") == "10"
    assert params_seen.get("cursor") == "tok_abc"


def test_list_newsletters_raises_authentication_error_on_401(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            content=json.dumps(
                {
                    "error": {
                        "code": "authentication_required",
                        "message": "invalid key",
                        "requestId": "req_nsl_list_1",
                    }
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with _client(handler) as client:
        with pytest.raises(AuthenticationError) as exc_info:
            client.newsletters.list()
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_nsl_list_1"


# ---------------------------------------------------------------------------
# retrieve() tests
# ---------------------------------------------------------------------------


def test_retrieve_newsletter_returns_typed_model(mock_client) -> None:
    nid = "120363201733549020@newsletter"

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == f"/v1/newsletters/{nid}"
        return httpx.Response(
            200,
            content=json.dumps(_newsletter(nid)).encode(),
            headers={"content-type": "application/json"},
        )

    with _client(handler) as client:
        result = client.newsletters.retrieve(nid)
    assert isinstance(result, Newsletter)
    assert result.id == nid
    assert result.name == "Acme Updates"
    assert result.invite == "XyZAbC123"
    assert result.owner == "15551234567@s.whatsapp.net"


def test_retrieve_newsletter_raises_authentication_error_on_401(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            content=json.dumps(
                {
                    "error": {
                        "code": "authentication_required",
                        "message": "invalid key",
                        "requestId": "req_nsl_get_1",
                    }
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with _client(handler) as client:
        with pytest.raises(AuthenticationError) as exc_info:
            client.newsletters.retrieve("120363201733549020@newsletter")
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_nsl_get_1"


# ---------------------------------------------------------------------------
# create() tests
# ---------------------------------------------------------------------------


def test_create_newsletter_returns_typed_model():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/newsletters"
        return httpx.Response(201, json=_newsletter())

    result = _client(handler).newsletters.create(
        name="Acme Updates", description="Weekly product news"
    )
    assert isinstance(result, Newsletter)
    assert result.id == "120363201733549020@newsletter"
    assert result.name == "Acme Updates"
    assert result.description == "Weekly product news"
    assert body_seen == {"name": "Acme Updates", "description": "Weekly product news"}


def test_create_newsletter_without_description():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(201, json=_newsletter(description=None))

    result = _client(handler).newsletters.create(name="Acme Updates")
    assert isinstance(result, Newsletter)
    assert body_seen == {"name": "Acme Updates"}


def test_create_newsletter_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "authentication_required",
                    "message": "invalid key",
                    "requestId": "req_nsl_1",
                }
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).newsletters.create(name="Acme Updates")
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_nsl_1"


# ---------------------------------------------------------------------------
# Missing-required-field test
# ---------------------------------------------------------------------------


def test_newsletter_validation_fails_when_required_field_missing():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(201, json={})

    with pytest.raises(ValidationError):
        _client(handler).newsletters.create(name="Acme Updates")
