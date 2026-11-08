from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Upload(BaseModel):
    """A reserved upload slot returned by ``POST /v1/uploads``.

    PUT the raw bytes to ``upload_url`` with ``method`` and ``headers`` before
    ``expires_at``, then pass ``file_id`` as ``mediaFileId`` on a send. The file
    is deleted at ``delete_at``.
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    file_id: str
    upload_url: str
    method: Literal["PUT"]
    headers: dict[str, str]
    expires_at: str
    delete_at: str
    max_bytes: float
    content_type: str
