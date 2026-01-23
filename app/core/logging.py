import logging
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars


def configure_logging(log_level: str = "INFO") -> None:
    resolved_level = logging._nameToLevel.get(log_level.upper(), logging.INFO)

    logging.basicConfig(level=resolved_level, format="%(message)s")

    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(resolved_level),
        cache_logger_on_first_use=True,
    )


def get_logger(**context: Any) -> structlog.BoundLogger:
    return structlog.get_logger().bind(**context)
