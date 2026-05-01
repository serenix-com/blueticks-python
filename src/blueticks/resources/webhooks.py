from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.page import Page
from blueticks.types.webhooks import Webhook, WebhookCreateResult


class WebhooksResource(BaseResource):
    def create(
        self,
        *,
        url: str,
        events: builtins.list[str],
        description: str | None = None,
    ) -> WebhookCreateResult:
        body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        data = self._client._request("POST", "/v1/webhooks", body=body)
        return WebhookCreateResult.model_validate(data)

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[Webhook]:
        """List webhooks, newest first. Cursor-paginated.

        :param limit: Page size, 1-200 (default 50 server-side).
        :param cursor: Opaque cursor from a previous ``Page.next_cursor``.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/webhooks", params=params or None)
        return Page[Webhook].model_validate(data)

    def get(self, webhook_id: str) -> Webhook:
        data = self._client._request("GET", f"/v1/webhooks/{webhook_id}")
        return Webhook.model_validate(data)

    def update(
        self,
        webhook_id: str,
        *,
        url: str | None = None,
        events: builtins.list[str] | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Webhook:
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status
        data = self._client._request("PATCH", f"/v1/webhooks/{webhook_id}", body=body)
        return Webhook.model_validate(data)

    def delete(self, webhook_id: str) -> DeletedResource:
        """Delete webhook.

        Delete a webhook subscription. Returns the deleted ref. Requires
        ``webhooks:write``.
        """
        data = self._client._request("DELETE", f"/v1/webhooks/{webhook_id}")
        return DeletedResource.model_validate(data)

    def rotate_secret(self, webhook_id: str) -> WebhookCreateResult:
        data = self._client._request("POST", f"/v1/webhooks/{webhook_id}/rotate-secret")
        return WebhookCreateResult.model_validate(data)
