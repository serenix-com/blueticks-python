# Changelog

All notable changes to `blueticks` will be documented in this file. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/).

## 6.0.0 — 2026-06-25

**Breaking — newsletter identity field renamed and split by surface.** The
backend split the `/v1/newsletters` identity field by response surface to match
how chats/contacts/groups list endpoints key rows. The SDK follows.

### Changed (BREAKING)

- `blueticks.types.newsletters.Newsletter` (returned by
  `client.newsletters.retrieve()` and `client.newsletters.create()`) renamed its
  identity field `id` → `newsletter_id` (JSON `newsletterId`). The stale `owner`
  field, no longer in the API spec, has been removed.
- `client.newsletters.list()` now returns
  `Page[blueticks.types.newsletters.NewsletterListItem]` instead of
  `Page[Newsletter]`. List rows key their identity field as `chat_id`
  (JSON `chatId`), matching the chats/contacts/groups list shape.

### Added

- `blueticks.types.newsletters.NewsletterListItem` — list-row model, exported
  from `blueticks.types`.

## 5.0.0 — 2026-06-18

**Breaking — webhook signing removed.** The backend no longer signs webhook
deliveries: payloads are no longer HMAC-signed, webhook create no longer
returns a `secret`, and `POST /v1/webhooks/{id}/rotate-secret` is gone. The
webhook resource now exposes plain CRUD only.

### Removed (BREAKING)

- `blueticks.webhooks.verify()` — the HMAC signature-verification helper is
  gone (deliveries are no longer signed).
- `WebhookVerificationError` — no longer raised or exported.
- `client.webhooks.rotate_secret()` — the endpoint no longer exists.
- `blueticks.types.webhooks.WebhookCreateResult` (the create-result type that
  carried `secret`) and `blueticks.types.webhooks.WebhookEvent` (used only by
  `verify`) have been removed from `blueticks.types`.

### Changed (BREAKING)

- `client.webhooks.create()` now returns a plain `Webhook` (no `secret`
  field) instead of `WebhookCreateResult`.

## 4.0.0 — 2026-05-27

**Breaking — wire rename.** The backend renamed the queued-send domain on
the wire: `POST/GET/PATCH /v1/messages*` → `POST/GET/PATCH /v1/scheduled-messages*`.
The SDK follows.

### Removed (BREAKING)

- `client.messages` is gone. The resource (and the underlying
  `blueticks.types.messages.Message` type) no longer exists.

### Changed (BREAKING)

- All queued-send methods now live on `client.scheduled_messages`:
  - `client.messages.send(...)` → `client.scheduled_messages.create(...)`
  - `client.messages.retrieve(id)` → `client.scheduled_messages.retrieve(id)`
  - `client.messages.list(...)` → `client.scheduled_messages.list(...)`
  - `client.messages.update(id, ...)` → `client.scheduled_messages.update(id, ...)`
- Response type renamed: `blueticks.types.messages.Message` →
  `blueticks.types.scheduled_messages.ScheduledMessage` (same shape).
- `client.scheduled_messages.list()` now accepts `chat_id`, `status`, and
  `q` query params (matching the spec) in addition to `limit` / `cursor`.

See `README.md` → "Migrating from 3.x → 4.0" for code samples.

## 3.4.0 — 2026-05-22

OpenAPI parity pass. The SDK now matches `backend/openapi.json`
operation-for-operation; an engineless drift check
(`.github/workflows/sdk-spec-drift.yml`) gates future regressions. The
`/v1/*` surface is pre-release — none of these changes affect production
callers yet.

### Changed

- `messages.send()` now takes the discriminated body shape that the
  backend's strict `anyOf` enforces (BE#50). Pass `type="text"|"media"|"poll"`
  plus the variant fields:
  ```python
  client.messages.send(to="+1...", type="text", text="hi")
  client.messages.send(to="+1...", type="media", media={"url": "...", "kind": "image"})
  client.messages.send(to="+1...", type="poll",  poll={"question": "...", "options": [...]})
  ```
- Single-item GETs now use `.retrieve(id)` instead of `.get(id)` (OpenAPI
  convention): `audiences`, `campaigns`, `chats`, `groups`, `webhooks`,
  `messages`, `scheduled_messages`. Also `engines.status()` →
  `engines.retrieve()`.
- `newsletters.create()` returns the typed 8-field `Newsletter` (was a
  3-field stub): `id`, `name`, `description?`, `owner?`, `created_at?`,
  `subscribers?`, `invite?`, `verification?` (`VERIFIED`/`UNVERIFIED`).

### Added

- `newsletters.list(*, limit, cursor) -> Page[Newsletter]` — `GET /v1/newsletters`
- `newsletters.retrieve(id) -> Newsletter` — `GET /v1/newsletters/{id}`
- `ping.retrieve() -> Ping` — typed response (`account_id`, `key_prefix`, `scopes`).
- `Message` now exposes `key`, `type`, `media_kind`, `poll_question`,
  `link_preview` (was reachable only via raw transport).

### Removed

- `engines.me`, `engines.logout`, `engines.reload` — no `/v1/*` endpoint in spec.
- `contacts.get_profile_picture` — no spec backing.
- `utils.validate_phone`, `utils.link_preview` — no spec backing.

### Fixed

- `groups.list()` was documented at `dev.blueticks.co` but absent from the
  SDK for ~9 days — now present.

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
