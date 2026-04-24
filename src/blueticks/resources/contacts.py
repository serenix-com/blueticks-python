from __future__ import annotations

from typing import Any, Dict, Optional

from blueticks._base_resource import BaseResource
from blueticks.types.contacts import Contact, ProfilePicture
from blueticks.types.page import Page


class ContactsResource(BaseResource):
    def list(
        self,
        *,
        query: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Page[Contact]:
        """Search the user's WhatsApp contacts. Cursor-paginated."""
        params: Dict[str, Any] = {}
        if query is not None:
            params["query"] = query
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request(
            "GET", "/v1/contacts", params=params or None
        )
        return Page[Contact].model_validate(data)

    def get_profile_picture(self, chat_id: str) -> ProfilePicture:
        """Retrieve the CDN URL for a contact's profile picture."""
        data = self._client._request(
            "GET", f"/v1/contacts/{chat_id}/profile_picture"
        )
        return ProfilePicture.model_validate(data)
