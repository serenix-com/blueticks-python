from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.contacts import Contact
from blueticks.types.page import Page


class ContactsResource(BaseResource):
    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Contact]:
        """List contacts.

        List WhatsApp contacts known to the connected engine. Cursor-paginated.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/contacts", params=params or None)
        return Page[Contact].model_validate(data)
