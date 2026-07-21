from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.chats import Chat, ChatType, OkResponse, Participant
from blueticks.types.page import Page


class ChatsResource(BaseResource):
    def list(
        self,
        *,
        search_token: str | None = None,
        filter: ChatType | None = None,  # noqa: A002
        include_last_message: bool | None = None,
        include_extended_info: bool | None = None,
        include_without_name: bool | None = None,
        include_archive: bool | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Chat]:
        """List chats.

        List the chats (conversations) the connected WhatsApp engine sees,
        most-recent first. Offset-paginated via ``limit`` + ``skip``, with an
        optional case-insensitive name search via ``search_token`` and a
        ``filter`` to restrict to one chat kind. Requires ``chats:read``.
        """
        params: dict[str, Any] = {}
        if search_token is not None:
            params["searchToken"] = search_token
        if filter is not None:
            params["filter"] = filter
        if include_last_message is not None:
            params["includeLastMessage"] = include_last_message
        if include_extended_info is not None:
            params["includeExtendedInfo"] = include_extended_info
        if include_without_name is not None:
            params["includeWithoutName"] = include_without_name
        if include_archive is not None:
            params["includeArchive"] = include_archive
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/chats", params=params or None)
        return Page[Chat].model_validate(envelope)

    def get(self, chat_id: str) -> Chat:
        """Get chat.

        Retrieve a single chat by its id — a phone number in international format
        (e.g. +14155551234) or a WhatsApp JID (``@c.us``, ``@g.us``, or
        ``@newsletter``). Requires ``chats:read``.
        """
        envelope = self._client._request("GET", f"/v1/chats/{chat_id}")
        return Chat.model_validate(envelope["data"])

    def list_participants(
        self,
        chat_id: str,
        *,
        search_token: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Participant]:
        """List chat participants.

        For group chats, returns the participant list (paginated). For DMs,
        returns the single counterparty. Requires ``chats:read``.
        """
        params: dict[str, Any] = {}
        if search_token is not None:
            params["searchToken"] = search_token
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request(
            "GET", f"/v1/chats/{chat_id}/participants", params=params or None
        )
        return Page[Participant].model_validate(envelope)

    def archive(self, chat_id: str) -> OkResponse:
        """Archive a chat on the connected engine, hiding it from the main list."""
        envelope = self._client._request("POST", f"/v1/chats/{chat_id}/archive")
        return OkResponse.model_validate(envelope["data"])

    def unarchive(self, chat_id: str) -> OkResponse:
        """Remove a chat from the archive, restoring it to the main chat list."""
        envelope = self._client._request("POST", f"/v1/chats/{chat_id}/unarchive")
        return OkResponse.model_validate(envelope["data"])

    def mark_read(self, chat_id: str) -> OkResponse:
        """Clear the unread badge on the connected engine for the given chat."""
        envelope = self._client._request("POST", f"/v1/chats/{chat_id}/mark_read")
        return OkResponse.model_validate(envelope["data"])
