from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import (
    apply_migrations,
    configure_test_db,
    login,
    signup,
)


def test_issue_card_and_status(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "cards")
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

        card_response = client.post(
            "/v1/cards",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"account_id": account_id, "type": "virtual"},
        )
        assert card_response.status_code == 201
        assert card_response.json()["status"] == "active"
        assert card_response.json()["last4"]
