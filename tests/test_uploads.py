from __future__ import annotations

import json

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.uploads import Upload


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=201):
    return httpx.Response(status, json={"success": True, "data": data})


def _upload():
    return {
        "fileId": "Ab12Cd34Ef56",
        "uploadUrl": "https://storage.example.test/put/Ab12Cd34Ef56",
        "method": "PUT",
        "headers": {"Content-Type": "image/png"},
        "expiresAt": "2026-04-23T01:00:00Z",
        "deleteAt": "2026-04-23T02:00:00Z",
        "maxBytes": 16777216,
        "contentType": "image/png",
    }


def test_create_upload_posts_camel_case_body_and_returns_typed_model():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        assert req.method == "POST"
        assert req.url.path == "/v1/uploads"
        return _ok(_upload())

    result = _client(handler).uploads.create(
        content_type="image/png", size_bytes=2048, filename="logo.png"
    )
    assert isinstance(result, Upload)
    assert result.file_id == "Ab12Cd34Ef56"
    assert result.method == "PUT"
    assert result.headers == {"Content-Type": "image/png"}
    assert result.max_bytes == 16777216
    assert body_seen == {"contentType": "image/png", "sizeBytes": 2048, "filename": "logo.png"}


def test_create_upload_omits_optional_fields_when_unset():
    body_seen: dict = {}

    def handler(req: httpx.Request) -> httpx.Response:
        body_seen.update(json.loads(req.content))
        return _ok(_upload())

    _client(handler).uploads.create(content_type="image/png")
    assert body_seen == {"contentType": "image/png"}


def test_create_upload_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_u1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).uploads.create(content_type="image/png")
    assert exc_info.value.request_id == "req_u1"
    assert exc_info.value.code == "authentication_required"


def test_upload_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).uploads.create(content_type="image/png")
