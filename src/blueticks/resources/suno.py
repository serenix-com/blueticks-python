from __future__ import annotations

from typing import Any

from blueticks._base_resource import BaseResource
from blueticks.types.suno import SongClip, SongGeneration, SunoAccount, SunoUpload


class SunoResource(BaseResource):
    def account(self) -> SunoAccount:
        """Get Suno account.

        Remaining credits, monthly usage, and plan on the connected Suno account.
        Requires ``suno:read``.
        """
        envelope = self._client._request("GET", "/v1/suno/account")
        return SunoAccount.model_validate(envelope["data"])

    def generate_song(
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
    ) -> SongGeneration:
        """Generate song.

        Submit a song generation to Suno from ``lyrics`` + ``style``. Returns two
        clip variants — poll each with :meth:`get_song` until ``status`` is
        ``complete``. Requires ``suno:write``.
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
        envelope = self._client._request("POST", "/v1/suno/songs", body=body)
        return SongGeneration.model_validate(envelope["data"])

    def get_song(self, song_id: str) -> SongClip:
        """Get song.

        Poll a single generated clip by id. When ``status`` is ``complete``,
        ``audio_url`` (MP3) and ``image_url`` are populated. Requires
        ``suno:read``.
        """
        envelope = self._client._request("GET", f"/v1/suno/songs/{song_id}")
        return SongClip.model_validate(envelope["data"])

    def upload(
        self,
        *,
        audio_url: str | None = None,
        audio_base64: str | None = None,
        file_name: str | None = None,
    ) -> SunoUpload:
        """Upload reference audio.

        Upload an audio recording (via ``audio_url`` or base64 ``audio_base64``)
        to Suno. Returns an ``upload_id`` to pass to :meth:`generate_song`. Max
        500 MB. Requires ``suno:write``.
        """
        body: dict[str, Any] = {}
        if audio_url is not None:
            body["audioUrl"] = audio_url
        if audio_base64 is not None:
            body["audioBase64"] = audio_base64
        if file_name is not None:
            body["fileName"] = file_name
        envelope = self._client._request("POST", "/v1/suno/uploads", body=body)
        return SunoUpload.model_validate(envelope["data"])
