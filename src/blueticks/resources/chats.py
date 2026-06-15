from __future__ import annotations

from collections.abc import Sequence  # avoids shadowing by `ChatsResource.list`
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.chats import (
    BatchMessageAcksResponse,
    Chat,
    ChatMedia,
    ChatMessage,
    ChatRef,
    LoadOlderMessagesResponse,
    MediaUrlResponse,
    Message,
    MessageAck,
    MessageType,
    OkResponse,
    Participant,
)
from blueticks.types.page import Page


class ChatsResource(BaseResource):
    def list(
        self,
        *,
        query: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Chat]:
        """List/search chats, newest first. Cursor-paginated."""
        params: dict[str, Any] = {}
        if query is not None:
            params["query"] = query
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/chats", params=params or None)
        return Page[Chat].model_validate(data)

    def get(self, chat_id: str) -> Chat:
        """Retrieve a chat by its JID."""
        data = self._client._request("GET", f"/v1/chats/{chat_id}")
        return Chat.model_validate(data)

    def list_participants(
        self,
        chat_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Participant]:
        """List participants in a group chat. Cursor-paginated."""
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request(
            "GET", f"/v1/chats/{chat_id}/participants", params=params or None
        )
        return Page[Participant].model_validate(data)

    def mark_read(self, chat_id: str) -> OkResponse:
        """Mark a chat as read (sends read receipts if enabled)."""
        data = self._client._request("POST", f"/v1/chats/{chat_id}/mark_read")
        return OkResponse.model_validate(data)

    def open(self, chat_id: str) -> ChatRef:
        """Open a chat on the engine (useful for UI-assisted workflows)."""
        data = self._client._request("POST", f"/v1/chats/{chat_id}/open")
        return ChatRef.model_validate(data)

    def list_messages(
        self,
        chat_id: str,
        *,
        order: str | None = None,
        query: str | None = None,
        since: str | None = None,
        until: str | None = None,
        message_types: list[MessageType] | None = None,  # type: ignore[valid-type]
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[ChatMessage]:
        """List messages in a chat. `order` is 'asc' (oldest-first) or
        'desc' (newest-first, default).

        `message_types` filters to specific message kinds (e.g. only
        `["document"]` to find PDFs). System events (gp2/revoked/
        newsletter_notification) are excluded by default unless
        explicitly listed.
        """
        params: dict[str, Any] = {}
        if order is not None:
            params["order"] = order
        if query is not None:
            params["query"] = query
        if since is not None:
            params["since"] = since
        if until is not None:
            params["until"] = until
        if message_types:
            # Server accepts comma-separated form for OpenAPI
            # `style: form, explode: false` parameter style.
            params["message_types"] = ",".join(message_types)
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", f"/v1/chats/{chat_id}/messages", params=params)
        return Page[ChatMessage].model_validate(data)

    def get_message(self, chat_id: str, key: str) -> ChatMessage:
        """Retrieve a single message by WhatsApp message key."""
        data = self._client._request("GET", f"/v1/chats/{chat_id}/messages/{key}")
        return ChatMessage.model_validate(data)

    def get_message_ack(self, chat_id: str, key: str) -> MessageAck:
        """Fetch ACK state for a single message."""
        data = self._client._request("GET", f"/v1/chats/{chat_id}/messages/{key}/ack")
        return MessageAck.model_validate(data)

    def react(self, chat_id: str, key: str, *, emoji: str) -> OkResponse:
        """Add or clear an emoji reaction on a message.

        Pass an empty string for ``emoji`` to clear an existing reaction.
        """
        data = self._client._request(
            "POST",
            f"/v1/chats/{chat_id}/messages/{key}/reactions",
            body={"emoji": emoji},
        )
        return OkResponse.model_validate(data)

    def load_older_messages(self, chat_id: str) -> LoadOlderMessagesResponse:
        """Pull older messages from the phone into the engine's local store."""
        data = self._client._request("POST", f"/v1/chats/{chat_id}/messages/load_older")
        return LoadOlderMessagesResponse.model_validate(data)

    def get_media(self, chat_id: str, key: str) -> ChatMedia:
        """Download message media (may be returned as base64)."""
        data = self._client._request("GET", f"/v1/chats/{chat_id}/messages/{key}/media")
        return ChatMedia.model_validate(data)

    def get_media_url(self, chat_id: str, key: str) -> MediaUrlResponse:
        """Get a short-lived URL for message media, if available."""
        data = self._client._request("GET", f"/v1/chats/{chat_id}/messages/{key}/media_url")
        return MediaUrlResponse.model_validate(data)

    def send_message(
        self,
        chat_id: str,
        *,
        type: str,
        text: str | None = None,
        link_preview: bool | dict[str, Any] | None = None,
        media: dict[str, Any] | None = None,
        poll: dict[str, Any] | None = None,
        url: str | None = None,
        from_: str | None = None,
        reply_to: str | None = None,
        mentions: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Send message to chat.

        Send a message immediately to a specific chat. The body is the same
        discriminated union as ``POST /v1/scheduled-messages`` minus ``to``
        (derived from the URL path) and ``send_at`` (this endpoint is
        fire-and-forget).

        **Variants:**

        - ``type="text"`` — required ``text`` (1–4096 chars). Optional
          ``url`` (bare-URL shortcut) and ``link_preview`` (bool or dict).
        - ``type="media"`` — required ``media`` dict with ``url`` or
          ``data_base64``. Optional ``kind``, ``caption``, ``filename``.
        - ``type="poll"`` — required ``poll`` dict with ``question`` and
          ``options`` (2–12 items). Optional ``allow_multiple``.

        All variants accept optional ``from_`` (international-format sender for multi-session
        workspaces), ``reply_to`` (wire ``key`` of a prior message to quote),
        and ``mentions`` (``{"ids": [...], "displays": [...]}``).

        The dispatch is direct — no DB row is created; the response carries
        the WhatsApp wire ``key``. For scheduled or queue-managed sends use
        :meth:`ScheduledMessagesResource.create` instead.
        """
        body: dict[str, Any] = {"type": type}
        if text is not None:
            body["text"] = text
        if link_preview is not None:
            body["link_preview"] = link_preview
        if media is not None:
            body["media"] = media
        if poll is not None:
            body["poll"] = poll
        if url is not None:
            body["url"] = url
        if from_ is not None:
            body["from"] = from_
        if reply_to is not None:
            body["reply_to"] = reply_to
        if mentions is not None:
            body["mentions"] = mentions

        data = self._client._request(
            "POST",
            f"/v1/chats/{chat_id}/messages",
            body=body,
            idempotency_key=idempotency_key,
        )
        return Message.model_validate(data)

    def batch_message_acks(self, *, message_keys: Sequence[str]) -> BatchMessageAcksResponse:
        """Batch-fetch ACK data for up to 200 message keys at once."""
        data = self._client._request(
            "POST",
            "/v1/chats/message_acks",
            body={"message_keys": message_keys},
        )
        return BatchMessageAcksResponse.model_validate(data)
