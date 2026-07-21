from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

CampaignStatus = Literal[
    "pending",
    "running",
    "paused",
    "complete_sent",
    "complete_delivered",
    "aborted",
]


class Campaign(BaseModel):
    """A bulk-message campaign with its live delivery counters."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    cmp_id: str
    name: str
    audience_id: str
    status: CampaignStatus
    total_count: int
    sent_count: int
    delivered_count: int
    read_count: int
    failed_count: int
    created_at: datetime.datetime
    started_at: Optional[datetime.datetime] = None  # noqa: UP045
    completed_at: Optional[datetime.datetime] = None  # noqa: UP045
    aborted_at: Optional[datetime.datetime] = None  # noqa: UP045
