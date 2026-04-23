from __future__ import annotations

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
