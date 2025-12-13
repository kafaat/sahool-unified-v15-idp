# ADR-004: Event Type = NATS Subject

## Status
Accepted

## Date
2025-01-01

## Context

In event-driven systems, there are typically two concepts:
- **event_type**: The type field in the event payload
- **subject**: The routing address in the message broker

Having these as separate values causes:
1. Complexity in routing logic
2. Potential mismatches
3. Debugging difficulties
4. Team confusion

## Decision

**event_type == NATS subject**

```python
# The event_type IS the NATS subject
event = create_event(
    event_type="astro.star.rising",  # This IS the NATS subject
    payload={...}
)

# Publishing
await nats.publish(
    subject=event["event_type"],  # Same value
    payload=event
)
```

### Naming Convention

```
<domain>.<entity>.<action>

Examples:
- astro.star.rising
- weather.anomaly.detected
- crop.stage.changed
- task.created
```

### Wildcard Subscriptions

```python
# Subscribe to all astro events
consumer.subscribe("astro.*.*")

# Subscribe to all rising events
consumer.subscribe("*.*.rising")

# Subscribe to specific event
consumer.subscribe("astro.star.rising")
```

## Consequences

### Positive
- ✅ Single source of truth for routing
- ✅ Easy debugging (grep by event_type)
- ✅ Clear subscription patterns
- ✅ No mapping layer needed

### Negative
- ❌ Cannot change event_type without changing routing
- ❌ Subject length limited by NATS

### Mitigations
- Schema versioning handles evolution: `schema_version: "2.0"`
- Keep event types concise (3 segments max)

## Implementation

See: `shared/events/base_event.py`

```python
@dataclass
class Event:
    event_type: str  # == NATS subject
    
    @property
    def subject(self) -> str:
        """NATS subject (same as event_type)"""
        return self.event_type
```

## Related
- ADR-001: Event Bus
- shared/events/base_event.py
