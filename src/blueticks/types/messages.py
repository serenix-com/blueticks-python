from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from blueticks.types.scheduled_messages import LinkPreview, WaMessageKey

# Message-kind filter accepted by messages.list `message_types`. Mirrors
# MESSAGE_TYPE_VALUES on the backend (src/services/api/v1/lib/message-types.ts).
MessageType = Literal[
    "chat",
    "image",
    "video",
    "document",
    "audio",
    "ptt",
    "sticker",
    "gif",
    "ptv",
    "poll_creation",
    "location",
    "vcard",
    "revoked",
]

# Reason the media bytes could not be downloaded (or never existed). None on success.
MediaUnavailableReason = Literal[
    "expired",
    "fetching",
    "awaiting_sender",
    "error",
    "no_media",
]


class QuotedMessage(BaseModel):
    """The message a reply quotes, embedded on :class:`Message.quoted_message`."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    wa_message_key: WaMessageKey
    text: Optional[str] = None  # noqa: UP045
    type: Optional[str] = None  # noqa: UP045
    author: Optional[str] = None  # noqa: UP045


class Message(BaseModel):
    """An engine-sourced message from GET /v1/messages and GET /v1/messages/{waMessageKey}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    wa_message_key: WaMessageKey
    chat_id: str
    # `from` is a reserved keyword; read it as `result.from_`.
    from_: str = Field(alias="from")
    author: Optional[str] = None  # noqa: UP045
    sender_name: Optional[str] = None  # noqa: UP045
    timestamp: Optional[datetime.datetime] = None  # noqa: UP045
    text: Optional[str] = None  # noqa: UP045
    type: str
    from_me: bool
    ack: Optional[int] = None  # noqa: UP045
    media_url: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045
    link_preview: Optional[LinkPreview] = None  # noqa: UP045
    quoted_message: Optional[QuotedMessage] = None  # noqa: UP045


class MessageAck(BaseModel):
    """Response from GET /v1/messages/ack/{waMessageKey}.

    ``ack`` codes: -1=error, 0=pending, 1=server, 2=device, 3=read, 4=played;
    None when the engine has not yet returned a status.
    """

    model_config = ConfigDict(extra="ignore")

    ack: Optional[int] = None  # noqa: UP045


class BatchMessageAck(BaseModel):
    """One entry in the POST /v1/messages/acks response page."""

    model_config = ConfigDict(extra="ignore")

    key: str
    ack: Optional[int] = None  # noqa: UP045
    found: bool


class LoadOlderResult(BaseModel):
    """Response from POST /v1/messages/load_older/{chatId}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    total_messages: Optional[int] = None  # noqa: UP045
    added: Optional[int] = None  # noqa: UP045
    can_load_more: bool
    history_unavailable: bool
    error: Optional[str] = None  # noqa: UP045


class MessageMedia(BaseModel):
    """Response from GET /v1/messages/media/{waMessageKey}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    url: Optional[str] = None  # noqa: UP045
    mimetype: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045
    data_base64: Optional[str] = None  # noqa: UP045
    # false when WA returned a preview JPEG instead of the original; None on
    # a genuine original.
    original_quality: Optional[bool] = None  # noqa: UP045
    media_unavailable: Optional[MediaUnavailableReason] = None  # noqa: UP045


class PinnedMessage(BaseModel):
    """One entry in the GET /v1/messages/pinned/{chatId} response page."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    key: str
    chat_id: str
    text: Optional[str] = None  # noqa: UP045
