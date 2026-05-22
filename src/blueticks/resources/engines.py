from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.engines import EngineStatus


class EnginesResource(BaseResource):
    def retrieve(self) -> EngineStatus:
        """Get engine status.

        Inspect or control the WhatsApp engine connected to the workspace.
        """
        data = self._client._request("GET", "/v1/engines")
        return EngineStatus.model_validate(data)
