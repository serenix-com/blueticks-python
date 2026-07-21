from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.audiences import (
    AppendContactsResult,
    Audience,
    AudienceContact,
    RemovedContact,
)
from blueticks.types.page import Page


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _page(items, **extra):
    body = {"success": True, "data": items, "limit": 50, "skip": 0, "total": len(items)}
    body.update(extra)
    return httpx.Response(200, json=body)


def _audience(aid="aud_1", **overrides):
    data = {"id": aid, "name": "A", "contactCount": 0, "createdAt": "2026-04-23T00:00:00Z"}
    data.update(overrides)
    return data


def test_list_audiences_returns_page():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.url.path == "/v1/audiences"
        return _page([_audience("aud_1"), _audience("aud_2")], total=2)

    page = _client(handler).audiences.list(order="desc", skip=0, limit=50)
    assert isinstance(page, Page)
    assert len(page.data) == 2
    assert isinstance(page.data[0], Audience)
    assert page.data[0].contact_count == 0
    assert params_seen == {"order": "desc", "skip": "0", "limit": "50"}


def test_create_audience_with_contacts():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/audiences"
        return _ok(_audience(contactCount=1))

    aud = _client(handler).audiences.create(
        name="A", contacts=[{"to": "+1", "variables": {"name": "X"}}]
    )
    assert aud.id == "aud_1"
    assert body_seen["name"] == "A"
    assert body_seen["contacts"][0]["to"] == "+1"


def test_get_audience():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/audiences/aud_1"
        return _ok(_audience("aud_1", contactCount=42))

    aud = _client(handler).audiences.get("aud_1")
    assert aud.contact_count == 42


def test_update_audience():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/audiences/aud_1"
        return _ok(_audience("aud_1", name="renamed"))

    aud = _client(handler).audiences.update("aud_1", name="renamed")
    assert aud.name == "renamed"
    assert body_seen == {"name": "renamed"}


def test_delete_audience_returns_deleted_ref():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/audiences/aud_1"
        return _ok({"id": "aud_1", "deleted": True})

    result = _client(handler).audiences.delete("aud_1")
    assert isinstance(result, DeletedResource)
    assert result.id == "aud_1"
    assert result.deleted is True


def test_append_contacts():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/audiences/aud_1/contacts"
        assert json.loads(req.content)["contacts"][0]["to"] == "+1"
        return _ok({"added": 1, "contactCount": 5})

    result = _client(handler).audiences.append_contacts(
        "aud_1", contacts=[{"to": "+1", "variables": {"name": "X"}}]
    )
    assert isinstance(result, AppendContactsResult)
    assert result.added == 1
    assert result.contact_count == 5


def test_update_contact():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/audiences/aud_1/contacts/ctc_1"
        return _ok(
            {
                "id": "ctc_1",
                "to": "+99",
                "variables": {"name": "Z"},
                "addedAt": "2026-04-23T00:00:00Z",
            }
        )

    c = _client(handler).audiences.update_contact(
        "aud_1", "ctc_1", to="+99", variables={"name": "Z"}
    )
    assert isinstance(c, AudienceContact)
    assert c.to == "+99"
    assert c.variables == {"name": "Z"}
    assert c.added_at.year == 2026
    assert body_seen == {"to": "+99", "variables": {"name": "Z"}}


def test_delete_contact_returns_ref():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/audiences/aud_1/contacts/ctc_1"
        return _ok({"id": "ctc_1"})

    result = _client(handler).audiences.delete_contact("aud_1", "ctc_1")
    assert isinstance(result, RemovedContact)
    assert result.id == "ctc_1"


def test_audiences_get_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_aud_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).audiences.get("aud_1")
    assert exc_info.value.request_id == "req_aud_1"


def test_audience_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).audiences.get("aud_1")
