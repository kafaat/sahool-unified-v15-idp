# SAHOOL Governance Pack | حزمة حوكمة سهول

**Version**: 3.2.0 (services.yaml) / 16.0.0 (agents.yaml)

Platform governance enforced automatically via Kyverno, GitOps (ArgoCD), CI Guards, and Backstage Templates.

هذا المجلد يفرض حوكمة المنصة تلقائيًا عبر Kyverno و GitOps و CI Guards و Backstage Templates.

## Directory Structure | الهيكل

```
governance/
├── services.yaml              # Service registry - single source of truth (71 services)
├── agents.yaml                # AI agent definitions (11 categories, A2A protocol)
├── credentials.template.yaml  # Credential configuration template
├── DEDUP_MATRIX.md            # Service deduplication matrix
├── decisions/                 # Architecture Decision Records
│   └── 0001-backend-root.md
├── design/                    # Design patterns & standards
│   └── design-tokens.yaml     # Design system tokens
├── events/                    # Event definitions & schemas
│   ├── catalog.yaml           # Event catalog
│   ├── events-registry.yaml   # Events registry
│   └── schemas/               # JSON schemas (alert, field, NDVI, weather)
├── policies/                  # Security & operational policies
│   └── kyverno/               # Kyverno policy-as-code
├── reliability/               # Reliability patterns
│   └── slo-definitions.yaml   # SLO definitions for all services
├── schemas/                   # Data schemas
│   ├── service-metadata.json  # Service metadata JSON schema
│   └── template-input.json    # Template input JSON schema
└── templates/                 # Service scaffolding templates
    ├── api-extension/         # API extension template
    ├── backend-service/       # Backend service template
    └── worker-service/        # Worker service template
```

## Key Files | الملفات الرئيسية

| File | Version | Purpose |
|------|---------|---------|
| `services.yaml` | 3.2.0 | **Source of truth** for all 71 microservices — ports, owners, tiers, lifecycle |
| `agents.yaml` | 16.0.0 | AI agent definitions across 11 categories (A2A protocol-compliant) |
| `events/catalog.yaml` | — | Event catalog defining all NATS subjects |
| `reliability/slo-definitions.yaml` | — | SLO targets for all service tiers |
| `DEDUP_MATRIX.md` | — | Service deduplication and consolidation tracking |

## Agent Categories | تصنيفات الوكلاء

Defined in `agents.yaml`: intelligence, advisory, analysis, monitoring, security, iot, precision, sustainability, market, social, operations.

## Enforced Policies | القواعد المفروضة

| Policy | Description |
|--------|-------------|
| `restrict-latest-tag` | Block `image:latest` in production |
| `require-resource-limits` | Enforce CPU/Memory limits on all pods |
| `require-governance-labels` | Require governance labels on all resources |
| `baseline-security` | Block privileged containers |

## Required Labels | التسميات المطلوبة

```yaml
sahool.io/owner: "<owner>"
sahool.io/team: "<team>"
sahool.io/lifecycle: "experimental|internal|production|deprecated|retired"
sahool.io/tier: "tier-1|tier-2|tier-3"
```

## CI Guards | حراس CI

Governance is enforced in CI via these workflows:
- `governance-ci.yml` — Validates services.yaml and agents.yaml structure
- `governance-validation.yml` — Validates policy compliance
- `governance-structure.yml` — Enforces directory structure conventions
- `event-contracts-guard.yml` — Validates event schema changes
- `api-contracts-guard.yml` — Guards API contract breaking changes

## Enforcement | التطبيق

Policies are applied automatically via ArgoCD:

```
gitops/argocd/applications/sahool-governance-policies.yaml
```

Any service without Owner/Lifecycle/Tier labels will be rejected.

أي خدمة بدون Owner/Lifecycle/Tier سيتم منعها.
