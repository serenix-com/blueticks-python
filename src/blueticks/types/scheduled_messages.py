from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

# Lifecycle status of a queued message, in send order.
MessageStatus = Literal[
    "pending",
    "before-wa-send",
    "bt-sent",
    "sending",
    "sent",
    "sent_pending_ack",
    "confirmed",
    "delivered",
    "received",
    "read",
    "played",
    "cancelled",
    "error",
    "failed",
    "expired",
]

# The three send variants shared by the send + schedule endpoints.
ScheduledMessageType = Literal["text", "media", "poll"]

MediaKind = Literal["image", "video", "audio", "document", "sticker", "voice", "gif"]


class WaMessageKey(BaseModel):
    """The composite WhatsApp wire key that uniquely identifies a message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    from_me: bool
    remote: Optional[str] = None  # noqa: UP045
    id: Optional[str] = None  # noqa: UP045
    serialized: Optional[str] = Field(default=None, alias="_serialized")  # noqa: UP045
    participant: Optional[str] = None  # noqa: UP045


class LinkPreview(BaseModel):
    """Resolved OpenGraph-style link preview attached to a message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    title: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    canonical_url: Optional[str] = None  # noqa: UP045
    thumbnail: Optional[str] = None  # noqa: UP045


class ScheduledMessage(BaseModel):
    """A message record from the user-messages queue.

    This is the shape returned by every ``/v1/scheduled-messages`` endpoint and
    by the direct-send ``POST /v1/messages/{chatId}``. For a direct send no DB
    row is created, so ``id`` is null and ``wa_message_key`` carries the wire key.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: Optional[str] = None  # noqa: UP045
    wa_message_key: Optional[WaMessageKey] = None  # noqa: UP045
    to: str
    type: ScheduledMessageType
    text: Optional[str] = None  # noqa: UP045
    media_url: Optional[str] = None  # noqa: UP045
    media_kind: Optional[MediaKind] = None  # noqa: UP045
    poll_question: Optional[str] = None  # noqa: UP045
    poll_options: Optional[list[str]] = None  # noqa: UP045
    poll_allow_multiple: Optional[bool] = None  # noqa: UP045
    status: MessageStatus
    send_at: Optional[datetime.datetime] = None  # noqa: UP045
    created_at: datetime.datetime
    confirmed_at: Optional[datetime.datetime] = None  # noqa: UP045
    received_at: Optional[datetime.datetime] = None  # noqa: UP045
    read_at: Optional[datetime.datetime] = None  # noqa: UP045
    played_at: Optional[datetime.datetime] = None  # noqa: UP045
    failed_at: Optional[datetime.datetime] = None  # noqa: UP045
    failure_reason: Optional[str] = None  # noqa: UP045
    secret: Optional[str] = None  # noqa: UP045
    link_preview: Optional[LinkPreview] = None  # noqa: UP045
