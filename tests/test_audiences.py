from __future__ import annotations

import json

import httpx

from blueticks import Blueticks


def _audience(aid: str = "aud_1", **overrides) -> dict:
    data = {
        "id": aid,
        "name": "A",
        "contact_count": 0,
        "created_at": "2026-04-23T00:00:00Z",
    }
    data.update(overrides)
    return data


def _contact(cid: str = "ctc_1", **overrides) -> dict:
    data = {
        "id": cid,
        "to": "+1",
        "variables": {"name": "X"},
        "added_at": "2026-04-23T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_create_audience_with_contacts():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/audiences"
        return httpx.Response(201, json=_audience(contact_count=1))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    aud = client.audiences.create(
        name="A",
        contacts=[{"to": "+1", "variables": {"name": "X"}}],
    )
    assert aud.id == "aud_1"
    assert body_seen["name"] == "A"
    assert body_seen["contacts"][0]["to"] == "+1"


def test_list_audiences():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/audiences"
        return httpx.Response(
            200,
            json={
                "data": [_audience("aud_1"), _audience("aud_2")],
                "has_more": False,
                "next_cursor": None,
            },
        )

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    page = client.audiences.list()
    assert len(page.data) == 2
    assert page.has_more is False
    assert page.next_cursor is None


def test_get_audience_with_page():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/audiences/aud_1"
        assert req.url.params.get("page") == "2"
        return httpx.Response(200, json=_audience("aud_1", page=2, has_more=False))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    aud = client.audiences.get("aud_1", page=2)
    assert aud.page == 2


def test_update_audience():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/audiences/aud_1"
        return httpx.Response(200, json=_audience("aud_1", name="renamed"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    aud = client.audiences.update("aud_1", name="renamed")
    assert aud.name == "renamed"
    assert body_seen == {"name": "renamed"}


def test_delete_audience():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/audiences/aud_1"
        return httpx.Response(200, json={"id": "aud_1", "deleted": True})

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    result = client.audiences.delete("aud_1")
    assert result.id == "aud_1"
    assert result.deleted is True


def test_append_contacts():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "POST"
        assert req.url.path == "/v1/audiences/aud_1/contacts"
        body = json.loads(req.content)
        assert body["contacts"][0]["to"] == "+1"
        return httpx.Response(200, json={"added": 1, "contact_count": 5})

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    result = client.audiences.append_contacts(
        "aud_1",
        contacts=[{"to": "+1", "variables": {"name": "X"}}],
    )
    assert result.added == 1
    assert result.contact_count == 5


def test_update_contact():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/audiences/aud_1/contacts/ctc_1"
        return httpx.Response(200, json=_contact("ctc_1", to="+99"))

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    c = client.audiences.update_contact("aud_1", "ctc_1", to="+99", variables={"name": "Z"})
    assert c.to == "+99"
    assert body_seen == {"to": "+99", "variables": {"name": "Z"}}


def test_delete_contact():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/audiences/aud_1/contacts/ctc_1"
        return httpx.Response(204)

    client = Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))
    assert client.audiences.delete_contact("aud_1", "ctc_1") is None
