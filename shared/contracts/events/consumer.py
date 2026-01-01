"""
Event Consumer
==============

Provides a unified interface for consuming domain events.
"""

import json
import logging
from typing import Callable, Dict, Type
from .base import BaseEvent
from .registry import EventRegistry

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Consumes domain events from the message broker.

    Usage:
        consumer = EventConsumer(nats_client)

        @consumer.on(FieldCreatedEvent)
        async def handle_field_created(event: FieldCreatedEvent):
            print(f"Field created: {event.field_id}")

        await consumer.start()
    """

    def __init__(self, nats_client=None, service_name: str = "unknown"):
        self._nats = nats_client
        self._service_name = service_name
        self._handlers: Dict[str, Callable] = {}
        self._subscriptions = []

    def on(self, event_class: Type[BaseEvent]):
        """Decorator to register an event handler"""

        def decorator(handler: Callable):
            event_type = event_class.EVENT_TYPE
            self._handlers[event_type] = (event_class, handler)
            logger.info(f"Registered handler for {event_type}")
            return handler

        return decorator

    def register(self, event_type: str, handler: Callable):
        """Programmatically register an event handler"""
        event_class = EventRegistry.get_event_class(event_type)
        if event_class:
            self._handlers[event_type] = (event_class, handler)

    async def start(self):
        """Start consuming events"""
        if not self._nats:
            logger.warning("No NATS client - consumer not started")
            return

        for event_type, (event_class, handler) in self._handlers.items():
            subject = f"sahool.events.{event_type}"

            async def message_handler(msg, ec=event_class, h=handler):
                try:
                    data = json.loads(msg.data.decode())
                    event = ec.from_dict(data)
                    await h(event)
                except Exception as e:
                    logger.error(f"Error handling event: {e}")

            sub = await self._nats.subscribe(subject, cb=message_handler)
            self._subscriptions.append(sub)
            logger.info(f"Subscribed to {subject}")

    async def stop(self):
        """Stop consuming events"""
        for sub in self._subscriptions:
            await sub.unsubscribe()
        self._subscriptions.clear()
        logger.info("Consumer stopped")
