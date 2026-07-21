from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class GroupParticipant(BaseModel):
    """A member of a WhatsApp group."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    chat_id: str
    is_admin: bool
    is_super_admin: bool
    name: Optional[str] = None  # noqa: UP045


class GroupListItem(BaseModel):
    """A group in a list response (GET /v1/groups, GET /v1/contacts/{id}/common_groups).

    The lightweight list shape — without ``announce`` or the ``participants``
    roster, which are only hydrated on the single-group endpoints.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    owner: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = None  # noqa: UP045
    last_message_at: Optional[datetime.datetime] = None  # noqa: UP045
    participant_count: Optional[int] = None  # noqa: UP045
    restrict: Optional[bool] = None  # noqa: UP045


class Group(BaseModel):
    """A single WhatsApp group, optionally including its participant roster."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    owner: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = None  # noqa: UP045
    last_message_at: Optional[datetime.datetime] = None  # noqa: UP045
    participant_count: Optional[int] = None  # noqa: UP045
    announce: Optional[bool] = None  # noqa: UP045
    restrict: Optional[bool] = None  # noqa: UP045
    participants: Optional[list[GroupParticipant]] = None  # noqa: UP045
