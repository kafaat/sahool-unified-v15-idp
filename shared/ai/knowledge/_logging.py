# Centralized logging for knowledge module.
# Falls back to stdlib logging when structlog is not installed (e.g. in tests).
from __future__ import annotations

try:
    import structlog

    get_logger = structlog.get_logger
except ModuleNotFoundError:  # pragma: no cover
    import logging

    def get_logger(name: str | None = None) -> logging.Logger:  # type: ignore[misc]
        return logging.getLogger(name)
