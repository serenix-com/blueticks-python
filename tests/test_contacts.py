from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.contacts import Contact
from blueticks.types.groups import GroupListItem
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def test_list_contacts_returns_page():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.method == "GET"
        assert req.url.path == "/v1/contacts"
        return _page(
            [
                {"chatId": "12345@c.us", "name": "Alice", "isBusiness": False},
                {"chatId": "67890@c.us", "name": "Bob Store", "isBusiness": True},
            ]
        )

    page = _client(handler).contacts.list(search_token="a", include_archive=True, limit=50)
    assert isinstance(page, Page)
    assert page.total == 2
    assert isinstance(page.data[0], Contact)
    assert page.data[0].chat_id == "12345@c.us"
    assert page.data[0].is_business is False
    assert page.data[1].is_business is True
    assert params_seen["searchToken"] == "a"
    assert params_seen["includeArchive"] == "true"
    assert params_seen["limit"] == "50"


def test_common_groups_returns_page_of_group_list_items():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/contacts/12345@c.us/common_groups"
        return _page(
            [
                {
                    "id": "111@g.us",
                    "name": "Shared Group",
                    "participantCount": 8,
                    "lastMessageAt": "2026-04-23T00:00:00Z",
                }
            ]
        )

    page = _client(handler).contacts.common_groups("12345@c.us")
    assert isinstance(page.data[0], GroupListItem)
    assert page.data[0].id == "111@g.us"
    assert page.data[0].participant_count == 8


def test_contacts_list_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_ctc_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).contacts.list()
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_ctc_1"


def test_contact_validation_fails_when_required_field_missing():
    def handler(req: httpx.Request) -> httpx.Response:
        # A page item missing the required chat_id.
        return _page([{"name": "Alice"}])

    with pytest.raises(ValidationError):
        _client(handler).contacts.list()
