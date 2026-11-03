from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.latest_chats import LatestChatsResponse


class LatestChatsResource(BaseResource):
    def retrieve(
        self,
        *,
        number_of_chats: int | None = None,
        number_of_messages: int | None = None,
    ) -> LatestChatsResponse:
        """Get latest chats & messages.

        Returns the most-recent non-archived chats (pinned first), each with its
        latest messages (newest-first). One call — no per-chat round-trips.
        ``number_of_chats`` is 1-200 (default 50); ``number_of_messages`` is 0-100
        per chat (default 20). Requires ``chats:read``.
        """
        params: dict[str, Any] = {}
        if number_of_chats is not None:
            params["numberOfChats"] = number_of_chats
        if number_of_messages is not None:
            params["numberOfMessages"] = number_of_messages
        envelope = self._client._request("GET", "/v1/latest-chats", params=params or None)
        return LatestChatsResponse.model_validate(envelope["data"])
