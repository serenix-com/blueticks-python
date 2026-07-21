from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

EngineType = Literal["gateway", "regular"]


class Engine(BaseModel):
    """One connected WhatsApp engine, as returned by GET /v1/engines.

    ``id`` is the engine session's MQTT presence client id (the same id space
    as ping's ``whatsapp_connections[].id``). ``type`` is ``gateway`` (a remote,
    server-side engine) or ``regular`` (the user's own WhatsApp Web extension).
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    type: EngineType
    connected: bool
    state: Optional[str] = None  # noqa: UP045
    stream: Optional[str] = None  # noqa: UP045
    has_synced: Optional[bool] = None  # noqa: UP045
