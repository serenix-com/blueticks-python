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
    audience_id: str = Field(alias="audienceId")
    status: CampaignStatus
    total_count: int = Field(alias="totalCount")
    sent_count: int = Field(alias="sentCount")
    delivered_count: int = Field(alias="deliveredCount")
    read_count: int = Field(alias="readCount")
    failed_count: int = Field(alias="failedCount")
    from_: Optional[str] = Field(default=None, alias="from")
    created_at: str = Field(alias="createdAt")
    started_at: Optional[str] = Field(default=None, alias="startedAt")
    completed_at: Optional[str] = Field(default=None, alias="completedAt")
    aborted_at: Optional[str] = Field(default=None, alias="abortedAt")
