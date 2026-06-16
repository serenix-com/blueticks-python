from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict, Field


class Contact(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    chat_id: str = Field(alias="chatId")
    name: Optional[str] = None  # noqa: UP045
    is_business: bool = Field(alias="isBusiness")


class ProfilePicture(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: Optional[str] = None  # noqa: UP045
