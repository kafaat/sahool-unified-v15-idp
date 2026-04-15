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
│   ├── 0001-backend-root.md   # ADR: Backend services root directory
│   ├── 0002-multi-tenancy.md  # ADR: Multi-tenancy strategy (RLS)
│   ├── 0003-event-versioning.md # ADR: Event versioning strategy
│   ├── 0004-api-versioning.md # ADR: API versioning strategy
│   └── 0005-service-mesh.md   # ADR: Service mesh strategy
├── design/                    # Design patterns & standards
│   └── design-tokens.yaml     # Design system tokens
├── events/                    # Event definitions & schemas
│   ├── catalog.yaml           # Event catalog
│   ├── events-registry.yaml   # Events registry
│   └── schemas/               # JSON schemas (alert, field, NDVI, weather)
├── policies/                  # Security & operational policies
│   ├── tenant-isolation.md    # Tenant isolation & RLS enforcement policy
│   ├── compliance-automation.md # Compliance automation & audit policy
│   └── kyverno/               # Kyverno policy-as-code (7 policies)
│       ├── baseline-security.yaml
│       ├── require-governance-labels.yaml
│       ├── require-resource-limits.yaml
│       ├── restrict-latest-tag.yaml
│       ├── require-network-policy.yaml
│       ├── require-pod-disruption-budget.yaml
│       └── restrict-image-registries.yaml
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

## Architecture Decision Records (ADRs) | سجلات القرارات المعمارية

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](decisions/0001-backend-root.md) | Backend Services Root Directory | Accepted |
| [ADR-0002](decisions/0002-multi-tenancy.md) | Multi-Tenancy Strategy (RLS) | Accepted |
| [ADR-0003](decisions/0003-event-versioning.md) | Event Versioning Strategy | Accepted |
| [ADR-0004](decisions/0004-api-versioning.md) | API Versioning Strategy | Accepted |
| [ADR-0005](decisions/0005-service-mesh.md) | Service Mesh Strategy | Accepted |

## Agent Categories | تصنيفات الوكلاء

Defined in `agents.yaml`: intelligence, advisory, analysis, monitoring, security, iot, precision, sustainability, market, social, operations.

## Enforced Policies | القواعد المفروضة

### Kyverno Admission Policies

| Policy | Mode | Description |
|--------|------|-------------|
| `baseline-security` | **Enforce** | Block privileged containers & host namespaces |
| `require-governance-labels` | **Enforce** | Require sahool.io/* labels on all resources |
| `require-resource-limits` | **Enforce** | Enforce CPU/Memory limits on all pods |
| `restrict-latest-tag` | **Enforce** | Block `:latest` image tags |
| `restrict-image-registries` | **Enforce** | Allow only approved container registries |
| `require-network-policy` | **Audit** | Log namespaces without NetworkPolicy |
| `require-pod-disruption-budget` | **Audit** | Log production deployments without PDB |

### Governance Policies

| Policy | Scope | Description |
|--------|-------|-------------|
| [Tenant Isolation](policies/tenant-isolation.md) | All services | RLS, audit trail, cross-tenant access rules |
| [Compliance Automation](policies/compliance-automation.md) | Compliance | GlobalGAP, pesticide, GDPR automation |

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
- `event-contracts-guard.yml` — **Blocks** event schema breaking changes (requires `BREAKING:` commit prefix)
- `api-contracts-guard.yml` — **Blocks** API contract breaking changes (requires `BREAKING:` commit prefix)
- `codeql-analysis.yml` — **Daily** CodeQL security analysis (Python + TypeScript)

## Enforcement | التطبيق

Policies are applied automatically via ArgoCD:

```
gitops/argocd/applications/sahool-governance-policies.yaml
```

Any service without Owner/Lifecycle/Tier labels will be rejected.

أي خدمة بدون Owner/Lifecycle/Tier سيتم منعها.
