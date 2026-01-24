from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, SignupRequest


def test_signup_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        SignupRequest(
            email="not-an-email",
            password="supersecure123",
            first_name="Ada",
            last_name="Lovelace",
            dob=date(1990, 1, 1),
        )


def test_signup_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        SignupRequest(
            email="ada@example.com",
            password="short",
            first_name="Ada",
            last_name="Lovelace",
            dob=date(1990, 1, 1),
        )


def test_signup_rejects_future_dob() -> None:
    with pytest.raises(ValidationError):
        SignupRequest(
            email="ada@example.com",
            password="supersecure123",
            first_name="Ada",
            last_name="Lovelace",
            dob=date.today() + timedelta(days=1),
        )


def test_signup_accepts_valid_payload() -> None:
    payload = SignupRequest(
        email="ada@example.com",
        password="supersecure123",
        first_name="Ada",
        last_name="Lovelace",
        dob=date(1990, 1, 1),
    )

    assert payload.email == "ada@example.com"


def test_signup_rejects_password_over_72_bytes() -> None:
    long_password = "a" * 73
    with pytest.raises(ValidationError):
        SignupRequest(
            email="ada@example.com",
            password=long_password,
            first_name="Ada",
            last_name="Lovelace",
            dob=date(1990, 1, 1),
        )


def test_login_rejects_password_over_72_bytes() -> None:
    long_password = "a" * 73
    with pytest.raises(ValidationError):
        LoginRequest(email="ada@example.com", password=long_password)
