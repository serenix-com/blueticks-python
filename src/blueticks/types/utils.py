from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict


class PhoneValidation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    valid: bool
    formatted_chat_id: Optional[str] = None  # noqa: UP045


class LinkPreview(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    thumbnail: Optional[str] = None  # noqa: UP045
    canonical_url: Optional[str] = None  # noqa: UP045
