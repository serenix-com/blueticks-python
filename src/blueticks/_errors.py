from __future__ import annotations

from typing import Any

import httpx


class BluetickError(Exception):
    """Base class for all Blueticks client errors."""

    status_code: int | None
    code: str | None
    message: str
    request_id: str | None
    response: httpx.Response | None

    def __init__(
        self,
        *,
        status_code: int | None = None,
        code: str | None = None,
        message: str = "",
        request_id: str | None = None,
        response: httpx.Response | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.request_id = request_id
        self.response = response
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"{self.status_code} {self.code}: {self.message} (request_id={self.request_id})"


class AuthenticationError(BluetickError):
    """401 — missing or invalid API key."""


class PermissionDeniedError(BluetickError):
    """403 — the key lacks the required scope or workspace access."""


class NotFoundError(BluetickError):
    """404 — the resource does not exist."""


class BadRequestError(BluetickError):
    """400 / 422 — the request was malformed or failed validation."""


class RateLimitError(BluetickError):
    """429 — the client is being throttled."""

    retry_after: float | None

    def __init__(self, *, retry_after: float | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.retry_after = retry_after


class APIError(BluetickError):
    """5xx or otherwise-unparseable error response from the API."""


class APIConnectionError(BluetickError):
    """Network failure: DNS, TLS, timeout, connection reset."""


_STATUS_TO_CLASS: dict[int, type[BluetickError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: BadRequestError,
    429: RateLimitError,
}


def _class_for_status(status: int) -> type[BluetickError]:
    return _STATUS_TO_CLASS.get(status, APIError)


def from_envelope(
    *,
    status_code: int,
    body: Any,
    response: httpx.Response | None,
    retry_after: float | None = None,
) -> BluetickError:
    """Map a non-2xx response body to a typed Blueticks exception."""
    cls = _class_for_status(status_code)

    error = body.get("error") if isinstance(body, dict) else None
    if isinstance(error, dict) and isinstance(error.get("code"), str):
        kwargs: dict[str, Any] = {
            "status_code": status_code,
            "code": error.get("code"),
            "message": error.get("message", ""),
            "request_id": error.get("request_id"),
            "response": response,
        }
        if cls is RateLimitError:
            kwargs["retry_after"] = retry_after
        return cls(**kwargs)

    # Fallback: unknown shape. Render the body as a truncated string.
    raw = body if isinstance(body, str) else repr(body)
    truncated = raw[:200] + ("..." if len(raw) > 200 else "")
    kwargs = {
        "status_code": status_code,
        "code": None,
        "message": truncated,
        "request_id": None,
        "response": response,
    }
    if cls is RateLimitError:
        kwargs["retry_after"] = retry_after
    return cls(**kwargs)
