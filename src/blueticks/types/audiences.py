from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class Audience(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    contact_count: int
    created_at: str
    contacts: Optional[List["Contact"]] = None
    page: Optional[int] = None
    has_more: Optional[bool] = None


class Contact(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    to: str
    variables: Dict[str, str]
    added_at: str


class AppendContactsResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    added: int
    contact_count: int


Audience.model_rebuild()
