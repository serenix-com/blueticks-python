from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Ping(BaseModel):
    """Response from GET /v1/ping."""

    model_config = ConfigDict(extra="ignore")

    account_id: str
    key_prefix: str
    scopes: list[str]
