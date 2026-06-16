from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict, Field


class GroupParticipant(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chat_id: str = Field(alias="chatId")
    is_admin: bool = Field(alias="isAdmin")
    is_super_admin: bool = Field(alias="isSuperAdmin")
    name: Optional[str] = None  # noqa: UP045


class Group(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    owner: Optional[str] = None  # noqa: UP045
    created_at: Optional[str] = Field(default=None, alias="createdAt")  # noqa: UP045
    last_message_at: Optional[str] = Field(default=None, alias="lastMessageAt")  # noqa: UP045
    participant_count: Optional[int] = Field(default=None, alias="participantCount")  # noqa: UP045
    announce: Optional[bool] = None  # noqa: UP045
    restrict: Optional[bool] = None  # noqa: UP045
    participants: Optional[list[GroupParticipant]] = None  # noqa: UP045
