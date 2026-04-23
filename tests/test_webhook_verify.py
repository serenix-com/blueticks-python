from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from blueticks.webhooks import WebhookVerificationError, verify


SECRET = "whsec_test_secret"


def _sign(payload: bytes, timestamp: int, secret: str = SECRET) -> str:
    return hmac.new(
        secret.encode(),
        f"{timestamp}.{payload.decode()}".encode(),
        hashlib.sha256,
    ).hexdigest()


def _headers(payload: bytes, ts_offset: int = 0, secret: str = SECRET) -> dict:
    ts = int(time.time()) + ts_offset
    sig = _sign(payload, ts, secret)
    return {
        "Blueticks-Webhook-Id": "wh_1",
        "Blueticks-Webhook-Timestamp": str(ts),
        "Blueticks-Webhook-Signature": f"v1={sig}",
    }


def test_verify_accepts_valid_signature():
    payload = json.dumps(
        {
            "id": "evt_1",
            "type": "message.delivered",
            "created_at": "2026-04-23T00:00:00Z",
            "data": {},
        }
    ).encode()
    event = verify(payload, _headers(payload), secret=SECRET)
    assert event.id == "evt_1"
    assert event.type == "message.delivered"


def test_verify_rejects_expired_timestamp():
    payload = b'{"id":"evt","type":"message.delivered","created_at":"2026-04-23T00:00:00Z","data":{}}'
    with pytest.raises(WebhookVerificationError, match="expired"):
        verify(payload, _headers(payload, ts_offset=-400), secret=SECRET)


def test_verify_rejects_tampered_payload():
    payload = b'{"id":"evt","type":"message.delivered","created_at":"2026-04-23T00:00:00Z","data":{}}'
    headers = _headers(payload)
    tampered = b'{"id":"evt","type":"message.FAILED","created_at":"2026-04-23T00:00:00Z","data":{}}'
    with pytest.raises(WebhookVerificationError, match="invalid_signature"):
        verify(tampered, headers, secret=SECRET)


def test_verify_rejects_wrong_secret():
    payload = b'{"id":"evt","type":"message.delivered","created_at":"2026-04-23T00:00:00Z","data":{}}'
    with pytest.raises(WebhookVerificationError, match="invalid_signature"):
        verify(payload, _headers(payload), secret="whsec_wrong")


def test_verify_missing_header():
    payload = b'{"id":"evt","type":"message.delivered","created_at":"2026-04-23T00:00:00Z","data":{}}'
    with pytest.raises(WebhookVerificationError):
        verify(payload, {}, secret=SECRET)


def test_verify_case_insensitive_headers():
    payload = b'{"id":"evt","type":"message.delivered","created_at":"2026-04-23T00:00:00Z","data":{}}'
    h = _headers(payload)
    lowered = {k.lower(): v for k, v in h.items()}
    event = verify(payload, lowered, secret=SECRET)
    assert event.id == "evt"


def test_verify_accepts_str_payload():
    payload = '{"id":"evt","type":"message.delivered","created_at":"2026-04-23T00:00:00Z","data":{}}'
    event = verify(payload, _headers(payload.encode()), secret=SECRET)
    assert event.id == "evt"
