from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import AuthenticationError
from blueticks.types.suno import SunoAccount, SunoClip, SunoGeneration, SunoUpload


def _clip(**overrides) -> dict:
    data = {
        "id": "clip_1",
        "status": "streaming",
        "audioUrl": None,
        "imageUrl": None,
        "title": None,
        "durationSec": None,
        "model": "v5.5",
    }
    data.update(overrides)
    return data


def test_suno_generate_returns_typed_model(mock_client) -> None:
    body_seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(request.content))
        assert request.method == "POST"
        assert request.url.path == "/v1/suno/songs"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "jobId": "job_abc123",
                    "clips": [
                        _clip(id="clip_1"),
                        _clip(id="clip_2", status="queued"),
                    ],
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.suno.generate(
            lyrics="[Verse]\nSunlight on the open road",
            style="upbeat pop, acoustic guitar",
            vocal_gender="f",
            weirdness=0.4,
            style_influence=0.7,
            upload_id="upl_ref_1",
            audio_influence=0.8,
            instrumental=False,
            model="v5.5",
            title="Morning",
            negative_style="metal",
            captcha_token="cf_tok",
        )
    assert isinstance(result, SunoGeneration)
    assert result.job_id == "job_abc123"
    assert len(result.clips) == 2
    assert isinstance(result.clips[0], SunoClip)
    assert result.clips[0].id == "clip_1"
    assert result.clips[0].status == "streaming"
    assert result.clips[1].status == "queued"
    assert result.clips[0].model == "v5.5"
    # Body fields serialize to the camelCase wire names.
    assert body_seen == {
        "lyrics": "[Verse]\nSunlight on the open road",
        "style": "upbeat pop, acoustic guitar",
        "negativeStyle": "metal",
        "vocalGender": "f",
        "weirdness": 0.4,
        "styleInfluence": 0.7,
        "audioInfluence": 0.8,
        "instrumental": False,
        "model": "v5.5",
        "title": "Morning",
        "uploadId": "upl_ref_1",
        "captchaToken": "cf_tok",
    }


def test_suno_generate_minimal_body(mock_client) -> None:
    body_seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(request.content))
        return httpx.Response(
            200,
            content=json.dumps({"jobId": "job_1", "clips": [_clip()]}).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        client.suno.generate(lyrics="la la la", style="lo-fi")
    assert body_seen == {"lyrics": "la la la", "style": "lo-fi"}


def test_suno_retrieve_returns_typed_model(mock_client) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/suno/songs/clip_1"
        return httpx.Response(
            200,
            content=json.dumps(
                _clip(
                    id="clip_1",
                    status="complete",
                    audioUrl="https://cdn.suno.example/clip_1.mp3",
                    imageUrl="https://cdn.suno.example/clip_1.jpg",
                    title="Morning",
                    durationSec=123.4,
                )
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.suno.retrieve("clip_1")
    assert isinstance(result, SunoClip)
    assert result.id == "clip_1"
    assert result.status == "complete"
    assert result.audio_url == "https://cdn.suno.example/clip_1.mp3"
    assert result.image_url == "https://cdn.suno.example/clip_1.jpg"
    assert result.title == "Morning"
    assert result.duration_sec == 123.4


def test_suno_upload_returns_typed_model(mock_client) -> None:
    body_seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(request.content))
        assert request.method == "POST"
        assert request.url.path == "/v1/suno/uploads"
        return httpx.Response(
            200,
            content=json.dumps({"uploadId": "upl_abc", "status": "complete"}).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.suno.upload(
            audio_url="https://example.com/me-singing.mp3",
            file_name="me-singing.mp3",
        )
    assert isinstance(result, SunoUpload)
    assert result.upload_id == "upl_abc"
    assert result.status == "complete"
    assert body_seen == {
        "audioUrl": "https://example.com/me-singing.mp3",
        "fileName": "me-singing.mp3",
    }


def test_suno_account_returns_typed_model(mock_client) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/v1/suno/account"
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "creditsLeft": 100.0,
                    "monthlyLimit": 500.0,
                    "monthlyUsage": 42.0,
                    "plan": "Pro Plan",
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.suno.account()
    assert isinstance(result, SunoAccount)
    assert result.credits_left == 100.0
    assert result.monthly_limit == 500.0
    assert result.monthly_usage == 42.0
    assert result.plan == "Pro Plan"


def test_suno_account_accepts_null_optionals(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=json.dumps(
                {
                    "creditsLeft": 0.0,
                    "monthlyLimit": None,
                    "monthlyUsage": None,
                    "plan": None,
                }
            ).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        result = client.suno.account()
    assert result.credits_left == 0.0
    assert result.monthly_limit is None
    assert result.plan is None


def test_suno_generate_propagates_authentication_error(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        body = {
            "error": {
                "code": "authentication_required",
                "message": "bad key",
                "requestId": "req_suno_1",
            }
        }
        return httpx.Response(
            401,
            content=json.dumps(body).encode(),
            headers={"content-type": "application/json"},
        )

    with mock_client(handler) as client:
        with pytest.raises(AuthenticationError) as info:
            client.suno.generate(lyrics="hi", style="pop")
    assert info.value.code == "authentication_required"
    assert info.value.message == "bad key"
    assert info.value.request_id == "req_suno_1"


def test_suno_generate_missing_required_field_raises_validation_error(mock_client) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{}", headers={"content-type": "application/json"})

    with mock_client(handler) as client:
        with pytest.raises(ValidationError):
            client.suno.generate(lyrics="hi", style="pop")
