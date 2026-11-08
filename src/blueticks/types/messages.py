from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from blueticks.types.scheduled_messages import LinkPreview, WaMessageKey

# Message-kind filter accepted by messages.list `message_types`. Mirrors the
# `messageTypes` enum in the OpenAPI spec (WhatsApp Web's own type names).
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
    "multi_vcard",
    "protocol",
    "status_notification",
    "payment",
    "groups_v4_invite",
    "template_button_reply",
    "product",
    "order",
    "interactive",
    "interactive_response",
    "reaction",
    "reaction_enc",
    "comment",
    "pin_message",
    "poll_update",
    "keep_in_chat",
    "request_phone_number",
    "call_log",
    "newsletter_admin_invite",
    "newsletter_follower_invite",
    "event_creation",
    "sharable_event_invite",
    "event_response",
    "album",
    "music",
    "sticker-pack",
    "poll_result_snapshot",
    "rich_response",
    "group-history",
    "message_history_notice",
    "native_flow",
    "buttons_response",
    "list",
    "list_response",
    "event_edit_encrypted",
    "message_edit_encrypted",
    "poll_edit_encrypted",
    "poll_add_option_encrypted",
]

# Normalized group notice action on a group-event message.
GroupEventAction = Literal[
    "join",
    "add",
    "leave",
    "remove",
    "promote",
    "demote",
    "subject",
    "description",
    "picture",
    "settings",
    "create",
    "modify",
    "auto_add",
    "join_request",
    "participants_resync",
    "other",
]

CallDirection = Literal["in", "out"]
CallMedia = Literal["voice", "video"]
CallOutcome = Literal["answered", "missed", "rejected", "unknown"]

InteractiveKind = Literal[
    "buttons",
    "native_flow",
    "buttons_response",
    "list",
    "list_response",
    "template",
    "template_button_reply",
    "interactive",
    "interactive_response",
]

# Reason the media bytes could not be downloaded (or never existed). None on success.
MediaUnavailableReason = Literal[
    "expired",
    "fetching",
    "awaiting_sender",
    "error",
    "no_media",
]


# Where an engine-sourced message was read from.
MessageSource = Literal["vault", "backup"]


class MessageListCoverage(BaseModel):
    """Coverage of a ``messages.list`` page: how far back the local store reaches.

    ``messages_scanned`` is how many stored messages the engine evaluated the
    query against (0 means only the WhatsApp search index was consulted).
    ``index_only`` true means an empty result is inconclusive.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    oldest_loaded_timestamp: Optional[float] = None  # noqa: UP045
    oldest_loaded_iso: Optional[str] = None  # noqa: UP045
    messages_scanned: Optional[int] = None  # noqa: UP045
    truncated: Optional[bool] = None  # noqa: UP045
    index_only: Optional[bool] = None  # noqa: UP045
    oldest_scanned_iso: Optional[str] = None  # noqa: UP045


class PublicReaction(BaseModel):
    """One reaction on a message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    emoji: str
    sender_id: Optional[str] = None  # noqa: UP045
    from_me: Optional[bool] = None  # noqa: UP045
    timestamp: Optional[datetime.datetime] = None  # noqa: UP045


class CallInfo(BaseModel):
    """Call details on a ``call_log`` message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    direction: CallDirection
    media: CallMedia
    outcome: CallOutcome
    duration_sec: Optional[int] = None  # noqa: UP045
    is_group: bool


class GroupEvent(BaseModel):
    """Normalized group notice on a group-event message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    action: GroupEventAction
    actor: Optional[str] = None  # noqa: UP045
    targets: Optional[list[str]] = None  # noqa: UP045


class InteractiveOption(BaseModel):
    """One button, list row or template option on an interactive message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: Optional[str] = None  # noqa: UP045
    title: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    section: Optional[str] = None  # noqa: UP045


class Interactive(BaseModel):
    """Interactive menu, click or reply attached to a message."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    kind: InteractiveKind
    options: Optional[list[InteractiveOption]] = None  # noqa: UP045
    selected_id: Optional[str] = None  # noqa: UP045
    selected_title: Optional[str] = None  # noqa: UP045
    quoted_id: Optional[str] = None  # noqa: UP045


class LoadCoverage(BaseModel):
    """How far back a chat (or a returned page) reaches.

    ``oldest_loaded_timestamp`` is epoch milliseconds; ``oldest_loaded_iso`` is the
    ISO 8601 form. Both are omitted when unknown.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    oldest_loaded_timestamp: Optional[float] = None  # noqa: UP045
    oldest_loaded_iso: Optional[str] = None  # noqa: UP045


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
    # DEPRECATED: the legacy v1 type (still emitted). Prefer `wa_type`.
    type: str
    from_me: bool
    ack: Optional[int] = None  # noqa: UP045
    media_url: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045
    link_preview: Optional[LinkPreview] = None  # noqa: UP045
    quoted_message: Optional[QuotedMessage] = None  # noqa: UP045
    source: Optional[MessageSource] = None  # noqa: UP045
    # Correlation token attached at send time; only on messages sent through this API.
    secret: Optional[str] = None  # noqa: UP045
    # WhatsApp Web's own message type (canonical). `type` above is deprecated.
    wa_type: Optional[str] = None  # noqa: UP045
    # WhatsApp Web's raw subtype, e.g. `add` or `remove` on group notices.
    subtype: Optional[str] = None  # noqa: UP045
    group_event: Optional[GroupEvent] = None  # noqa: UP045
    call: Optional[CallInfo] = None  # noqa: UP045
    interactive: Optional[Interactive] = None  # noqa: UP045
    reactions: Optional[list[PublicReaction]] = None  # noqa: UP045


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
    # The spec marks these two always-present; they are optional here so a
    # response from a backend that predates them still parses.
    # How many older pages this call actually pulled (1..pages).
    pages_executed: Optional[int] = None  # noqa: UP045
    # How far back the chat is now loaded.
    coverage: Optional[LoadCoverage] = None  # noqa: UP045


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
