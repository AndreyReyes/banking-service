from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.core.logging import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._logger = get_logger()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )
        start_time = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = int((perf_counter() - start_time) * 1000)
            self._logger.exception(
                "request.failed",
                status_code=500,
                duration_ms=duration_ms,
            )
            clear_contextvars()
            raise

        duration_ms = int((perf_counter() - start_time) * 1000)
        response.headers["X-Request-Id"] = request_id
        self._logger.info(
            "request.completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        clear_contextvars()
        return response
