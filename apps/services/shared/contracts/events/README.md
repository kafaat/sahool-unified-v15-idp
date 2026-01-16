# Event Contracts

> **Version:** 16.0.0
> **Last Updated:** December 2025

## Overview

This directory contains the single source of truth for all event schemas in the SAHOOL platform.

## Rules

1. **All events MUST have a schema** in this folder
2. **Breaking changes require a new version** (v2, v3...)
3. **Producers must attach `schema_ref`** in the event envelope
4. **Consumers validate payload** against the schema before processing

## Schema Registry

The `registry.json` file contains metadata about all registered event schemas:

```json
{
  "schemas": [
    {
      "ref": "events.field.created:v1",
      "file": "field.created.v1.json",
      "topic": "field.created",
      "version": 1,
      "owner": "field_suite",
      "breaking_policy": "new_version"
    }
  ]
}
```

## Adding a New Event

1. Create a JSON Schema file: `{domain}.{event}.v1.json`
2. Add entry to `registry.json`
3. Run `make event-catalog` to update documentation
4. Create tests in `tests/integration/test_events.py`

## Schema Versioning

- **Backward Compatible Changes**: Add optional fields (same version)
- **Breaking Changes**: Create new version file (e.g., `field.created.v2.json`)

### Examples of Breaking Changes

- Removing a required field
- Changing field type
- Renaming a field
- Adding new required field

## Validation

Events are validated at:

1. **Enqueue time** - Before adding to outbox
2. **Publish time** - Before sending to message bus
3. **Consume time** - Before processing

## Event Envelope

All events are wrapped in a standard envelope:

```python
{
    "event_id": "uuid",
    "event_type": "field.created",
    "event_version": 1,
    "tenant_id": "uuid",
    "correlation_id": "uuid",
    "occurred_at": "2025-01-01T00:00:00Z",
    "schema_ref": "events.field.created:v1",
    "producer": "field_suite",
    "payload": { ... }
}
```

## Owners

| Owner         | Events                   |
| ------------- | ------------------------ |
| field_suite   | field._, farm._, crop.\* |
| advisor       | advisor.\*               |
| kernel_domain | user._, tenant._         |
