"""Logging configuration for JiraLite."""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure logging for JiraLite.

    Args:
        debug: Enable debug-level logging
    """
    level = logging.DEBUG if debug else logging.INFO

    # Create formatter that doesn't log secrets
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler - always output to stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    # Ensure errors always show
    handler.setLevel(logging.ERROR)

    # Configure root logger
    root_logger = logging.getLogger("jiralite")
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Add second handler for debug output when debug is enabled
    if debug:
        debug_handler = logging.StreamHandler(sys.stderr)
        debug_handler.setFormatter(formatter)
        debug_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(debug_handler)

    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


class SecureFilter(logging.Filter):
    """Filter that redacts sensitive information from log records."""

    REDACT_KEYS = {"authorization", "api_token", "password", "secret"}

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record, redacting sensitive data.

        Args:
            record: Log record to filter

        Returns:
            True (always allow record)
        """
        # Redact message if it contains sensitive keywords
        message = record.getMessage().lower()
        for key in self.REDACT_KEYS:
            if key in message:
                record.msg = "[REDACTED]"
                record.args = ()
                break

        return True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance with secure filtering
    """
    logger = logging.getLogger(f"jiralite.{name}")
    logger.addFilter(SecureFilter())
    return logger
