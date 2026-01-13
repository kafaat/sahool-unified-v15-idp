# SAHOOL Next Platform Enhancements (Implemented)

Date: 2025-12-13

✅ Billing + Quotas skeleton: `apps/billing-core/` + GitOps app
✅ Feature flags + experiments baseline: `flagd` + GitOps app + OpenFeature guidance
✅ Multi-cluster delivery: Argo CD ApplicationSet

Next recommended (optional):

- Move billing-core storage to Postgres + migrations
- Integrate billing enforcement into api-gateway (authz middleware)
- Replace flagd with Unleash for UI-driven flags
- Add per-region data residency policies for SaaS
