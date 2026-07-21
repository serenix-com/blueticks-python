from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.ping import Ping


class PingResource(BaseResource):
    def retrieve(self) -> Ping:
        """Ping.

        Health and connectivity probe. Confirms the Blueticks API server is live
        and lists the WhatsApp engines currently connected to this account.
        """
        envelope = self._client._request("GET", "/v1/ping")
        return Ping.model_validate(envelope["data"])
