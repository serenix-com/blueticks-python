from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(extra="ignore")

    id: str
    url: str
    events: List[str]
    description: Optional[str] = None
    status: WebhookStatus
    created_at: str


class WebhookCreateResult(Webhook):
    secret: str


class WebhookEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    type: str
    created_at: str
    data: Dict[str, Any]
