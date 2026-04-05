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

        @staticmethod
        def _safe_extra(kw: dict[str, object]) -> dict[str, object] | None:
            """Wrap structlog-style kwargs under a single ``context`` key.

            stdlib logging reserves many ``LogRecord`` attribute names
            (e.g. ``message``, ``name``, ``args``).  Passing structlog kwargs
            directly via ``extra=kw`` can raise ``KeyError`` (overwriting a
            reserved attribute) or ``TypeError`` (unexpected keyword argument
            to ``_log()``).  Nesting them keeps the data accessible without
            conflicting with reserved attributes.
            """
            return {"context": kw} if kw else None

        # --- public API matching structlog usage in the knowledge module ---

        def debug(self, event: object = "", **kw: object) -> None:
            self._logger.debug(str(event), extra=self._safe_extra(kw))

        def info(self, event: object = "", **kw: object) -> None:
            self._logger.info(str(event), extra=self._safe_extra(kw))

        def warning(self, event: object = "", **kw: object) -> None:
            self._logger.warning(str(event), extra=self._safe_extra(kw))

        warn = warning

        def error(self, event: object = "", **kw: object) -> None:
            self._logger.error(str(event), extra=self._safe_extra(kw))

        def critical(self, event: object = "", **kw: object) -> None:
            self._logger.critical(str(event), extra=self._safe_extra(kw))

        def exception(self, event: object = "", **kw: object) -> None:
            self._logger.exception(str(event), extra=self._safe_extra(kw))

        def bind(self, **kw: object) -> _StdlibLoggerAdapter:
            """No-op bind — structlog bind() returns a new logger with bound
            context; here we simply return *self* to keep the call-chain
            working without structlog."""
            return self

    def get_logger(name: str | None = None) -> _StdlibLoggerAdapter:  # type: ignore[misc]
        return _StdlibLoggerAdapter(logging.getLogger(name))
