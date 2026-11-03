from __future__ import annotations

import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class RealtimeTopics(BaseModel):
    """MQTT topics to subscribe to."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    messages: str


class RealtimeToken(BaseModel):
    """MQTT credentials from ``POST /v1/realtime/token``."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    broker_url: str
    username: str
    password: str
    expires_at: datetime.datetime
    expires_in_seconds: int
    topics: RealtimeTopics
