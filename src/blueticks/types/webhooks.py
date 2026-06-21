from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

WebhookStatus = Literal["enabled", "disabled"]

WebhookEventType = Literal[
    "message.queued",
    "message.sending",
    "message.delivered",
    "message.failed",
    "message.read",
    "session.connected",
    "session.disconnected",
    "campaign.started",
    "campaign.paused",
    "campaign.resumed",
    "campaign.completed",
    "campaign.aborted",
]


class Webhook(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    url: str
    events: list[str]
    description: Optional[str] = None
    status: WebhookStatus
    created_at: str = Field(alias="createdAt")
