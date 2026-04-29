from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.utils import LinkPreview, PhoneValidation


class UtilsResource(BaseResource):
    def validate_phone(self, *, phone_or_chat_id: str) -> PhoneValidation:
        """Validate a phone number or chat-id; returns the engine's canonical form."""
        data = self._client._request(
            "POST",
            "/v1/utils/validate_phone",
            body={"phone_or_chat_id": phone_or_chat_id},
        )
        return PhoneValidation.model_validate(data)

    def link_preview(self, *, url: str) -> LinkPreview:
        """Fetch OpenGraph-style metadata for a URL (uses the engine's renderer)."""
        data = self._client._request("GET", "/v1/utils/link_preview", params={"url": url})
        return LinkPreview.model_validate(data)
