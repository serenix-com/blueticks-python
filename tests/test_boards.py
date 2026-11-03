from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.boards import (
    BoardDetail,
    BoardItem,
    BoardRow,
    BulkItemsResponse,
    FindSimilarResponse,
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


_BOARD = {
    "board_id": "b1",
    "name": "Tasks",
    "description": "Agent tasks",
    "domain": "tasks",
    "agent_managed": True,
    "memory_retention_days": 30,
    "item_count": 4,
    "web_url": "https://app.blueticks.co/boards/b1",
    "created_at": "2026-04-23T00:00:00Z",
    "updated_at": "2026-04-24T00:00:00Z",
}


def _detail():
    return {
        **_BOARD,
        "columns": [
            {
                "column_id": "c1",
                "title": "Status",
                "type": "status",
                "options": [{"label": "Open", "bgcolor": "#fff"}],
            }
        ],
    }


def _item(iid="i1", **overrides):
    data = {
        "item_id": iid,
        "text": "Call Dana",
        "status": {"label": "Open", "bgcolor": "#fff"},
        "priority": None,
        "due_date": "2026-05-01",
        "cells": {"c1": "x", "c2": 3},
        "source": {"chat_id": "1@c.us", "message_key": "k1", "extracted_at": 1700000000},
        "confidence": 0.8,
        "last_seen_at": 1700000001,
        "web_url": "https://app.blueticks.co/boards/b1/i1",
        "created_at": "2026-04-23T00:00:00Z",
        "updated_at": "2026-04-24T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_list_boards_returns_page():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.method == "GET"
        assert req.url.path == "/v1/boards"
        return _page([_BOARD])

    page = _client(handler).boards.list(domain="tasks", agent_managed=True, order="asc", limit=10)
    assert isinstance(page, Page)
    assert isinstance(page.data[0], BoardRow)
    assert page.data[0].memory_retention_days == 30
    assert page.data[0].created_at.year == 2026
    assert params_seen == {
        "domain": "tasks",
        "agent_managed": "true",
        "order": "asc",
        "limit": "10",
    }


def test_create_board():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/boards"
        return _ok(_detail())

    board = _client(handler).boards.create(
        entity_kind="deals", description="Sales deals", memory_retention_days=14
    )
    assert isinstance(board, BoardDetail)
    assert board.columns[0].options[0].label == "Open"
    assert body_seen == {
        "entity_kind": "deals",
        "description": "Sales deals",
        "memory_retention_days": 14,
    }


def test_retrieve_board():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/boards/b1"
        return _ok(_detail())

    board = _client(handler).boards.retrieve("b1")
    assert board.board_id == "b1"
    assert board.agent_managed is True


def test_list_board_items():
    params_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        params_seen.update(dict(req.url.params))
        assert req.method == "GET"
        assert req.url.path == "/v1/boards/b1/items"
        return _page([_item(), _item("i2", status=None)])

    page = _client(handler).boards.list_items(
        "b1", status="Open", active_only=True, updated_since="2026-04-01T00:00:00Z", skip=5
    )
    assert isinstance(page.data[0], BoardItem)
    assert page.data[0].status is not None and page.data[0].status.label == "Open"
    assert page.data[0].cells == {"c1": "x", "c2": 3}
    assert page.data[0].source is not None and page.data[0].source.chat_id == "1@c.us"
    assert page.data[1].status is None
    assert params_seen == {
        "status": "Open",
        "active_only": "true",
        "updated_since": "2026-04-01T00:00:00Z",
        "skip": "5",
    }


def test_create_board_item_serializes_snake_case_body():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/boards/b1/items"
        return _ok(_item(), status=201)

    item = _client(handler).boards.create_item(
        "b1",
        text="Call Dana",
        status="Open",
        due_date="2026-05-01",
        source={"chat_id": "1@c.us"},
        confidence=0.8,
        allow_duplicate=True,
    )
    assert isinstance(item, BoardItem)
    assert item.item_id == "i1"
    assert body_seen == {
        "text": "Call Dana",
        "status": "Open",
        "due_date": "2026-05-01",
        "source": {"chat_id": "1@c.us"},
        "confidence": 0.8,
        "allow_duplicate": True,
    }


def test_update_board_item_soft_delete():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "PATCH"
        assert req.url.path == "/v1/boards/b1/items/i1"
        return _ok(_item(text="Updated"))

    item = _client(handler).boards.update_item(
        "b1", "i1", text="Updated", deleted=True, note="dup", cells={"c1": 2}
    )
    assert item.text == "Updated"
    assert body_seen == {"text": "Updated", "cells": {"c1": 2}, "deleted": True, "note": "dup"}


def test_bulk_upsert_board_items():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/boards/b1/items/bulk"
        return _ok(
            {
                "created": [_item("i1")],
                "updated": [_item("i2")],
                "unchanged": 3,
                "board": {"board_id": "b1", "name": "Tasks", "web_url": "https://x/b1"},
            }
        )

    result = _client(handler).boards.bulk_upsert_items(
        "b1", items=[{"text": "a"}, {"text": "b"}], mode="upsert"
    )
    assert isinstance(result, BulkItemsResponse)
    assert [i.item_id for i in result.created] == ["i1"]
    assert result.updated[0].item_id == "i2"
    assert result.unchanged == 3
    assert result.board.name == "Tasks"
    assert body_seen == {"items": [{"text": "a"}, {"text": "b"}], "mode": "upsert"}


def test_find_similar_board_items():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/boards/b1/items/find-similar"
        return _ok(
            {
                "matches": [
                    {"candidate_index": 0, "item_id": "i1", "text": "Call Dana", "score": 0.92}
                ],
                "misses": [1],
            }
        )

    result = _client(handler).boards.find_similar_items("b1", candidates=["call dana", "new"])
    assert isinstance(result, FindSimilarResponse)
    assert result.matches[0].score == 0.92
    assert result.misses == [1]
    assert body_seen == {"candidates": [{"text": "call dana"}, {"text": "new"}]}


def test_boards_retrieve_raises_authentication_error_on_401():
    with pytest.raises(AuthenticationError) as exc_info:
        _client(lambda req: _unauth()).boards.retrieve("b1")
    assert exc_info.value.request_id == "req_x1"
    assert exc_info.value.code == "authentication_required"


def test_boards_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).boards.retrieve("b1")
