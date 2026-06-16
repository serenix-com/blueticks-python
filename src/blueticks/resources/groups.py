from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.groups import Group
from blueticks.types.page import Page


class GroupsResource(BaseResource):
    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        q: str | None = None,
    ) -> Page[Group]:
        """List groups.

        List the groups the connected WhatsApp engine sees. Supports cursor pagination
        (`limit`+`cursor`) and an optional case-insensitive substring search on the
        group name via `q`.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if q is not None:
            params["q"] = q
        data = self._client._request("GET", "/v1/groups", params=params or None)
        return Page[Group].model_validate(data)

    def create(self, *, name: str, participants: list[str]) -> Group:
        """Create a new group with an initial participant list."""
        data = self._client._request(
            "POST", "/v1/groups", body={"name": name, "participants": participants}
        )
        return Group.model_validate(data)

    def get(self, group_id: str) -> Group:
        """Retrieve group metadata by JID."""
        data = self._client._request("GET", f"/v1/groups/{group_id}")
        return Group.model_validate(data)

    def update(
        self,
        group_id: str,
        *,
        name: str | None = None,
        settings: dict[str, bool] | None = None,
    ) -> Group:
        """Rename the group and/or update admin-only settings."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if settings is not None:
            body["settings"] = settings
        data = self._client._request("PATCH", f"/v1/groups/{group_id}", body=body)
        return Group.model_validate(data)

    def add_member(self, group_id: str, *, chat_id: str) -> Group:
        """Invite a contact to the group."""
        data = self._client._request(
            "POST", f"/v1/groups/{group_id}/members", body={"chatId": chat_id}
        )
        return Group.model_validate(data)

    def remove_member(self, group_id: str, chat_id: str) -> Group:
        """Remove a participant from the group."""
        data = self._client._request("DELETE", f"/v1/groups/{group_id}/members/{chat_id}")
        return Group.model_validate(data)

    def promote_admin(self, group_id: str, chat_id: str) -> Group:
        """Grant admin rights to a participant."""
        data = self._client._request("POST", f"/v1/groups/{group_id}/members/{chat_id}/admin")
        return Group.model_validate(data)

    def demote_admin(self, group_id: str, chat_id: str) -> Group:
        """Revoke admin rights from a participant."""
        data = self._client._request("DELETE", f"/v1/groups/{group_id}/members/{chat_id}/admin")
        return Group.model_validate(data)

    def set_picture(
        self,
        group_id: str,
        *,
        file_data_url: str,
        file_name: str | None = None,
        file_mime_type: str | None = None,
    ) -> Group:
        """Upload a new group avatar (base64 data URL)."""
        body: dict[str, Any] = {"fileDataUrl": file_data_url}
        if file_name is not None:
            body["fileName"] = file_name
        if file_mime_type is not None:
            body["fileMimeType"] = file_mime_type
        data = self._client._request("PUT", f"/v1/groups/{group_id}/picture", body=body)
        return Group.model_validate(data)

    def leave(self, group_id: str) -> None:
        """Leave the group (as the authenticated user). Returns 204 No Content."""
        self._client._request("DELETE", f"/v1/groups/{group_id}/members/me")
        return None
