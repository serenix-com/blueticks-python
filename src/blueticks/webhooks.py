from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Mapping, Optional, Union

from blueticks._errors import BluetickError
from blueticks.types.webhooks import WebhookEvent


__all__ = ["verify", "WebhookVerificationError"]


class WebhookVerificationError(BluetickError):
    """Raised when a webhook signature cannot be verified."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            status_code=None,
            code="webhook_verification_failed",
            message=reason,
            request_id=None,
        )


_DEFAULT_TOLERANCE_SECONDS = 300


def _header(headers: Mapping[str, str], name: str) -> Optional[str]:
    if name in headers:
        return headers[name]
    lower = name.lower()
    for k, v in headers.items():
        if k.lower() == lower:
            return v
    return None


def verify(
    payload: Union[bytes, str],
    headers: Mapping[str, str],
    *,
    secret: str,
    tolerance: int = _DEFAULT_TOLERANCE_SECONDS,
) -> WebhookEvent:
    """Verify a webhook signature and return the parsed ``WebhookEvent``.

    Raises :class:`WebhookVerificationError` if the headers are missing, the
    timestamp is outside the tolerance window, or the signature does not match.
    """
    timestamp_raw = _header(headers, "Blueticks-Webhook-Timestamp")
    signature_raw = _header(headers, "Blueticks-Webhook-Signature")
    if not timestamp_raw or not signature_raw:
        raise WebhookVerificationError("missing required headers")

    try:
        timestamp = int(timestamp_raw)
    except ValueError as e:
        raise WebhookVerificationError("invalid timestamp") from e

    if abs(time.time() - timestamp) > tolerance:
        raise WebhookVerificationError("expired timestamp")

    if isinstance(payload, str):
        payload_bytes = payload.encode()
    else:
        payload_bytes = payload

    signed = f"{timestamp}.{payload_bytes.decode()}".encode()
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()

    # Parse "v1=<hex>" from the signature header.
    parts = [p.strip() for p in signature_raw.split(",")]
    supplied = None
    for p in parts:
        if p.startswith("v1="):
            supplied = p[3:]
            break
    if supplied is None:
        raise WebhookVerificationError("invalid_signature: missing v1 scheme")

    if not hmac.compare_digest(expected, supplied):
        raise WebhookVerificationError("invalid_signature: mismatch")

    return WebhookEvent.model_validate(json.loads(payload_bytes.decode()))
