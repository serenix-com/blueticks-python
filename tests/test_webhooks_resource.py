from __future__ import annotations

import json

import httpx

from blueticks import Blueticks


def _webhook_payload(wid: str = "wh_1", **overrides) -> dict:
    data = {
        "id": wid,
        "url": "https://a.com/hook",
        "events": ["message.delivered"],
        "description": None,
        "status": "enabled",
        "created_at": "2026-04-23T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_create_webhook_returns_secret():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/webhooks"
        return httpx.Response(
            201,
            json=_webhook_payload(secret="whsec_abc"),
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    wh = client.webhooks.create(
        url="https://a.com/hook",
        events=["message.delivered"],
        description="d",
    )
    assert wh.secret == "whsec_abc"
    assert body_seen["url"] == "https://a.com/hook"
    assert body_seen["events"] == ["message.delivered"]
    assert body_seen["description"] == "d"


def test_list_webhooks():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/webhooks"
        return httpx.Response(
            200,
            json={
                "data": [_webhook_payload("wh_1"), _webhook_payload("wh_2")],
                "has_more": False,
                "next_cursor": None,
            },
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    page = client.webhooks.list()
    assert len(page.data) == 2
    assert page.data[0].id == "wh_1"
    assert page.has_more is False


def test_get_webhook():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/webhooks/wh_1"
        return httpx.Response(200, json=_webhook_payload("wh_1"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    wh = client.webhooks.get("wh_1")
    assert wh.id == "wh_1"


def test_update_webhook():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/webhooks/wh_1"
        return httpx.Response(200, json=_webhook_payload("wh_1", status="disabled"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    wh = client.webhooks.update("wh_1", status="disabled")
    assert wh.status == "disabled"
    assert body_seen == {"status": "disabled"}


def test_delete_webhook_returns_typed_ref():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/webhooks/wh_1"
        return httpx.Response(200, json={"id": "wh_1", "deleted": True})

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    result = client.webhooks.delete("wh_1")
    assert result.id == "wh_1"
    assert result.deleted is True


def test_rotate_secret_returns_new_secret():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/webhooks/wh_1/rotate-secret"
        return httpx.Response(200, json=_webhook_payload("wh_1", secret="whsec_new"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    wh = client.webhooks.rotate_secret("wh_1")
    assert wh.secret == "whsec_new"
