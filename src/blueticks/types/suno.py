from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

SongStatus = Literal["submitted", "queued", "running", "streaming", "complete", "error"]


class SunoAccount(BaseModel):
    """Response from GET /v1/suno/account — credits, usage, and plan."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    credits_left: float
    monthly_limit: Optional[float] = None  # noqa: UP045
    monthly_usage: Optional[float] = None  # noqa: UP045
    plan: Optional[str] = None  # noqa: UP045


class SongClip(BaseModel):
    """A single generated song variant. Poll GET /v1/suno/songs/{id} until complete."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    id: str
    status: SongStatus
    audio_url: Optional[str] = None  # noqa: UP045
    image_url: Optional[str] = None  # noqa: UP045
    title: Optional[str] = None  # noqa: UP045
    duration_sec: Optional[float] = None  # noqa: UP045
    model: Optional[str] = None  # noqa: UP045
    error_type: Optional[str] = None  # noqa: UP045
    error_message: Optional[str] = None  # noqa: UP045


class SongGeneration(BaseModel):
    """Response from POST /v1/suno/songs — the job id plus its two clip variants."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    job_id: str
    clips: list[SongClip]


class SunoUpload(BaseModel):
    """Response from POST /v1/suno/uploads — the reference-audio upload handle."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")

    upload_id: str
    status: str
