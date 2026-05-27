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
        type: str,
        text: str | None = None,
        link_preview: bool | dict[str, Any] | None = None,
        media: dict[str, Any] | None = None,
        poll: dict[str, Any] | None = None,
        send_at: str | None = None,
        from_: str | None = None,
        reply_to: str | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Send message.

        Send a message via WhatsApp. The body is a discriminated union — set the
        `type` field to one of `text`, `media`, or `poll`.

        **Variants:**

        - `type: "text"` — required `text` (1–4096 chars).
        - `type: "media"` — required `media` dict with `url` (HTTPS). Optional `kind`,
          `caption`, `filename`.
        - `type: "poll"` — required `poll` dict with `question` and `options` (2–12
          items). Optional `allow_multiple`.

        All variants accept optional `send_at` (ISO 8601), `from_` (E.164 sender),
        and `reply_to` (wire key of a prior message to quote-reply).
        """
        body: dict[str, Any] = {"type": type, "to": to}
        if text is not None:
            body["text"] = text
        if link_preview is not None:
            body["link_preview"] = link_preview
        if media is not None:
            body["media"] = media
        if poll is not None:
            body["poll"] = poll
        if send_at is not None:
            body["send_at"] = send_at
        if from_ is not None:
            body["from"] = from_
        if reply_to is not None:
            body["reply_to"] = reply_to

        data = self._client._request(
            "POST",
            "/v1/messages",
            body=body,
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)

    def retrieve(self, message_id: str) -> Message:
        """Get message.

        Get the current status of a message by ID.
        """
        data = self._client._request("GET", f"/v1/messages/{message_id}")
        return Message.model_validate(data)

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Message]:
        """List messages sent through the API, newest first (cursor-paginated)."""
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/messages", params=params or None)
        return Page[Message].model_validate(data)

    def update(
        self,
        message_id: str,
        *,
        text: str | None = None,
        media_url: str | None = None,
        media_caption: str | None = None,
        send_at: str | None = None,
    ) -> Message:
        """Update message.

        Edit a previously-queued message that has not dispatched yet. Accepts a
        subset of ``text``, ``media_url``, ``media_caption``, ``send_at`` — at
        least one is required. Returns 400 once the message has advanced past the
        editable window (status not in ``pending``/``sending``).
        """
        body: dict[str, Any] = {}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["media_url"] = media_url
        if media_caption is not None:
            body["media_caption"] = media_caption
        if send_at is not None:
            body["send_at"] = send_at
        data = self._client._request("PATCH", f"/v1/messages/{message_id}", body=body)
        return Message.model_validate(data)
