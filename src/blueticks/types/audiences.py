from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Audience(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    contact_count: int
    created_at: str
    contacts: Optional[list[Contact]] = None
    page: Optional[int] = None
    has_more: Optional[bool] = None


class Contact(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    to: str
    variables: dict[str, str]
    added_at: str


class AppendContactsResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    added: int
    contact_count: int


Audience.model_rebuild()
