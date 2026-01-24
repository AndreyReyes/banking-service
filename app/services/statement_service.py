from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Account, Transaction, User


class StatementService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_statement(self, user: User, account: Account) -> list[Transaction]:
        if account.holder.user_id != user.id:
            raise ValueError("account not accessible")
        return list(
            self._session.scalars(
                select(Transaction)
                .where(Transaction.account_id == account.id)
                .order_by(Transaction.created_at.desc())
            )
        )
