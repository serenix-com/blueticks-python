from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from blueticks._errors import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    RateLimitError,
)
from blueticks._transport import Transport


def _envelope(code: str, message: str = "x", request_id: str = "req_1") -> bytes:
    body = {"error": {"code": code, "message": message, "request_id": request_id}}
    return json.dumps(body).encode()


def _ok(body: Any) -> bytes:
    return json.dumps(body).encode()


def _mock(handler):
    return httpx.MockTransport(handler)


def _make_transport(mock: httpx.MockTransport, *, max_retries: int = 2) -> Transport:
    return Transport(
        api_key="bt_test_abc",
        base_url="https://example.test",
        timeout=5.0,
        max_retries=max_retries,
        user_agent_suffix=None,
        version="1.0.0",
        http_transport=mock,
    )


def test_get_returns_parsed_json_on_200() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer bt_test_abc"
        assert "blueticks-python/1.0.0" in request.headers["user-agent"]
        return httpx.Response(200, content=_ok({"hello": "world"}))

    transport = _make_transport(_mock(handler))
    result = transport.request("GET", "/v1/ping", params=None, body=None)
    assert result == {"hello": "world"}


def test_401_raises_authentication_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, content=_envelope("authentication_required", "bad"))

    transport = _make_transport(_mock(handler))
    with pytest.raises(AuthenticationError) as info:
        transport.request("GET", "/v1/ping", params=None, body=None)
    assert info.value.code == "authentication_required"
    assert info.value.message == "bad"


def test_non_json_body_still_raises_api_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(502, content=b"<html>bad gateway</html>")

    transport = _make_transport(_mock(handler))
    with pytest.raises(APIError) as info:
        transport.request("GET", "/v1/ping", params=None, body=None)
    assert info.value.status_code == 502


def test_429_with_retry_after_retries_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(
                429,
                headers={"retry-after": "0"},
                content=_envelope("rate_limited", "slow"),
            )
        return httpx.Response(200, content=_ok({"ok": True}))

    transport = _make_transport(_mock(handler), max_retries=3)
    result = transport.request("GET", "/v1/ping", params=None, body=None)
    assert result == {"ok": True}
    assert calls["n"] == 2


def test_429_exhausts_retries_and_raises_rate_limit() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"retry-after": "0"}, content=_envelope("rate_limited"))

    transport = _make_transport(_mock(handler), max_retries=1)
    with pytest.raises(RateLimitError) as info:
        transport.request("GET", "/v1/ping", params=None, body=None)
    assert info.value.retry_after == 0.0


def test_503_retries_then_succeeds() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(503, content=_envelope("internal_error"))
        return httpx.Response(200, content=_ok({"ok": True}))

    transport = _make_transport(_mock(handler), max_retries=2)
    result = transport.request("GET", "/v1/ping", params=None, body=None)
    assert result == {"ok": True}


def test_post_does_not_retry_on_5xx_without_idempotency_key() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(503, content=_envelope("internal_error"))

    transport = _make_transport(_mock(handler), max_retries=3)
    with pytest.raises(APIError):
        transport.request("POST", "/v1/messages", params=None, body={"x": 1})
    assert calls["n"] == 1


def test_connection_error_retries() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.ConnectError("dns fail")
        return httpx.Response(200, content=_ok({"ok": True}))

    transport = _make_transport(_mock(handler), max_retries=2)
    result = transport.request("GET", "/v1/ping", params=None, body=None)
    assert result == {"ok": True}


def test_connection_error_exhausted_raises_api_connection_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("dns fail")

    transport = _make_transport(_mock(handler), max_retries=1)
    with pytest.raises(APIConnectionError):
        transport.request("GET", "/v1/ping", params=None, body=None)


def test_user_agent_includes_suffix() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["ua"] = request.headers["user-agent"]
        return httpx.Response(200, content=_ok({}))

    t = Transport(
        api_key="k",
        base_url="https://example.test",
        timeout=5.0,
        max_retries=0,
        user_agent_suffix="myapp/1.2",
        version="1.0.0",
        http_transport=_mock(handler),
    )
    t.request("GET", "/v1/ping", params=None, body=None)
    assert captured["ua"] == "blueticks-python/1.0.0 myapp/1.2"


def test_query_params_are_sent() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, content=_ok({}))

    transport = _make_transport(_mock(handler))
    transport.request("GET", "/v1/messages", params={"limit": 10}, body=None)
    assert "limit=10" in captured["url"]


def test_body_is_json_encoded() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.content
        return httpx.Response(200, content=_ok({}))

    transport = _make_transport(_mock(handler))
    transport.request("POST", "/v1/messages", params=None, body={"text": "hi"})
    assert json.loads(captured["body"]) == {"text": "hi"}
