from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

WebhookStatus = Literal["enabled", "disabled"]

# The events a webhook can subscribe to (accepted by create/update).
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
    "new_message_received_webhook",
    "message_reaction_webhook",
    "ack_changed_webhook",
    "participant_joined_via_link_webhook",
    "participant_added_by_admin_webhook",
    "participant_left_group_webhook",
    "participant_kicked_from_group_webhook",
    "group_admin_changed_webhook",
    "group_name_changed_webhook",
    "group_description_changed_webhook",
    "group_message_pinned_webhook",
    "poll_vote_webhook",
    "reply_to_my_message_webhook",
    "message_deleted_revoked_webhook",
    "message_edited_webhook",
]


class Webhook(BaseModel):
    """A registered webhook subscription."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    url: str
    events: list[str]
    description: Optional[str] = None  # noqa: UP045
    status: WebhookStatus
    created_at: datetime.datetime


class WebhookEvent(BaseModel):
    """A webhook delivery payload, parsed and verified by ``blueticks.webhooks.verify``.

    Not an API response type — this is the JSON body POSTed to your endpoint.
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    type: str
    created_at: str
    data: dict[str, Any]
