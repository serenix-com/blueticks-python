from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Newsletter(BaseModel):
    """Single-object response model for a WhatsApp newsletter (channel).

    Returned by ``GET /v1/newsletters/{id}`` and ``POST /v1/newsletters``.
    The identity field is ``newsletterId`` on the wire.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    newsletter_id: str = Field(alias="newsletterId")
    name: str
    description: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = Field(default=None, alias="createdAt")  # noqa: UP045
    subscribers: Optional[int] = None  # noqa: UP045
    invite: Optional[str] = None  # noqa: UP045
    verification: Optional[Literal["VERIFIED", "UNVERIFIED"]] = None  # noqa: UP045


class NewsletterListItem(BaseModel):
    """List-row response model for a WhatsApp newsletter (channel).

    Returned in each ``data[]`` row of ``GET /v1/newsletters``. Identical to
    :class:`Newsletter` except the identity field is ``chatId`` on the wire
    (matching how chats/contacts/groups list endpoints key rows by ``chatId``).
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chat_id: str = Field(alias="chatId")
    name: str
    description: Optional[str] = None  # noqa: UP045
    created_at: Optional[datetime.datetime] = Field(default=None, alias="createdAt")  # noqa: UP045
    subscribers: Optional[int] = None  # noqa: UP045
    invite: Optional[str] = None  # noqa: UP045
    verification: Optional[Literal["VERIFIED", "UNVERIFIED"]] = None  # noqa: UP045
