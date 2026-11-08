from __future__ import annotations

import builtins
from urllib.parse import quote

from pydantic import TypeAdapter

from blueticks._base_resource import BaseResource
from blueticks.types.identity import Identity, IdentityBatchResponse

_IDENTITY_LIST = TypeAdapter(builtins.list[Identity])


class IdentityResource(BaseResource):
    def retrieve(self, identity_id: str) -> Identity:
        """Resolve an identity.

        Resolve a single WhatsApp JID (``…@lid``, ``…@c.us``, ``…@s.whatsapp.net``
        or ``…@g.us``) to its canonical phone-form identity via the account engine
        store + cache, scoped to the API-key owner. An unknown identity returns
        ``resolved=False`` (fail closed), never a 404; a malformed id raises a 400.
        The id is URL-encoded for you. Requires ``contacts:read``.
        """
        envelope = self._client._request("GET", f"/v1/identity/{quote(identity_id, safe='')}")
        return Identity.model_validate(envelope["data"])

    def resolve_batch(self, ids: builtins.list[str]) -> IdentityBatchResponse:
        """Resolve identities (batch).

        Resolve up to 100 WhatsApp JIDs to their canonical phone-form identities
        in one call. Order-preserving; each element has the same shape as
        :meth:`retrieve`. Requires ``contacts:read``.
        """
        envelope = self._client._request("POST", "/v1/identity/resolve", body={"ids": ids})
        return IdentityBatchResponse(data=_IDENTITY_LIST.validate_python(envelope["data"]))
