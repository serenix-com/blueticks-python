from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from pydantic import BaseModel, ConfigDict, Field


class Ping(BaseModel):
    """Response from GET /v1/ping."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    account_id: str = Field(alias="accountId")
    key_prefix: str
    scopes: list[str]
