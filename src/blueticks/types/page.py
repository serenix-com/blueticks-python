from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from blueticks.types.messages import MessageListCoverage

T = TypeVar("T")


class AnsweredBy(BaseModel):
    """The engine (and account number) that answered a list read."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    engine_id: str = Field(alias="engineId")
    number_id: Optional[str] = Field(default=None, alias="numberId")
    phone_number: Optional[str] = Field(default=None, alias="phoneNumber")


class PageSources(BaseModel):
    """Where the rows of a page were read from, when not all from the live engine."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    backup: Optional[int] = None


class Page(BaseModel, Generic[T]):
    """Offset-paginated list envelope.

    Every v1 list endpoint returns this shape. Iterate ``data`` for the current
    page; advance by passing ``skip=skip+limit`` to the next ``list(...)`` call.
    ``total`` is the count of items matching the query across all pages, so the
    iteration is complete once ``skip + len(data) >= total``.

    ``has_more``, ``coverage``, ``since_reached``, ``auto_loaded_pages`` and
    ``sources`` are only populated by ``messages.list`` (the cross-account message
    search). ``next_cursor`` is ``None`` on the last page and equals the next
    ``skip`` value. ``answered_by`` names the engine that served a live read.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    data: list[T]
    limit: int
    skip: int
    total: int
    next_cursor: Optional[str] = Field(default=None, alias="nextCursor")  # noqa: UP045
    answered_by: Optional[AnsweredBy] = Field(default=None, alias="answeredBy")  # noqa: UP045
    has_more: Optional[bool] = Field(default=None, alias="hasMore")  # noqa: UP045
    coverage: Optional[MessageListCoverage] = None  # noqa: UP045
    since_reached: Optional[bool] = Field(default=None, alias="sinceReached")  # noqa: UP045
    auto_loaded_pages: Optional[int] = Field(default=None, alias="autoLoadedPages")  # noqa: UP045
    sources: Optional[PageSources] = None  # noqa: UP045
