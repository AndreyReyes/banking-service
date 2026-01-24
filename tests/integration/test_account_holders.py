from pathlib import Path

from fastapi.testclient import TestClient

from app.db import session as db_session
from app.main import create_app
from tests.integration.utils import (
    apply_migrations,
    configure_test_db,
    create_user,
    login,
)


def test_account_holder_create_read_list_requires_auth(
    tmp_path: Path, monkeypatch
) -> None:
    database_url = configure_test_db(tmp_path, monkeypatch, "holders")
    apply_migrations(database_url)
    app = create_app()

    SessionLocal = db_session.get_sessionmaker()
    with SessionLocal() as session:
        create_user(session, "ada@example.com", "supersecure123")
        session.commit()

    with TestClient(app) as client:
        tokens = login(client, "ada@example.com", "supersecure123")

        unauthenticated = client.get("/v1/account-holders")
        assert unauthenticated.status_code == 401

        create_response = client.post(
            "/v1/account-holders",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "first_name": "Ada",
                "last_name": "Lovelace",
                "dob": "1990-01-01",
            },
        )
        assert create_response.status_code == 201
        holder_id = create_response.json()["id"]

        list_response = client.get(
            "/v1/account-holders",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        get_response = client.get(
            f"/v1/account-holders/{holder_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert get_response.status_code == 200
        assert get_response.json()["id"] == holder_id
