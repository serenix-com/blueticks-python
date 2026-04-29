from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

CampaignStatus = Literal[
    "pending",
    "running",
    "paused",
    "complete_sent",
    "complete_delivered",
    "aborted",
]


class Campaign(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    name: str
    audience_id: str
    status: CampaignStatus
    total_count: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    from_: Optional[str] = Field(default=None, alias="from")
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    aborted_at: Optional[str] = None
