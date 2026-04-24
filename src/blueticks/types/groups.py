from __future__ import annotations

from typing import Optional  # noqa: UP045

from pydantic import BaseModel, ConfigDict


class Group(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: Optional[str] = None  # noqa: UP045
    description: Optional[str] = None  # noqa: UP045
    owner: Optional[str] = None  # noqa: UP045
    created_at: Optional[str] = None  # noqa: UP045
    participant_count: Optional[int] = None  # noqa: UP045
    announce: Optional[bool] = None  # noqa: UP045
    restrict: Optional[bool] = None  # noqa: UP045
