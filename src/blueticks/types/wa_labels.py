from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WaLabel(BaseModel):
    """A native WhatsApp Business label (from ``GET /v1/wa-labels``)."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    color: Optional[str] = None  # noqa: UP045


class WaLabelsResult(BaseModel):
    """Outcome of applying native WhatsApp labels to a message's chat on send."""

    model_config = ConfigDict(extra="ignore")

    requested: int
    applied: bool
    error: Optional[str] = None  # noqa: UP045
