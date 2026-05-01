from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class DeletedResource(BaseModel):
    """Response envelope returned by DELETE endpoints.

    Returned by:
    - DELETE /v1/audiences/{id}
    - DELETE /v1/scheduled-messages/{id}
    - DELETE /v1/webhooks/{id}
    """

    model_config = ConfigDict(extra="ignore")

    id: str
    deleted: Literal[True]
