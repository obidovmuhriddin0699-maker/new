"""Structured logging (JSON lines) with a per-request ID."""

import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Keys that must never appear in logs, even if passed via ``extra``.
_REDACT_KEYS = {"password", "token", "access_token", "refresh_token", "secret", "authorization"}
_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        for key, value in record.__dict__.items():
            if key in _RESERVED or key.startswith("_"):
                continue
            payload[key] = "***" if key.lower() in _REDACT_KEYS else value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


# access_token / client_secret / fb_exchange_token values in URLs or bodies.
_SECRET_PARAM = re.compile(
    r"((?:access_token|client_secret|fb_exchange_token|input_token)=)[^&\s\"']+", re.IGNORECASE
)
_HTTP_LOGGERS = ("httpx", "httpcore", "urllib3", "aiogram")


class SecretRedactionFilter(logging.Filter):
    """Masks token-like query parameters in a log message, whatever the log level."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001 - never break logging
            return True
        redacted = _SECRET_PARAM.sub(r"\1***", message)
        if redacted != message:
            record.msg, record.args = redacted, None
        return True


_FILTER = SecretRedactionFilter()


def install_secret_filters() -> None:
    """Idempotent. Installed on import of the Meta integration and by configure_logging,
    so API, Celery worker and CLI processes are all covered."""
    for name in _HTTP_LOGGERS:
        logger = logging.getLogger(name)
        if _FILTER not in logger.filters:
            logger.addFilter(_FILTER)


def configure_logging(level: str = "INFO", json_output: bool = True) -> None:
    handler = logging.StreamHandler(sys.stdout)
    if json_output:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    # HTTP client libraries log full request URLs at INFO. Meta's API takes tokens and
    # the app secret as query parameters, so these loggers must never log at INFO.
    for noisy in _HTTP_LOGGERS:
        logging.getLogger(noisy).setLevel(logging.WARNING)
    install_secret_filters()
    # uvicorn access logs are replaced by our request middleware
    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False
