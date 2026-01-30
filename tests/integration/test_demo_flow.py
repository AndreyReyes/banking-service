from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import apply_migrations, configure_test_db, login, signup


def test_demo_flow_signup_login_accounts_transfer_statement(
    tmp_path: Path, monkeypatch
) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "demo-flow")
    apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        signup(client, "demo@example.com", "supersecure123")
        tokens = login(client, "demo@example.com", "supersecure123")
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        source_account = client.post(
            "/v1/accounts",
            headers=headers,
            json={"type": "checking", "currency": "USD"},
        )
        assert source_account.status_code == 201
        source_account_id = source_account.json()["id"]

        destination_account = client.post(
            "/v1/accounts",
            headers=headers,
            json={"type": "savings", "currency": "USD"},
        )
        assert destination_account.status_code == 201
        destination_account_id = destination_account.json()["id"]

        deposit_response = client.post(
            "/v1/transactions",
            headers=headers,
            json={
                "account_id": source_account_id,
                "type": "deposit",
                "amount": 10000,
                "currency": "USD",
            },
        )
        assert deposit_response.status_code == 201

        transfer_response = client.post(
            "/v1/transfers",
            headers=headers,
            json={
                "from_account_id": source_account_id,
                "to_account_id": destination_account_id,
                "amount": 2500,
                "currency": "USD",
            },
        )
        assert transfer_response.status_code == 201

        source_statement = client.get(
            f"/v1/statements/{source_account_id}",
            headers=headers,
        )
        assert source_statement.status_code == 200
        source_payload = source_statement.json()
        assert source_payload["balance"] == 7500
        source_types = {tx["type"] for tx in source_payload["transactions"]}
        assert {"deposit", "transfer_out"} <= source_types

        destination_statement = client.get(
            f"/v1/statements/{destination_account_id}",
            headers=headers,
        )
        assert destination_statement.status_code == 200
        destination_payload = destination_statement.json()
        assert destination_payload["balance"] == 2500
        assert len(destination_payload["transactions"]) == 1
        assert destination_payload["transactions"][0]["type"] == "transfer_in"
