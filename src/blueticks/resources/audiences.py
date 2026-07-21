from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.audiences import (
    AppendContactsResult,
    Audience,
    AudienceContact,
    RemovedContact,
)
from blueticks.types.page import Page


class AudiencesResource(BaseResource):
    def list(
        self,
        *,
        order: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Audience]:
        """List audiences.

        List the audiences in your workspace, newest first. Offset-paginated via
        ``limit`` + ``skip``. Requires ``audiences:read``.
        """
        params: dict[str, Any] = {}
        if order is not None:
            params["order"] = order
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/audiences", params=params or None)
        return Page[Audience].model_validate(envelope)

    def create(
        self,
        *,
        name: str,
        contacts: builtins.list[dict[str, Any]] | None = None,
    ) -> Audience:
        """Create audience.

        Create a new audience. Returns the audience with ``contact_count: 0``.
        Requires ``audiences:write``.
        """
        body: dict[str, Any] = {"name": name}
        if contacts is not None:
            body["contacts"] = contacts
        envelope = self._client._request("POST", "/v1/audiences", body=body)
        return Audience.model_validate(envelope["data"])

    def get(self, audience_id: str) -> Audience:
        """Get audience.

        Retrieve a single audience by id, including its ``contact_count`` and
        variable schema. Requires ``audiences:read``.
        """
        envelope = self._client._request("GET", f"/v1/audiences/{audience_id}")
        return Audience.model_validate(envelope["data"])

    def update(self, audience_id: str, *, name: str) -> Audience:
        """Update audience.

        Rename an audience or update its variable schema. Requires
        ``audiences:write``.
        """
        envelope = self._client._request(
            "PATCH", f"/v1/audiences/{audience_id}", body={"name": name}
        )
        return Audience.model_validate(envelope["data"])

    def delete(self, audience_id: str) -> DeletedResource:
        """Delete audience.

        Soft-delete an audience. 409 if it's referenced by an active campaign.
        Returns the deleted ref. Requires ``audiences:write``.
        """
        envelope = self._client._request("DELETE", f"/v1/audiences/{audience_id}")
        return DeletedResource.model_validate(envelope["data"])

    def append_contacts(
        self,
        audience_id: str,
        *,
        contacts: builtins.list[dict[str, Any]],
    ) -> AppendContactsResult:
        """Append contacts to audience.

        Append contacts to an audience. Duplicates (by ``to``) are skipped.
        Requires ``audiences:write``.
        """
        envelope = self._client._request(
            "POST",
            f"/v1/audiences/{audience_id}/contacts",
            body={"contacts": contacts},
        )
        return AppendContactsResult.model_validate(envelope["data"])

    def update_contact(
        self,
        audience_id: str,
        contact_id: str,
        *,
        to: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> AudienceContact:
        """Update audience contact.

        Edit a contact's phone or variables. Requires ``audiences:write``.
        """
        body: dict[str, Any] = {}
        if to is not None:
            body["to"] = to
        if variables is not None:
            body["variables"] = variables
        envelope = self._client._request(
            "PATCH",
            f"/v1/audiences/{audience_id}/contacts/{contact_id}",
            body=body,
        )
        return AudienceContact.model_validate(envelope["data"])

    def delete_contact(self, audience_id: str, contact_id: str) -> RemovedContact:
        """Remove audience contact.

        Remove a contact from an audience. Requires ``audiences:write``.
        """
        envelope = self._client._request(
            "DELETE", f"/v1/audiences/{audience_id}/contacts/{contact_id}"
        )
        return RemovedContact.model_validate(envelope["data"])
