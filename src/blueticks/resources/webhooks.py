from __future__ import annotations

from typing import Any, Dict, List, Optional

from blueticks._base_resource import BaseResource
from blueticks.types.webhooks import Webhook, WebhookCreateResult


class WebhooksResource(BaseResource):
    def create(
        self,
        *,
        url: str,
        events: List[str],
        description: Optional[str] = None,
    ) -> WebhookCreateResult:
        body: Dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        data = self._client._request("POST", "/v1/webhooks", body=body)
        return WebhookCreateResult.model_validate(data)

    def list(self) -> List[Webhook]:
        data = self._client._request("GET", "/v1/webhooks")
        items = data.get("data", data) if isinstance(data, dict) else data
        return [Webhook.model_validate(item) for item in items]

    def get(self, webhook_id: str) -> Webhook:
        data = self._client._request("GET", f"/v1/webhooks/{webhook_id}")
        return Webhook.model_validate(data)

    def update(
        self,
        webhook_id: str,
        *,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Webhook:
        body: Dict[str, Any] = {}
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

    def delete(self, webhook_id: str) -> None:
        self._client._request("DELETE", f"/v1/webhooks/{webhook_id}")
        return None

    def rotate_secret(self, webhook_id: str) -> WebhookCreateResult:
        data = self._client._request(
            "POST", f"/v1/webhooks/{webhook_id}/rotate-secret"
        )
        return WebhookCreateResult.model_validate(data)
