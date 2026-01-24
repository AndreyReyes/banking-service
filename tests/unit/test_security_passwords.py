import pytest

from app.core.security import hash_password, verify_password


def test_hash_password_rejects_over_72_bytes() -> None:
    with pytest.raises(ValueError):
        hash_password("a" * 73)


def test_verify_password_rejects_over_72_bytes() -> None:
    assert verify_password("a" * 73, "$2b$12$invalidhash") is False
