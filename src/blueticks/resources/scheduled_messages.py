from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.page import Page
from blueticks.types.scheduled_messages import ScheduledMessage


class ScheduledMessagesResource(BaseResource):
    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Page[ScheduledMessage]:
        """List scheduled messages.

        Retrieves a list of all resources from the service.
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        data = self._client._request("GET", "/v1/scheduled-messages", params=params or None)
        return Page[ScheduledMessage].model_validate(data)

    def retrieve(self, scheduled_message_id: str) -> ScheduledMessage:
        """Get scheduled message.

        Retrieves a single resource with the given id from the service.
        """
        data = self._client._request("GET", f"/v1/scheduled-messages/{scheduled_message_id}")
        return ScheduledMessage.model_validate(data)

    def update(
        self,
        scheduled_message_id: str,
        *,
        text: str | None = None,
        media_url: str | None = None,
        media_caption: str | None = None,
        send_at: str | None = None,
    ) -> ScheduledMessage:
        """Update scheduled message.

        Updates the resource identified by id using data.
        """
        body: dict[str, Any] = {}
        if text is not None:
            body["text"] = text
        if media_url is not None:
            body["media_url"] = media_url
        if media_caption is not None:
            body["media_caption"] = media_caption
        if send_at is not None:
            body["send_at"] = send_at
        data = self._client._request(
            "PATCH", f"/v1/scheduled-messages/{scheduled_message_id}", body=body
        )
        return ScheduledMessage.model_validate(data)

    def delete(self, scheduled_message_id: str) -> None:
        """Cancel scheduled message.

        Removes the resource with id.
        """
        self._client._request("DELETE", f"/v1/scheduled-messages/{scheduled_message_id}")
        return None
