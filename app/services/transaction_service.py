from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Account, Transaction, User


class TransactionService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def deposit(
        self, user: User, account: Account, amount: int, currency: str
    ) -> Transaction:
        self._ensure_owner(user, account)
        self._ensure_currency(account, currency)

        account.balance += amount
        transaction = Transaction(
            account_id=account.id,
            type="deposit",
            amount=amount,
            currency=currency,
        )
        self._session.add(transaction)
        self._session.flush()
        return transaction

    def withdraw(
        self, user: User, account: Account, amount: int, currency: str
    ) -> Transaction:
        self._ensure_owner(user, account)
        self._ensure_currency(account, currency)

        if account.balance - amount < 0:
            raise ValueError("insufficient funds")

        account.balance -= amount
        transaction = Transaction(
            account_id=account.id,
            type="withdrawal",
            amount=amount,
            currency=currency,
        )
        self._session.add(transaction)
        self._session.flush()
        return transaction

    def _ensure_owner(self, user: User, account: Account) -> None:
        if account.holder.user_id != user.id:
            raise ValueError("account not accessible")

    def _ensure_currency(self, account: Account, currency: str) -> None:
        if account.currency != currency:
            raise ValueError("currency mismatch")
