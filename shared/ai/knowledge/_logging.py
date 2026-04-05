# Centralized logging for knowledge module.
# Falls back to stdlib logging when structlog is not installed (e.g. in tests).
from __future__ import annotations

try:
    import structlog

    get_logger = structlog.get_logger
except ModuleNotFoundError:  # pragma: no cover
    import logging

    class _StdlibLoggerAdapter:
        """Thin adapter that accepts structlog-style ``logger.info(event, **kw)``
        calls and forwards them to a stdlib ``logging.Logger``, packing the
        extra keyword arguments into the *extra* dict so they don't raise
        ``TypeError: Logger._log() got an unexpected keyword argument ...``.
        """

        def __init__(self, logger: logging.Logger) -> None:
            self._logger = logger

        # --- public API matching structlog usage in the knowledge module ---

        def debug(self, event: object = "", **kw: object) -> None:
            self._logger.debug(str(event), extra=kw if kw else None)

        def info(self, event: object = "", **kw: object) -> None:
            self._logger.info(str(event), extra=kw if kw else None)

        def warning(self, event: object = "", **kw: object) -> None:
            self._logger.warning(str(event), extra=kw if kw else None)

        warn = warning

        def error(self, event: object = "", **kw: object) -> None:
            self._logger.error(str(event), extra=kw if kw else None)

        def critical(self, event: object = "", **kw: object) -> None:
            self._logger.critical(str(event), extra=kw if kw else None)

        def exception(self, event: object = "", **kw: object) -> None:
            self._logger.exception(str(event), extra=kw if kw else None)

        def bind(self, **kw: object) -> _StdlibLoggerAdapter:
            """No-op bind — structlog bind() returns a new logger with bound
            context; here we simply return *self* to keep the call-chain
            working without structlog."""
            return self

    def get_logger(name: str | None = None) -> _StdlibLoggerAdapter:  # type: ignore[misc]
        return _StdlibLoggerAdapter(logging.getLogger(name))
