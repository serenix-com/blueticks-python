from __future__ import annotations

import builtins
from typing import Any

from pydantic import TypeAdapter

from blueticks._base_resource import BaseResource
from blueticks.types.chats import Chat, ChatType, OkResponse, Participant
from blueticks.types.engines import EngineTarget
from blueticks.types.page import Page
from blueticks.types.wa_labels import WaLabel

_WA_LABELS = TypeAdapter(builtins.list[WaLabel])


class ChatsResource(BaseResource):
    def list(
        self,
        *,
        search_token: str | None = None,
        filter: ChatType | None = None,  # noqa: A002
        kinds: builtins.list[ChatType] | None = None,
        since: str | None = None,
        include_last_message: bool | None = None,
        include_extended_info: bool | None = None,
        include_without_name: bool | None = None,
        include_archive: bool | None = None,
        engine: EngineTarget | None = None,
        engine_id: str | None = None,
        number_id: str | None = None,
        phone: str | None = None,
        fanout_limit: int | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Chat]:
        """List chats.

        List the chats (conversations) the connected WhatsApp engine sees,
        most-recent first. Offset-paginated via ``limit`` + ``skip``, with an
        optional case-insensitive name search via ``search_token`` and a
        ``filter`` to restrict to one chat kind, or ``kinds`` to keep only several
        kinds. ``since`` (ISO 8601, offset allowed) keeps only chats whose last
        message is at/after that instant (approximate).
        """
        params: dict[str, Any] = {}
        if search_token is not None:
            params["searchToken"] = search_token
        if engine is not None:
            params["engine"] = engine
        if engine_id is not None:
            params["engineId"] = engine_id
        if number_id is not None:
            params["numberId"] = number_id
        if phone is not None:
            params["phone"] = phone
        if fanout_limit is not None:
            params["fanoutLimit"] = fanout_limit
        if filter is not None:
            params["filter"] = filter
        if kinds:
            params["kinds"] = kinds
        if since is not None:
            params["since"] = since
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
        ``@newsletter``).
        """
        envelope = self._client._request("GET", f"/v1/chats/{chat_id}")
        return Chat.model_validate(envelope["data"])

    def list_participants(
        self,
        chat_id: str,
        *,
        search_token: str | None = None,
        engine: EngineTarget | None = None,
        engine_id: str | None = None,
        number_id: str | None = None,
        phone: str | None = None,
        fanout_limit: int | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Participant]:
        """List chat participants.

        For group chats, returns the participant list (paginated). For DMs,
        returns the single counterparty.
        """
        params: dict[str, Any] = {}
        if search_token is not None:
            params["searchToken"] = search_token
        if engine is not None:
            params["engine"] = engine
        if engine_id is not None:
            params["engineId"] = engine_id
        if number_id is not None:
            params["numberId"] = number_id
        if phone is not None:
            params["phone"] = phone
        if fanout_limit is not None:
            params["fanoutLimit"] = fanout_limit
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request(
            "GET", f"/v1/chats/{chat_id}/participants", params=params or None
        )
        return Page[Participant].model_validate(envelope)

    def list_wa_labels(self, chat_id: str) -> builtins.list[WaLabel]:
        """List native WhatsApp Business labels on a chat.

        Returns the native labels currently applied to ``chat_id``. Ids come from
        :meth:`blueticks.resources.wa_labels.WaLabelsResource.list`.
        """
        envelope = self._client._request("GET", f"/v1/chats/{chat_id}/wa-labels")
        return _WA_LABELS.validate_python(envelope["data"])

    def update_wa_labels(self, chat_id: str, *, label_ids: builtins.list[str]) -> OkResponse:
        """Replace native WhatsApp Business labels on a chat.

        ``label_ids`` is the full replacement set (at most 20). An empty list
        clears all native labels from the chat.
        """
        envelope = self._client._request(
            "PATCH", f"/v1/chats/{chat_id}/wa-labels", body={"labelIds": label_ids}
        )
        return OkResponse.model_validate(envelope["data"])

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
