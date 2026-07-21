from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.suno import SongClip, SongGeneration, SunoAccount, SunoUpload


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def _clip(cid="clip_1", **overrides):
    data = {
        "id": cid,
        "status": "complete",
        "audioUrl": "https://cdn.suno/x.mp3",
        "imageUrl": "https://cdn.suno/x.jpg",
        "title": "My Song",
        "durationSec": 182.5,
        "model": "chirp-v4",
        "errorType": None,
        "errorMessage": None,
    }
    data.update(overrides)
    return data


def test_account():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/suno/account"
        return _ok(
            {"creditsLeft": 250.0, "monthlyLimit": 500.0, "monthlyUsage": 250.0, "plan": "pro"}
        )

    result = _client(handler).suno.account()
    assert isinstance(result, SunoAccount)
    assert result.credits_left == 250.0
    assert result.monthly_usage == 250.0
    assert result.plan == "pro"


def test_generate_song_serializes_camel_case():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/suno/songs"
        return _ok({"jobId": "job_1", "clips": [_clip("clip_1"), _clip("clip_2")]})

    result = _client(handler).suno.generate_song(
        lyrics="la la la",
        style="lofi",
        vocal_gender="f",
        weirdness=0.3,
        style_influence=0.7,
        upload_id="up_1",
    )
    assert isinstance(result, SongGeneration)
    assert result.job_id == "job_1"
    assert len(result.clips) == 2
    assert result.clips[0].duration_sec == 182.5
    assert body_seen == {
        "lyrics": "la la la",
        "style": "lofi",
        "vocalGender": "f",
        "weirdness": 0.3,
        "styleInfluence": 0.7,
        "uploadId": "up_1",
    }


def test_get_song():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.url.path == "/v1/suno/songs/clip_1"
        return _ok(_clip("clip_1", status="running", audioUrl=None))

    result = _client(handler).suno.get_song("clip_1")
    assert isinstance(result, SongClip)
    assert result.status == "running"
    assert result.audio_url is None


def test_upload_serializes_camel_case():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/suno/uploads"
        return _ok({"uploadId": "up_9", "status": "ready"})

    result = _client(handler).suno.upload(audio_url="https://x/a.mp3", file_name="a.mp3")
    assert isinstance(result, SunoUpload)
    assert result.upload_id == "up_9"
    assert body_seen == {"audioUrl": "https://x/a.mp3", "fileName": "a.mp3"}


def test_suno_account_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_suno_1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).suno.account()
    assert exc_info.value.request_id == "req_suno_1"


def test_suno_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).suno.account()
