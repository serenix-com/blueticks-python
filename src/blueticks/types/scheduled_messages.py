from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ScheduledMessageStatus = Literal["pending", "confirmed", "received", "read", "played", "failed"]
ScheduledMessageType = Literal["text", "media", "poll"]
MediaKind = Literal["image", "video", "audio", "document", "sticker", "voice", "gif"]


class LinkPreview(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    title: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    canonical_url: Optional[str] = Field(default=None, alias="canonicalUrl")  # noqa: UP045
    thumbnail: Optional[str] = None  # noqa: UP045


class ScheduledMessage(BaseModel):
    """A message queued for delivery via /v1/scheduled-messages."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    key: Optional[str] = None  # noqa: UP045
    to: str
    from_: Optional[str] = Field(default=None, alias="from")  # noqa: UP045
    type: ScheduledMessageType
    text: Optional[str] = None  # noqa: UP045
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")  # noqa: UP045
    media_kind: Optional[MediaKind] = Field(default=None, alias="mediaKind")  # noqa: UP045
    poll_question: Optional[str] = Field(default=None, alias="pollQuestion")  # noqa: UP045
    status: ScheduledMessageStatus
    send_at: Optional[str] = Field(default=None, alias="sendAt")  # noqa: UP045
    created_at: str = Field(alias="createdAt")
    confirmed_at: Optional[str] = Field(default=None, alias="confirmedAt")  # noqa: UP045
    received_at: Optional[str] = Field(default=None, alias="receivedAt")  # noqa: UP045
    read_at: Optional[str] = Field(default=None, alias="readAt")  # noqa: UP045
    played_at: Optional[str] = Field(default=None, alias="playedAt")  # noqa: UP045
    failed_at: Optional[str] = Field(default=None, alias="failedAt")  # noqa: UP045
    failure_reason: Optional[str] = Field(default=None, alias="failureReason")  # noqa: UP045
    link_preview: Optional[LinkPreview] = Field(default=None, alias="linkPreview")  # noqa: UP045
