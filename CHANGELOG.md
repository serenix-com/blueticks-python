# Changelog

All notable changes to `blueticks` will be documented in this file. This project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] — unreleased

### Added
- Initial release.
- `Blueticks.ping()` — health check for the API.
- `Blueticks.account.retrieve()` — fetch the authenticated account.
- Typed exception hierarchy: `AuthenticationError`, `PermissionError`, `NotFoundError`,
  `BadRequestError`, `RateLimitError`, `APIError`, `APIConnectionError`.
- Retry logic with exponential backoff + jitter (429, 502, 503, 504, network errors).
- Python 3.9, 3.10, 3.11, 3.12 support.
