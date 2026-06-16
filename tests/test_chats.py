from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.chats import (
    BatchMessageAcksResponse,
    Chat,
    ChatMedia,
    ChatMessage,
    ChatRef,
    LoadOlderMessagesResponse,
    MediaUrlResponse,
    Message,
    MessageAck,
    OkResponse,
    Participant,
)


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _chat(cid: str = "chat_1", **overrides) -> dict:
    data = {
        "id": cid,
        "name": "Acme",
        "isGroup": False,
        "isNewsletter": False,
        "lastMessageAt": "2026-04-23T00:00:00Z",
        "unreadCount": 3,
        "markedUnread": False,
    }
    data.update(overrides)
    return data


def _chat_message(**overrides) -> dict:
    data = {
        "key": "msg_key_1",
        "chatId": "chat_1",
        "from": "+15551234567",
        "timestamp": "2026-04-23T00:00:00Z",
        "text": "hello",
        "type": "chat",
        "fromMe": False,
        "ack": 3,
        "mediaUrl": None,
        "caption": None,
        "filename": None,
    }
    data.update(overrides)
    return data


def test_list_chats_returns_page_of_chats():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/chats"
        return httpx.Response(
            200,
            json={
                "data": [_chat("chat_1"), _chat("chat_2")],
                "has_more": False,
                "next_cursor": None,
            },
        )

    page = _client(handler).chats.list(query="acme", limit=10)
    assert len(page.data) == 2
    assert isinstance(page.data[0], Chat)
    assert page.data[0].id == "chat_1"


def test_get_chat_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/chat_1"
        return httpx.Response(200, json=_chat("chat_1"))

    chat = _client(handler).chats.get("chat_1")
    assert isinstance(chat, Chat)
    assert chat.unread_count == 3


def test_list_participants_returns_page():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/chat_1/participants"
        return httpx.Response(
            200,
            json={
                "data": [{"chatId": "12345@c.us", "isAdmin": True, "isSuperAdmin": False}],
                "has_more": False,
                "next_cursor": None,
            },
        )

    page = _client(handler).chats.list_participants("chat_1")
    assert isinstance(page.data[0], Participant)
    assert page.data[0].is_admin is True


def test_mark_read_returns_ok_response():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/chats/chat_1/mark_read"
        return httpx.Response(200, json={"ok": True})

    result = _client(handler).chats.mark_read("chat_1")
    assert isinstance(result, OkResponse)
    assert result.ok is True


def test_open_returns_chat_ref():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/chat_1/open"
        return httpx.Response(200, json={"chatId": "chat_1"})

    result = _client(handler).chats.open("chat_1")
    assert isinstance(result, ChatRef)
    assert result.chat_id == "chat_1"


def test_list_messages_returns_page_of_chat_messages():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages"
        assert req.url.params.get("chatId") == "chat_1"
        assert req.url.params.get("order") == "asc"
        assert req.url.params.get("messageTypes") == "image,video"
        return httpx.Response(
            200,
            json={"data": [_chat_message()], "has_more": True, "next_cursor": "cur_2"},
        )

    page = _client(handler).chats.list_messages(
        "chat_1", order="asc", message_types=["image", "video"]
    )
    assert isinstance(page.data[0], ChatMessage)
    assert page.data[0].from_ == "+15551234567"
    assert page.next_cursor == "cur_2"


def test_get_message_returns_chat_message():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/msg_key_1"
        assert req.url.params.get("chatId") == "chat_1"
        return httpx.Response(200, json=_chat_message())

    msg = _client(handler).chats.get_message("msg_key_1", chat_id="chat_1")
    assert isinstance(msg, ChatMessage)
    assert msg.text == "hello"


def test_get_message_ack_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/ack/msg_key_1"
        return httpx.Response(200, json={"ack": 3})

    result = _client(handler).chats.get_message_ack("msg_key_1")
    assert isinstance(result, MessageAck)
    assert result.ack == 3


def test_react_returns_ok_response():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.url.path == "/v1/messages/reactions/msg_key_1"
        return httpx.Response(200, json={"ok": True})

    result = _client(handler).chats.react("msg_key_1", emoji="🔥")
    assert isinstance(result, OkResponse)
    assert body_seen == {"emoji": "🔥"}


def test_load_older_messages_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/load_older/chat_1"
        return httpx.Response(200, json={"totalMessages": 124, "added": 24, "canLoadMore": True})

    result = _client(handler).chats.load_older_messages("chat_1")
    assert isinstance(result, LoadOlderMessagesResponse)
    assert result.added == 24
    assert result.can_load_more is True


def test_get_media_returns_chat_media():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/media/msg_key_1"
        return httpx.Response(
            200,
            json={
                "url": "https://cdn.example/x.jpg",
                "mimetype": "image/jpeg",
                "filename": "x.jpg",
                "dataBase64": None,
                "originalQuality": True,
                "mediaUnavailable": None,
            },
        )

    result = _client(handler).chats.get_media("msg_key_1")
    assert isinstance(result, ChatMedia)
    assert result.mimetype == "image/jpeg"


def test_get_media_url_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/messages/media_url/msg_key_1"
        return httpx.Response(200, json={"url": "https://cdn.example/y.jpg"})

    result = _client(handler).chats.get_media_url("msg_key_1")
    assert isinstance(result, MediaUrlResponse)
    assert result.url == "https://cdn.example/y.jpg"


def test_batch_message_acks_returns_typed_model():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/acks"
        return httpx.Response(
            200,
            json={
                "data": [
                    {"key": "msg_a", "ack": 3},
                    {"key": "msg_b", "ack": 1},
                    {"key": "msg_c", "ack": None},
                ]
            },
        )

    result = _client(handler).chats.batch_message_acks(message_keys=["msg_a", "msg_b", "msg_c"])
    assert isinstance(result, BatchMessageAcksResponse)
    assert body_seen == {"messageKeys": ["msg_a", "msg_b", "msg_c"]}
    assert result.data[0].key == "msg_a"
    assert result.data[0].ack == 3
    assert result.data[1].ack == 1
    assert result.data[2].ack is None


def _message_response(**overrides) -> dict:
    data = {
        "id": None,
        "key": "wamid.HBg_test",
        "to": "chat_1",
        "from": "+15551234567",
        "type": "text",
        "text": "hello there",
        "mediaUrl": None,
        "mediaKind": None,
        "pollQuestion": None,
        "status": "confirmed",
        "sendAt": None,
        "createdAt": "2026-05-28T00:00:00Z",
        "confirmedAt": "2026-05-28T00:00:01Z",
        "receivedAt": None,
        "readAt": None,
        "playedAt": None,
        "failedAt": None,
        "failureReason": None,
        "linkPreview": None,
    }
    data.update(overrides)
    return data


def test_send_message_text_returns_typed_model():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/messages/chat_1"
        return httpx.Response(201, json=_message_response())

    result = _client(handler).chats.send_message(
        "chat_1",
        type="text",
        text="hello there",
        link_preview=False,
        reply_to="wamid.prev",
    )
    assert isinstance(result, Message)
    assert result.key == "wamid.HBg_test"
    assert result.type == "text"
    assert result.status == "confirmed"
    assert body_seen == {
        "type": "text",
        "text": "hello there",
        "linkPreview": False,
        "replyTo": "wamid.prev",
    }


def test_send_message_media_returns_typed_model():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.url.path == "/v1/messages/chat_1"
        return httpx.Response(
            201,
            json=_message_response(
                type="media",
                text=None,
                mediaUrl="https://cdn.example/x.jpg",
                mediaKind="image",
            ),
        )

    result = _client(handler).chats.send_message(
        "chat_1",
        type="media",
        media={
            "url": "https://cdn.example/x.jpg",
            "kind": "image",
            "caption": "look at this",
        },
        mentions={"ids": ["12345@c.us"], "displays": ["Alice"]},
    )
    assert isinstance(result, Message)
    assert result.type == "media"
    assert result.media_kind == "image"
    assert body_seen["media"]["url"] == "https://cdn.example/x.jpg"
    assert body_seen["mentions"] == {"ids": ["12345@c.us"], "displays": ["Alice"]}


def test_send_message_poll_returns_typed_model():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.url.path == "/v1/messages/chat_1"
        return httpx.Response(
            201,
            json=_message_response(
                type="poll",
                text=None,
                pollQuestion="Tea or coffee?",
            ),
        )

    result = _client(handler).chats.send_message(
        "chat_1",
        type="poll",
        poll={
            "question": "Tea or coffee?",
            "options": ["Tea", "Coffee"],
            "allow_multiple": False,
        },
        from_="+15551234567",
    )
    assert isinstance(result, Message)
    assert result.type == "poll"
    assert result.poll_question == "Tea or coffee?"
    assert body_seen == {
        "type": "poll",
        "poll": {
            "question": "Tea or coffee?",
            "options": ["Tea", "Coffee"],
            "allow_multiple": False,
        },
        "from": "+15551234567",
    }


def test_send_message_forwards_idempotency_key():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.headers.get("Idempotency-Key") == "idem_abc"
        return httpx.Response(201, json=_message_response())

    result = _client(handler).chats.send_message(
        "chat_1",
        type="text",
        text="hi",
        idempotency_key="idem_abc",
    )
    assert isinstance(result, Message)


def test_chats_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "requestId": "req_chats_1",
                }
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).chats.get("chat_1")
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_chats_1"


def test_chat_validation_fails_when_required_field_missing():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    with pytest.raises(ValidationError):
        _client(handler).chats.get("chat_1")
