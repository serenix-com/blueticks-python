from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import AuthenticationError
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


def _scheduled(sid: str = "msg_1", **overrides) -> dict:
    data = {
        "id": sid,
        "key": None,
        "to": "+15551234567",
        "from": None,
        "type": "text",
        "text": "hello",
        "mediaUrl": None,
        "mediaKind": None,
        "pollQuestion": None,
        "status": "pending",
        "sendAt": None,
        "createdAt": "2026-04-23T00:00:00Z",
        "confirmedAt": None,
        "receivedAt": None,
        "readAt": None,
        "playedAt": None,
        "failedAt": None,
        "failureReason": None,
        "linkPreview": None,
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# list()
# ---------------------------------------------------------------------------


def test_list_scheduled_messages(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/scheduled-messages"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "data": [_scheduled("msg_1"), _scheduled("msg_2", status="received")],
                    "has_more": False,
                    "next_cursor": None,
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        page = client.scheduled_messages.list()
    assert isinstance(page, Page)
    assert len(page.data) == 2
    assert page.data[0].id == "msg_1"
    assert page.data[1].status == "received"
    assert page.has_more is False


def test_list_scheduled_messages_passes_all_params(mock_client) -> None:
    seen_params: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen_params.update(dict(req.url.params))
        return httpx.Response(
            200,
            content=json.dumps({"data": [], "has_more": True, "next_cursor": "cur_next"}).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        page = client.scheduled_messages.list(
            limit=25,
            cursor="cur_abc",
            chat_id="15551234567@c.us",
            status="pending",
            q="hello",
        )
    assert seen_params == {
        "limit": "25",
        "cursor": "cur_abc",
        "chatId": "15551234567@c.us",
        "status": "pending",
        "q": "hello",
    }
    assert page.next_cursor == "cur_next"


# ---------------------------------------------------------------------------
# create() — text variant
# ---------------------------------------------------------------------------


def test_create_text_posts_to_v1_scheduled_messages(mock_client) -> None:
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/scheduled-messages"
        return httpx.Response(
            201,
            content=json.dumps(_scheduled("msg_1", to="+15551234567", text="hello")).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        m = client.scheduled_messages.create(to="+15551234567", type="text", text="hello")
    assert isinstance(m, ScheduledMessage)
    assert m.id == "msg_1"
    assert m.type == "text"
    assert body_seen["type"] == "text"
    assert body_seen["to"] == "+15551234567"
    assert body_seen["text"] == "hello"


def test_create_text_with_from_and_send_at(mock_client) -> None:
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            content=json.dumps(
                _scheduled(
                    "msg_2",
                    **{"from": "+19995550000"},
                    to="+15551234567",
                    status="pending",
                    sendAt="2026-05-01T09:00:00Z",
                )
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        m = client.scheduled_messages.create(
            to="+15551234567",
            type="text",
            text="reminder",
            send_at="2026-05-01T09:00:00Z",
            from_="+19995550000",
        )
    assert m.from_ == "+19995550000"
    assert body_seen["from"] == "+19995550000"
    assert body_seen["sendAt"] == "2026-05-01T09:00:00Z"


def test_create_media_includes_media_dict(mock_client) -> None:
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            content=json.dumps(
                _scheduled(
                    "msg_3",
                    type="media",
                    text=None,
                    mediaUrl="https://cdn.example.com/receipt.pdf",
                    mediaKind="document",
                )
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        m = client.scheduled_messages.create(
            to="+15551234567",
            type="media",
            media={
                "url": "https://cdn.example.com/receipt.pdf",
                "kind": "document",
                "filename": "receipt.pdf",
            },
        )
    assert isinstance(m, ScheduledMessage)
    assert m.type == "media"
    assert m.media_url == "https://cdn.example.com/receipt.pdf"
    assert m.media_kind == "document"
    assert body_seen["type"] == "media"
    assert body_seen["media"]["url"] == "https://cdn.example.com/receipt.pdf"
    assert body_seen["media"]["filename"] == "receipt.pdf"


def test_create_poll_includes_poll_dict(mock_client) -> None:
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            201,
            content=json.dumps(
                _scheduled("msg_4", type="poll", text=None, pollQuestion="Pizza?")
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        m = client.scheduled_messages.create(
            to="+15551234567",
            type="poll",
            poll={"question": "Pizza?", "options": ["Yes", "No"], "allow_multiple": False},
        )
    assert isinstance(m, ScheduledMessage)
    assert m.type == "poll"
    assert m.poll_question == "Pizza?"
    assert body_seen["type"] == "poll"
    assert body_seen["poll"]["question"] == "Pizza?"
    assert body_seen["poll"]["options"] == ["Yes", "No"]


def test_create_with_idempotency_key_sets_header(mock_client) -> None:
    headers_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        headers_seen.update(dict(req.headers))
        return httpx.Response(
            201,
            content=json.dumps(_scheduled("msg_5")).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        client.scheduled_messages.create(
            to="+15551234567", type="text", text="hi", idempotency_key="key-abc"
        )
    assert headers_seen["idempotency-key"] == "key-abc"


# ---------------------------------------------------------------------------
# retrieve()
# ---------------------------------------------------------------------------


def test_retrieve_scheduled_message(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/scheduled-messages/msg_xyz"
        return httpx.Response(
            200,
            content=json.dumps(
                _scheduled(
                    "msg_xyz",
                    status="received",
                    confirmedAt="2026-04-23T00:00:01Z",
                    receivedAt="2026-04-23T00:00:02Z",
                )
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        m = client.scheduled_messages.retrieve("msg_xyz")
    assert isinstance(m, ScheduledMessage)
    assert m.id == "msg_xyz"
    assert m.status == "received"
    assert m.received_at == "2026-04-23T00:00:02Z"


# ---------------------------------------------------------------------------
# update()
# ---------------------------------------------------------------------------


def test_update_patches_to_v1_scheduled_messages_id(mock_client) -> None:
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "PATCH"
        assert req.url.path == "/v1/scheduled-messages/msg_xyz"
        body_seen.update(json.loads(req.content))
        return httpx.Response(
            200,
            content=json.dumps(_scheduled("msg_xyz", text="edited")).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.scheduled_messages.update("msg_xyz", text="edited")
    assert isinstance(result, ScheduledMessage)
    assert result.id == "msg_xyz"
    assert result.text == "edited"
    assert body_seen == {"text": "edited"}


# ---------------------------------------------------------------------------
# error + validation paths
# ---------------------------------------------------------------------------


def test_scheduled_messages_propagates_authentication_error(mock_client) -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        body = {
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "requestId": "req_z",
            }
        }
        return httpx.Response(
            401,
            content=json.dumps(body).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        with pytest.raises(AuthenticationError) as info:
            client.scheduled_messages.retrieve("msg_1")
    assert info.value.code == "authentication_required"
    assert info.value.message == "bad key"
    assert info.value.request_id == "req_z"


def test_scheduled_messages_missing_required_field_raises_validation_error(
    mock_client,
) -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{}", headers={"content-type": "application/json"})

    with mock_client(handler) as client:
        with pytest.raises(ValidationError):
            client.scheduled_messages.retrieve("msg_1")
