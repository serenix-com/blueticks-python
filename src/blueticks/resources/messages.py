from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.chats import OkResponse
from blueticks.types.messages import (
    BatchMessageAck,
    LoadOlderResult,
    Message,
    MessageAck,
    MessageMedia,
    MessageType,
    PinnedMessage,
)
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


class MessagesResource(BaseResource):
    def list(
        self,
        *,
        chat_id: str | None = None,
        search_token: str | None = None,
        order: str | None = None,
        since: str | None = None,
        until: str | None = None,
        message_types: builtins.list[MessageType] | None = None,
        load_from_phone_if_needed: bool | None = None,
        include_media_content: bool | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Message]:
        """List messages (all chats).

        Offset-paginated list of messages across the whole account. Pass
        ``chat_id`` to scope to a single chat, or omit it to search across all
        chats. Supports free-text search (``search_token``), a date range
        (``since``/``until``), and message-kind filtering (``message_types``).
        Requires ``chats:read``.
        """
        params: dict[str, Any] = {}
        if chat_id is not None:
            params["chatId"] = chat_id
        if search_token is not None:
            params["searchToken"] = search_token
        if order is not None:
            params["order"] = order
        if since is not None:
            params["since"] = since
        if until is not None:
            params["until"] = until
        if message_types:
            # `style: form, explode: false` — the server expects a CSV list.
            params["messageTypes"] = ",".join(message_types)
        if load_from_phone_if_needed is not None:
            params["loadFromPhoneIfNeeded"] = load_from_phone_if_needed
        if include_media_content is not None:
            params["includeMediaContent"] = include_media_content
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/messages", params=params or None)
        return Page[Message].model_validate(envelope)

    def retrieve(self, wa_message_key: str, *, chat_id: str | None = None) -> Message:
        """Get message.

        Fetch a single message by its complete WhatsApp message key. Requires
        ``chats:read``.
        """
        params: dict[str, Any] | None = {"chatId": chat_id} if chat_id is not None else None
        envelope = self._client._request("GET", f"/v1/messages/{wa_message_key}", params=params)
        return Message.model_validate(envelope["data"])

    def send(
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
        with_typing: bool | None = None,
        typing_seconds: float | None = None,
    ) -> ScheduledMessage:
        """Send message.

        Send a message immediately to ``chat_id``. Set ``type`` to ``text``,
        ``media``, or ``poll``. The dispatch is direct — no DB row is created;
        the response carries the WhatsApp wire key under ``wa_message_key``. For
        scheduled or queue-managed sends use
        :meth:`ScheduledMessagesResource.create` instead.
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
        if with_typing is not None:
            body["withTyping"] = with_typing
        if typing_seconds is not None:
            body["typingSeconds"] = typing_seconds
        envelope = self._client._request("POST", f"/v1/messages/{chat_id}", body=body)
        return ScheduledMessage.model_validate(envelope["data"])

    def get_ack(self, wa_message_key: str, *, chat_id: str | None = None) -> MessageAck:
        """Get message delivery status.

        Returns the WhatsApp ack value for a sent message: -1=error, 0=pending,
        1=server, 2=device, 3=read, 4=played. Requires ``chats:read``.
        """
        params: dict[str, Any] | None = {"chatId": chat_id} if chat_id is not None else None
        envelope = self._client._request("GET", f"/v1/messages/ack/{wa_message_key}", params=params)
        return MessageAck.model_validate(envelope["data"])

    def batch_acks(
        self,
        *,
        message_keys: builtins.list[str],
        chat_id: str | None = None,
    ) -> Page[BatchMessageAck]:
        """Batch get message acks.

        Get delivery status for up to 200 sent messages in one call. Requires
        ``chats:read``.
        """
        body: dict[str, Any] = {"messageKeys": message_keys}
        if chat_id is not None:
            body["chatId"] = chat_id
        envelope = self._client._request("POST", "/v1/messages/acks", body=body)
        return Page[BatchMessageAck].model_validate(envelope)

    def load_older(self, chat_id: str) -> LoadOlderResult:
        """Load older messages.

        Asks the engine to pull older history from the connected phone for chats
        that haven't been fully synced yet. Requires ``chats:read``.
        """
        envelope = self._client._request("POST", f"/v1/messages/load_older/{chat_id}")
        return LoadOlderResult.model_validate(envelope["data"])

    def get_media(
        self,
        wa_message_key: str,
        *,
        chat_id: str | None = None,
        max_attempts: int | None = None,
    ) -> MessageMedia:
        """Get message media.

        Download the media attached to a WhatsApp message. Returns either a
        hosted ``url`` or inline ``data_base64``, plus mimetype and filename.
        Pass ``max_attempts=1`` to skip the server-side readiness poll.
        """
        params: dict[str, Any] = {}
        if chat_id is not None:
            params["chatId"] = chat_id
        if max_attempts is not None:
            params["maxAttempts"] = max_attempts
        envelope = self._client._request(
            "GET", f"/v1/messages/media/{wa_message_key}", params=params or None
        )
        return MessageMedia.model_validate(envelope["data"])

    def pin(
        self,
        wa_message_key: str,
        *,
        chat_id: str | None = None,
        duration: int | None = None,
    ) -> OkResponse:
        """Pin a message to the top of its chat.

        Optionally pass a ``duration`` (seconds) to control when the pin expires
        — defaults to 7 days. Requires ``chats:write``.
        """
        params: dict[str, Any] | None = {"chatId": chat_id} if chat_id is not None else None
        body: dict[str, Any] | None = {"duration": duration} if duration is not None else None
        envelope = self._client._request(
            "POST", f"/v1/messages/pin/{wa_message_key}", params=params, body=body
        )
        return OkResponse.model_validate(envelope["data"])

    def unpin(self, wa_message_key: str, *, chat_id: str | None = None) -> OkResponse:
        """Remove an existing pin from a message. Requires ``chats:write``."""
        params: dict[str, Any] | None = {"chatId": chat_id} if chat_id is not None else None
        envelope = self._client._request(
            "POST", f"/v1/messages/unpin/{wa_message_key}", params=params
        )
        return OkResponse.model_validate(envelope["data"])

    def list_pinned(self, chat_id: str) -> Page[PinnedMessage]:
        """List the currently pinned messages in a chat. Requires ``chats:read``."""
        envelope = self._client._request("GET", f"/v1/messages/pinned/{chat_id}")
        return Page[PinnedMessage].model_validate(envelope)

    def react(
        self,
        wa_message_key: str,
        *,
        emoji: str,
        chat_id: str | None = None,
    ) -> OkResponse:
        """React to a message.

        Add or replace your reaction to a message. Pass an empty ``emoji`` string
        to remove. Requires ``chats:write``.
        """
        params: dict[str, Any] | None = {"chatId": chat_id} if chat_id is not None else None
        envelope = self._client._request(
            "POST",
            f"/v1/messages/reactions/{wa_message_key}",
            params=params,
            body={"emoji": emoji},
        )
        return OkResponse.model_validate(envelope["data"])
