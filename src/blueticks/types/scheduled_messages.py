from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict


class ScheduledMessage(BaseModel):
    """A message queued for future delivery via /v1/scheduled-messages."""

    model_config = ConfigDict(extra="ignore")

    id: str
    to: Optional[str] = None  # noqa: UP045
    text: Optional[str] = None  # noqa: UP045
    media_url: Optional[str] = None  # noqa: UP045
    media_caption: Optional[str] = None  # noqa: UP045
    media_filename: Optional[str] = None  # noqa: UP045
    media_mime_type: Optional[str] = None  # noqa: UP045
    send_at: Optional[str] = None  # noqa: UP045
    status: Optional[str] = None  # noqa: UP045
    is_recurring: bool
    recurrence_rule: Optional[str] = None  # noqa: UP045
    created_at: Optional[str] = None  # noqa: UP045
    updated_at: Optional[str] = None  # noqa: UP045
