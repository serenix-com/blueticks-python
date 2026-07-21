from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.page import Page
from blueticks.types.webhooks import Webhook


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _webhook(wid="wh_1", **overrides):
    data = {
        "id": wid,
        "url": "https://a.com/hook",
        "events": ["message.delivered"],
        "description": None,
        "status": "enabled",
        "createdAt": "2026-04-23T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_create_webhook():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/webhooks"
        return _ok(_webhook(), status=201)

    wh = _client(handler).webhooks.create(
        url="https://a.com/hook", events=["message.delivered"], description="d"
    )
    assert isinstance(wh, Webhook)
    assert wh.id == "wh_1"
    assert wh.status == "enabled"
    assert wh.created_at.year == 2026
    assert body_seen == {
        "url": "https://a.com/hook",
        "events": ["message.delivered"],
        "description": "d",
    }


def test_list_webhooks():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/webhooks"
        return _page([_webhook("wh_1"), _webhook("wh_2")])

    page = _client(handler).webhooks.list()
    assert isinstance(page, Page)
    assert len(page.data) == 2
    assert page.data[0].id == "wh_1"


def test_get_webhook():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/webhooks/wh_1"
        return _ok(_webhook("wh_1"))

    assert _client(handler).webhooks.get("wh_1").id == "wh_1"


def test_update_webhook():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/webhooks/wh_1"
        return _ok(_webhook("wh_1", status="disabled"))

    wh = _client(handler).webhooks.update("wh_1", status="disabled")
    assert wh.status == "disabled"
    assert body_seen == {"status": "disabled"}


def test_delete_webhook():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/webhooks/wh_1"
        return _ok({"id": "wh_1", "deleted": True})

    result = _client(handler).webhooks.delete("wh_1")
    assert isinstance(result, DeletedResource)
    assert result.id == "wh_1"
    assert result.deleted is True


def test_webhooks_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_wh_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).webhooks.get("wh_1")
    assert exc_info.value.request_id == "req_wh_1"


def test_webhook_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).webhooks.get("wh_1")
