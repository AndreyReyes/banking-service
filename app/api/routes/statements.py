from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Account, User
from app.db.session import get_db
from app.schemas.statements import StatementResponse
from app.services.statement_service import StatementService


router = APIRouter(prefix="/v1/statements", tags=["statements"])


@router.get("/{account_id}", response_model=StatementResponse)
def get_statement(
    account_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> StatementResponse:
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")

    service = StatementService(session)
    try:
        transactions = service.get_statement(current_user, account)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return StatementResponse(
        account_id=account.id,
        currency=account.currency,
        balance=account.balance,
        generated_at=datetime.now(timezone.utc),
        transactions=transactions,
    )
