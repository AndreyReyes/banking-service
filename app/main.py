from fastapi import FastAPI

from app.api.routes.account_holders import router as account_holders_router
from app.api.routes.accounts import router as accounts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.cards import router as cards_router
from app.api.routes.health import router as health_router
from app.api.routes.statements import router as statements_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.transfers import router as transfers_router
from app.core.config import get_settings
from app.core.errors import add_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import assert_db_healthy


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Banking Service",
        version="0.1.0",
    )

    app.add_middleware(RequestLoggingMiddleware)
    add_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(account_holders_router)
    app.include_router(accounts_router)
    app.include_router(transactions_router)
    app.include_router(transfers_router)
    app.include_router(cards_router)
    app.include_router(statements_router)

    @app.on_event("startup")
    def _startup_health_check() -> None:
        assert_db_healthy()

    return app


app = create_app()
