from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.suno import SunoAccount, SunoClip, SunoGeneration, SunoUpload


class SunoResource(BaseResource):
    def generate(
        self,
        *,
        lyrics: str,
        style: str,
        negative_style: str | None = None,
        vocal_gender: str | None = None,
        weirdness: float | None = None,
        style_influence: float | None = None,
        audio_influence: float | None = None,
        instrumental: bool | None = None,
        model: str | None = None,
        title: str | None = None,
        upload_id: str | None = None,
        captcha_token: str | None = None,
    ) -> SunoGeneration:
        """Generate song.

        Submit a song generation to Suno from ``lyrics`` + ``style``, optionally
        steering ``vocalGender``, ``weirdness``, ``styleInfluence``, and a reference
        recording (``uploadId`` from POST /v1/suno/uploads, with ``audioInfluence``
        controlling how closely the cover follows it). Returns two clip variants —
        poll each with ``GET /v1/suno/songs/{id}`` until ``status`` is ``complete``.
        Requires ``suno:write``.
        """
        body: dict[str, Any] = {"lyrics": lyrics, "style": style}
        if negative_style is not None:
            body["negativeStyle"] = negative_style
        if vocal_gender is not None:
            body["vocalGender"] = vocal_gender
        if weirdness is not None:
            body["weirdness"] = weirdness
        if style_influence is not None:
            body["styleInfluence"] = style_influence
        if audio_influence is not None:
            body["audioInfluence"] = audio_influence
        if instrumental is not None:
            body["instrumental"] = instrumental
        if model is not None:
            body["model"] = model
        if title is not None:
            body["title"] = title
        if upload_id is not None:
            body["uploadId"] = upload_id
        if captcha_token is not None:
            body["captchaToken"] = captcha_token
        data = self._client._request("POST", "/v1/suno/songs", body=body)
        return SunoGeneration.model_validate(data)

    def retrieve(self, id: str) -> SunoClip:
        """Get song.

        Poll a single generated clip by id. When ``status`` is ``complete``,
        ``audioUrl`` (MP3) and ``imageUrl`` are populated. Requires ``suno:read``.
        """
        data = self._client._request("GET", f"/v1/suno/songs/{id}")
        return SunoClip.model_validate(data)

    def upload(
        self,
        *,
        audio_url: str | None = None,
        audio_base64: str | None = None,
        file_name: str | None = None,
    ) -> SunoUpload:
        """Upload reference audio.

        Upload an audio recording (via ``audioUrl`` or base64 ``audioBase64``) to
        Suno. Returns an ``uploadId`` to pass to POST /v1/suno/songs as ``uploadId``
        to cover/transform it. Max 500 MB. Requires ``suno:write``.
        """
        body: dict[str, Any] = {}
        if audio_url is not None:
            body["audioUrl"] = audio_url
        if audio_base64 is not None:
            body["audioBase64"] = audio_base64
        if file_name is not None:
            body["fileName"] = file_name
        data = self._client._request("POST", "/v1/suno/uploads", body=body or None)
        return SunoUpload.model_validate(data)

    def account(self) -> SunoAccount:
        """Get Suno account.

        Remaining credits, monthly usage, and plan on the connected Suno account.
        Requires ``suno:read``.
        """
        data = self._client._request("GET", "/v1/suno/account")
        return SunoAccount.model_validate(data)
