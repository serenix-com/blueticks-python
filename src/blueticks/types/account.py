from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class Account(BaseModel):
    """Response from GET /v1/account."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    timezone: Optional[str] = None  # noqa: UP045
    created_at: datetime
