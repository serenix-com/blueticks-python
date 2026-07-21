from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.campaigns import Campaign
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items):
    return httpx.Response(
        200,
        json={"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)},
    )


def _campaign(cid="cmp_1", **overrides):
    data = {
        "cmpId": cid,
        "name": "n",
        "audienceId": "aud_1",
        "status": "pending",
        "totalCount": 0,
        "sentCount": 0,
        "deliveredCount": 0,
        "readCount": 0,
        "failedCount": 0,
        "createdAt": "2026-04-23T00:00:00Z",
        "startedAt": None,
        "completedAt": None,
        "abortedAt": None,
    }
    data.update(overrides)
    return data


def test_create_campaign_serializes_camel_case_body():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/campaigns"
        return _ok(_campaign())

    c = _client(handler).campaigns.create(
        name="n",
        audience_id="aud_1",
        text="hi",
        media_url="https://cdn.example/x.jpg",
        media_caption="cap",
        on_missing_variable="skip",
    )
    assert isinstance(c, Campaign)
    assert c.cmp_id == "cmp_1"
    assert c.audience_id == "aud_1"
    assert body_seen == {
        "name": "n",
        "audienceId": "aud_1",
        "text": "hi",
        "mediaUrl": "https://cdn.example/x.jpg",
        "mediaCaption": "cap",
        "onMissingVariable": "skip",
    }


def test_list_campaigns():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/campaigns"
        return _page([_campaign("cmp_1"), _campaign("cmp_2", status="running", sentCount=3)])

    page = _client(handler).campaigns.list()
    assert isinstance(page, Page)
    assert len(page.data) == 2
    assert page.data[1].status == "running"
    assert page.data[1].sent_count == 3


def test_get_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/campaigns/cmp_1"
        return _ok(_campaign("cmp_1"))

    c = _client(handler).campaigns.get("cmp_1")
    assert c.cmp_id == "cmp_1"


def test_pause_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/campaigns/cmp_1/pause"
        return _ok(_campaign("cmp_1", status="paused"))

    assert _client(handler).campaigns.pause("cmp_1").status == "paused"


def test_resume_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/campaigns/cmp_1/resume"
        return _ok(_campaign("cmp_1", status="running"))

    assert _client(handler).campaigns.resume("cmp_1").status == "running"


def test_cancel_campaign():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/campaigns/cmp_1/cancel"
        return _ok(_campaign("cmp_1", status="aborted", abortedAt="2026-04-23T01:00:00Z"))

    c = _client(handler).campaigns.cancel("cmp_1")
    assert c.status == "aborted"
    assert c.aborted_at is not None


def test_campaigns_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_cmp_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).campaigns.get("cmp_1")
    assert exc_info.value.request_id == "req_cmp_1"


def test_campaign_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).campaigns.get("cmp_1")
