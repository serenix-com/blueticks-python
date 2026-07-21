from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Audience(BaseModel):
    """An audience (a named, reusable list of campaign recipients)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    name: str
    contact_count: int
    created_at: datetime.datetime


class AudienceContact(BaseModel):
    """A single contact row inside an audience."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    to: str
    variables: dict[str, Any]
    added_at: datetime.datetime


class AppendContactsResult(BaseModel):
    """Response from POST /v1/audiences/{id}/contacts."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    added: int
    contact_count: int


class RemovedContact(BaseModel):
    """Response from DELETE /v1/audiences/{id}/contacts/{contactId}."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
