from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict

# Free-form per-column values on a board item, keyed by column id.
CellsMap = dict[str, Union[str, float]]

BulkItemsMode = Literal["upsert"]


class OptionRef(BaseModel):
    """A column option (status / priority label) and its colour."""

    model_config = ConfigDict(extra="ignore")

    label: str
    bgcolor: str


class BoardColumn(BaseModel):
    """A column on a board, with its selectable options."""

    model_config = ConfigDict(extra="ignore")

    column_id: str
    title: str
    type: str
    options: list[OptionRef]


class BoardRow(BaseModel):
    """A board as returned by ``GET /v1/boards``."""

    model_config = ConfigDict(extra="ignore")

    board_id: str
    name: str
    description: Optional[str] = None  # noqa: UP045
    domain: Optional[str] = None  # noqa: UP045
    agent_managed: bool
    memory_retention_days: Optional[int] = None  # noqa: UP045
    item_count: Optional[int] = None  # noqa: UP045
    web_url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BoardDetail(BoardRow):
    """A board with its columns and options (``GET /v1/boards/{id}`` and create)."""

    columns: list[BoardColumn]


class BoardRef(BaseModel):
    """Short board reference embedded in bulk-upsert responses."""

    model_config = ConfigDict(extra="ignore")

    board_id: str
    name: str
    description: Optional[str] = None  # noqa: UP045
    domain: Optional[str] = None  # noqa: UP045
    web_url: str


class ItemSource(BaseModel):
    """Provenance of a board item: the chat/message it was extracted from."""

    model_config = ConfigDict(extra="ignore")

    chat_id: Optional[str] = None  # noqa: UP045
    chat_name: Optional[str] = None  # noqa: UP045
    message_key: Optional[str] = None  # noqa: UP045
    excerpt: Optional[str] = None  # noqa: UP045
    extracted_at: Optional[int] = None  # noqa: UP045


class BoardItem(BaseModel):
    """A board item (task / lead / invoice row)."""

    model_config = ConfigDict(extra="ignore")

    item_id: str
    text: str
    status: Optional[OptionRef] = None  # noqa: UP045
    priority: Optional[OptionRef] = None  # noqa: UP045
    due_date: Optional[str] = None  # noqa: UP045
    cells: Optional[CellsMap] = None  # noqa: UP045
    source: Optional[ItemSource] = None  # noqa: UP045
    confidence: Optional[float] = None  # noqa: UP045
    last_seen_at: Optional[int] = None  # noqa: UP045
    web_url: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BulkItemsResponse(BaseModel):
    """Result of ``POST /v1/boards/{boardId}/items/bulk``."""

    model_config = ConfigDict(extra="ignore")

    created: list[BoardItem]
    updated: list[BoardItem]
    unchanged: int
    board: BoardRef


class SimilarMatch(BaseModel):
    """One candidate matched to an existing board item."""

    model_config = ConfigDict(extra="ignore")

    candidate_index: int
    item_id: str
    text: str
    score: float


class FindSimilarResponse(BaseModel):
    """Result of ``POST /v1/boards/{boardId}/items/find-similar``."""

    model_config = ConfigDict(extra="ignore")

    matches: list[SimilarMatch]
    # Indexes of candidates with no match.
    misses: list[int]
