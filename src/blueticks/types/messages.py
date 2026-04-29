from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

MessageStatus = Literal["scheduled", "queued", "sending", "delivered", "failed"]


class Message(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    to: str
    from_: Optional[str] = Field(default=None, alias="from")
    text: Optional[str] = None
    media_url: Optional[str] = None
    status: MessageStatus
    send_at: Optional[str] = None
    created_at: str
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    read_at: Optional[str] = None
    failed_at: Optional[str] = None
    failure_reason: Optional[str] = None
