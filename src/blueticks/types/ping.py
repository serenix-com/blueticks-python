from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

ConnectionType = Literal["gateway", "regular"]


class PingConnection(BaseModel):
    """One connected WhatsApp engine reported by GET /v1/ping."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    type: ConnectionType
    connected: Literal[True]


class Ping(BaseModel):
    """Response from GET /v1/ping.

    Health/connectivity probe: ``api`` confirms the API server is live, and
    ``whatsapp_connections`` lists the WhatsApp engines currently connected to
    this account. An empty list means no engine is connected.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    api: Literal["ok"]
    account_id: str
    whatsapp_connections: list[PingConnection]
    message: Optional[str] = None  # noqa: UP045
