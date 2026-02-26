# Security Documentation

> وثائق الأمن | Security Documentation

Threat modeling, data classification, and security analysis for the SAHOOL platform.

## Contents

| Document | Description |
|----------|-------------|
| [DATA_CLASSIFICATION.md](./DATA_CLASSIFICATION.md) | Data classification policy (PII, PHI, credentials) |
| [THREAT_MODEL_STRIDE.md](./THREAT_MODEL_STRIDE.md) | STRIDE threat model analysis |

## Security Stack

- **CodeQL**: Semantic code analysis
- **Bandit**: Python security linting
- **Semgrep**: Pattern-based scanning
- **Trivy**: Container vulnerability scanning
- **Gitleaks**: Secret detection

## Related

- [SECURITY.md](../../SECURITY.md) — Root security policy
- [Security Policies](../../governance/policies/) — Kyverno policies
- [Security Tests](../../tests/security/) — Security test suite
- [Compliance](../compliance/) — Compliance checklists
