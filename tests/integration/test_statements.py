from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import (
    apply_migrations,
    configure_test_db,
    login,
    signup,
)


def test_statement_returns_summary_and_transactions(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "statements")
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

        client.post(
            "/v1/transactions",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "account_id": account_id,
                "type": "deposit",
                "amount": 1500,
                "currency": "USD",
            },
        )

        statement_response = client.get(
            f"/v1/statements/{account_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert statement_response.status_code == 200
        payload = statement_response.json()
        assert payload["account_id"] == account_id
        assert payload["balance"] == 1500
        assert len(payload["transactions"]) == 1
