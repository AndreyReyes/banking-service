from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import get_settings
from app.db.models import AccountHolder, AuditLog, RefreshToken, User


class AuthService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._settings = get_settings()

    def create_user_with_holder(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        dob,
    ) -> tuple[User, AccountHolder]:
        existing = self._session.scalar(select(User).where(User.email == email))
        if existing:
            raise ValueError("email already registered")

        hashed_password = security.hash_password(password)
        user = User(email=email, hashed_password=hashed_password)
        holder = AccountHolder(
            user=user,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
        )
        self._session.add_all([user, holder])
        self._session.flush()
        return user, holder

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self._session.scalar(select(User).where(User.email == email))
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

    def issue_tokens(self, user: User, ip_address: str, device_id: str) -> dict:
        access_token, access_expires_at = security.create_access_token(
            user.id, user.email
        )

        refresh_token = security.create_refresh_token()
        refresh_token_hash = security.hash_refresh_token(refresh_token)
        now = datetime.now(timezone.utc)
        refresh_expires_at = now + timedelta(days=self._settings.refresh_token_ttl_days)

        refresh_row = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            family_id=str(uuid4()),
            issued_at=now,
            expires_at=refresh_expires_at,
            ip_address=ip_address,
            device_id=device_id,
        )
        self._session.add(refresh_row)
        self._write_audit_log(
            user_id=user.id,
            event_type="login",
            status="success",
            ip_address=ip_address,
            device_id=device_id,
        )
        self._session.flush()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": int((access_expires_at - now).total_seconds()),
        }

    def rotate_refresh_token(
        self, token: str, ip_address: str, device_id: str
    ) -> dict | None:
        token_hash = security.hash_refresh_token(token)
        refresh_row = self._session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        if not refresh_row:
            return None
        if refresh_row.revoked_at is not None:
            return None
        now = datetime.now(timezone.utc)
        expires_at = self._normalize_timestamp(refresh_row.expires_at)
        if expires_at <= now:
            refresh_row.revoked_at = now
            return None

        refresh_row.revoked_at = now
        user = self._session.get(User, refresh_row.user_id)
        if not user:
            return None

        access_token, access_expires_at = security.create_access_token(
            user.id, user.email
        )
        new_refresh_token = security.create_refresh_token()
        new_refresh_hash = security.hash_refresh_token(new_refresh_token)
        refresh_expires_at = now + timedelta(days=self._settings.refresh_token_ttl_days)

        new_refresh_row = RefreshToken(
            user_id=user.id,
            token_hash=new_refresh_hash,
            family_id=refresh_row.family_id,
            issued_at=now,
            expires_at=refresh_expires_at,
            ip_address=ip_address,
            device_id=device_id,
        )
        self._session.add(new_refresh_row)
        self._write_audit_log(
            user_id=user.id,
            event_type="token_refresh",
            status="success",
            ip_address=ip_address,
            device_id=device_id,
        )
        self._session.flush()

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "expires_in": int((access_expires_at - now).total_seconds()),
        }

    def _normalize_timestamp(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

    def write_audit_log(
        self,
        user_id: int | None,
        event_type: str,
        status: str,
        ip_address: str,
        device_id: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        self._write_audit_log(
            user_id=user_id,
            event_type=event_type,
            status=status,
            ip_address=ip_address,
            device_id=device_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
        )

    def _write_audit_log(
        self,
        user_id: int | None,
        event_type: str,
        status: str,
        ip_address: str,
        device_id: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        audit_log = AuditLog(
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            ip_address=ip_address,
            device_id=device_id,
            meta=metadata,
        )
        self._session.add(audit_log)
