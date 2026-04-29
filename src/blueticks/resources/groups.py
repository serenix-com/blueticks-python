from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.groups import Group


class GroupsResource(BaseResource):
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
    ) -> dict[str, Any]:
        """Rename the group and/or update admin-only settings."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if settings is not None:
            body["settings"] = settings
        return self._client._request("PATCH", f"/v1/groups/{group_id}", body=body)  # type: ignore[no-any-return]

    def add_member(self, group_id: str, *, chat_id: str) -> dict[str, Any]:
        """Invite a contact to the group."""
        return self._client._request(  # type: ignore[no-any-return]
            "POST", f"/v1/groups/{group_id}/members", body={"chat_id": chat_id}
        )

    def remove_member(self, group_id: str, chat_id: str) -> dict[str, Any]:
        """Remove a participant from the group."""
        return self._client._request("DELETE", f"/v1/groups/{group_id}/members/{chat_id}")  # type: ignore[no-any-return]

    def promote_admin(self, group_id: str, chat_id: str) -> dict[str, Any]:
        """Grant admin rights to a participant."""
        return self._client._request("POST", f"/v1/groups/{group_id}/members/{chat_id}/admin")  # type: ignore[no-any-return]

    def demote_admin(self, group_id: str, chat_id: str) -> dict[str, Any]:
        """Revoke admin rights from a participant."""
        return self._client._request("DELETE", f"/v1/groups/{group_id}/members/{chat_id}/admin")  # type: ignore[no-any-return]

    def set_picture(
        self,
        group_id: str,
        *,
        file_data_url: str,
        file_name: str | None = None,
        file_mime_type: str | None = None,
    ) -> dict[str, Any]:
        """Upload a new group avatar (base64 data URL)."""
        body: dict[str, Any] = {"file_data_url": file_data_url}
        if file_name is not None:
            body["file_name"] = file_name
        if file_mime_type is not None:
            body["file_mime_type"] = file_mime_type
        return self._client._request("PUT", f"/v1/groups/{group_id}/picture", body=body)  # type: ignore[no-any-return]

    def leave(self, group_id: str) -> dict[str, Any]:
        """Leave the group (as the authenticated user)."""
        return self._client._request("DELETE", f"/v1/groups/{group_id}/members/me")  # type: ignore[no-any-return]
