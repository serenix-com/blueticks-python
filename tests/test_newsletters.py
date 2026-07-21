from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.newsletters import Newsletter, NewsletterListItem
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _list_item(**overrides):
    data = {
        "chatId": "120363201733549020@newsletter",
        "name": "Acme Updates",
        "description": "Weekly product news",
        "createdAt": "2026-04-23T00:00:00Z",
        "subscribers": 1042,
        "invite": "XyZAbC123",
        "verification": "VERIFIED",
    }
    data.update(overrides)
    return data


def _newsletter(**overrides):
    data = {
        "newsletterId": "120363201733549020@newsletter",
        "name": "Acme Updates",
        "description": "Weekly product news",
        "createdAt": "2026-04-23T00:00:00Z",
        "subscribers": 1042,
        "invite": "XyZAbC123",
        "verification": "VERIFIED",
    }
    data.update(overrides)
    return data


def test_list_newsletters_returns_page():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.url.path == "/v1/newsletters"
        return _page([_list_item()])

    page = _client(handler).newsletters.list(search_token="acme", limit=10)
    assert isinstance(page, Page)
    assert isinstance(page.data[0], NewsletterListItem)
    assert page.data[0].chat_id == "120363201733549020@newsletter"
    assert page.data[0].subscribers == 1042
    assert page.data[0].verification == "VERIFIED"
    assert params_seen["searchToken"] == "acme"


def test_create_newsletter():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/newsletters"
        return _ok(_newsletter(), status=201)

    result = _client(handler).newsletters.create(
        name="Acme Updates", description="Weekly product news"
    )
    assert isinstance(result, Newsletter)
    assert result.newsletter_id == "120363201733549020@newsletter"
    assert body_seen == {"name": "Acme Updates", "description": "Weekly product news"}


def test_retrieve_newsletter():
    nid = "120363201733549020@newsletter"

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == f"/v1/newsletters/{nid}"
        return _ok(_newsletter())

    result = _client(handler).newsletters.retrieve(nid)
    assert isinstance(result, Newsletter)
    assert result.newsletter_id == nid
    assert result.invite == "XyZAbC123"


def test_newsletters_retrieve_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_nsl_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).newsletters.retrieve("120363201733549020@newsletter")
    assert exc_info.value.request_id == "req_nsl_1"


def test_newsletter_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({}, status=201)).newsletters.create(name="Acme")
