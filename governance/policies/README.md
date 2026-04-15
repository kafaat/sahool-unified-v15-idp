# Security & Operational Policies

> السياسات الأمنية والتشغيلية | Security & Operational Policies

Kubernetes admission policies enforced via [Kyverno](https://kyverno.io/) to ensure security, resource governance, and operational standards across the SAHOOL platform.

## Contents

```
policies/
├── kyverno/                              # Kyverno admission policies
│   ├── baseline-security.yaml            # Block privileged containers & host namespaces
│   ├── require-governance-labels.yaml    # Enforce owner/team/lifecycle/tier labels
│   ├── require-resource-limits.yaml      # CPU/memory limits enforcement
│   ├── restrict-latest-tag.yaml          # Block mutable :latest image tags
│   ├── require-network-policy.yaml       # Enforce NetworkPolicy per namespace
│   ├── require-pod-disruption-budget.yaml # Require PDB for production workloads
│   └── restrict-image-registries.yaml    # Restrict container image registries
├── tenant-isolation.md                   # Tenant isolation & RLS enforcement policy
└── compliance-automation.md              # Compliance automation & audit policy
```

## Policy Categories

| Category | Policy | Enforcement |
|----------|--------|-------------|
| **Security** | `baseline-security.yaml` | Enforce — blocks privileged containers |
| **Governance** | `require-governance-labels.yaml` | Enforce — requires sahool.io/* labels |
| **Resources** | `require-resource-limits.yaml` | Enforce — requires CPU/memory limits |
| **Images** | `restrict-latest-tag.yaml` | Enforce — blocks `:latest` tags |
| **Network** | `require-network-policy.yaml` | Audit — logs missing NetworkPolicies |
| **Availability** | `require-pod-disruption-budget.yaml` | Audit — logs missing PDBs |
| **Registry** | `restrict-image-registries.yaml` | Enforce — restricts to approved registries |
| **Tenant Isolation** | `tenant-isolation.md` | Policy — RLS, audit, cross-tenant rules |
| **Compliance** | `compliance-automation.md` | Policy — GlobalGAP, pesticide, GDPR automation |

## Enforcement Levels

- **Enforce**: Blocks non-compliant resources at admission
- **Audit**: Logs violations without blocking (transition to Enforce after review)
- **Report**: Generates compliance reports

## Related

- [Helm Charts](../../helm/) — Kubernetes deployment manifests
- [Security Docs](../../docs/security/) — Threat models and data classification
- [SLO Definitions](../reliability/) — Service level objectives
- [Architecture Decisions](../decisions/) — ADRs for governance choices
