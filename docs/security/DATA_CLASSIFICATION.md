# SAHOOL Data Classification Policy

> **Version:** 16.0.0
> **Last Updated:** December 2025
> **Status:** Active
> **Owner:** Security Team

## 1. Purpose

This document defines data classification levels for SAHOOL platform and the handling requirements for each level.

## 2. Classification Levels

### 2.1 Public

**Definition:** Information that can be freely shared with anyone.

**Examples:**
- Marketing materials
- Public documentation
- Open source code
- General agricultural information

**Handling Requirements:**
- No special handling required
- Can be published on public websites
- No encryption required for transmission

### 2.2 Internal

**Definition:** Information for internal use within the organization.

**Examples:**
- Internal documentation
- Development guidelines
- Architecture diagrams
- Non-sensitive configuration

**Handling Requirements:**
- Share only with employees/contractors
- Do not publish externally without approval
- Standard access controls

### 2.3 Sensitive

**Definition:** Information that could cause harm if disclosed.

**Examples:**
- Farm owner identifiers
- Phone numbers and contact info
- Internal notes and comments
- Aggregated business metrics
- Field boundaries (non-precise)
- User profiles

**Handling Requirements:**
- Access on need-to-know basis
- Encrypt in transit (TLS)
- Log access attempts
- Anonymize in non-production environments
- Mask in logs

### 2.4 Restricted

**Definition:** Highly sensitive information requiring strictest controls.

**Examples:**
- Authentication secrets (JWT keys, API keys)
- Database credentials
- Private keys and certificates
- Precise field ownership mapping
- Financial data
- Health-related crop data

**Handling Requirements:**
- Access strictly limited
- Never in logs (any level)
- Never in `.env.example` or documentation
- Store only via Vault/KMS/HSM
- Encrypt at rest
- Audit all access
- Rotate regularly

## 3. Data Inventory

### 3.1 kernel_domain

| Data | Classification | Storage | Notes |
|------|---------------|---------|-------|
| User email | Sensitive | PostgreSQL | Encrypted at rest |
| User password hash | Restricted | PostgreSQL | bcrypt/PBKDF2 |
| JWT tokens | Restricted | Memory/Redis | Short-lived |
| Tenant ID | Internal | PostgreSQL | UUID |
| User roles | Sensitive | PostgreSQL | RBAC |

### 3.2 field_suite

| Data | Classification | Storage | Notes |
|------|---------------|---------|-------|
| Field name | Sensitive | PostgreSQL | |
| Field boundaries | Sensitive | PostgreSQL/PostGIS | Geometry |
| Farm location | Sensitive | PostgreSQL | Approximate |
| Crop type | Internal | PostgreSQL | |
| NDVI values | Internal | PostgreSQL | Time-series |

### 3.3 advisor

| Data | Classification | Storage | Notes |
|------|---------------|---------|-------|
| AI queries | Sensitive | PostgreSQL | User input |
| Recommendations | Internal | PostgreSQL | AI output |
| RAG documents | Internal | Vector DB | Knowledge base |
| Feedback | Sensitive | PostgreSQL | User opinions |

### 3.4 Infrastructure

| Data | Classification | Storage | Notes |
|------|---------------|---------|-------|
| Database passwords | Restricted | Vault | Never in ENV |
| API keys (external) | Restricted | Vault | Rotate quarterly |
| TLS private keys | Restricted | Filesystem | Never in Git |
| CA private key | Restricted | Offline/HSM | Air-gapped |
| Service tokens | Restricted | Vault | Short TTL |

## 4. Handling Rules

### 4.1 Secrets Management

```
┌─────────────────────────────────────────────────────────────┐
│                    SECRETS FLOW                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ❌ NEVER                      ✅ ALWAYS                   │
│   ─────────────                 ──────────                  │
│   • .env files in Git           • HashiCorp Vault          │
│   • Hardcoded in code           • Cloud KMS                │
│   • Logs (any level)            • Environment injection    │
│   • Error messages              • Short-lived tokens       │
│   • API responses               • Rotation policies        │
│   • .env.example with real      • Audit logging            │
│     values                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Logging Rules

| Classification | Allowed in Logs | Format |
|----------------|-----------------|--------|
| Public | Yes | Plain text |
| Internal | Yes | Plain text |
| Sensitive | Masked only | `user_email: j***@***.com` |
| Restricted | Never | `[REDACTED]` |

### 4.3 Development Environment

| Classification | Dev Environment | Notes |
|----------------|-----------------|-------|
| Public | Real data OK | |
| Internal | Real data OK | |
| Sensitive | Anonymized | Use faker |
| Restricted | Synthetic only | Never real secrets |

### 4.4 Backup and Retention

| Classification | Backup Encryption | Retention | Disposal |
|----------------|-------------------|-----------|----------|
| Public | Optional | As needed | Standard delete |
| Internal | Optional | 1 year | Standard delete |
| Sensitive | Required | Per policy | Secure delete |
| Restricted | Required (AES-256) | Minimum | Cryptographic erasure |

## 5. Compliance Mapping

| Requirement | Classification Level | Notes |
|-------------|---------------------|-------|
| GDPR Personal Data | Sensitive/Restricted | PII handling |
| PCI-DSS Card Data | Restricted | If applicable |
| Local Data Laws | Varies | Yemen data residency |

## 6. Enforcement

### 6.1 CI/CD Gates

```yaml
# Automated checks in CI
- detect-secrets scan
- No *.key, *.pem in repository
- No hardcoded credentials
- Classification labels on PRs touching Sensitive/Restricted
```

### 6.2 Code Review

- PRs touching Restricted data require Security team review
- Sensitive data handling requires documentation

### 6.3 Monitoring

- Vault audit logs for Restricted access
- Database query logging for Sensitive tables
- Alert on anomalous access patterns

## 7. Incident Response

If Restricted data is exposed:
1. Immediately rotate all affected credentials
2. Notify Security team within 1 hour
3. Document incident in security log
4. Conduct root cause analysis
5. Implement preventive measures

## 8. Training

All developers must complete:
- [ ] Data classification training (annual)
- [ ] Secure coding practices
- [ ] Secrets management with Vault

## 9. Review

This policy is reviewed quarterly and updated as needed.

| Date | Reviewer | Changes |
|------|----------|---------|
| 2025-12 | Security Team | Initial policy |
