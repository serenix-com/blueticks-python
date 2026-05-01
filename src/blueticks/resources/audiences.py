from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.audiences import AppendContactsResult, Audience, Contact
from blueticks.types.page import Page


class AudiencesResource(BaseResource):
    def create(
        self,
        *,
        name: str,
        contacts: builtins.list[dict[str, Any]] | None = None,
    ) -> Audience:
        body: dict[str, Any] = {"name": name}
        if contacts is not None:
            body["contacts"] = contacts
        data = self._client._request("POST", "/v1/audiences", body=body)
        return Audience.model_validate(data)

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Audience]:
        """List audiences, newest first. Cursor-paginated."""
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/audiences", params=params or None)
        return Page[Audience].model_validate(data)

    def get(self, audience_id: str, *, page: int | None = None) -> Audience:
        params: dict[str, Any] | None = None
        if page is not None:
            params = {"page": page}
        data = self._client._request("GET", f"/v1/audiences/{audience_id}", params=params)
        return Audience.model_validate(data)

    def update(self, audience_id: str, *, name: str) -> Audience:
        data = self._client._request("PATCH", f"/v1/audiences/{audience_id}", body={"name": name})
        return Audience.model_validate(data)

    def delete(self, audience_id: str) -> DeletedResource:
        """Delete audience.

        Soft-delete an audience. 409 if it`s referenced by an active campaign.
        Returns the deleted ref. Requires ``audiences:write``.
        """
        data = self._client._request("DELETE", f"/v1/audiences/{audience_id}")
        return DeletedResource.model_validate(data)

    def append_contacts(
        self,
        audience_id: str,
        *,
        contacts: builtins.list[dict[str, Any]],
    ) -> AppendContactsResult:
        data = self._client._request(
            "POST",
            f"/v1/audiences/{audience_id}/contacts",
            body={"contacts": contacts},
        )
        return AppendContactsResult.model_validate(data)

    def update_contact(
        self,
        audience_id: str,
        contact_id: str,
        *,
        to: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> Contact:
        body: dict[str, Any] = {}
        if to is not None:
            body["to"] = to
        if variables is not None:
            body["variables"] = variables
        data = self._client._request(
            "PATCH",
            f"/v1/audiences/{audience_id}/contacts/{contact_id}",
            body=body,
        )
        return Contact.model_validate(data)

    def delete_contact(self, audience_id: str, contact_id: str) -> None:
        self._client._request("DELETE", f"/v1/audiences/{audience_id}/contacts/{contact_id}")
        return None
