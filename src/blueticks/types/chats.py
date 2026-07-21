from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

ChatType = Literal["contact", "group", "newsletter"]


class Chat(BaseModel):
    """A chat (conversation) as seen by the connected WhatsApp engine."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    chat_id: str
    name: Optional[str] = None  # noqa: UP045
    chat_type: ChatType
    pinned: Optional[bool] = None  # noqa: UP045
    archived: Optional[bool] = None  # noqa: UP045
    last_message_at: Optional[datetime.datetime] = None  # noqa: UP045
    unread_count: Optional[int] = None  # noqa: UP045
    marked_unread: bool
    last_message_text: Optional[str] = None  # noqa: UP045
    last_message_from_me: Optional[bool] = None  # noqa: UP045


class Participant(BaseModel):
    """A participant returned by GET /v1/chats/{chatId}/participants."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    chat_id: str
    name: Optional[str] = None  # noqa: UP045
    is_admin: bool
    is_super_admin: Optional[bool] = None  # noqa: UP045


class OkResponse(BaseModel):
    """Generic ``{ "ok": true }`` envelope.

    Returned by the fire-and-forget chat/message mutations: archive, unarchive,
    mark_read (chats) and pin, unpin, react (messages).
    """

    model_config = ConfigDict(extra="ignore")

    ok: Literal[True]
