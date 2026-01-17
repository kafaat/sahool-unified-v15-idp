# SAHOOL Shared Contracts

This directory contains all shared contracts between services.

## Purpose

- **Single Source of Truth**: All events and API schemas defined here
- **Prevent Drift**: Services must import from here, not define locally
- **Documentation**: Auto-generated docs from schemas

## Structure

```
shared/contracts/
├── events/          # Event schemas (NATS messages)
├── openapi/         # OpenAPI specifications
└── README.md        # This file
```

## Rules

1. **No inline definitions**: Events/APIs must be defined here first
2. **Versioning**: Use semantic versioning for breaking changes
3. **Validation**: All contracts must have JSON Schema
4. **Backward compatibility**: New fields must be optional

## Usage

### Python Services

```python
from shared.contracts.events import FieldUpdatedEvent

event = FieldUpdatedEvent(field_id="123", ndvi=0.65)
await nats.publish("field.updated", event.json())
```

### TypeScript Services

```typescript
import { FieldUpdatedEvent } from "@sahool/contracts";

const event: FieldUpdatedEvent = {
  fieldId: "123",
  ndvi: 0.65,
};
```

## Adding New Contracts

1. Create schema file in appropriate directory
2. Add to `__init__.py` exports
3. Update documentation
4. Run `make contracts-validate`
