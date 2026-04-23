from __future__ import annotations

import json

import httpx

from blueticks import Blueticks


def _campaign(cid: str = "cmp_1", **overrides) -> dict:
    data = {
        "id": cid,
        "name": "n",
        "audience_id": "aud_1",
        "status": "pending",
        "total_count": 0,
        "sent_count": 0,
        "delivered_count": 0,
        "read_count": 0,
        "failed_count": 0,
        "from": None,
        "created_at": "2026-04-23T00:00:00Z",
        "started_at": None,
        "completed_at": None,
        "aborted_at": None,
    }
    data.update(overrides)
    return data


def test_create_campaign_serializes_from_alias():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/campaigns"
        return httpx.Response(201, json=_campaign())

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    c = client.campaigns.create(
        name="n",
        audience_id="aud_1",
        text="hi",
        from_="+2",
        on_missing_variable="error",
    )
    assert c.id == "cmp_1"
    assert body_seen["from"] == "+2"
    assert "from_" not in body_seen
    assert body_seen["text"] == "hi"
    assert body_seen["on_missing_variable"] == "error"


def test_list_campaigns():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/campaigns"
        return httpx.Response(200, json={"data": [_campaign("cmp_1"), _campaign("cmp_2")]})

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    items = client.campaigns.list()
    assert len(items) == 2


def test_get_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/campaigns/cmp_1"
        return httpx.Response(200, json=_campaign("cmp_1"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    c = client.campaigns.get("cmp_1")
    assert c.id == "cmp_1"


def test_pause_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/campaigns/cmp_1/pause"
        return httpx.Response(200, json=_campaign("cmp_1", status="paused"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    c = client.campaigns.pause("cmp_1")
    assert c.status == "paused"


def test_resume_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/campaigns/cmp_1/resume"
        return httpx.Response(200, json=_campaign("cmp_1", status="running"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    c = client.campaigns.resume("cmp_1")
    assert c.status == "running"


def test_cancel_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/campaigns/cmp_1/cancel"
        return httpx.Response(200, json=_campaign("cmp_1", status="aborted"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    c = client.campaigns.cancel("cmp_1")
    assert c.status == "aborted"
