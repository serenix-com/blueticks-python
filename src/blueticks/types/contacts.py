from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Contact(BaseModel):
    """A WhatsApp contact from the workspace contact book."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    chat_id: str
    name: Optional[str] = None  # noqa: UP045
    is_business: Optional[bool] = None  # noqa: UP045
