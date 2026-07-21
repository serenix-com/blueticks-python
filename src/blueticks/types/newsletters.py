from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Verification = Literal["VERIFIED", "UNVERIFIED"]


class NewsletterListItem(BaseModel):
    """A newsletter (channel) in the list response (GET /v1/newsletters).

    The list endpoint keys the channel by ``chat_id``; the create/get endpoints
    key it by ``newsletter_id`` (see :class:`Newsletter`).
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    chat_id: str
    name: str
    description: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = None  # noqa: UP045
    subscribers: Optional[int] = None  # noqa: UP045
    invite: Optional[str] = None  # noqa: UP045
    verification: Optional[Verification] = None  # noqa: UP045


class Newsletter(BaseModel):
    """A WhatsApp newsletter (channel), as returned by create/get."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    newsletter_id: str
    name: str
    description: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = None  # noqa: UP045
    subscribers: Optional[int] = None  # noqa: UP045
    invite: Optional[str] = None  # noqa: UP045
    verification: Optional[Verification] = None  # noqa: UP045
