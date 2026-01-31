# API Documentation

## Interactive docs

When the service is running, FastAPI serves:
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Base path

All endpoints are versioned under `/v1`.

## Authentication

All protected endpoints require a bearer token:

```
Authorization: Bearer <access_token>
```

Tokens are issued by:
- `POST /v1/auth/signup`
- `POST /v1/auth/login`

## Accounts

- `POST /v1/accounts` — create an account for the current user
- `GET /v1/accounts` — list accounts for the current user
- `GET /v1/accounts/{account_id}` — get account details for the current user

## Transactions

- `POST /v1/transactions` — create a deposit or withdrawal

## Transfers

- `POST /v1/transfers` — transfer funds between two accounts

## Statements

- `GET /v1/statements/{account_id}` — statement summary + transactions

## Cards

- `POST /v1/cards` — issue a card for an account
- `GET /v1/cards/{card_id}` — retrieve card details

## Account holders

- `GET /v1/account-holders` — list account holders
- `GET /v1/account-holders/{holder_id}` — retrieve account holder details

## Health

- `GET /v1/health` — readiness check (includes DB connectivity)

