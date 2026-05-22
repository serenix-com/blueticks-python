from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


class Newsletter(BaseModel):
    """Response model for a WhatsApp newsletter (channel)."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    description: Optional[str] = None  # noqa: UP045
    owner: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = None  # noqa: UP045
    subscribers: Optional[int] = None  # noqa: UP045
    invite: Optional[str] = None  # noqa: UP045
    verification: Optional[Literal["VERIFIED", "UNVERIFIED"]] = None  # noqa: UP045
