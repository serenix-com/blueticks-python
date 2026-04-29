from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.messages import Message
from blueticks.types.page import Page


class MessagesResource(BaseResource):
    def send(
        self,
        *,
        to: str,
        text: str | None = None,
        media_url: str | None = None,
        media_caption: str | None = None,
        send_at: str | None = None,
        from_: str | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Send a message immediately, or schedule one for later with ``send_at``."""
        body: dict[str, Any] = {"to": to}
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

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Message]:
        """List messages sent through the API, newest first. Cursor-paginated."""
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/messages", params=params or None)
        return Page[Message].model_validate(data)
