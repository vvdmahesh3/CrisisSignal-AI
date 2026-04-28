"""
CrisisSignal AI — Structured Logging
Phase 4: Replaces print() statements with a properly configured logger.

Usage:
    from app.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Alert created", extra={"alert_id": 42})

In production (JSON_LOGS=true), every log line is a single JSON object
that log aggregators (Datadog, GCP Cloud Logging, AWS CloudWatch) can parse.
"""

import os
import json
import logging
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects.
    Compatible with Cloud Logging, Datadog, Loki, etc.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include any extra fields passed via extra={}
        for key, value in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text",
                "filename", "funcName", "id", "levelname", "levelno",
                "lineno", "message", "module", "msecs", "msg", "name",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "thread", "threadName",
            ):
                log_obj[key] = value

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def configure_logging(app=None):
    """
    Configure the root logger for the application.

    - Development: human-readable coloured output to stdout
    - Production (JSON_LOGS=true): JSON format to stdout for log aggregators

    Call once from create_app().
    """
    use_json = os.getenv("JSON_LOGS", "false").lower() == "true"
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove default handlers (avoids duplicate log lines in gunicorn)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if use_json:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))

    root_logger.addHandler(handler)

    # Quieten noisy third-party loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.WARNING)
    logging.getLogger("engineio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if app:
        app.logger.setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Use this in every module instead of print()."""
    return logging.getLogger(name)
