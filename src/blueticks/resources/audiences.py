from __future__ import annotations

from typing import Any, Dict, List, Optional

from blueticks._base_resource import BaseResource
from blueticks.types.audiences import AppendContactsResult, Audience, Contact
from blueticks.types.page import Page


class AudiencesResource(BaseResource):
    def create(
        self,
        *,
        name: str,
        contacts: Optional[List[Dict[str, Any]]] = None,
    ) -> Audience:
        body: Dict[str, Any] = {"name": name}
        if contacts is not None:
            body["contacts"] = contacts
        data = self._client._request("POST", "/v1/audiences", body=body)
        return Audience.model_validate(data)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Page[Audience]:
        """List audiences, newest first. Cursor-paginated."""
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/audiences", params=params or None)
        return Page[Audience].model_validate(data)

    def get(self, audience_id: str, *, page: Optional[int] = None) -> Audience:
        params: Optional[Dict[str, Any]] = None
        if page is not None:
            params = {"page": page}
        data = self._client._request(
            "GET", f"/v1/audiences/{audience_id}", params=params
        )
        return Audience.model_validate(data)

    def update(self, audience_id: str, *, name: str) -> Audience:
        data = self._client._request(
            "PATCH", f"/v1/audiences/{audience_id}", body={"name": name}
        )
        return Audience.model_validate(data)

    def delete(self, audience_id: str) -> None:
        self._client._request("DELETE", f"/v1/audiences/{audience_id}")
        return None

    def append_contacts(
        self,
        audience_id: str,
        *,
        contacts: List[Dict[str, Any]],
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
        to: Optional[str] = None,
        variables: Optional[Dict[str, str]] = None,
    ) -> Contact:
        body: Dict[str, Any] = {}
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
        self._client._request(
            "DELETE", f"/v1/audiences/{audience_id}/contacts/{contact_id}"
        )
        return None
