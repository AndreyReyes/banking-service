# Roadmap

Planned work items and follow-ups for the banking service.

## Near-term
- Replace FastAPI `on_event` startup hooks with lifespan handlers to resolve
  deprecation warnings and centralize startup/shutdown logic.
- Add integration coverage for error envelope mappings across common HTTP
  statuses (400, 403, 404, 409, 422, 500) to ensure consistent payloads.
- Define and implement an admin account model and lifecycle, including:
  - Security and authorization rules for elevated access.
  - How admin accounts are created, stored, and managed.
  - Auditability, rotation, and safe operational workflows.
- Add an admin-only API to list all account holders once admin creation and
  authorization rules are in place.
- Add auth hardening items:
  - Detect refresh token reuse and invalidate the entire family.
  - Revoke token families on password changes or suspicious activity.
  - Store refresh tokens in HTTP-only cookies for browser clients.
  - Track access token `jti` values for server-side revocation.
- Re-enable Black formatting checks after repo-wide formatting cleanup.
- Re-enable mypy checks after resolving route/schema type mismatches.

## Mid-term
- Adopt a Vite + React frontend with a typed API client and auth flow.
- On new browser sessions, fetch the current user's account holders and accounts
  from the API instead of relying on in-memory state from creation flows. This
  is currently blocked on the admin account model and permissions for any
  global listing needs.
