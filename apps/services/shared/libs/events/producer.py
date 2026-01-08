"""
SAHOOL Event Producer
Helper for producing events with schema validation
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from shared.libs.outbox.models import OutboxEvent

from .envelope import EventEnvelope
from .schema_registry import SchemaRegistry

logger = logging.getLogger(__name__)

# Singleton registry instance (loaded once)
_registry: SchemaRegistry | None = None


def get_registry() -> SchemaRegistry:
    """Get or load the schema registry"""
    global _registry
    if _registry is None:
        _registry = SchemaRegistry.load()
    return _registry


def reload_registry() -> SchemaRegistry:
    """Force reload of the schema registry (useful for testing)"""
    global _registry
    _registry = SchemaRegistry.load()
    return _registry


def enqueue_event(
    db: Session,
    *,
    event_type: str,
    schema_ref: str,
    tenant_id: UUID,
    correlation_id: UUID,
    producer: str,
    payload: dict[str, Any],
    event_version: int = 1,
) -> UUID:
    """
    Enqueue an event to the outbox with schema validation.

    This function:
    1. Validates that schema_ref exists in registry
    2. Validates payload against the schema
    3. Creates an EventEnvelope
    4. Writes to outbox table

    Args:
        db: SQLAlchemy session (should be same transaction as business data)
        event_type: Event type (e.g., 'field.created')
        schema_ref: Schema reference (e.g., 'events.field.created:v1')
        tenant_id: Tenant UUID
        correlation_id: Correlation ID for tracing
        producer: Producing service/domain name
        payload: Event payload (must match schema)
        event_version: Schema version (default: 1)

    Returns:
        UUID of the created outbox event

    Raises:
        KeyError: If schema_ref is not registered
        jsonschema.ValidationError: If payload doesn't match schema
    """
    registry = get_registry()

    # Validate schema_ref exists
    entry = registry.entry(schema_ref)
    logger.debug(f"Found schema entry: {entry.ref}")

    # Validate payload against schema
    registry.validate(schema_ref, payload)
    logger.debug(f"Payload validated against {schema_ref}")

    # Create envelope
    envelope = EventEnvelope(
        event_type=event_type,
        event_version=event_version,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        schema_ref=schema_ref,
        producer=producer,
        payload=payload,
    )

    # Create outbox row
    row = OutboxEvent(
        event_type=envelope.event_type,
        event_version=envelope.event_version,
        schema_ref=envelope.schema_ref,
        tenant_id=envelope.tenant_id,
        correlation_id=envelope.correlation_id,
        payload_json=envelope.model_dump_json(),
    )

    db.add(row)
    db.flush()  # Get the ID without committing

    logger.info(f"Enqueued event {row.id} type={event_type} schema={schema_ref} tenant={tenant_id}")

    return row.id


def create_event_payload(
    schema_ref: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create and validate an event payload.

    Useful for constructing payloads before enqueuing.

    Args:
        schema_ref: Schema reference
        **kwargs: Payload fields

    Returns:
        Validated payload dictionary

    Raises:
        KeyError: If schema_ref is not registered
        jsonschema.ValidationError: If payload doesn't match schema
    """
    registry = get_registry()
    registry.validate(schema_ref, kwargs)
    return kwargs


def validate_payload(schema_ref: str, payload: dict[str, Any]) -> bool:
    """
    Validate a payload without enqueuing.

    Args:
        schema_ref: Schema reference
        payload: Payload to validate

    Returns:
        True if valid

    Raises:
        KeyError: If schema_ref is not registered
        jsonschema.ValidationError: If payload doesn't match schema
    """
    registry = get_registry()
    registry.validate(schema_ref, payload)
    return True
