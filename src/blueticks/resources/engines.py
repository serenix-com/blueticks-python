from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.engines import Engine


class EnginesResource(BaseResource):
    def list(self) -> list[Engine]:
        """List engines.

        List the WhatsApp engines connected to this workspace — one entry per
        online engine. Each entry carries its own ``id`` (the engine session's
        MQTT presence client id), its ``type`` (``gateway`` or ``regular``), and
        its connectivity status. Returns an empty list when no engine is
        connected.
        """
        envelope = self._client._request("GET", "/v1/engines")
        return [Engine.model_validate(item) for item in envelope["data"]]
