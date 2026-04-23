from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blueticks._client import Blueticks


class BaseResource:
    """Shared plumbing for all resource classes. Holds a reference to the parent client."""

    def __init__(self, client: Blueticks) -> None:
        self._client = client
