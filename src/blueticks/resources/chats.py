from __future__ import annotations

from typing import Any, Dict, Optional

from blueticks._base_resource import BaseResource
from blueticks.types.chats import Chat, ChatMedia, ChatMessage, Participant
from blueticks.types.page import Page


class ChatsResource(BaseResource):
    def list(
        self,
        *,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Page[Chat]:
        """List/search chats, newest first. Cursor-paginated."""
        params: Dict[str, Any] = {}
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
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Page[Participant]:
        """List participants in a group chat. Cursor-paginated."""
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request(
            "GET", f"/v1/chats/{chat_id}/participants", params=params or None
        )
        return Page[Participant].model_validate(data)

    def mark_read(self, chat_id: str) -> Dict[str, Any]:
        """Mark a chat as read (sends read receipts if enabled)."""
        return self._client._request("POST", f"/v1/chats/{chat_id}/mark_read")

    def open(self, chat_id: str) -> Dict[str, Any]:
        """Open a chat on the engine (useful for UI-assisted workflows)."""
        return self._client._request("POST", f"/v1/chats/{chat_id}/open")

    def list_messages(
        self,
        chat_id: str,
        *,
        mode: str = "latest",
        query: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Page[ChatMessage]:
        """List messages in a chat. `mode` is 'latest' or 'history'."""
        params: Dict[str, Any] = {"mode": mode}
        if query is not None:
            params["query"] = query
        if since is not None:
            params["since"] = since
        if until is not None:
            params["until"] = until
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request(
            "GET", f"/v1/chats/{chat_id}/messages", params=params
        )
        return Page[ChatMessage].model_validate(data)

    def get_message(self, chat_id: str, key: str) -> ChatMessage:
        """Retrieve a single message by WhatsApp message key."""
        data = self._client._request(
            "GET", f"/v1/chats/{chat_id}/messages/{key}"
        )
        return ChatMessage.model_validate(data)

    def get_message_ack(self, chat_id: str, key: str) -> Dict[str, Any]:
        """Fetch ACK state for a single message."""
        return self._client._request(
            "GET", f"/v1/chats/{chat_id}/messages/{key}/ack"
        )

    def react(self, chat_id: str, key: str, *, emoji: str) -> Dict[str, Any]:
        """Add or clear an emoji reaction on a message."""
        return self._client._request(
            "POST",
            f"/v1/chats/{chat_id}/messages/{key}/reactions",
            body={"emoji": emoji},
        )

    def load_older_messages(self, chat_id: str) -> Dict[str, Any]:
        """Pull older messages from the phone into the engine's local store."""
        return self._client._request(
            "POST", f"/v1/chats/{chat_id}/messages/load_older"
        )

    def get_media(self, chat_id: str, key: str) -> ChatMedia:
        """Download message media (may be returned as base64)."""
        data = self._client._request(
            "GET", f"/v1/chats/{chat_id}/messages/{key}/media"
        )
        return ChatMedia.model_validate(data)

    def get_media_url(self, chat_id: str, key: str) -> Dict[str, Any]:
        """Get a short-lived URL for message media, if available."""
        return self._client._request(
            "GET", f"/v1/chats/{chat_id}/messages/{key}/media_url"
        )

    def batch_message_acks(self, *, message_keys: list[str]) -> Dict[str, Any]:
        """Batch-fetch ACK data for up to 200 message keys at once."""
        return self._client._request(
            "POST",
            "/v1/chats/message_acks",
            body={"message_keys": message_keys},
        )
