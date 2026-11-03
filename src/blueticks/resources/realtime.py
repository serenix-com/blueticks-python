from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.realtime import RealtimeToken


class RealtimeResource(BaseResource):
    def create_token(self) -> RealtimeToken:
        """Get MQTT credentials for receiving messages in real time.

        Trades your API key for an MQTT credential. Useful when there is no public
        URL to deliver a webhook to — your process dials out and subscribes, so
        nothing needs to be exposed. The result carries the broker URL, the
        username and password to connect with, and the topic to subscribe to. The
        credential does not practically expire, so fetching it once at start-up is
        enough. Requires ``chats:read``.
        """
        envelope = self._client._request("POST", "/v1/realtime/token")
        return RealtimeToken.model_validate(envelope["data"])
