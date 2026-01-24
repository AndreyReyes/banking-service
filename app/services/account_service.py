from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Account, AccountHolder, User


class AccountService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_for_user(self, user: User, account_type: str, currency: str) -> Account:
        holder = self._get_holder(user)
        if not holder:
            raise ValueError("account holder not found")

        account = Account(
            holder_id=holder.id,
            type=account_type,
            currency=currency,
            balance=0,
            status="active",
        )
        self._session.add(account)
        self._session.flush()
        return account

    def list_for_user(self, user: User) -> list[Account]:
        holder = self._get_holder(user)
        if not holder:
            return []
        return list(
            self._session.scalars(select(Account).where(Account.holder_id == holder.id))
        )

    def get_for_user(self, user: User, account_id: int) -> Account | None:
        holder = self._get_holder(user)
        if not holder:
            return None
        return self._session.scalar(
            select(Account).where(
                Account.holder_id == holder.id, Account.id == account_id
            )
        )

    def _get_holder(self, user: User) -> AccountHolder | None:
        return self._session.scalar(
            select(AccountHolder).where(AccountHolder.user_id == user.id)
        )
