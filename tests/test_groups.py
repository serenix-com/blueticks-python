from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.groups import Group, GroupListItem
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _group(gid="111@g.us", **overrides):
    data = {
        "id": gid,
        "name": "Acme Team",
        "description": "Internal coordination",
        "owner": "12345@c.us",
        "createdAt": "2026-04-23T00:00:00Z",
        "lastMessageAt": "2026-04-24T00:00:00Z",
        "participantCount": 5,
        "announce": False,
        "restrict": False,
        "participants": [
            {"chatId": "12345@c.us", "isAdmin": True, "isSuperAdmin": True, "name": "Owner"}
        ],
    }
    data.update(overrides)
    return data


def _group_list_item(gid="111@g.us", **overrides):
    data = {
        "id": gid,
        "name": "Acme Team",
        "description": None,
        "owner": "12345@c.us",
        "createdAt": "2026-04-23T00:00:00Z",
        "lastMessageAt": "2026-04-24T00:00:00Z",
        "participantCount": 5,
        "restrict": False,
    }
    data.update(overrides)
    return data


def test_list_groups_returns_page_of_list_items():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.url.path == "/v1/groups"
        return _page([_group_list_item("111@g.us"), _group_list_item("222@g.us", name="Beta")])

    page = _client(handler).groups.list(search_token="acme", limit=10)
    assert isinstance(page, Page)
    assert isinstance(page.data[0], GroupListItem)
    assert page.data[1].name == "Beta"
    assert params_seen["searchToken"] == "acme"
    assert params_seen["limit"] == "10"


def test_create_group_returns_typed_group():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/groups"
        return _ok(_group("new@g.us"))

    g = _client(handler).groups.create(name="Acme Team", participants=["12345@c.us"])
    assert isinstance(g, Group)
    assert g.participants[0].chat_id == "12345@c.us"
    assert body_seen == {"name": "Acme Team", "participants": ["12345@c.us"]}


def test_get_group_with_include_participants():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.url.path == "/v1/groups/111@g.us"
        return _ok(_group("111@g.us"))

    g = _client(handler).groups.get("111@g.us", include="participants")
    assert g.participant_count == 5
    assert params_seen["include"] == "participants"


def test_update_group():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        return _ok(_group("111@g.us", name="Renamed"))

    g = _client(handler).groups.update(
        "111@g.us", name="Renamed", settings={"announce": True, "editInfoAdminsOnly": True}
    )
    assert g.name == "Renamed"
    assert body_seen == {
        "name": "Renamed",
        "settings": {"announce": True, "editInfoAdminsOnly": True},
    }


def test_add_member_serializes_camel_case():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.url.path == "/v1/groups/111@g.us/members"
        return _ok(_group("111@g.us", participantCount=6))

    g = _client(handler).groups.add_member("111@g.us", chat_id="99999@c.us")
    assert g.participant_count == 6
    assert body_seen == {"chatId": "99999@c.us"}


def test_remove_member():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/groups/111@g.us/members/99999@c.us"
        return _ok(_group("111@g.us", participantCount=4))

    assert _client(handler).groups.remove_member("111@g.us", "99999@c.us").participant_count == 4


def test_promote_admin():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/groups/111@g.us/members/99999@c.us/admin"
        return _ok(_group("111@g.us"))

    assert isinstance(_client(handler).groups.promote_admin("111@g.us", "99999@c.us"), Group)


def test_demote_admin():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/groups/111@g.us/members/99999@c.us/admin"
        return _ok(_group("111@g.us"))

    assert isinstance(_client(handler).groups.demote_admin("111@g.us", "99999@c.us"), Group)


def test_set_picture_serializes_camel_case():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PUT"
        assert req.url.path == "/v1/groups/111@g.us/picture"
        return _ok(_group("111@g.us"))

    _client(handler).groups.set_picture(
        "111@g.us",
        file_data_url="data:image/png;base64,iVBORw0KG...",
        file_name="logo.png",
        file_mime_type="image/png",
    )
    assert body_seen == {
        "fileDataUrl": "data:image/png;base64,iVBORw0KG...",
        "fileName": "logo.png",
        "fileMimeType": "image/png",
    }


def test_leave_group_returns_none_on_204():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/groups/111@g.us/members/me"
        return httpx.Response(204)

    assert _client(handler).groups.leave("111@g.us") is None


def test_groups_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_grp_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).groups.get("111@g.us")
    assert exc_info.value.request_id == "req_grp_1"


def test_group_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).groups.get("111@g.us")
