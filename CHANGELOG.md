# Changelog

All notable changes to `blueticks` will be documented in this file. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/).

## 3.2.0 — 2026-04-30

### Added
- `ChatMedia.original_quality: Optional[bool]` — False when WA returned
  a preview JPEG instead of the original sender uploaded (#113 — only
  affects own-sent newsletter media). None/absent on the genuine
  original from the sender.
- `ChatMedia.media_unavailable: Optional[MediaUnavailableReason]` —
  reason the bytes couldn't be retrieved (`"expired"`, `"fetching"`,
  `"error"`, `"no_media"`). None/absent on success.
- New `MediaUnavailableReason` Literal type — string-enum of the 4
  reasons.

The `client.chats.get_media()` method already existed; this release
fleshes out its response shape so consumers can detect preview-fidelity
fallback and unavailable-bytes states without a separate retry.

## 3.1.0 — 2026-04-29

### Added
- `client.chats.list_messages()` now accepts `message_types: list[MessageType]` —
  filter to specific message kinds (e.g. `["document"]` for PDFs, `["image"]`
  for photos). System events (`gp2`, `revoked`, `newsletter_notification`) are
  excluded by default unless explicitly listed.
- New `MessageType` Literal — string-enum of the 13 WhatsApp message kinds.
- `ChatMessage.caption` and `ChatMessage.filename` — surfaced for media
  messages so document listings are self-describing without an extra
  media-fetch round-trip.

### Fixed
- Stale list-test mocks (`test_audiences`, `test_campaigns`,
  `test_webhooks_resource`) now use the cursor-paginated `Page<T>` envelope.
  Behaviour-only test fix.

## 1.1.0 — 2026-04-23

### Added
- `client.messages.send()` and `client.messages.get()` for the `/v1/messages` endpoints (send now or schedule, URL-based media, idempotency-key support)
- `client.webhooks` — full CRUD plus `rotate_secret()`
- `client.audiences` — CRUD plus contact-level endpoints
- `client.campaigns` — CRUD plus `pause()`, `resume()`, `cancel()`
- `blueticks.webhooks.verify()` helper for HMAC signature verification in webhook handlers
- `WebhookVerificationError` exception

## [1.0.0] — unreleased

### Added
- Initial release.
- `Blueticks.ping()` — health check for the API.
- `Blueticks.account.retrieve()` — fetch the authenticated account.
- Typed exception hierarchy: `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`,
  `BadRequestError`, `RateLimitError`, `APIError`, `APIConnectionError`.
- Retry logic with exponential backoff + jitter (429, 502, 503, 504, network errors).
- Python 3.9, 3.10, 3.11, 3.12 support.
