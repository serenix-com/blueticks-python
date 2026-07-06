from __future__ import annotations

# ruff: noqa: UP045  # Pydantic field annotations need Optional[T] for Python 3.9 (see CLAUDE.md)
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Generation status for a single Suno clip. Terminal states: "complete" or
# "error". Mirrors the `status` enum on GenerateSongResponse.clips[] and
# GetSongResponse.
SunoClipStatus = Literal[
    "submitted",
    "queued",
    "running",
    "streaming",
    "complete",
    "error",
]


class SunoClip(BaseModel):
    """A single generated song variant returned by the Suno endpoints.

    Returned directly by ``GET /v1/suno/songs/{id}`` and nested in each
    ``clips[]`` row of ``POST /v1/suno/songs``. Poll by ``id`` until
    ``status`` is ``complete`` (or ``error``).
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str
    status: SunoClipStatus
    audio_url: Optional[str] = Field(default=None, alias="audioUrl")  # noqa: UP045
    image_url: Optional[str] = Field(default=None, alias="imageUrl")  # noqa: UP045
    title: Optional[str] = None  # noqa: UP045
    duration_sec: Optional[float] = Field(default=None, alias="durationSec")  # noqa: UP045
    model: Optional[str] = None  # noqa: UP045
    error_type: Optional[str] = Field(default=None, alias="errorType")  # noqa: UP045
    error_message: Optional[str] = Field(default=None, alias="errorMessage")  # noqa: UP045


class SunoGeneration(BaseModel):
    """Response from ``POST /v1/suno/songs`` — a submitted generation.

    Carries the batch ``job_id`` and the (typically two) ``clips`` variants.
    Poll each clip by its ``id`` with ``GET /v1/suno/songs/{id}``.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    job_id: str = Field(alias="jobId")
    clips: list[SunoClip]


class SunoUpload(BaseModel):
    """Response from ``POST /v1/suno/uploads`` — a reference-audio upload.

    Pass ``upload_id`` to ``POST /v1/suno/songs`` (as ``upload_id``) to
    cover/transform the uploaded recording.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    upload_id: str = Field(alias="uploadId")
    status: str


class SunoAccount(BaseModel):
    """Response from ``GET /v1/suno/account`` — connected Suno account status.

    Remaining credits, monthly usage, and plan on the connected Suno account.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    credits_left: float = Field(alias="creditsLeft")
    monthly_limit: Optional[float] = Field(default=None, alias="monthlyLimit")  # noqa: UP045
    monthly_usage: Optional[float] = Field(default=None, alias="monthlyUsage")  # noqa: UP045
    plan: Optional[str] = None  # noqa: UP045
