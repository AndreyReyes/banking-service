from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Account, User
from app.db.session import get_db
from app.schemas.cards import CardCreate, CardRead
from app.services.card_service import CardService


router = APIRouter(prefix="/v1/cards", tags=["cards"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CardRead)
def issue_card(
    payload: CardCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> CardRead:
    account = session.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")

    service = CardService(session)
    try:
        card = service.issue_card(current_user, account, payload.type)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return card
