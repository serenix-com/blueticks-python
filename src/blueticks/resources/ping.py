from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.ping import Ping


class PingResource(BaseResource):
    def retrieve(self) -> Ping:
        """Health check.

        Returns basic info about the authenticated API key.
        """
        data = self._client._request("GET", "/v1/ping")
        return Ping.model_validate(data)
