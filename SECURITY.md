# Security Considerations

This document captures security-relevant configuration and operational notes.

## Secrets and configuration
- Never commit secrets to the repository.
- `JWT_SECRET` must be set in production (`APP_ENV=prod`/`production`).
- The service fails fast on startup if `JWT_SECRET` is not overridden in production.

## Authentication
- Passwords are hashed using bcrypt.
- Access tokens are JWTs with issuer/audience validation and expirations.
- Refresh tokens are stored as hashes and rotated on use.

## Auditing
- Sensitive actions write audit logs with IP address and device ID.
