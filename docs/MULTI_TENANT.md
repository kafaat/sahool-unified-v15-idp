# SAHOOL Multi-Tenant Architecture

## Overview

SAHOOL uses PostgreSQL Row-Level Security (RLS) for complete tenant isolation at the database level.

## How It Works

1. **Tenant Context**: Set via `SET app.current_tenant = 'tenant_id'`
2. **RLS Policies**: Automatically filter all queries by `tenant_id`
3. **NATS Headers**: Tenant ID propagated via message headers
4. **TenantAwareNATS**: Automatic tenant filtering on event subscriptions

## Usage

```python
from packages.platform_bootstrap.src.tenant import TenantContext, TenantAwareNATS

# Database-level tenant isolation
async with TenantContext(tenant_id="tenant_abc", db_pool=pool):
    # All queries automatically filtered by tenant
    fields = await conn.fetch("SELECT * FROM fields")
    # Only returns fields for tenant_abc

# NATS-level tenant isolation
tenant_nats = TenantAwareNATS(event_bus, tenant_id="tenant_abc")
await tenant_nats.publish_event("field", "created", {"name": "North Field"})
```

## Security

- No tenant can access another tenant's data
- Enforced at database level (bypasses application bugs)
- 7 tables covered: fields, sensors, irrigation_schedules, ndvi_data, weather_data, marketplace_listings, chat_messages
- Admin bypass via `sahool_admin` role (audit-logged)
