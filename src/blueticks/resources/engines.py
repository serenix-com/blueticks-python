from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.engines import EngineStatus, WhatsAppMe


class EnginesResource(BaseResource):
    def status(self) -> EngineStatus:
        """Current connection status of the user's WhatsApp engine."""
        data = self._client._request("GET", "/v1/engines")
        return EngineStatus.model_validate(data)

    def me(self) -> WhatsAppMe:
        """Authenticated WhatsApp account profile (phone, pushname, platform)."""
        data = self._client._request("GET", "/v1/engines/me")
        return WhatsAppMe.model_validate(data)

    def logout(self) -> dict[str, Any]:
        """Force the engine to log out of WhatsApp Web."""
        return self._client._request("POST", "/v1/engines/logout")  # type: ignore[no-any-return]

    def reload(self) -> dict[str, Any]:
        """Force the engine's WhatsApp Web tab to reload."""
        return self._client._request("POST", "/v1/engines/reload")  # type: ignore[no-any-return]
