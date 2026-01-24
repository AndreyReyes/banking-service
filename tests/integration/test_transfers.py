from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import (
    apply_migrations,
    configure_test_db,
    login,
    signup,
)


def test_transfer_moves_balance_between_accounts(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "transfers")
    apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        signup(client, "ada@example.com", "supersecure123")
        tokens = login(client, "ada@example.com", "supersecure123")

        from_response = client.post(
            "/v1/accounts",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"type": "checking", "currency": "USD"},
        )
        to_response = client.post(
            "/v1/accounts",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"type": "savings", "currency": "USD"},
        )
        from_id = from_response.json()["id"]
        to_id = to_response.json()["id"]

        client.post(
            "/v1/transactions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "account_id": from_id,
                "type": "deposit",
                "amount": 10000,
                "currency": "USD",
            },
        )

        transfer_response = client.post(
            "/v1/transfers",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "from_account_id": from_id,
                "to_account_id": to_id,
                "amount": 2500,
                "currency": "USD",
            },
        )
        assert transfer_response.status_code == 201

        from_read = client.get(
            f"/v1/accounts/{from_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        to_read = client.get(
            f"/v1/accounts/{to_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert from_read.json()["balance"] == 7500
        assert to_read.json()["balance"] == 2500


def test_transfer_rejects_same_account(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "same-account")
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

        transfer_response = client.post(
            "/v1/transfers",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "from_account_id": account_id,
                "to_account_id": account_id,
                "amount": 100,
                "currency": "USD",
            },
        )
        assert transfer_response.status_code == 400
