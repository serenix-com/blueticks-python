from __future__ import annotations

import builtins
from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types._deleted_resource import DeletedResource
from blueticks.types.page import Page
from blueticks.types.webhooks import Webhook


class WebhooksResource(BaseResource):
    def list(
        self,
        *,
        order: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Webhook]:
        """List webhooks in the workspace. Offset-paginated via ``limit`` + ``skip``."""
        params: dict[str, Any] = {}
        if order is not None:
            params["order"] = order
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/webhooks", params=params or None)
        return Page[Webhook].model_validate(envelope)

    def create(
        self,
        *,
        url: str,
        events: builtins.list[str],
        description: str | None = None,
    ) -> Webhook:
        """Register a new webhook."""
        body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        envelope = self._client._request("POST", "/v1/webhooks", body=body)
        return Webhook.model_validate(envelope["data"])

    def get(self, webhook_id: str) -> Webhook:
        """Get a webhook by id."""
        envelope = self._client._request("GET", f"/v1/webhooks/{webhook_id}")
        return Webhook.model_validate(envelope["data"])

    def update(
        self,
        webhook_id: str,
        *,
        url: str | None = None,
        events: builtins.list[str] | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Webhook:
        """Update a webhook."""
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        if status is not None:
            body["status"] = status
        envelope = self._client._request("PATCH", f"/v1/webhooks/{webhook_id}", body=body)
        return Webhook.model_validate(envelope["data"])

    def delete(self, webhook_id: str) -> DeletedResource:
        """Delete a webhook. Returns the deleted ref."""
        envelope = self._client._request("DELETE", f"/v1/webhooks/{webhook_id}")
        return DeletedResource.model_validate(envelope["data"])
