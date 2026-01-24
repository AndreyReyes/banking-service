from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.account_holders import AccountHolderCreate, AccountHolderRead
from app.services.account_holder_service import AccountHolderService


router = APIRouter(prefix="/v1/account-holders", tags=["account-holders"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AccountHolderRead)
def create_account_holder(
    payload: AccountHolderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AccountHolderRead:
    service = AccountHolderService(session)
    try:
        holder = service.create_for_user(
            current_user, payload.first_name, payload.last_name, payload.dob
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return holder


@router.get("", response_model=list[AccountHolderRead])
def list_account_holders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[AccountHolderRead]:
    service = AccountHolderService(session)
    return service.list_for_user(current_user)


@router.get("/{holder_id}", response_model=AccountHolderRead)
def get_account_holder(
    holder_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> AccountHolderRead:
    service = AccountHolderService(session)
    holder = service.get_for_user(current_user, holder_id)
    if not holder:
        raise HTTPException(status_code=404, detail="account holder not found")
    return holder
