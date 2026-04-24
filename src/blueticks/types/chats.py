from __future__ import annotations

from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict, Field


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


class ChatMedia(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: Optional[str] = None  # noqa: UP045
    mimetype: Optional[str] = None  # noqa: UP045
    filename: Optional[str] = None  # noqa: UP045
    data_base64: Optional[str] = None  # noqa: UP045
