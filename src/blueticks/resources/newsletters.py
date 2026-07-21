from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.newsletters import Newsletter, NewsletterListItem
from blueticks.types.page import Page


class NewslettersResource(BaseResource):
    def list(
        self,
        *,
        search_token: str | None = None,
        include_archive: bool | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[NewsletterListItem]:
        """List newsletters.

        List newsletters visible to the connected WhatsApp engine.
        Offset-paginated via ``limit`` + ``skip``. Requires ``newsletters:read``.
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
        envelope = self._client._request("GET", "/v1/newsletters", params=params or None)
        return Page[NewsletterListItem].model_validate(envelope)

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> Newsletter:
        """Create newsletter.

        Create a new WhatsApp newsletter (channel). Requires ``messages:write``
        scope (newsletter creation shares the messages write budget).
        """
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        envelope = self._client._request("POST", "/v1/newsletters", body=body)
        return Newsletter.model_validate(envelope["data"])

    def retrieve(self, newsletter_id: str) -> Newsletter:
        """Get newsletter.

        Retrieve a newsletter by its JID. Requires ``newsletters:read``.
        """
        envelope = self._client._request("GET", f"/v1/newsletters/{newsletter_id}")
        return Newsletter.model_validate(envelope["data"])
