from __future__ import annotations

from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict


class EngineStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")

    connected: bool
    state: Optional[str] = None  # noqa: UP045
    stream: Optional[str] = None  # noqa: UP045
    has_synced: Optional[bool] = None  # noqa: UP045


class WhatsAppMe(BaseModel):
    model_config = ConfigDict(extra="ignore")

    phone: Optional[str] = None  # noqa: UP045
    name: Optional[str] = None  # noqa: UP045
    platform: Optional[str] = None  # noqa: UP045
