from __future__ import annotations

from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict


class Contact(BaseModel):
    model_config = ConfigDict(extra="ignore")

    chat_id: str
    name: Optional[str] = None  # noqa: UP045
    is_business: bool


class ProfilePicture(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: Optional[str] = None  # noqa: UP045
