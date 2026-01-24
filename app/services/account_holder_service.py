from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AccountHolder, User


class AccountHolderService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_for_user(
        self, user: User, first_name: str, last_name: str, dob
    ) -> AccountHolder:
        existing = self._session.scalar(
            select(AccountHolder).where(AccountHolder.user_id == user.id)
        )
        if existing:
            raise ValueError("account holder already exists")

        holder = AccountHolder(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            dob=dob,
        )
        self._session.add(holder)
        self._session.flush()
        return holder

    def list_for_user(self, user: User) -> list[AccountHolder]:
        holder = self._session.scalar(
            select(AccountHolder).where(AccountHolder.user_id == user.id)
        )
        return [holder] if holder else []

    def get_for_user(self, user: User, holder_id: int) -> AccountHolder | None:
        return self._session.scalar(
            select(AccountHolder).where(
                AccountHolder.user_id == user.id, AccountHolder.id == holder_id
            )
        )
