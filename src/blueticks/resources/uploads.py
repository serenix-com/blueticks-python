from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.uploads import Upload


class UploadsResource(BaseResource):
    def create(
        self,
        *,
        content_type: str,
        size_bytes: int | None = None,
        filename: str | None = None,
    ) -> Upload:
        """Reserve an upload slot.

        Reserve a signed upload URL for a media file. PUT the raw bytes to
        ``upload_url`` with the returned ``headers`` before ``expires_at``, then
        pass ``file_id`` as ``media_file_id`` on a media send or schedule.
        """
        body: dict[str, Any] = {"contentType": content_type}
        if size_bytes is not None:
            body["sizeBytes"] = size_bytes
        if filename is not None:
            body["filename"] = filename
        envelope = self._client._request("POST", "/v1/uploads", body=body)
        return Upload.model_validate(envelope["data"])
