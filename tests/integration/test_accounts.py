from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.integration.utils import (
    apply_migrations,
    configure_test_db,
    login,
    signup,
)


def test_accounts_create_view_list(tmp_path: Path, monkeypatch) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "accounts")
    apply_migrations(database_url)
    app = create_app()

    with TestClient(app) as client:
        signup(client, "ada@example.com", "supersecure123")
        tokens = login(client, "ada@example.com", "supersecure123")

        create_response = client.post(
            "/v1/accounts",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={"type": "checking", "currency": "USD"},
        )
        assert create_response.status_code == 201
        account_id = create_response.json()["id"]

        list_response = client.get(
            "/v1/accounts",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        get_response = client.get(
            f"/v1/accounts/{account_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert get_response.status_code == 200
        assert get_response.json()["id"] == account_id
