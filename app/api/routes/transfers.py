from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Account, User
from app.db.session import get_db
from app.schemas.transfers import TransferCreate, TransferRead
from app.services.transfer_service import TransferService


router = APIRouter(prefix="/v1/transfers", tags=["transfers"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TransferRead)
def create_transfer(
    payload: TransferCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> TransferRead:
    from_account = session.get(Account, payload.from_account_id)
    to_account = session.get(Account, payload.to_account_id)
    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="account not found")

    service = TransferService(session)
    try:
        with session.begin_nested():
            transfer = service.transfer(
                current_user,
                from_account,
                to_account,
                payload.amount,
                payload.currency,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return transfer
