from __future__ import annotations

import httpx
import pytest
from pydantic import ValidationError

from blueticks import Blueticks
from blueticks._errors import AuthenticationError
from blueticks.types.wa_labels import WaLabel


def _client(handler):
    return Blueticks(api_key="bt_live_test", _http_transport=httpx.MockTransport(handler))


def _ok(data, status=200):
    return httpx.Response(status, json={"success": True, "data": data})


def test_list_wa_labels_returns_typed_list():
    def handler(req: httpx.Request) -> httpx.Response:
        assert req.method == "GET"
        assert req.url.path == "/v1/wa-labels"
        return _ok(
            [
                {"id": "1", "name": "VIP", "color": "#ff0000"},
                {"id": "2", "name": None, "color": None},
            ]
        )

    labels = _client(handler).wa_labels.list()
    assert all(isinstance(label, WaLabel) for label in labels)
    assert [label.id for label in labels] == ["1", "2"]
    assert labels[0].name == "VIP"
    assert labels[0].color == "#ff0000"
    assert labels[1].name is None


def test_list_wa_labels_raises_authentication_error_on_401():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={
                "success": False,
                "error": {
                    "code": "authentication_required",
                    "message": "bad key",
                    "request_id": "req_w1",
                },
            },
        )

    with pytest.raises(AuthenticationError) as exc_info:
        _client(handler).wa_labels.list()
    assert exc_info.value.request_id == "req_w1"


def test_wa_labels_validation_fails_when_required_field_missing():
    with pytest.raises(ValidationError):
        _client(lambda req: _ok({})).wa_labels.list()
