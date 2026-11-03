from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.boards import (
    BoardDetail,
    BoardItem,
    BoardRow,
    BulkItemsResponse,
    CellsMap,
    FindSimilarResponse,
    ItemSource,
)
from blueticks.types.page import Page


def _source_body(source: ItemSource | dict[str, Any]) -> dict[str, Any]:
    if isinstance(source, ItemSource):
        return source.model_dump(exclude_none=True)
    return source


def _item_body(
    *,
    text: str | None,
    status: str | None,
    priority: str | None,
    due_date: str | None,
    cells: CellsMap | None,
    source: ItemSource | dict[str, Any] | None,
    confidence: float | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if text is not None:
        body["text"] = text
    if status is not None:
        body["status"] = status
    if priority is not None:
        body["priority"] = priority
    if due_date is not None:
        body["due_date"] = due_date
    if cells is not None:
        body["cells"] = cells
    if source is not None:
        body["source"] = _source_body(source)
    if confidence is not None:
        body["confidence"] = confidence
    return body


class BoardsResource(BaseResource):
    def list(
        self,
        *,
        domain: str | None = None,
        agent_managed: bool | None = None,
        order: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[BoardRow]:
        """List boards.

        List boards, newest first. Filter by ``domain`` or ``agent_managed``.
        Offset-paginated via ``limit`` + ``skip``. Requires ``boards:read``.
        """
        params: dict[str, Any] = {}
        if domain is not None:
            params["domain"] = domain
        if agent_managed is not None:
            params["agent_managed"] = agent_managed
        if order is not None:
            params["order"] = order
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/boards", params=params or None)
        return Page[BoardRow].model_validate(envelope)

    def create(
        self,
        *,
        domain: str | None = None,
        entity_kind: str | None = None,
        name: str | None = None,
        description: str | None = None,
        agent_id: str | None = None,
        memory_retention_days: int | None = None,
    ) -> BoardDetail:
        """Create or find board.

        Find-or-create the agent memory board for (``agent_id``, ``domain``). Pass
        ``domain`` for a built-in board (``tasks``/``leads``/``invoices``) or
        ``entity_kind`` to open a NEW dynamic (``custom:<slug>``) board with a
        generic template — ``description`` is then required. Returns the existing
        board if one exists, else provisions it from the domain template. Requires
        ``boards:write``.
        """
        body: dict[str, Any] = {}
        if domain is not None:
            body["domain"] = domain
        if entity_kind is not None:
            body["entity_kind"] = entity_kind
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if agent_id is not None:
            body["agent_id"] = agent_id
        if memory_retention_days is not None:
            body["memory_retention_days"] = memory_retention_days
        envelope = self._client._request("POST", "/v1/boards", body=body)
        return BoardDetail.model_validate(envelope["data"])

    def retrieve(self, board_id: str) -> BoardDetail:
        """Get board.

        Retrieve a board with its columns, options and item count. Requires
        ``boards:read``.
        """
        envelope = self._client._request("GET", f"/v1/boards/{board_id}")
        return BoardDetail.model_validate(envelope["data"])

    def list_items(
        self,
        board_id: str,
        *,
        status: str | None = None,
        order: str | None = None,
        active_only: bool | None = None,
        updated_since: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[BoardItem]:
        """List board items.

        List a board's items (tasks). Pass ``active_only=True`` to return only
        items updated within the retention window whose status is non-terminal
        (the AI's "active memory" view). Filter by ``status`` label or
        ``updated_since`` (ISO 8601 / epoch-ms cutoff). Requires ``boards:read``.
        """
        params: dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if order is not None:
            params["order"] = order
        if active_only is not None:
            params["active_only"] = active_only
        if updated_since is not None:
            params["updated_since"] = updated_since
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request(
            "GET", f"/v1/boards/{board_id}/items", params=params or None
        )
        return Page[BoardItem].model_validate(envelope)

    def create_item(
        self,
        board_id: str,
        *,
        text: str,
        status: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        cells: CellsMap | None = None,
        source: ItemSource | dict[str, Any] | None = None,
        confidence: float | None = None,
        allow_duplicate: bool | None = None,
    ) -> BoardItem:
        """Create board item.

        Create one item. ``status``/``priority`` are given as LABELS and resolved
        to the board's options server-side (unknown label → 422 with the valid
        labels). Dedupe fingerprint + provenance are stamped server-side. Requires
        ``boards:write``.
        """
        body = _item_body(
            text=text,
            status=status,
            priority=priority,
            due_date=due_date,
            cells=cells,
            source=source,
            confidence=confidence,
        )
        if allow_duplicate is not None:
            body["allow_duplicate"] = allow_duplicate
        envelope = self._client._request("POST", f"/v1/boards/{board_id}/items", body=body)
        return BoardItem.model_validate(envelope["data"])

    def update_item(
        self,
        board_id: str,
        item_id: str,
        *,
        text: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        due_date: str | None = None,
        cells: CellsMap | None = None,
        source: ItemSource | dict[str, Any] | None = None,
        confidence: float | None = None,
        deleted: bool | None = None,
        note: str | None = None,
    ) -> BoardItem:
        """Update board item.

        Update cells, soft-delete (``deleted=True``) or restore (``deleted=False``)
        an item. ``note`` is recorded in the item's history. Requires
        ``boards:write``.
        """
        body = _item_body(
            text=text,
            status=status,
            priority=priority,
            due_date=due_date,
            cells=cells,
            source=source,
            confidence=confidence,
        )
        if deleted is not None:
            body["deleted"] = deleted
        if note is not None:
            body["note"] = note
        envelope = self._client._request(
            "PATCH", f"/v1/boards/{board_id}/items/{item_id}", body=body
        )
        return BoardItem.model_validate(envelope["data"])

    def bulk_upsert_items(
        self,
        board_id: str,
        *,
        items: builtins.list[dict[str, Any]],
        mode: str | None = None,
    ) -> BulkItemsResponse:
        """Bulk upsert board items.

        Create or merge many items in one call. Each item (a dict with the same
        keys as :meth:`create_item`: ``text`` plus optional ``status``,
        ``priority``, ``due_date``, ``cells``, ``source``, ``confidence``,
        ``allow_duplicate``) is fingerprinted and matched against the board's
        existing items — a match is patched, a miss is created. Requires
        ``boards:write``.
        """
        body: dict[str, Any] = {"items": items}
        if mode is not None:
            body["mode"] = mode
        envelope = self._client._request("POST", f"/v1/boards/{board_id}/items/bulk", body=body)
        return BulkItemsResponse.model_validate(envelope["data"])

    def find_similar_items(
        self, board_id: str, *, candidates: builtins.list[str]
    ) -> FindSimilarResponse:
        """Find similar board items.

        Server-side dedupe: match each candidate text against the board's items by
        normalized fingerprint + fuzzy token overlap, returning match pairs (and the
        indexes of the misses). Use before creating to avoid duplicates. Requires
        ``boards:read``.
        """
        body = {"candidates": [{"text": c} for c in candidates]}
        envelope = self._client._request(
            "POST", f"/v1/boards/{board_id}/items/find-similar", body=body
        )
        return FindSimilarResponse.model_validate(envelope["data"])
