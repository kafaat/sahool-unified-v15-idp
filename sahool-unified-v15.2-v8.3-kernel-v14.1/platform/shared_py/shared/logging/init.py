from __future__ import annotations

import logging
import structlog


def configure_logging(service_name: str, log_level: str = "INFO") -> None:
    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)
    logging.basicConfig(level=level)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    return structlog.get_logger(name)


class EventLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name

    def published(self, event_type: str, **kwargs):
        logging.getLogger(self.service_name).info(
            "event_published %s %s", event_type, kwargs
        )

    def consumed(self, event_type: str, **kwargs):
        logging.getLogger(self.service_name).info(
            "event_consumed %s %s", event_type, kwargs
        )
