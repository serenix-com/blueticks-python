from __future__ import annotations

from blueticks._base_resource import BaseResource
from blueticks.types.account import Account


class AccountResource(BaseResource):
    def retrieve(self) -> Account:
        """Retrieve the authenticated account.

        Returns the account associated with the API key used for this request.
        """
        data = self._client._request("GET", "/v1/account")
        return Account.model_validate(data)
