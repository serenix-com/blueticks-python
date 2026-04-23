from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Account(BaseModel):
    """Response from GET /v1/account."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    timezone: str | None
    created_at: datetime
