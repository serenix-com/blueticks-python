from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.chats import OkResponse
from blueticks.types.messages import (
    BatchMessageAck,
    LoadOlderResult,
    Message,
    MessageAck,
    MessageMedia,
    PinnedMessage,
)
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 20, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _message(**overrides):
    data = {
        "waMessageKey": {
            "fromMe": False,
            "remote": "12345@c.us",
            "id": "ABCD",
            "_serialized": "false_12345@c.us_ABCD",
            "participant": None,
        },
        "chatId": "12345@c.us",
        "from": "12345@c.us",
        "author": None,
        "senderName": "Alice",
        "timestamp": "2026-04-23T00:00:00Z",
        "text": "hello",
        "type": "chat",
        "fromMe": False,
        "ack": 3,
        "mediaUrl": None,
        "filename": None,
        "linkPreview": None,
        "quotedMessage": None,
    }
    data.update(overrides)
    return data


def test_list_messages_returns_page_with_has_more():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.url.path == "/v1/messages"
        return _page([_message()], hasMore=True)

    page = _client(handler).messages.list(
        chat_id="12345@c.us",
        search_token="hi",
        message_types=["chat", "image"],
        since="2026-04-01T00:00:00Z",
        limit=20,
    )
    assert isinstance(page, Page)
    assert page.has_more is True
    assert isinstance(page.data[0], Message)
    assert page.data[0].from_ == "12345@c.us"
    assert page.data[0].wa_message_key.serialized == "false_12345@c.us_ABCD"
    assert page.data[0].sender_name == "Alice"
    assert params_seen["chatId"] == "12345@c.us"
    assert params_seen["messageTypes"] == "chat,image"
    assert params_seen["searchToken"] == "hi"


def test_retrieve_message():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/false_12345@c.us_ABCD"
        assert req.url.params.get("chatId") == "12345@c.us"
        return _ok(_message(quotedMessage={"waMessageKey": {"fromMe": True}, "text": "prev"}))

    msg = _client(handler).messages.retrieve("false_12345@c.us_ABCD", chat_id="12345@c.us")
    assert isinstance(msg, Message)
    assert msg.text == "hello"
    assert msg.quoted_message.text == "prev"
    assert msg.quoted_message.wa_message_key.from_me is True


def test_send_message_serializes_camel_case_body():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/12345@c.us"
        return httpx.Response(
            201,
            json={
                "success": True,
                "data": {
                    "id": None,
                    "waMessageKey": {"fromMe": True, "id": "X"},
                    "to": "12345@c.us",
                    "type": "text",
                    "text": "hi there",
                    "status": "sent",
                    "createdAt": "2026-04-23T00:00:00Z",
                },
            },
        )

    result = _client(handler).messages.send(
        "12345@c.us",
        type="text",
        text="hi there",
        reply_to="wamid.prev",
        with_typing=True,
        typing_seconds=1.5,
    )
    assert isinstance(result, ScheduledMessage)
    assert result.to == "12345@c.us"
    assert result.status == "sent"
    assert result.wa_message_key.from_me is True
    assert body_seen == {
        "type": "text",
        "text": "hi there",
        "replyTo": "wamid.prev",
        "withTyping": True,
        "typingSeconds": 1.5,
    }


def test_send_media_message():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return _ok(
            {
                "id": None,
                "to": "12345@c.us",
                "type": "media",
                "mediaUrl": "https://cdn.example/x.jpg",
                "mediaKind": "image",
                "status": "sent",
                "createdAt": "2026-04-23T00:00:00Z",
            },
            status=201,
        )

    result = _client(handler).messages.send(
        "12345@c.us",
        type="media",
        media_url="https://cdn.example/x.jpg",
        media_kind="image",
        media_filename="x.jpg",
    )
    assert result.type == "media"
    assert result.media_kind == "image"
    assert body_seen == {
        "type": "media",
        "mediaUrl": "https://cdn.example/x.jpg",
        "mediaKind": "image",
        "mediaFilename": "x.jpg",
    }


def test_get_ack():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/ack/wamid.X"
        return _ok({"ack": 3})

    result = _client(handler).messages.get_ack("wamid.X")
    assert isinstance(result, MessageAck)
    assert result.ack == 3


def test_batch_acks_returns_page():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/acks"
        return _page(
            [
                {"key": "k1", "ack": 3, "found": True},
                {"key": "k2", "ack": None, "found": False},
            ]
        )

    page = _client(handler).messages.batch_acks(message_keys=["k1", "k2"], chat_id="12345@c.us")
    assert isinstance(page, Page)
    assert isinstance(page.data[0], BatchMessageAck)
    assert page.data[0].found is True
    assert page.data[1].ack is None
    assert body_seen == {"messageKeys": ["k1", "k2"], "chatId": "12345@c.us"}


def test_load_older():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/load_older/12345@c.us"
        return _ok(
            {
                "totalMessages": 124,
                "added": 24,
                "canLoadMore": True,
                "historyUnavailable": False,
            }
        )

    result = _client(handler).messages.load_older("12345@c.us")
    assert isinstance(result, LoadOlderResult)
    assert result.added == 24
    assert result.can_load_more is True
    assert result.history_unavailable is False


def test_get_media():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/media/wamid.X"
        assert req.url.params.get("maxAttempts") == "1"
        return _ok(
            {
                "url": "https://cdn.example/y.jpg",
                "mimetype": "image/jpeg",
                "filename": "y.jpg",
                "dataBase64": None,
                "originalQuality": True,
                "mediaUnavailable": None,
            }
        )

    result = _client(handler).messages.get_media("wamid.X", chat_id="12345@c.us", max_attempts=1)
    assert isinstance(result, MessageMedia)
    assert result.mimetype == "image/jpeg"
    assert result.original_quality is True


def test_pin_with_duration():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/pin/wamid.X"
        return _ok({"ok": True})

    result = _client(handler).messages.pin("wamid.X", chat_id="12345@c.us", duration=3600)
    assert isinstance(result, OkResponse)
    assert body_seen == {"duration": 3600}


def test_unpin():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/unpin/wamid.X"
        return _ok({"ok": True})

    assert _client(handler).messages.unpin("wamid.X").ok is True


def test_list_pinned_returns_page():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/pinned/12345@c.us"
        return _page([{"key": "k1", "chatId": "12345@c.us", "text": "pinned!"}])

    page = _client(handler).messages.list_pinned("12345@c.us")
    assert isinstance(page.data[0], PinnedMessage)
    assert page.data[0].text == "pinned!"


def test_react():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.url.path == "/v1/messages/reactions/wamid.X"
        return _ok({"ok": True})

    result = _client(handler).messages.react("wamid.X", emoji="🔥", chat_id="12345@c.us")
    assert isinstance(result, OkResponse)
    assert body_seen == {"emoji": "🔥"}


def test_messages_retrieve_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_msg_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).messages.retrieve("wamid.X")
    assert exc_info.value.request_id == "req_msg_1"


def test_message_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).messages.retrieve("wamid.X")
