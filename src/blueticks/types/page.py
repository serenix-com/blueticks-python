from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from blueticks.types.messages import LoadCoverage

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Offset-paginated list envelope.

    Every v1 list endpoint returns this shape. Iterate ``data`` for the current
    page; advance by passing ``skip=skip+limit`` to the next ``list(...)`` call.
    ``total`` is the count of items matching the query across all pages, so the
    iteration is complete once ``skip + len(data) >= total``.

    ``has_more`` is only populated by ``messages.list`` (the cross-account
    message search); it is ``None`` on every other list endpoint. ``coverage`` is
    likewise only populated by ``messages.list``: how far back the returned page
    reaches (oldest message timestamp in the page).
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    data: list[T]
    limit: int
    skip: int
    total: int
    has_more: Optional[bool] = Field(default=None, alias="hasMore")  # noqa: UP045
    coverage: Optional[LoadCoverage] = None  # noqa: UP045
