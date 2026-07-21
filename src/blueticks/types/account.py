from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Account(BaseModel):
    """Response from GET /v1/account."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    name: str
    user_email: Optional[str] = None  # noqa: UP045
    timezone: Optional[str] = None  # noqa: UP045
    created_at: datetime.datetime
