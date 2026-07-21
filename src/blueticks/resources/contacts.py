from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.contacts import Contact
from blueticks.types.groups import GroupListItem
from blueticks.types.page import Page


class ContactsResource(BaseResource):
    def list(
        self,
        *,
        search_token: str | None = None,
        include_archive: bool | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Contact]:
        """List contacts.

        List your workspace contact book — everyone the connected WhatsApp
        account has messaged. Offset-paginated via ``limit`` + ``skip``. Requires
        ``contacts:read``.
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
        envelope = self._client._request("GET", "/v1/contacts", params=params or None)
        return Page[Contact].model_validate(envelope)

    def common_groups(self, contact_id: str) -> Page[GroupListItem]:
        """Get common groups.

        List the groups the connected WhatsApp account shares with this contact
        (WhatsApp's "groups in common"). ``contact_id`` is the contact's JID
        (e.g. ``12345@c.us``). Requires ``groups:read``.
        """
        envelope = self._client._request("GET", f"/v1/contacts/{contact_id}/common_groups")
        return Page[GroupListItem].model_validate(envelope)
