from __future__ import annotations

import secrets

from sqlalchemy.orm import Session

from app.db.models import Account, Card, User


class CardService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def issue_card(self, user: User, account: Account, card_type: str) -> Card:
        if account.holder.user_id != user.id:
            raise ValueError("account not accessible")

        last4 = str(secrets.randbelow(10000)).zfill(4)
        card = Card(
            account_id=account.id,
            type=card_type,
            last4=last4,
            status="active",
        )
        self._session.add(card)
        self._session.flush()
        return card
