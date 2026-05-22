from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.newsletters import Newsletter
from blueticks.types.page import Page


class NewslettersResource(BaseResource):
    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Newsletter]:
        """List newsletters.

        List newsletters visible to the connected WhatsApp engine. Cursor-paginated via `limit` + `cursor`. Requires `newsletters:read` scope.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/newsletters", params=params or None)
        raw: list[Any] = data.get("data", [])
        return Page[Newsletter](
            data=[Newsletter.model_validate(item) for item in raw],
            has_more=data["has_more"],
            next_cursor=data.get("next_cursor"),
        )

    def retrieve(self, id: str) -> Newsletter:
        """Get newsletter.

        Retrieve a newsletter by its JID. Requires `newsletters:read` scope.
        """
        data = self._client._request("GET", f"/v1/newsletters/{id}")
        return Newsletter.model_validate(data)

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> Newsletter:
        """Create newsletter.

        Create a new WhatsApp newsletter (channel). Requires `messages:write` scope (newsletter creation shares the messages write budget).
        """
        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        data = self._client._request("POST", "/v1/newsletters", body=body)
        return Newsletter.model_validate(data)
