from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import User
from app.db.session import get_db, get_sessionmaker
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    RefreshRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _get_request_context(request: Request) -> tuple[str, str]:
    ip_address = request.client.host if request.client else "unknown"
    device_id = request.headers.get("X-Device-Id", "unknown")
    return ip_address, device_id


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
def signup(
    payload: SignupRequest,
    request: Request,
    session: Session = Depends(get_db),
) -> SignupResponse:
    service = AuthService(session)
    ip_address, device_id = _get_request_context(request)

    try:
        with session.begin():
            user, holder = service.create_user_with_holder(
                email=payload.email,
                password=payload.password,
                first_name=payload.first_name,
                last_name=payload.last_name,
                dob=payload.dob,
            )
            service.write_audit_log(
                user_id=user.id,
                event_type="signup",
                status="success",
                ip_address=ip_address,
                device_id=device_id,
            )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return SignupResponse(user=user, account_holder=holder)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    request: Request,
    session: Session = Depends(get_db),
) -> TokenResponse:
    service = AuthService(session)
    ip_address, device_id = _get_request_context(request)

    user = service.authenticate_user(payload.email, payload.password)
    if not user:
        SessionLocal = get_sessionmaker()
        with SessionLocal.begin() as audit_session:
            AuthService(audit_session).write_audit_log(
                user_id=None,
                event_type="login",
                status="failure",
                ip_address=ip_address,
                device_id=device_id,
                metadata={"email": payload.email},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials"
        )

    tokens = service.issue_tokens(user, ip_address, device_id)

    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    request: Request,
) -> TokenResponse:
    SessionLocal = get_sessionmaker()
    ip_address, device_id = _get_request_context(request)

    tokens: dict | None = None
    with SessionLocal.begin() as refresh_session:
        tokens = AuthService(refresh_session).rotate_refresh_token(
            payload.refresh_token, ip_address, device_id
        )

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token"
        )

    return TokenResponse(**tokens)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(id=current_user.id, email=current_user.email)
