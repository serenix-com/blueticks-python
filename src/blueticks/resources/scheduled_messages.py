from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


class ScheduledMessagesResource(BaseResource):
    def list(
        self,
        *,
        chat_id: str | None = None,
        search_token: str | None = None,
        status: str | None = None,
        order: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[ScheduledMessage]:
        """List scheduled messages.

        List messages in the user-messages queue (all sources: API, dashboard,
        extension), newest first (offset-paginated). Optionally filter by
        ``chat_id`` and/or lifecycle ``status``.
        """
        params: dict[str, Any] = {}
        if chat_id is not None:
            params["chatId"] = chat_id
        if search_token is not None:
            params["searchToken"] = search_token
        if status is not None:
            params["status"] = status
        if order is not None:
            params["order"] = order
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/scheduled-messages", params=params or None)
        return Page[ScheduledMessage].model_validate(envelope)

    def create(
        self,
        chat_id: str,
        *,
        type: str,  # noqa: A002
        text: str | None = None,
        media_url: str | None = None,
        media_base64: str | None = None,
        media_kind: str | None = None,
        media_filename: str | None = None,
        poll_question: str | None = None,
        poll_options: builtins.list[str] | None = None,
        poll_allow_multiple: bool | None = None,
        reply_to: str | None = None,
        secret: str | None = None,
        send_at: str | None = None,
        idempotency_key: str | None = None,
    ) -> ScheduledMessage:
        """Schedule message.

        Send or schedule a WhatsApp message to ``chat_id`` (an E.164 phone or a
        WhatsApp chat id like ``12345@c.us`` / ``...@g.us`` / ``...@newsletter``).
        Set ``type`` to ``text``, ``media``, or ``poll``. Omit ``send_at`` to send
        immediately; set it (RFC 3339, ≥10s and ≤365d in the future) to defer.

        - ``type="text"`` — required ``text`` (1–4096 chars).
        - ``type="media"`` — required ``media_url`` (HTTPS) or ``media_base64``.
          Optional ``media_kind``, ``media_filename``.
        - ``type="poll"`` — required ``poll_question`` and ``poll_options``
          (2–12 items). Optional ``poll_allow_multiple``.
        """
        body: dict[str, Any] = {"type": type}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["mediaUrl"] = media_url
        if media_base64 is not None:
            body["mediaBase64"] = media_base64
        if media_kind is not None:
            body["mediaKind"] = media_kind
        if media_filename is not None:
            body["mediaFilename"] = media_filename
        if poll_question is not None:
            body["pollQuestion"] = poll_question
        if poll_options is not None:
            body["pollOptions"] = poll_options
        if poll_allow_multiple is not None:
            body["pollAllowMultiple"] = poll_allow_multiple
        if reply_to is not None:
            body["replyTo"] = reply_to
        if secret is not None:
            body["secret"] = secret
        if send_at is not None:
            body["sendAt"] = send_at
        envelope = self._client._request(
            "POST",
            f"/v1/scheduled-messages/{chat_id}",
            body=body,
            idempotency_key=idempotency_key,
        )
        return ScheduledMessage.model_validate(envelope["data"])

    def retrieve(self, scheduled_message_id: str) -> ScheduledMessage:
        """Get scheduled message.

        Get the current status of a message by ID.
        """
        envelope = self._client._request("GET", f"/v1/scheduled-messages/{scheduled_message_id}")
        return ScheduledMessage.model_validate(envelope["data"])

    def update(
        self,
        scheduled_message_id: str,
        *,
        type: str | None = None,  # noqa: A002
        text: str | None = None,
        media_url: str | None = None,
        media_base64: str | None = None,
        media_kind: str | None = None,
        media_filename: str | None = None,
        poll_question: str | None = None,
        poll_options: builtins.list[str] | None = None,
        poll_allow_multiple: bool | None = None,
        reply_to: str | None = None,
        secret: str | None = None,
        send_at: str | None = None,
    ) -> ScheduledMessage:
        """Update scheduled message.

        Edit a previously-queued message that has not dispatched yet (status
        ``pending``). Every field is optional — send only the fields you want to
        change; at least one is required.
        """
        body: dict[str, Any] = {}
        if type is not None:
            body["type"] = type
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["mediaUrl"] = media_url
        if media_base64 is not None:
            body["mediaBase64"] = media_base64
        if media_kind is not None:
            body["mediaKind"] = media_kind
        if media_filename is not None:
            body["mediaFilename"] = media_filename
        if poll_question is not None:
            body["pollQuestion"] = poll_question
        if poll_options is not None:
            body["pollOptions"] = poll_options
        if poll_allow_multiple is not None:
            body["pollAllowMultiple"] = poll_allow_multiple
        if reply_to is not None:
            body["replyTo"] = reply_to
        if secret is not None:
            body["secret"] = secret
        if send_at is not None:
            body["sendAt"] = send_at
        envelope = self._client._request(
            "PATCH", f"/v1/scheduled-messages/{scheduled_message_id}", body=body
        )
        return ScheduledMessage.model_validate(envelope["data"])

    def delete(self, scheduled_message_id: str) -> DeletedResource:
        """Delete scheduled message.

        Delete a scheduled or queued message so it will not be sent. Soft-deletes
        the message and records a cancellation in its delivery log. 404 if no
        pending/queued message with this id is owned by the caller.
        """
        envelope = self._client._request("DELETE", f"/v1/scheduled-messages/{scheduled_message_id}")
        return DeletedResource.model_validate(envelope["data"])
