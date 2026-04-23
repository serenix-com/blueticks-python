from __future__ import annotations

import pytest

from blueticks._errors import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    BadRequestError,
    BluetickError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    from_envelope,
)


def test_base_class_is_exception() -> None:
    assert issubclass(BluetickError, Exception)


def test_all_subclasses_inherit_bluetick_error() -> None:
    for cls in [
        AuthenticationError,
        PermissionError,
        NotFoundError,
        BadRequestError,
        RateLimitError,
        APIError,
        APIConnectionError,
    ]:
        assert issubclass(cls, BluetickError)


def test_str_renders_status_code_and_request_id() -> None:
    err = BluetickError(
        status_code=401,
        code="authentication_required",
        message="bad key",
        request_id="req_123",
    )
    assert str(err) == "401 authentication_required: bad key (request_id=req_123)"


def test_str_handles_missing_request_id() -> None:
    err = BluetickError(status_code=500, code="internal_error", message="boom", request_id=None)
    assert "request_id=None" in str(err)


@pytest.mark.parametrize(
    "status,code,expected_cls",
    [
        (401, "authentication_required", AuthenticationError),
        (403, "permission_denied", PermissionError),
        (404, "not_found", NotFoundError),
        (400, "invalid_request", BadRequestError),
        (422, "invalid_request", BadRequestError),
        (429, "rate_limited", RateLimitError),
        (500, "internal_error", APIError),
        (503, "internal_error", APIError),
    ],
)
def test_from_envelope_maps_status_to_typed_exception(
    status: int, code: str, expected_cls: type[BluetickError]
) -> None:
    err = from_envelope(
        status_code=status,
        body={"error": {"code": code, "message": "m", "request_id": "r"}},
        response=None,
    )
    assert isinstance(err, expected_cls)
    assert err.status_code == status
    assert err.code == code
    assert err.message == "m"
    assert err.request_id == "r"


def test_from_envelope_falls_back_when_body_has_no_error_key() -> None:
    err = from_envelope(status_code=502, body={"weird": "shape"}, response=None)
    assert isinstance(err, APIError)
    assert err.code is None
    # raw body, truncated
    assert "weird" in err.message


def test_from_envelope_truncates_long_bodies() -> None:
    big = "x" * 500
    err = from_envelope(status_code=500, body=big, response=None)
    assert len(err.message) <= 210  # 200 truncated chars + ellipsis marker


def test_rate_limit_error_carries_retry_after() -> None:
    err = RateLimitError(
        status_code=429,
        code="rate_limited",
        message="slow down",
        request_id=None,
        retry_after=30.0,
    )
    assert err.retry_after == 30.0
