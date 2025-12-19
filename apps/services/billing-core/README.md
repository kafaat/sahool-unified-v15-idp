# billing-core

Tenant billing + plan + quota service (SaaS control-plane).

Responsibilities:
- tenants
- plans
- quota definitions
- usage accounting (from events/metrics)
- enforcement signals (rate limits, feature entitlements)

This is a skeleton intended to integrate with your existing gateway + auth.

Endpoints (example):
- POST /tenants
- POST /plans
- POST /tenants/{id}/plan
- GET  /tenants/{id}/quota
- POST /usage/events (ingest usage signals)
