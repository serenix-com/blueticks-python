from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict, Field

# Status + media-kind enums for the Message response shape returned by
# POST /v1/chats/{chat_id}/messages. Identical to the scheduled-messages
# enums; duplicated here to keep chats.py self-contained (the chats
# resource shouldn't have to import from scheduled_messages).
MessageStatus = Literal["pending", "confirmed", "received", "read", "played", "failed"]
MessageKind = Literal["text", "media", "poll"]
MessageMediaKind = Literal["image", "video", "audio", "document", "sticker", "voice", "gif"]


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
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    is_group: bool = Field(alias="isGroup")
    is_newsletter: bool = Field(alias="isNewsletter")
    last_message_at: Optional[str] = Field(default=None, alias="lastMessageAt")  # noqa: UP045
    unread_count: Optional[int] = Field(default=None, alias="unreadCount")  # noqa: UP045
    marked_unread: bool = Field(alias="markedUnread")


class Participant(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chat_id: str = Field(alias="chatId")
    is_admin: bool = Field(alias="isAdmin")
    is_super_admin: Optional[bool] = Field(default=None, alias="isSuperAdmin")  # noqa: UP045


class ChatMessage(BaseModel):
    """A message as returned by /v1/chats/{id}/messages — engine-sourced."""

    # `from` is a reserved keyword; populate_by_name lets callers read
    # result.from_ while the wire field stays `from`.
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: str
    chat_id: str = Field(alias="chatId")
    from_: str = Field(alias="from")
    timestamp: Optional[str] = None  # noqa: UP045
    text: Optional[str] = None  # noqa: UP045
    type: str
    from_me: bool = Field(alias="fromMe")
    ack: Optional[int] = None  # noqa: UP045
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")  # noqa: UP045
    # Caption + filename for media messages. For documents, `filename` is
    # the only discriminator (text is empty). For images/videos, `caption`
    # carries the user-visible text. Both are None for plain chat msgs and
    # for media without a caption.
    caption: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045


MediaUnavailableReason = Literal[
    "expired",
    "fetching",
    "awaiting_sender",
    "error",
    "no_media",
]


class ChatMedia(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    url: Optional[str] = None  # noqa: UP045
    mimetype: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045
    data_base64: Optional[str] = Field(default=None, alias="dataBase64")  # noqa: UP045
    # false when WA returned a preview JPEG instead of the original (#113 —
    # own-sent newsletter media only). None/absent when bytes are the
    # genuine original from the sender.
    original_quality: Optional[bool] = Field(default=None, alias="originalQuality")  # noqa: UP045
    # Reason the bytes couldn't be retrieved. None/absent on success.
    # "expired" = WA aged the file out of CDN retention. "fetching" = WA is
    # mid-download from its CDN — transient, retry in a few seconds.
    # "awaiting_sender" = WA's CDN doesn't have the file but has asked the
    # sender's device to reupload it; only completes when the sender's
    # WhatsApp client is open and online. "error" = unexpected failure.
    # "no_media" = the message is text-only/revoked/location/vcard.
    media_unavailable: Optional[MediaUnavailableReason] = Field(  # noqa: UP045
        default=None,
        alias="mediaUnavailable",
        description=(
            "Set when the bytes could not be downloaded or never existed. "
            '"expired" = WA aged the file out of CDN retention. '
            '"fetching" = WA is mid-download from its CDN — transient, retry in a few seconds. '
            "\"awaiting_sender\" = WA's CDN does not have the file but has asked the sender's "
            "device to reupload it; only completes when the sender's WhatsApp client is open and "
            'online. "error" = unexpected failure. "no_media" = the message is text-only / revoked '
            "/ location / vcard."
        ),
    )


class OkResponse(BaseModel):
    """Generic ok envelope returned by mark_read and react endpoints."""

    model_config = ConfigDict(extra="ignore")

    ok: Literal[True]


class ChatRef(BaseModel):
    """Response from POST /v1/chats/{chatId}/open."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chat_id: str = Field(alias="chatId")


class MessageAck(BaseModel):
    """Response from GET /v1/messages/ack/{waMessageKey}.

    `ack` codes: -1=error, 0=pending, 1=server, 2=device, 3=read, 4=played;
    None when no engine response.
    """

    model_config = ConfigDict(extra="ignore")

    ack: Optional[int] = None  # noqa: UP045


class LoadOlderMessagesResponse(BaseModel):
    """Response from POST /v1/messages/load_older/{chatId}."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    total_messages: Optional[int] = Field(default=None, alias="totalMessages")  # noqa: UP045
    added: Optional[int] = None  # noqa: UP045
    can_load_more: bool = Field(alias="canLoadMore")


class MediaUrlResponse(BaseModel):
    """Response from GET /v1/messages/media_url/{waMessageKey}."""

    model_config = ConfigDict(extra="ignore")

    url: Optional[str] = None  # noqa: UP045


class BatchMessageAckEntry(BaseModel):
    """One entry in :class:`BatchMessageAcksResponse.data`.

    `ack` codes: -1=error, 0=pending, 1=server, 2=device, 3=read, 4=played;
    `None` when the engine has not yet returned a status for this key.
    """

    model_config = ConfigDict(extra="ignore")

    key: str
    ack: Optional[int] = None  # noqa: UP045


class BatchMessageAcksResponse(BaseModel):
    """Response from POST /v1/messages/acks."""

    model_config = ConfigDict(extra="ignore")

    data: list[BatchMessageAckEntry]


class MessageLinkPreview(BaseModel):
    """Resolved link preview attached to a sent message."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    title: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    canonical_url: Optional[str] = Field(default=None, alias="canonicalUrl")  # noqa: UP045
    thumbnail: Optional[str] = None  # noqa: UP045


class Message(BaseModel):
    """Response from POST /v1/messages/{chatId} — a fire-and-forget send.

    Mirrors the ScheduledMessage shape but is emitted by the direct-send
    endpoint, where ``id`` is null (no DB row is created) and ``key`` carries
    the WhatsApp wire key.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: Optional[str] = None  # noqa: UP045
    key: Optional[str] = None  # noqa: UP045
    to: str
    from_: Optional[str] = Field(default=None, alias="from")  # noqa: UP045
    type: MessageKind
    text: Optional[str] = None  # noqa: UP045
    media_url: Optional[str] = Field(default=None, alias="mediaUrl")  # noqa: UP045
    media_kind: Optional[MessageMediaKind] = Field(default=None, alias="mediaKind")  # noqa: UP045
    poll_question: Optional[str] = Field(default=None, alias="pollQuestion")  # noqa: UP045
    status: MessageStatus
    send_at: Optional[str] = Field(default=None, alias="sendAt")  # noqa: UP045
    created_at: str = Field(alias="createdAt")
    confirmed_at: Optional[str] = Field(default=None, alias="confirmedAt")  # noqa: UP045
    received_at: Optional[str] = Field(default=None, alias="receivedAt")  # noqa: UP045
    read_at: Optional[str] = Field(default=None, alias="readAt")  # noqa: UP045
    played_at: Optional[str] = Field(default=None, alias="playedAt")  # noqa: UP045
    failed_at: Optional[str] = Field(default=None, alias="failedAt")  # noqa: UP045
    failure_reason: Optional[str] = Field(default=None, alias="failureReason")  # noqa: UP045
    link_preview: Optional[MessageLinkPreview] = Field(default=None, alias="linkPreview")  # noqa: UP045
