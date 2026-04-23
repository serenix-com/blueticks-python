from __future__ import annotations

import json

import httpx

from blueticks import Blueticks


def test_send_posts_to_v1_messages():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages"
        return httpx.Response(
            201,
            json={
                "id": "msg_1",
                "to": json.loads(req.content)["to"],
                "from": None,
                "text": "hi",
                "media_url": None,
                "status": "queued",
                "send_at": None,
                "created_at": "2026-04-23T00:00:00Z",
                "sent_at": None,
                "delivered_at": None,
                "read_at": None,
                "failed_at": None,
                "failure_reason": None,
            },
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    m = client.messages.send(to="+1", text="hi")
    assert m.id == "msg_1"
    assert body_seen["to"] == "+1"
    assert body_seen["text"] == "hi"


def test_send_with_from_and_send_at():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            json={
                "id": "msg_2",
                "to": "+1",
                "from": "+2",
                "text": None,
                "media_url": "https://a.com/x",
                "status": "scheduled",
                "send_at": "2026-05-01T09:00:00Z",
                "created_at": "2026-04-23T00:00:00Z",
                "sent_at": None,
                "delivered_at": None,
                "read_at": None,
                "failed_at": None,
                "failure_reason": None,
            },
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    m = client.messages.send(
        to="+1",
        media_url="https://a.com/x",
        send_at="2026-05-01T09:00:00Z",
        from_="+2",
    )
    assert m.from_ == "+2"
    assert body_seen["from"] == "+2"  # serialized as 'from' not 'from_'
    assert body_seen["send_at"] == "2026-05-01T09:00:00Z"


def test_send_with_idempotency_key_sets_header():
    headers_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        headers_seen.update(dict(req.headers))
        return httpx.Response(
            201,
            json={
                "id": "msg_3",
                "to": "+1",
                "from": None,
                "text": "hi",
                "media_url": None,
                "status": "queued",
                "send_at": None,
                "created_at": "2026-04-23T00:00:00Z",
                "sent_at": None,
                "delivered_at": None,
                "read_at": None,
                "failed_at": None,
                "failure_reason": None,
            },
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    client.messages.send(to="+1", text="hi", idempotency_key="key-abc")
    assert headers_seen["idempotency-key"] == "key-abc"


def test_get_by_id():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/messages/msg_xyz"
        return httpx.Response(
            200,
            json={
                "id": "msg_xyz",
                "to": "+1",
                "from": None,
                "text": "hi",
                "media_url": None,
                "status": "delivered",
                "send_at": None,
                "created_at": "2026-04-23T00:00:00Z",
                "sent_at": "2026-04-23T00:00:01Z",
                "delivered_at": "2026-04-23T00:00:02Z",
                "read_at": None,
                "failed_at": None,
                "failure_reason": None,
            },
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    m = client.messages.get("msg_xyz")
    assert m.status == "delivered"
