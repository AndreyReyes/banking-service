from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Account, User
from app.db.session import get_db
from app.schemas.transactions import TransactionCreate, TransactionRead
from app.services.transaction_service import TransactionService


router = APIRouter(prefix="/v1/transactions", tags=["transactions"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransactionRead)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TransactionRead:
    account = session.get(Account, payload.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")

    service = TransactionService(session)
    try:
        if payload.type == "deposit":
            transaction = service.deposit(
                current_user, account, payload.amount, payload.currency
            )
        elif payload.type == "withdrawal":
            transaction = service.withdraw(
                current_user, account, payload.amount, payload.currency
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="unsupported transaction type",
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return transaction
