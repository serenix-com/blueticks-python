from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.messages import Message


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _message(mid: str = "msg_1", **overrides) -> dict:
    data = {
        "id": mid,
        "key": None,
        "to": "+15551234567",
        "from": None,
        "type": "text",
        "text": "hello",
        "media_url": None,
        "media_kind": None,
        "poll_question": None,
        "status": "queued",
        "send_at": None,
        "created_at": "2026-04-23T00:00:00Z",
        "sent_at": None,
        "delivered_at": None,
        "read_at": None,
        "failed_at": None,
        "failure_reason": None,
        "link_preview": None,
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# send() – text variant
# ---------------------------------------------------------------------------


def test_send_text_posts_to_v1_messages():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages"
        return httpx.Response(201, json=_message("msg_1", to="+15551234567", text="hello"))

    m = _client(handler).messages.send(to="+15551234567", type="text", text="hello")
    assert isinstance(m, Message)
    assert m.id == "msg_1"
    assert m.type == "text"
    assert body_seen["type"] == "text"
    assert body_seen["to"] == "+15551234567"
    assert body_seen["text"] == "hello"


def test_send_text_with_from_and_send_at():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            json=_message(
                "msg_2",
                **{"from": "+19995550000"},
                to="+15551234567",
                status="scheduled",
                send_at="2026-05-01T09:00:00Z",
            ),
        )

    m = _client(handler).messages.send(
        to="+15551234567",
        type="text",
        text="reminder",
        send_at="2026-05-01T09:00:00Z",
        from_="+19995550000",
    )
    assert m.from_ == "+19995550000"
    assert body_seen["from"] == "+19995550000"
    assert body_seen["send_at"] == "2026-05-01T09:00:00Z"


# ---------------------------------------------------------------------------
# send() – media variant
# ---------------------------------------------------------------------------


def test_send_media_includes_media_dict():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            json=_message(
                "msg_3",
                type="media",
                text=None,
                media_url="https://cdn.example.com/receipt.pdf",
                media_kind="document",
            ),
        )

    m = _client(handler).messages.send(
        to="+15551234567",
        type="media",
        media={
            "url": "https://cdn.example.com/receipt.pdf",
            "kind": "document",
            "filename": "receipt.pdf",
        },
    )
    assert isinstance(m, Message)
    assert m.type == "media"
    assert m.media_url == "https://cdn.example.com/receipt.pdf"
    assert m.media_kind == "document"
    assert body_seen["type"] == "media"
    assert body_seen["media"]["url"] == "https://cdn.example.com/receipt.pdf"
    assert body_seen["media"]["filename"] == "receipt.pdf"


# ---------------------------------------------------------------------------
# send() – poll variant
# ---------------------------------------------------------------------------


def test_send_poll_includes_poll_dict():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            json=_message(
                "msg_4",
                type="poll",
                text=None,
                poll_question="Pizza?",
            ),
        )

    m = _client(handler).messages.send(
        to="+15551234567",
        type="poll",
        poll={"question": "Pizza?", "options": ["Yes", "No"], "allow_multiple": False},
    )
    assert isinstance(m, Message)
    assert m.type == "poll"
    assert m.poll_question == "Pizza?"
    assert body_seen["type"] == "poll"
    assert body_seen["poll"]["question"] == "Pizza?"
    assert body_seen["poll"]["options"] == ["Yes", "No"]


# ---------------------------------------------------------------------------
# send() – idempotency key
# ---------------------------------------------------------------------------


def test_send_with_idempotency_key_sets_header():
    headers_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        headers_seen.update(dict(req.headers))
        return httpx.Response(201, json=_message("msg_5"))

    _client(handler).messages.send(
        to="+15551234567", type="text", text="hi", idempotency_key="key-abc"
    )
    assert headers_seen["idempotency-key"] == "key-abc"


# ---------------------------------------------------------------------------
# retrieve()
# ---------------------------------------------------------------------------


def test_retrieve_message_by_id():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/messages/msg_xyz"
        return httpx.Response(
            200,
            json=_message(
                "msg_xyz",
                status="delivered",
                sent_at="2026-04-23T00:00:01Z",
                delivered_at="2026-04-23T00:00:02Z",
            ),
        )

    m = _client(handler).messages.retrieve("msg_xyz")
    assert isinstance(m, Message)
    assert m.id == "msg_xyz"
    assert m.status == "delivered"
    assert m.delivered_at == "2026-04-23T00:00:02Z"


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------


def test_list_messages_returns_page():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/messages"
        return httpx.Response(
            200,
            json={
                "data": [_message("msg_a"), _message("msg_b", status="delivered")],
                "has_more": False,
                "next_cursor": None,
            },
        )

    from blueticks.types.page import Page

    result = _client(handler).messages.list()
    assert isinstance(result, Page)
    assert len(result.data) == 2
    assert result.data[0].id == "msg_a"


# ---------------------------------------------------------------------------
# Error path
# ---------------------------------------------------------------------------


def test_retrieve_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_msg_1",
                }
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).messages.retrieve("msg_1")
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_msg_1"


# ---------------------------------------------------------------------------
# Missing-required-field test
# ---------------------------------------------------------------------------


def test_message_validation_fails_when_required_field_missing():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    with pytest.raises(ValidationError):
        _client(handler).messages.retrieve("msg_1")


# ---------------------------------------------------------------------------
# update() – PATCH /v1/messages/{id}
# ---------------------------------------------------------------------------


def test_update_patches_to_v1_messages_id():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "PATCH"
        assert req.url.path == "/v1/messages/msg_xyz"
        body_seen.update(json.loads(req.content))
        return httpx.Response(200, json=_message(mid="msg_xyz", text="edited"))

    result = _client(handler).messages.update("msg_xyz", text="edited")
    assert isinstance(result, Message)
    assert result.id == "msg_xyz"
    assert result.text == "edited"
    assert body_seen == {"text": "edited"}


def test_update_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_upd_1",
                }
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).messages.update("msg_xyz", text="x")
    assert exc_info.value.request_id == "req_upd_1"
