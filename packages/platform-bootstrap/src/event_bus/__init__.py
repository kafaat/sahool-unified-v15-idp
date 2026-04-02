"""SAHOOL Event Bus - NATS JetStream client for service-to-service communication."""

from .nats_client import SAHOOLEventBus, EventMessage

__all__ = ["SAHOOLEventBus", "EventMessage"]
