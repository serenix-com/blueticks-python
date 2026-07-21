from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.chats import Chat, OkResponse, Participant
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _chat(cid="12345@c.us", **overrides):
    data = {
        "chatId": cid,
        "name": "Acme",
        "chatType": "contact",
        "pinned": False,
        "archived": False,
        "lastMessageAt": "2026-04-23T00:00:00Z",
        "unreadCount": 3,
        "markedUnread": False,
        "lastMessageText": "hi there",
        "lastMessageFromMe": False,
    }
    data.update(overrides)
    return data


def test_list_chats_returns_page():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.method == "GET"
        assert req.url.path == "/v1/chats"
        return _page([_chat("a@c.us"), _chat("b@g.us", chatType="group")])

    page = _client(handler).chats.list(
        search_token="acme", filter="contact", include_last_message=True, limit=50
    )
    assert isinstance(page, Page)
    assert len(page.data) == 2
    assert isinstance(page.data[0], Chat)
    assert page.data[0].chat_id == "a@c.us"
    assert page.data[0].unread_count == 3
    assert page.data[1].chat_type == "group"
    assert params_seen["searchToken"] == "acme"
    assert params_seen["filter"] == "contact"
    assert params_seen["includeLastMessage"] == "true"


def test_get_chat_returns_typed_model():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/12345@c.us"
        return _ok(_chat("12345@c.us"))

    chat = _client(handler).chats.get("12345@c.us")
    assert isinstance(chat, Chat)
    assert chat.marked_unread is False
    assert chat.last_message_from_me is False


def test_list_participants_returns_page():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/12345@g.us/participants"
        return _page([{"chatId": "111@c.us", "name": "Al", "isAdmin": True, "isSuperAdmin": False}])

    page = _client(handler).chats.list_participants("12345@g.us", search_token="al")
    assert isinstance(page.data[0], Participant)
    assert page.data[0].chat_id == "111@c.us"
    assert page.data[0].is_admin is True


def test_archive_returns_ok():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/chats/12345@c.us/archive"
        return _ok({"ok": True})

    result = _client(handler).chats.archive("12345@c.us")
    assert isinstance(result, OkResponse)
    assert result.ok is True


def test_unarchive_returns_ok():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/12345@c.us/unarchive"
        return _ok({"ok": True})

    assert _client(handler).chats.unarchive("12345@c.us").ok is True


def test_mark_read_returns_ok():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/chats/12345@c.us/mark_read"
        return _ok({"ok": True})

    assert _client(handler).chats.mark_read("12345@c.us").ok is True


def test_chats_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_chats_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).chats.get("12345@c.us")
    assert exc_info.value.request_id == "req_chats_1"


def test_chat_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).chats.get("12345@c.us")
