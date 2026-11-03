from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.latest_chats import LatestChatsResponse
from blueticks.types.messages import Message


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _unauth():
    return httpx.Response(
        401,
        json={
            "success": False,
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "request_id": "req_x1",
            },
        },
    )


def _chat():
    return {
        "chatId": "12345@c.us",
        "name": "Acme",
        "chatType": "contact",
        "pinned": True,
        "archived": False,
        "lastMessageAt": "2026-04-23T00:00:00Z",
        "unreadCount": 2,
        "markedUnread": False,
        "lastMessageText": "hi",
        "lastMessageFromMe": False,
        "messages": [
            {
                "waMessageKey": {"fromMe": False, "remote": "12345@c.us", "id": "A1"},
                "chatId": "12345@c.us",
                "from": "12345@c.us",
                "timestamp": "2026-04-23T00:00:00Z",
                "text": "hi",
                "type": "chat",
                "fromMe": False,
                "source": "vault",
                "secret": "corr-1",
            }
        ],
    }


def test_retrieve_latest_chats():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.method == "GET"
        assert req.url.path == "/v1/latest-chats"
        return _ok({"chats": [_chat()], "totalChats": 1, "numberOfChats": 5, "numberOfMessages": 3})

    result = _client(handler).latest_chats.retrieve(number_of_chats=5, number_of_messages=3)
    assert isinstance(result, LatestChatsResponse)
    assert result.total_chats == 1
    assert result.number_of_chats == 5
    chat = result.chats[0]
    assert chat.chat_type == "contact"
    assert chat.pinned is True
    assert chat.unread_count == 2
    assert isinstance(chat.messages[0], Message)
    assert chat.messages[0].from_ == "12345@c.us"
    assert chat.messages[0].source == "vault"
    assert chat.messages[0].secret == "corr-1"
    assert params_seen == {"numberOfChats": "5", "numberOfMessages": "3"}


def test_latest_chats_raises_authentication_error_on_401():
    with pytest.raises(AuthenticationError) as exc_info:
        _client(lambda req: _unauth()).latest_chats.retrieve()
    assert exc_info.value.request_id == "req_x1"
    assert exc_info.value.code == "authentication_required"


def test_latest_chats_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).latest_chats.retrieve()
