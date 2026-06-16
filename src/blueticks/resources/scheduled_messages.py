from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


class ScheduledMessagesResource(BaseResource):
    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        chat_id: str | None = None,
        status: str | None = None,
        q: str | None = None,
    ) -> Page[ScheduledMessage]:
        """List messages.

        List messages in the user-messages queue (all sources: API, dashboard,
        extension), newest first (cursor-paginated). Optionally filter by
        ``chat_id`` and/or lifecycle ``status``.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if chat_id is not None:
            params["chatId"] = chat_id
        if status is not None:
            params["status"] = status
        if q is not None:
            params["q"] = q
        data = self._client._request("GET", "/v1/scheduled-messages", params=params or None)
        return Page[ScheduledMessage].model_validate(data)

    def create(
        self,
        *,
        to: str,
        type: str,
        text: str | None = None,
        link_preview: bool | dict[str, Any] | None = None,
        media: dict[str, Any] | None = None,
        poll: dict[str, Any] | None = None,
        url: str | None = None,
        send_at: str | None = None,
        from_: str | None = None,
        reply_to: str | None = None,
        idempotency_key: str | None = None,
    ) -> ScheduledMessage:
        """Send message.

        Send a message via WhatsApp. The body is a discriminated union — set the
        ``type`` field to one of ``text``, ``media``, or ``poll``.

        **Variants:**

        - ``type="text"`` — required ``text`` (1–4096 chars).
        - ``type="media"`` — required ``media`` dict with ``url`` (HTTPS).
          Optional ``kind``, ``caption``, ``filename``.
        - ``type="poll"`` — required ``poll`` dict with ``question`` and
          ``options`` (2–12 items). Optional ``allow_multiple``.

        All variants accept optional ``send_at`` (ISO 8601, ≥10s future, ≤365d),
        ``from_`` (international-format sender for multi-session workspaces), and ``reply_to``
        (wire ``key`` of a prior message to quote).
        """
        body: dict[str, Any] = {"type": type, "to": to}
        if text is not None:
            body["text"] = text
        if link_preview is not None:
            body["linkPreview"] = link_preview
        if media is not None:
            body["media"] = media
        if poll is not None:
            body["poll"] = poll
        if url is not None:
            body["url"] = url
        if send_at is not None:
            body["sendAt"] = send_at
        if from_ is not None:
            body["from"] = from_
        if reply_to is not None:
            body["replyTo"] = reply_to

        data = self._client._request(
            "POST",
            "/v1/scheduled-messages",
            body=body,
            idempotency_key=idempotency_key,
        )
        return ScheduledMessage.model_validate(data)

    def retrieve(self, scheduled_message_id: str) -> ScheduledMessage:
        """Get message.

        Get the current status of a message by ID.
        """
        data = self._client._request("GET", f"/v1/scheduled-messages/{scheduled_message_id}")
        return ScheduledMessage.model_validate(data)

    def update(
        self,
        scheduled_message_id: str,
        *,
        text: str | None = None,
        media_url: str | None = None,
        media_caption: str | None = None,
        send_at: str | None = None,
    ) -> ScheduledMessage:
        """Update message.

        Edit a previously-pending message that has not dispatched yet. Accepts a
        subset of ``text``, ``media_url``, ``media_caption``, ``send_at`` — at
        least one is required. Returns 400 once the message has advanced past
        the editable window (status is no longer ``pending``).
        """
        body: dict[str, Any] = {}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["mediaUrl"] = media_url
        if media_caption is not None:
            body["mediaCaption"] = media_caption
        if send_at is not None:
            body["sendAt"] = send_at
        data = self._client._request(
            "PATCH", f"/v1/scheduled-messages/{scheduled_message_id}", body=body
        )
        return ScheduledMessage.model_validate(data)
