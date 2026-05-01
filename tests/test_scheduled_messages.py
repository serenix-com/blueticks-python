from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import AuthenticationError
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


def _scheduled(sid: str = "sched_1", **overrides) -> dict:
    data = {
        "id": sid,
        "to": "+12025550100",
        "text": "hello future",
        "media_url": None,
        "media_caption": None,
        "media_filename": None,
        "media_mime_type": None,
        "send_at": "2026-06-01T09:00:00Z",
        "status": "pending",
        "is_recurring": False,
        "recurrence_rule": None,
        "created_at": "2026-04-23T00:00:00Z",
        "updated_at": "2026-04-23T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_list_scheduled_messages(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/scheduled-messages"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "data": [_scheduled("sched_1"), _scheduled("sched_2", is_recurring=True)],
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
    assert page.data[0].id == "sched_1"
    assert page.data[1].is_recurring is True
    assert page.has_more is False


def test_list_scheduled_messages_passes_pagination_params(mock_client) -> None:
    seen_params: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen_params.update(dict(req.url.params))
        return httpx.Response(
            200,
            content=json.dumps({"data": [], "has_more": True, "next_cursor": "cur_next"}).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        page = client.scheduled_messages.list(limit=25, cursor="cur_abc")
    assert seen_params == {"limit": "25", "cursor": "cur_abc"}
    assert page.next_cursor == "cur_next"


def test_retrieve_scheduled_message(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/scheduled-messages/sched_1"
        return httpx.Response(
            200,
            content=json.dumps(_scheduled("sched_1", text="reminder")).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.scheduled_messages.retrieve("sched_1")
    assert isinstance(result, ScheduledMessage)
    assert result.id == "sched_1"
    assert result.text == "reminder"


def test_update_scheduled_message(mock_client) -> None:
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/scheduled-messages/sched_1"
        return httpx.Response(
            200,
            content=json.dumps(_scheduled("sched_1", text="updated")).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.scheduled_messages.update(
            "sched_1",
            text="updated",
            send_at="2026-07-01T09:00:00Z",
        )
    assert result.text == "updated"
    assert body_seen == {"text": "updated", "send_at": "2026-07-01T09:00:00Z"}


def test_delete_scheduled_message_returns_none(mock_client) -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "DELETE"
        assert req.url.path == "/v1/scheduled-messages/sched_1"
        return httpx.Response(204)

    with mock_client(handler) as client:
        assert client.scheduled_messages.delete("sched_1") is None


def test_scheduled_messages_propagates_authentication_error(mock_client) -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        body = {
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "request_id": "req_z",
            }
        }
        return httpx.Response(
            401,
            content=json.dumps(body).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        with pytest.raises(AuthenticationError) as info:
            client.scheduled_messages.retrieve("sched_1")
    assert info.value.code == "authentication_required"
    assert info.value.message == "bad key"
    assert info.value.request_id == "req_z"


def test_scheduled_messages_missing_required_field_raises_validation_error(mock_client) -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{}", headers={"content-type": "application/json"})

    with mock_client(handler) as client:
        with pytest.raises(ValidationError):
            client.scheduled_messages.retrieve("sched_1")
