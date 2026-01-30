# Roadmap

Planned work items and follow-ups for the banking service.

## Near-term
- Replace FastAPI `on_event` startup hooks with lifespan handlers to resolve
  deprecation warnings and centralize startup/shutdown logic.
- Add integration coverage for error envelope mappings across common HTTP
  statuses (400, 403, 404, 409, 422, 500) to ensure consistent payloads.
- Add demo flow integration test and CLI client for end-to-end validation.
- Add a minimal static frontend to showcase the core flow.
- Add auth hardening items:
  - Detect refresh token reuse and invalidate the entire family.
  - Revoke token families on password changes or suspicious activity.
  - Store refresh tokens in HTTP-only cookies for browser clients.
  - Track access token `jti` values for server-side revocation.
- Re-enable Black formatting checks after repo-wide formatting cleanup.
- Re-enable mypy checks after resolving route/schema type mismatches.

## Mid-term
- Adopt a Vite + React frontend with a typed API client and auth flow.
