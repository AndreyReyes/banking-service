from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import (
    apply_migrations,
    configure_test_db,
    login,
    signup,
)


def test_deposit_and_withdrawal_affect_balance(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "transactions")
    apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        signup(client, "ada@example.com", "supersecure123")
        tokens = login(client, "ada@example.com", "supersecure123")

        account_response = client.post(
            "/v1/accounts",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"type": "checking", "currency": "USD"},
        )
        account_id = account_response.json()["id"]

        deposit_response = client.post(
            "/v1/transactions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "account_id": account_id,
                "type": "deposit",
                "amount": 5000,
                "currency": "USD",
            },
        )
        assert deposit_response.status_code == 201

        withdrawal_response = client.post(
            "/v1/transactions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "account_id": account_id,
                "type": "withdrawal",
                "amount": 2000,
                "currency": "USD",
            },
        )
        assert withdrawal_response.status_code == 201

        account_read = client.get(
            f"/v1/accounts/{account_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert account_read.status_code == 200
        assert account_read.json()["balance"] == 3000


def test_withdrawal_rejects_negative_balance(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "withdrawals")
    apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        signup(client, "ada@example.com", "supersecure123")
        tokens = login(client, "ada@example.com", "supersecure123")

        account_response = client.post(
            "/v1/accounts",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"type": "checking", "currency": "USD"},
        )
        account_id = account_response.json()["id"]

        withdrawal_response = client.post(
            "/v1/transactions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "account_id": account_id,
                "type": "withdrawal",
                "amount": 100,
                "currency": "USD",
            },
        )
        assert withdrawal_response.status_code == 400
