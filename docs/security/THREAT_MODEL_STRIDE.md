# SAHOOL Threat Model (STRIDE)

> **Version:** 16.0.0
> **Last Updated:** December 2025
> **Status:** Active
> **Review Frequency:** Quarterly

## 1. Overview

This document describes the threat model for the SAHOOL agricultural platform using the STRIDE methodology.

### 1.1 Scope

**In Scope:**

- Services: kernel_domain, field_suite, advisor
- Infrastructure: API Gateway, NATS, PostgreSQL, Redis
- Assets: Tenant data, field geometries, auth tokens, NDVI data
- Interfaces: REST APIs, WebSocket, Mobile app, Event bus

**Out of Scope:**

- Physical security
- Social engineering (covered in security awareness training)
- Third-party services (weather APIs, satellite providers)

### 1.2 Trust Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
│                    (Untrusted Zone)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS/WSS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DMZ (Kong Gateway)                         │
│   - Rate limiting    - Authentication    - TLS termination      │
└────────────────────────┬────────────────────────────────────────┘
                         │ mTLS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Internal Services                             │
│  ┌──────────┐  ┌──────────────┐  ┌─────────┐                   │
│  │  kernel  │  │ field_suite  │  │ advisor │                   │
│  └────┬─────┘  └──────┬───────┘  └────┬────┘                   │
│       │               │               │                         │
│       └───────────────┼───────────────┘                         │
│                       │ mTLS                                    │
│                       ▼                                         │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐         │
│  │ Postgres │  │   NATS   │  │  Redis  │  │  Vault  │         │
│  └──────────┘  └──────────┘  └─────────┘  └─────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## 2. STRIDE Analysis

### 2.1 Spoofing

**Threat:** Attacker impersonates a legitimate service or user.

| Asset            | Threat                         | Likelihood | Impact | Risk   | Mitigation                       |
| ---------------- | ------------------------------ | ---------- | ------ | ------ | -------------------------------- |
| Service Identity | Fake service connecting to bus | Medium     | High   | High   | mTLS with internal CA            |
| User Identity    | Token theft/replay             | Medium     | High   | High   | Short-lived JWT + refresh tokens |
| API Client       | Forged requests                | Low        | Medium | Medium | API key rotation, rate limiting  |

**Mitigations Implemented:**

- ✅ mTLS for service-to-service communication
- ✅ Internal CA for certificate issuance
- ✅ JWT with short expiration (30 min)
- ✅ Refresh token rotation
- 🔄 Certificate rotation automation (planned)

### 2.2 Tampering

**Threat:** Attacker modifies data in transit or at rest.

| Asset            | Threat                    | Likelihood | Impact   | Risk   | Mitigation                          |
| ---------------- | ------------------------- | ---------- | -------- | ------ | ----------------------------------- |
| Event Payloads   | Message modification      | Low        | High     | Medium | Schema validation, signed envelopes |
| Database Records | Unauthorized modification | Low        | Critical | High   | RBAC, audit logging                 |
| Field Boundaries | Geometry manipulation     | Low        | High     | Medium | Change history, validation          |

**Mitigations Implemented:**

- ✅ TLS for all communication
- ✅ Event schema validation (Sprint 4)
- ✅ Database access via service accounts only
- 🔄 Signed event envelopes (planned)
- 🔄 Immutable audit log (Sprint 6)

### 2.3 Repudiation

**Threat:** User denies performing an action.

| Asset        | Threat                  | Likelihood | Impact | Risk   | Mitigation                     |
| ------------ | ----------------------- | ---------- | ------ | ------ | ------------------------------ |
| User Actions | Deny field modification | Medium     | Medium | Medium | Audit logs with correlation_id |
| API Requests | Deny API call           | Low        | Low    | Low    | Request logging                |
| Events       | Deny event emission     | Low        | Medium | Low    | Event store with timestamps    |

**Mitigations Implemented:**

- ✅ correlation_id in all events
- ✅ Request logging at gateway
- 🔄 Immutable audit trail (Sprint 6)
- 🔄 User action audit (Sprint 6)

### 2.4 Information Disclosure

**Threat:** Sensitive data is exposed to unauthorized parties.

| Asset            | Threat              | Likelihood | Impact   | Risk   | Mitigation         |
| ---------------- | ------------------- | ---------- | -------- | ------ | ------------------ |
| Secrets in ENV   | ENV file exposure   | Medium     | Critical | High   | Vault for secrets  |
| Secrets in Logs  | Accidental logging  | Medium     | High     | High   | Log redaction      |
| PII in Responses | Over-fetching       | Low        | Medium   | Medium | Response filtering |
| Field Locations  | Precise coordinates | Low        | Medium   | Low    | Access control     |

**Mitigations Implemented:**

- ✅ Vault for secrets management
- ✅ `.gitignore` for sensitive files
- ✅ detect-secrets in CI
- 🔄 Log redaction middleware (planned)
- 🔄 Response field filtering (planned)

### 2.5 Denial of Service

**Threat:** Service availability is impacted.

| Asset       | Threat           | Likelihood | Impact   | Risk   | Mitigation                   |
| ----------- | ---------------- | ---------- | -------- | ------ | ---------------------------- |
| API Gateway | Request flooding | High       | High     | High   | Rate limiting                |
| Database    | Query overload   | Medium     | Critical | High   | Connection pooling, timeouts |
| Event Bus   | Message flooding | Low        | High     | Medium | Queue limits                 |

**Mitigations Implemented:**

- ✅ Kong rate limiting
- ✅ Database connection pooling
- 🔄 Circuit breakers (planned)
- 🔄 Bulkhead pattern (planned)

### 2.6 Elevation of Privilege

**Threat:** User gains unauthorized access or permissions.

| Asset            | Threat                     | Likelihood | Impact   | Risk | Mitigation       |
| ---------------- | -------------------------- | ---------- | -------- | ---- | ---------------- |
| Admin Functions  | Normal user accesses admin | Medium     | Critical | High | RBAC enforcement |
| Cross-Tenant     | Access other tenant data   | Low        | Critical | High | Tenant isolation |
| Service Accounts | Over-privileged service    | Medium     | High     | High | Least privilege  |

**Mitigations Implemented:**

- ✅ RBAC with role hierarchy
- ✅ Tenant ID validation on all queries
- ✅ Service-specific database users
- 🔄 Privileged access reviews (planned)

## 3. Risk Matrix

```
              │ Low Impact │ Medium Impact │ High Impact │ Critical Impact │
──────────────┼────────────┼───────────────┼─────────────┼─────────────────│
High          │   Medium   │     High      │   Critical  │    Critical     │
Likelihood    │            │               │             │                 │
──────────────┼────────────┼───────────────┼─────────────┼─────────────────│
Medium        │    Low     │    Medium     │    High     │    Critical     │
Likelihood    │            │               │             │                 │
──────────────┼────────────┼───────────────┼─────────────┼─────────────────│
Low           │    Low     │     Low       │   Medium    │      High       │
Likelihood    │            │               │             │                 │
```

## 4. Security Controls Summary

### Implemented (Sprint 5)

- [x] Internal CA for mTLS
- [x] Service certificate generation
- [x] Unified TLS client library
- [x] Vault integration
- [x] Secrets in Vault (not ENV)
- [x] CI gates for keys/secrets

### Planned (Future Sprints)

- [ ] Signed event envelopes
- [ ] Immutable audit logging
- [ ] Log redaction
- [ ] Certificate auto-rotation
- [ ] Penetration testing

## 5. Review History

| Date    | Reviewer      | Changes                 |
| ------- | ------------- | ----------------------- |
| 2025-12 | Security Team | Initial STRIDE analysis |

## 6. References

- [STRIDE Threat Modeling](https://docs.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
