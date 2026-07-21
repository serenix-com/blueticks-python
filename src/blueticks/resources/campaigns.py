from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.campaigns import Campaign
from blueticks.types.page import Page


class CampaignsResource(BaseResource):
    def list(
        self,
        *,
        order: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ) -> Page[Campaign]:
        """List campaigns.

        List the campaigns in your workspace, newest first, each with its live
        counters. Offset-paginated via ``limit`` + ``skip``. Requires
        ``campaigns:read``.
        """
        params: dict[str, Any] = {}
        if order is not None:
            params["order"] = order
        if skip is not None:
            params["skip"] = skip
        if limit is not None:
            params["limit"] = limit
        envelope = self._client._request("GET", "/v1/campaigns", params=params or None)
        return Page[Campaign].model_validate(envelope)

    def create(
        self,
        *,
        name: str,
        audience_id: str,
        text: str | None = None,
        media_url: str | None = None,
        media_caption: str | None = None,
        on_missing_variable: str | None = None,
    ) -> Campaign:
        """Create campaign.

        Schedule a new bulk-message campaign. Returns the campaign in ``pending``
        state. Requires ``campaigns:write``.
        """
        body: dict[str, Any] = {"name": name, "audienceId": audience_id}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["mediaUrl"] = media_url
        if media_caption is not None:
            body["mediaCaption"] = media_caption
        if on_missing_variable is not None:
            body["onMissingVariable"] = on_missing_variable
        envelope = self._client._request("POST", "/v1/campaigns", body=body)
        return Campaign.model_validate(envelope["data"])

    def get(self, campaign_id: str) -> Campaign:
        """Get campaign.

        Retrieve a single campaign by id, including its status and live delivery
        counters. Poll this to track progress. Requires ``campaigns:read``.
        """
        envelope = self._client._request("GET", f"/v1/campaigns/{campaign_id}")
        return Campaign.model_validate(envelope["data"])

    def pause(self, campaign_id: str) -> Campaign:
        """Pause a running campaign. 409 if not ``running``. Requires ``campaigns:write``."""
        envelope = self._client._request("POST", f"/v1/campaigns/{campaign_id}/pause")
        return Campaign.model_validate(envelope["data"])

    def resume(self, campaign_id: str) -> Campaign:
        """Resume a paused campaign. 409 if not ``paused``. Requires ``campaigns:write``."""
        envelope = self._client._request("POST", f"/v1/campaigns/{campaign_id}/resume")
        return Campaign.model_validate(envelope["data"])

    def cancel(self, campaign_id: str) -> Campaign:
        """Cancel a campaign. 409 if already terminal. Requires ``campaigns:write``."""
        envelope = self._client._request("POST", f"/v1/campaigns/{campaign_id}/cancel")
        return Campaign.model_validate(envelope["data"])
