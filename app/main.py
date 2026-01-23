from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import get_settings
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
    app.include_router(health_router)

    @app.on_event("startup")
    def _startup_health_check() -> None:
        assert_db_healthy()

    return app


app = create_app()
