from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Cursor-paginated list envelope.

    Every v1 list endpoint returns this shape. Iterate ``data`` for the
    current page; pass ``next_cursor`` back as the ``cursor`` keyword of
    the next ``list(cursor=...)`` call to continue. When ``has_more`` is
    False, ``next_cursor`` is None and the iteration is complete.
    """

    model_config = ConfigDict(extra="ignore")

    data: list[T]
    has_more: bool
    next_cursor: Optional[str] = None  # noqa: UP045
