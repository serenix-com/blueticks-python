from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.groups import Group


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _group(gid: str = "grp_1", **overrides) -> dict:
    data = {
        "id": gid,
        "name": "Acme Team",
        "description": "Internal coordination",
        "owner": "12345@c.us",
        "created_at": "2026-04-23T00:00:00Z",
        "last_message_at": "2026-04-24T00:00:00Z",
        "participant_count": 5,
        "announce": False,
        "restrict": False,
        "participants": None,
    }
    data.update(overrides)
    return data


def test_create_group_returns_typed_group():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/groups"
        return httpx.Response(200, json=_group("grp_new"))

    g = _client(handler).groups.create(name="Acme Team", participants=["12345@c.us"])
    assert isinstance(g, Group)
    assert body_seen == {"name": "Acme Team", "participants": ["12345@c.us"]}
    assert g.id == "grp_new"


def test_get_group_returns_typed_group():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/groups/grp_1"
        return httpx.Response(200, json=_group("grp_1"))

    g = _client(handler).groups.get("grp_1")
    assert isinstance(g, Group)
    assert g.participant_count == 5


def test_update_group_returns_typed_group():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/groups/grp_1"
        return httpx.Response(200, json=_group("grp_1", name="Renamed"))

    g = _client(handler).groups.update("grp_1", name="Renamed", settings={"announce": True})
    assert isinstance(g, Group)
    assert g.name == "Renamed"
    assert body_seen == {"name": "Renamed", "settings": {"announce": True}}


def test_add_member_returns_typed_group():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/groups/grp_1/members"
        return httpx.Response(200, json=_group("grp_1", participant_count=6))

    g = _client(handler).groups.add_member("grp_1", chat_id="99999@c.us")
    assert isinstance(g, Group)
    assert g.participant_count == 6
    assert body_seen == {"chat_id": "99999@c.us"}


def test_remove_member_returns_typed_group():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/groups/grp_1/members/99999@c.us"
        return httpx.Response(200, json=_group("grp_1", participant_count=4))

    g = _client(handler).groups.remove_member("grp_1", "99999@c.us")
    assert isinstance(g, Group)
    assert g.participant_count == 4


def test_promote_admin_returns_typed_group():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/groups/grp_1/members/99999@c.us/admin"
        return httpx.Response(200, json=_group("grp_1"))

    g = _client(handler).groups.promote_admin("grp_1", "99999@c.us")
    assert isinstance(g, Group)


def test_demote_admin_returns_typed_group():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/groups/grp_1/members/99999@c.us/admin"
        return httpx.Response(200, json=_group("grp_1"))

    g = _client(handler).groups.demote_admin("grp_1", "99999@c.us")
    assert isinstance(g, Group)


def test_set_picture_returns_typed_group():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PUT"
        assert req.url.path == "/v1/groups/grp_1/picture"
        return httpx.Response(200, json=_group("grp_1"))

    g = _client(handler).groups.set_picture(
        "grp_1",
        file_data_url="data:image/png;base64,iVBORw0KG...",
        file_name="logo.png",
        file_mime_type="image/png",
    )
    assert isinstance(g, Group)
    assert body_seen["file_data_url"].startswith("data:image/png;base64")
    assert body_seen["file_name"] == "logo.png"
    assert body_seen["file_mime_type"] == "image/png"


def test_leave_group_returns_none_on_204():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/groups/grp_1/members/me"
        return httpx.Response(204)

    assert _client(handler).groups.leave("grp_1") is None


def test_groups_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_groups_1",
                }
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).groups.get("grp_1")
    assert exc_info.value.code == "authentication_required"
    assert exc_info.value.request_id == "req_groups_1"


def test_group_validation_fails_when_required_field_missing():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    with pytest.raises(ValidationError):
        _client(handler).groups.get("grp_1")
