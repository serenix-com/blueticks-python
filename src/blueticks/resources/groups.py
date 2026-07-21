from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.groups import Group, GroupListItem
from blueticks.types.page import Page


class GroupsResource(BaseResource):
    def list(
        self,
        *,
        search_token: str | None = None,
        include_archive: bool | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[GroupListItem]:
        """List groups.

        List the groups the connected WhatsApp engine sees. Offset-paginated via
        ``limit`` + ``skip`` with an optional case-insensitive name search via
        ``search_token``.
        """
        params: dict[str, Any] = {}
        if search_token is not None:
            params["searchToken"] = search_token
        if include_archive is not None:
            params["includeArchive"] = include_archive
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/groups", params=params or None)
        return Page[GroupListItem].model_validate(envelope)

    def create(self, *, name: str, participants: builtins.list[str]) -> Group:
        """Create a WhatsApp group with the given name and initial participants."""
        envelope = self._client._request(
            "POST", "/v1/groups", body={"name": name, "participants": participants}
        )
        return Group.model_validate(envelope["data"])

    def get(self, group_id: str, *, include: str | None = None) -> Group:
        """Get group.

        Retrieve a single group by its ``@g.us`` id, including its subject,
        description, and (with ``include="participants"``) its participant list.
        Requires ``groups:read``.
        """
        params: dict[str, Any] | None = {"include": include} if include is not None else None
        envelope = self._client._request("GET", f"/v1/groups/{group_id}", params=params)
        return Group.model_validate(envelope["data"])

    def update(
        self,
        group_id: str,
        *,
        name: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Group:
        """Update group metadata. Provide at least one of ``name`` or ``settings``."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if settings is not None:
            body["settings"] = settings
        envelope = self._client._request("PATCH", f"/v1/groups/{group_id}", body=body)
        return Group.model_validate(envelope["data"])

    def add_member(
        self,
        group_id: str,
        *,
        chat_id: str | None = None,
        participants: builtins.list[str] | None = None,
    ) -> Group:
        """Add a member to the group by chatId (JID) or phone number (E.164)."""
        body: dict[str, Any] = {}
        if chat_id is not None:
            body["chatId"] = chat_id
        if participants is not None:
            body["participants"] = participants
        envelope = self._client._request("POST", f"/v1/groups/{group_id}/members", body=body)
        return Group.model_validate(envelope["data"])

    def remove_member(self, group_id: str, chat_id: str) -> Group:
        """Remove a participant from the group."""
        envelope = self._client._request("DELETE", f"/v1/groups/{group_id}/members/{chat_id}")
        return Group.model_validate(envelope["data"])

    def promote_admin(self, group_id: str, chat_id: str) -> Group:
        """Grant admin privileges to a group member."""
        envelope = self._client._request("POST", f"/v1/groups/{group_id}/members/{chat_id}/admin")
        return Group.model_validate(envelope["data"])

    def demote_admin(self, group_id: str, chat_id: str) -> Group:
        """Revoke admin privileges from a group member."""
        envelope = self._client._request("DELETE", f"/v1/groups/{group_id}/members/{chat_id}/admin")
        return Group.model_validate(envelope["data"])

    def set_picture(
        self,
        group_id: str,
        *,
        file_data_url: str | None = None,
        url: str | None = None,
        file_name: str | None = None,
        file_mime_type: str | None = None,
    ) -> Group:
        """Set group picture.

        Replace the group picture. Provide the image as ``file_data_url`` (base64
        data URL, PNG/JPEG, ≤20 MiB) or ``url`` (https). Requires ``groups:write``.
        """
        body: dict[str, Any] = {}
        if file_data_url is not None:
            body["fileDataUrl"] = file_data_url
        if url is not None:
            body["url"] = url
        if file_name is not None:
            body["fileName"] = file_name
        if file_mime_type is not None:
            body["fileMimeType"] = file_mime_type
        envelope = self._client._request("PUT", f"/v1/groups/{group_id}/picture", body=body)
        return Group.model_validate(envelope["data"])

    def leave(self, group_id: str) -> None:
        """Leave the group as the authenticated identity. Idempotent (204 No Content)."""
        self._client._request("DELETE", f"/v1/groups/{group_id}/members/me")
        return None
