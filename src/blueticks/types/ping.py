from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from pydantic import BaseModel, ConfigDict


class Ping(BaseModel):
    """Response from GET /v1/ping."""

    model_config = ConfigDict(extra="ignore")

    account_id: str
    key_prefix: str
    scopes: list[str]
