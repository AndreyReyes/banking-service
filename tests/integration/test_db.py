from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.db import session as db_session


def test_db_session_connectivity(tmp_path: Path) -> None:
    db_file = tmp_path / "connectivity.db"
    database_url = f"sqlite:///{db_file}"
    engine = db_session.create_engine_from_url(database_url)

    assert db_session.check_db_health(engine) is True


def test_alembic_migration_applies_to_empty_db(tmp_path: Path) -> None:
    db_file = tmp_path / "alembic.db"
    database_url = f"sqlite:///{db_file}"
    config = Config("alembic.ini")
    config.set_main_option("script_location", "app/db/migrations")
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")

    engine = db_session.create_engine_from_url(database_url)
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name='alembic_version'"
            )
        )
        assert result.fetchone() is not None
