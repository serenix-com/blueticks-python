from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict, Field

# Single source of truth for the WhatsApp message-`type` enum. Mirrors
# MESSAGE_TYPE_VALUES on the backend (src/services/api/v1/lib/message-types.ts).
# Used by ChatMessage.type (response) and message_types filter (request).
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


class Chat(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    is_group: bool
    last_message_at: Optional[str] = None  # noqa: UP045
    unread_count: Optional[int] = None  # noqa: UP045


class Participant(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chat_id: str
    is_admin: bool
    is_super_admin: Optional[bool] = None  # noqa: UP045


class ChatMessage(BaseModel):
    """A message as returned by /v1/chats/{id}/messages — engine-sourced."""

    # `from` is a reserved keyword; populate_by_name lets callers read
    # result.from_ while the wire field stays `from`.
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: str
    chat_id: str
    from_: str = Field(alias="from")
    timestamp: Optional[str] = None  # noqa: UP045
    text: Optional[str] = None  # noqa: UP045
    type: str
    from_me: bool
    ack: Optional[int] = None  # noqa: UP045
    media_url: Optional[str] = None  # noqa: UP045
    # Caption + filename for media messages. For documents, `filename` is
    # the only discriminator (text is empty). For images/videos, `caption`
    # carries the user-visible text. Both are None for plain chat msgs and
    # for media without a caption.
    caption: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045


MediaUnavailableReason = Literal[
    "expired",
    "fetching",
    "error",
    "no_media",
]


class ChatMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: Optional[str] = None  # noqa: UP045
    mimetype: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045
    data_base64: Optional[str] = None  # noqa: UP045
    # false when WA returned a preview JPEG instead of the original (#113 —
    # own-sent newsletter media only). None/absent when bytes are the
    # genuine original from the sender.
    original_quality: Optional[bool] = None  # noqa: UP045
    # Reason the bytes couldn't be retrieved. None/absent on success.
    media_unavailable: Optional[MediaUnavailableReason] = None  # noqa: UP045
