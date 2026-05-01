from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict


class GroupParticipant(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chat_id: str
    is_admin: bool
    is_super_admin: bool
    name: Optional[str] = None  # noqa: UP045


class Group(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    owner: Optional[str] = None  # noqa: UP045
    created_at: Optional[str] = None  # noqa: UP045
    last_message_at: Optional[str] = None  # noqa: UP045
    participant_count: Optional[int] = None  # noqa: UP045
    announce: Optional[bool] = None  # noqa: UP045
    restrict: Optional[bool] = None  # noqa: UP045
    participants: Optional[list[GroupParticipant]] = None  # noqa: UP045
