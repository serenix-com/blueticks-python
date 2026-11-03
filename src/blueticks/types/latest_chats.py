from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from blueticks.types.chats import ChatType
from blueticks.types.messages import Message


class LatestChatWithMessages(BaseModel):
    """A recent chat together with its latest messages (newest-first)."""

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
    messages: list[Message]


class LatestChatsResponse(BaseModel):
    """Result of ``GET /v1/latest-chats``."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    chats: list[LatestChatWithMessages]
    total_chats: int
    number_of_chats: int
    number_of_messages: int
