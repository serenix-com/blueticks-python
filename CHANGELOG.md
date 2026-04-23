# Changelog

All notable changes to `blueticks` will be documented in this file. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/).

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
