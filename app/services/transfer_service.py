from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Account, Transaction, Transfer, User


class TransferService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def transfer(
        self,
        user: User,
        from_account: Account,
        to_account: Account,
        amount: int,
        currency: str,
    ) -> Transfer:
        if from_account.holder.user_id != user.id:
            raise ValueError("account not accessible")
        if from_account.currency != currency or to_account.currency != currency:
            raise ValueError("currency mismatch")
        if from_account.balance - amount < 0:
            raise ValueError("insufficient funds")

        from_account.balance -= amount
        to_account.balance += amount

        transfer = Transfer(
            from_account_id=from_account.id,
            to_account_id=to_account.id,
            amount=amount,
            currency=currency,
        )
        self._session.add(transfer)
        self._session.add_all(
            [
                Transaction(
                    account_id=from_account.id,
                    type="transfer_out",
                    amount=amount,
                    currency=currency,
                ),
                Transaction(
                    account_id=to_account.id,
                    type="transfer_in",
                    amount=amount,
                    currency=currency,
                ),
            ]
        )
        self._session.flush()
        return transfer
