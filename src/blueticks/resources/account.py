from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.account import Account


class AccountResource(BaseResource):
    def retrieve(self) -> Account:
        """Get account.

        Retrieve the account the API key belongs to.
        """
        envelope = self._client._request("GET", "/v1/account")
        return Account.model_validate(envelope["data"])
