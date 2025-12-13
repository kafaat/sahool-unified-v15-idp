# Billing + Quotas (SaaS)

## What’s included
- `apps/billing-core/` skeleton service
- Suggested enforcement integration points:
  - API Gateway: check entitlements via `billing-core /enforce`
  - Rate limiting: per-tenant quotas
  - Rollouts-safe and GitOps-managed

## Recommended enforcement layers
1) **Gateway**: deny if over quota (HTTP 429)
2) **Async jobs**: scheduler checks quota before enqueuing NDVI jobs
3) **Eventing**: services emit usage signals; billing-core aggregates

## Next steps
- Replace in-memory stores with Postgres tables
- Integrate with your auth JWT (tenant_id claim)
- Add metering events consumers (NATS/Kafka) for usage
