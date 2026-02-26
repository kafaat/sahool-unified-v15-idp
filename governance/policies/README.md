# Security & Operational Policies

> السياسات الأمنية والتشغيلية | Security & Operational Policies

Kubernetes admission policies enforced via [Kyverno](https://kyverno.io/) to ensure security, resource governance, and operational standards across the SAHOOL platform.

## Contents

```
policies/
└── kyverno/          # Kyverno admission policies
    ├── require-labels.yaml       # Enforce mandatory labels
    ├── resource-limits.yaml      # CPU/memory limits enforcement
    ├── security-context.yaml     # Pod security standards
    └── ...
```

## Policy Categories

| Category | Purpose |
|----------|---------|
| **Labels** | Require `app`, `version`, `team`, `tier` labels on all resources |
| **Resource Limits** | Enforce CPU/memory requests and limits on all containers |
| **Security Context** | Non-root containers, read-only filesystem, drop capabilities |
| **Image Policies** | Restrict container registries, require image digests |
| **Network Policies** | Namespace isolation, egress restrictions |

## Enforcement

Policies are applied at the Kubernetes admission level:
- **Enforce**: Blocks non-compliant resources
- **Audit**: Logs violations without blocking
- **Report**: Generates compliance reports

## Related

- [Helm Charts](../../helm/) — Kubernetes deployment manifests
- [Security Docs](../../docs/security/) — Threat models and data classification
- [SLO Definitions](../reliability/) — Service level objectives
