# SAHOOL Multi-Tenant Architecture

## Overview

SAHOOL uses PostgreSQL Row-Level Security (RLS) for complete tenant isolation at the database level.

## How It Works

1. **Tenant Context**: Set via `set_config('app.current_tenant', '<tenant_id>', false)`
2. **RLS Policies**: Automatically filter all queries by `tenant_id`
3. **Event Payload**: Tenant ID propagated via `tenant_id` field in the JSON event body
4. **TenantAwareNATS**: Automatic tenant filtering on event subscriptions

## Usage

```python
# Assuming packages/platform-bootstrap/src is on PYTHONPATH
from tenant import TenantContext, TenantAwareNATS

# Database-level tenant isolation
async with TenantContext(tenant_id="123e4567-e89b-12d3-a456-426614174000", db_pool=pool) as ctx:
    # All queries automatically filtered by tenant
    fields = await ctx.conn.fetch("SELECT * FROM fields")
    # Only returns fields for this tenant

# NATS-level tenant isolation
tenant_nats = TenantAwareNATS(event_bus, tenant_id="123e4567-e89b-12d3-a456-426614174000")
await tenant_nats.publish_event("field", "created", {"name": "North Field"})
```

## Security

- No tenant can access another tenant's data
- Enforced at database level (bypasses application bugs)
- 7 tables covered: fields, sensors, irrigation_schedules, ndvi_data, weather_data, marketplace_listings, chat_messages
- Admin bypass via `sahool_admin` role (audit-logged)
