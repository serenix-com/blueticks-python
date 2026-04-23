from __future__ import annotations

from blueticks._base_resource import BaseResource


class PingResource(BaseResource):
    def retrieve(self) -> None:  # pragma: no cover
        raise NotImplementedError
