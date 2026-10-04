import json
import logging
import os
from datetime import datetime, timezone

try:
    import structlog  # type: ignore
except ImportError:  # local deterministic mode can still run
    structlog = None


class StdJsonLogger:
    def __init__(self, logger: logging.Logger, context: dict | None = None):
        self.logger = logger
        self.context = context or {}

    def bind(self, **kwargs):
        return StdJsonLogger(self.logger, {**self.context, **kwargs})

    def _write(self, level: int, event: str, **kwargs):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **self.context,
            **kwargs,
        }
        self.logger.log(level, json.dumps(payload, default=str))

    def info(self, event: str, **kwargs):
        self._write(logging.INFO, event, **kwargs)

    def exception(self, event: str, **kwargs):
        self._write(logging.ERROR, event, **kwargs)
        self.logger.exception(event)


def configure_logging() -> None:
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(message)s")
    if structlog is not None:
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso", utc=True),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
        )


def get_logger():
    if structlog is not None:
        return structlog.get_logger()
    return StdJsonLogger(logging.getLogger("techcv"))
