from __future__ import annotations

from typing import Any, Dict, Optional

from blueticks._base_resource import BaseResource
from blueticks.types.messages import Message


class MessagesResource(BaseResource):
    def send(
        self,
        *,
        to: str,
        text: Optional[str] = None,
        media_url: Optional[str] = None,
        media_caption: Optional[str] = None,
        send_at: Optional[str] = None,
        from_: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Message:
        """Send a message immediately, or schedule one for later with ``send_at``."""
        body: Dict[str, Any] = {"to": to}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["media_url"] = media_url
        if media_caption is not None:
            body["media_caption"] = media_caption
        if send_at is not None:
            body["send_at"] = send_at
        if from_ is not None:
            body["from"] = from_

        data = self._client._request(
            "POST",
            "/v1/messages",
            body=body,
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)

    def get(self, message_id: str) -> Message:
        """Retrieve a single message by id."""
        data = self._client._request("GET", f"/v1/messages/{message_id}")
        return Message.model_validate(data)
