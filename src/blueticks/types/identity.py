from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

IdentityType = Literal["user", "group", "unknown"]
IdentitySource = Literal["engine", "cache", "unknown"]


class Identity(BaseModel):
    """A WhatsApp JID resolved to its canonical phone-form identity.

    An unknown identity is returned with ``resolved=False`` (never a 404).
    """

    model_config = ConfigDict(extra="ignore")

    input: str
    resolved: bool
    canonical: Optional[str] = None  # noqa: UP045
    phone: Optional[str] = None  # noqa: UP045
    lid: Optional[str] = None  # noqa: UP045
    aliases: list[str]
    type: IdentityType
    source: IdentitySource


class IdentityBatchResponse(BaseModel):
    """Result of ``POST /v1/identity/resolve`` (order-preserving)."""

    model_config = ConfigDict(extra="ignore")

    data: list[Identity]
