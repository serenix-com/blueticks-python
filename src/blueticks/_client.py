from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from blueticks.types.ping import Ping

from blueticks._errors import BluetickError
from blueticks._transport import Transport
from blueticks._version import __version__

_DEFAULT_BASE_URL = "https://api.blueticks.co"
_DEFAULT_TIMEOUT = 30.0
_DEFAULT_MAX_RETRIES = 2


class Blueticks:
    """Synchronous client for the Blueticks API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        user_agent: str | None = None,
        _http_transport: httpx.BaseTransport | None = None,
    ) -> None:
        resolved_key = api_key if api_key is not None else os.environ.get("BLUETICKS_API_KEY")
        if not resolved_key:
            raise BluetickError(
                status_code=None,
                code="authentication_required",
                message=(
                    "No api_key provided. Pass Blueticks(api_key=...) "
                    "or set BLUETICKS_API_KEY in your environment."
                ),
                request_id=None,
            )
        self._api_key = resolved_key

        resolved_base = (
            base_url
            if base_url is not None
            else os.environ.get("BLUETICKS_BASE_URL") or _DEFAULT_BASE_URL
        )
        self._base_url = resolved_base

        self._transport = Transport(
            api_key=self._api_key,
            base_url=self._base_url,
            timeout=timeout,
            max_retries=max_retries,
            user_agent_suffix=user_agent,
            version=__version__,
            http_transport=_http_transport,
        )

        # Lazy-imported to avoid import cycles and to keep core import cheap.
        from blueticks.resources.account import AccountResource
        from blueticks.resources.audiences import AudiencesResource
        from blueticks.resources.campaigns import CampaignsResource
        from blueticks.resources.chats import ChatsResource
        from blueticks.resources.contacts import ContactsResource
        from blueticks.resources.engines import EnginesResource
        from blueticks.resources.groups import GroupsResource
        from blueticks.resources.messages import MessagesResource
        from blueticks.resources.utils import UtilsResource
        from blueticks.resources.webhooks import WebhooksResource

        self.account = AccountResource(self)
        self.audiences = AudiencesResource(self)
        self.campaigns = CampaignsResource(self)
        self.chats = ChatsResource(self)
        self.contacts = ContactsResource(self)
        self.engines = EnginesResource(self)
        self.groups = GroupsResource(self)
        self.messages = MessagesResource(self)
        self.utils = UtilsResource(self)
        self.webhooks = WebhooksResource(self)

    # -- Public API ----------------------------------------------------------

    def ping(self) -> Ping:
        from blueticks.resources.ping import PingResource

        return PingResource(self).retrieve()

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Blueticks:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # -- Internal ------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        return self._transport.request(
            method,
            path,
            params=params,
            body=body,
            idempotency_key=idempotency_key,
        )
