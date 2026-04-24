from __future__ import annotations

from typing import Any, Dict, Optional

from blueticks._base_resource import BaseResource
from blueticks.types.campaigns import Campaign
from blueticks.types.page import Page


class CampaignsResource(BaseResource):
    def create(
        self,
        *,
        name: str,
        audience_id: str,
        text: Optional[str] = None,
        media_url: Optional[str] = None,
        media_caption: Optional[str] = None,
        from_: Optional[str] = None,
        on_missing_variable: Optional[str] = None,
    ) -> Campaign:
        body: Dict[str, Any] = {"name": name, "audience_id": audience_id}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["media_url"] = media_url
        if media_caption is not None:
            body["media_caption"] = media_caption
        if from_ is not None:
            body["from"] = from_
        if on_missing_variable is not None:
            body["on_missing_variable"] = on_missing_variable
        data = self._client._request("POST", "/v1/campaigns", body=body)
        return Campaign.model_validate(data)

    def list(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> Page[Campaign]:
        """List campaigns, newest first. Cursor-paginated."""
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/campaigns", params=params or None)
        return Page[Campaign].model_validate(data)

    def get(self, campaign_id: str) -> Campaign:
        data = self._client._request("GET", f"/v1/campaigns/{campaign_id}")
        return Campaign.model_validate(data)

    def pause(self, campaign_id: str) -> Campaign:
        data = self._client._request("POST", f"/v1/campaigns/{campaign_id}/pause")
        return Campaign.model_validate(data)

    def resume(self, campaign_id: str) -> Campaign:
        data = self._client._request("POST", f"/v1/campaigns/{campaign_id}/resume")
        return Campaign.model_validate(data)

    def cancel(self, campaign_id: str) -> Campaign:
        data = self._client._request("POST", f"/v1/campaigns/{campaign_id}/cancel")
        return Campaign.model_validate(data)
