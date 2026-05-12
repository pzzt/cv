"""
Logging configuration for the application.

Provides structured logging setup for:
- Development (pretty console output)
- Production (JSON for log aggregation)
- Docker environments (structured logs)

Why custom logging setup:
- JSON logs for production/log aggregation
- Consistent format across all modules
- Easy to parse and analyze
"""

import json
import logging
import sys
from enum import StrEnum


class LogFormat(StrEnum):
    """Supported log formats."""

    JSON = "json"
    PLAIN = "plain"


class JsonFormatter(logging.Formatter):
    """
    Structured JSON log formatter.

    Outputs logs as JSON for easy parsing by log aggregation systems.
    Includes standard fields plus any extra context.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO", log_format: LogFormat = LogFormat.PLAIN) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type (json or plain)
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Set formatter
    if log_format == LogFormat.JSON:
        formatter: logging.Formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure uvicorn loggers
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Suppress noisy loggers
    logging.getLogger("markdown").setLevel(logging.WARNING)
