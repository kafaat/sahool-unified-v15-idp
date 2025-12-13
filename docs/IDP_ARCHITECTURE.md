# SAHOOL IDP Architecture (Microservices + SaaS + HCI)

## Goals
- Reduce onboarding time for new devs (minutes, not days)
- Standardize service creation (Golden Paths)
- Enforce baseline security/observability (Policy + Templates)
- Self-service: create service → build → deploy to dev/staging/prod via GitOps

## Core components
1) **Backstage**: Developer portal + catalog + templates.
2) **GitOps** (Argo CD): Environment reconciliation & progressive delivery.
3) **Rollouts**: Canary/Blue-Green.
4) **Policies** (Kyverno): Guardrails.
5) **Observability**: Prometheus/Grafana/Tempo/OTel.

## Golden Path (service lifecycle)
- Scaffold service (template) → includes:
  - Dockerfile
  - /healthz /readyz /metrics
  - OTel init
  - structured logging
  - Helm values snippet + Rollouts defaults
  - Catalog registration (`catalog-info.yaml`)
- Push code → CI builds image → GitOps deploys → Rollouts runs analysis → auto-rollback on failure.

## SaaS multi-tenant conventions
- All inbound requests must carry `x-tenant-id` (or JWT claim)
- Events must include `tenant_id` and `correlation_id`
- Metrics labels include `tenant_id` (when safe)

## HCI conventions
- Use k3s/k8s on bare metal
- Prefer MetalLB for LoadBalancer
- Prefer Longhorn (or your HCI storage) for PV
- GitOps is the single source of truth (air-gapped friendly)

## Repository layout recommendation
- `apps/<service>` : microservices
- `k8s/helm/...` : charts
- `gitops/` : Argo CD apps + env overlays
- `idp/` : Backstage + templates + tooling
