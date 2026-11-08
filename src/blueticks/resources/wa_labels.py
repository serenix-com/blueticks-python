from __future__ import annotations

from pydantic import TypeAdapter

from blueticks._base_resource import BaseResource
from blueticks.types.wa_labels import WaLabel

_WA_LABELS = TypeAdapter(list[WaLabel])


class WaLabelsResource(BaseResource):
    def list(self) -> list[WaLabel]:
        """List native WhatsApp Business labels.

        Returns the native WhatsApp Business labels configured on the connected
        account. Use the ``id`` values with ``chats.update_wa_labels`` or the
        ``wa_label_ids`` argument of the send and schedule methods.
        """
        envelope = self._client._request("GET", "/v1/wa-labels")
        return _WA_LABELS.validate_python(envelope["data"])
