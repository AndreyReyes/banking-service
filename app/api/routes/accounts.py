from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.accounts import AccountCreate, AccountRead
from app.services.account_service import AccountService


router = APIRouter(prefix="/v1/accounts", tags=["accounts"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountRead)
def create_account(
    payload: AccountCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AccountRead:
    service = AccountService(session)
    try:
        account = service.create_for_user(current_user, payload.type, payload.currency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return account


@router.get("", response_model=list[AccountRead])
def list_accounts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[AccountRead]:
    service = AccountService(session)
    return service.list_for_user(current_user)


@router.get("/{account_id}", response_model=AccountRead)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AccountRead:
    service = AccountService(session)
    account = service.get_for_user(current_user, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="account not found")
    return account
