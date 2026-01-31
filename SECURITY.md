# Security Policy | سياسة الأمان

## Supported Versions | الإصدارات المدعومة

| Version | Supported          |
| ------- | ------------------ |
| 16.x.x  | :white_check_mark: |
| < 16.0  | :x:                |

## Reporting a Vulnerability | الإبلاغ عن ثغرة أمنية

### English

We take security vulnerabilities seriously. If you discover a security issue, please follow these steps:

1. **Do NOT** disclose the vulnerability publicly until it has been addressed
2. Email security concerns to: security@kafaat.sa
3. Include as much detail as possible:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

### العربية

نأخذ الثغرات الأمنية على محمل الجد. إذا اكتشفت مشكلة أمنية، يرجى اتباع الخطوات التالية:

1. **لا تفصح** عن الثغرة علناً حتى يتم معالجتها
2. أرسل مخاوفك الأمنية إلى: security@kafaat.sa
3. قم بتضمين أكبر قدر ممكن من التفاصيل:
   - وصف الثغرة
   - خطوات إعادة الإنتاج
   - التأثير المحتمل
   - الإصلاح المقترح (إن وجد)

سنؤكد الاستلام خلال 48 ساعة ونقدم رداً مفصلاً خلال 7 أيام.

---

## Security Architecture | البنية الأمنية

### Authentication & Authorization | المصادقة والتفويض

#### JWT Token Management
```
Access Token:  30 minutes TTL
Refresh Token: 7 days TTL
Algorithm:     RS256 (asymmetric)
```

#### Role-Based Access Control (RBAC)
| Role | Permissions |
|------|-------------|
| `admin` | Full access to all resources |
| `supervisor` | Read + limited write access |
| `operator` | Service operations only |
| `viewer` | Read-only access |
| `farmer` | Field-specific operations |
| `agronomist` | Advisory and analysis access |

#### Multi-Factor Authentication (2FA)
- TOTP (Time-based One-Time Password)
- SMS verification
- Email verification
- Biometric (mobile app)

### Network Security | أمان الشبكة

#### TLS Configuration
```yaml
Minimum Version: TLS 1.2
Preferred Version: TLS 1.3
Certificate Rotation: 90 days

Cipher Suites (Priority Order):
  - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```

#### Firewall Rules
| Port | Service | Access |
|------|---------|--------|
| 443 | HTTPS | Public |
| 80 | HTTP → HTTPS redirect | Public |
| 22 | SSH | Internal only |
| 5432 | PostgreSQL | Internal only |
| 6379 | Redis | Internal only |
| 4222 | NATS | Internal only |
| 8000 | Kong API Gateway | Internal only |

#### Rate Limiting
| Tier | Requests/min | Requests/hour | Burst |
|------|--------------|---------------|-------|
| Free | 30 | 500 | 50 |
| Standard | 60 | 2,000 | 100 |
| Premium | 120 | 5,000 | 200 |
| Internal | 1,000 | 50,000 | 2,000 |

**Endpoint-Specific Limits:**
```yaml
/api/v1/auth/login:     10 req/min (brute-force protection)
/api/v1/analyze:        10 req/min (heavy processing)
/api/v1/field-health:   30 req/min
/api/v1/weather:        60 req/min
/api/v1/sensors:       100 req/min
/healthz:              unlimited
```

---

## Data Protection | حماية البيانات

### Data Classification
| Level | Examples | Protection |
|-------|----------|------------|
| **Public** | Marketing content | None required |
| **Internal** | API docs, metrics | Authentication |
| **Confidential** | User data, farm data | Encryption + RBAC |
| **Restricted** | Credentials, keys | Vault + audit |

### Encryption Standards
```yaml
At Rest:
  Algorithm: AES-256-GCM
  Key Management: HashiCorp Vault
  Database: Transparent Data Encryption (TDE)
  Mobile: SQLCipher

In Transit:
  Protocol: TLS 1.2+
  Certificate Pinning: Mobile apps
  HSTS: max-age=31536000
```

### Data Masking
Automatically masked in logs and exports:
- Social Security Numbers (SSN)
- Credit card numbers
- Passwords and secrets
- API keys and tokens
- Personal phone numbers

### Backup Security
```yaml
Frequency: Daily
Retention: 30 days + offsite
Encryption: AES-256-GCM
Verification: Weekly integrity checks
RTO: 4 hours
RPO: 24 hours
```

---

## Code Security | أمان الكود

### Static Analysis Tools
| Tool | Language | Purpose |
|------|----------|---------|
| **CodeQL** | Python, TypeScript | Semantic vulnerability analysis |
| **Bandit** | Python | Security-focused linting |
| **Semgrep** | Multi-language | Pattern-based scanning |
| **ESLint Security** | JavaScript/TypeScript | JS security rules |
| **Trivy** | Containers | Vulnerability scanning |
| **Gitleaks** | All | Secret detection |
| **TruffleHog** | All | Secret detection |

### Dependency Scanning
```yaml
Tools:
  - npm audit (Node.js)
  - pip-audit (Python)
  - Dependabot (GitHub)
  - Snyk (optional)

Policy:
  - Critical: Block merge, fix immediately
  - High: Fix within 7 days
  - Medium: Fix within 30 days
  - Low: Fix in next release
```

### Pre-commit Hooks
```bash
# Installed hooks
- gitleaks        # Secret detection
- bandit          # Python security
- eslint          # JavaScript linting
- prettier        # Code formatting
- pytest          # Unit tests
```

---

## Container Security | أمان الحاويات

### Base Image Policy
```yaml
Allowed Registries:
  - docker.io/library/*
  - ghcr.io/sahool/*
  - gcr.io/distroless/*

Prohibited:
  - latest tag (must use specific version)
  - Unknown registries
  - Unscanned images
```

### Runtime Security
```yaml
Security Context:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false

Capabilities:
  drop: [ALL]
  add: [NET_BIND_SERVICE] # Only if needed

Seccomp: RuntimeDefault
AppArmor: runtime/default
```

### Image Scanning
```yaml
Tools: Trivy + Grype
Schedule: Daily + on push
Policy:
  - Block on CRITICAL vulnerabilities
  - Warn on HIGH vulnerabilities
  - Report MEDIUM and below
```

---

## Secrets Management | إدارة الأسرار

### HashiCorp Vault Integration
```yaml
Provider: HashiCorp Vault
Storage: Raft (HA)
Auto-Unseal: AWS KMS / Azure Key Vault / GCP Cloud KMS
UI: Enabled (admin only)

Lease TTL:
  Default: 168 hours (7 days)
  Maximum: 720 hours (30 days)
```

### Secret Rotation Policy
| Secret Type | Rotation Period |
|-------------|-----------------|
| Database passwords | 90 days |
| API keys | 180 days |
| JWT signing keys | 90 days |
| TLS certificates | 60 days |
| Service accounts | 90 days |

### Environment Variables
```bash
# Required for all services
DATABASE_URL=postgresql://...?sslmode=require
REDIS_URL=redis://...
NATS_URL=nats://...
JWT_SECRET_KEY=<from-vault>
```

**Never commit:**
- `.env` files with real values
- API keys or tokens
- Database credentials
- Private keys
- Service account JSON files

---

## Infrastructure Security | أمان البنية التحتية

### PostgreSQL Hardening
```yaml
TLS: Required (sslmode=require)
Authentication: SCRAM-SHA-256
Max Connections: 200
Connection Pooling: PgBouncer (transaction mode)
Row-Level Security: Enabled
Audit Logging: All DDL + DML operations

pg_hba.conf:
  - hostssl all all 0.0.0.0/0 scram-sha-256
  - host all all 127.0.0.1/32 scram-sha-256
```

### Redis Security
```yaml
Password: Required (ACL enabled)
TLS: Required
Max Memory: 2GB
Eviction: volatile-lru
Dangerous Commands: Renamed (FLUSHDB, CONFIG, DEBUG)

ACL Users:
  - sahool_app: Read/write session and cache keys
  - sahool_admin: Full access (restricted)
```

### NATS Security
```yaml
TLS: Required (TLS 1.2+)
Authentication: NKey (Ed25519) or JWT
JetStream Encryption: AES-256-GCM
Cluster Auth: Mutual TLS

Subject Permissions:
  - sahool.> : Application events
  - _INBOX.> : Request-reply pattern
  - $SYS.> : System monitoring (admin only)
```

### Kong API Gateway
```yaml
Plugins Enabled:
  - rate-limiting
  - key-auth / oauth2
  - cors
  - request-transformer
  - response-transformer
  - ip-restriction
  - bot-detection
  - acl

Security Headers:
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security: max-age=31536000
  - Content-Security-Policy: [configured per app]
```

---

## Application Security | أمان التطبيقات

### Web Application (Next.js)
```yaml
CSP (Content Security Policy):
  - Nonce-based inline scripts
  - Strict source allowlists
  - No unsafe-eval

CSRF Protection:
  - Double-submit cookie pattern
  - SameSite=Strict cookies

XSS Prevention:
  - DOMPurify for HTML sanitization
  - React auto-escaping
  - Input validation (Zod)

Session Security:
  - HttpOnly cookies
  - Secure flag (HTTPS only)
  - 30-minute idle timeout
  - 12-hour absolute timeout
```

### Mobile Application (Flutter)
```yaml
Certificate Pinning: Enabled
Secure Storage: flutter_secure_storage
Database Encryption: SQLCipher
Root/Jailbreak Detection: safe_device
Screenshot Prevention: secure_application
Biometric Auth: local_auth
Obfuscation: Enabled for release builds
```

### API Security
```yaml
Input Validation:
  - Pydantic v2 (Python)
  - class-validator (Node.js)
  - Zod (TypeScript)

Output Encoding:
  - JSON serialization with escaping
  - No raw SQL in responses

SQL Injection Prevention:
  - Parameterized queries only
  - ORM (Prisma, SQLAlchemy)
  - No raw SQL concatenation

File Upload:
  - Type validation (magic bytes)
  - Size limits (10MB default)
  - Virus scanning (optional)
  - Isolated storage
```

---

## Monitoring & Incident Response | المراقبة والاستجابة للحوادث

### Security Monitoring
```yaml
Tools:
  - Prometheus: Metrics collection
  - Grafana: Dashboards and alerts
  - Sentry: Error tracking
  - Audit logs: All security events

Alert Categories:
  - Authentication failures (>10/min)
  - Rate limit violations
  - Unusual API patterns
  - Certificate expiration (<30 days)
  - Backup failures
```

### Incident Response
```yaml
Severity Levels:
  P1 (Critical): Data breach, service down
  P2 (High): Security vulnerability, degraded service
  P3 (Medium): Non-critical security issue
  P4 (Low): Minor security improvement

Response Times:
  P1: 15 minutes
  P2: 1 hour
  P3: 24 hours
  P4: 7 days
```

### Audit Logging
All security-relevant events are logged:
- Authentication attempts (success/failure)
- Authorization decisions
- Data access (read/write/delete)
- Configuration changes
- Administrative actions

```json
{
  "timestamp": "2026-01-30T10:30:00Z",
  "event_type": "auth.login",
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "result": "success",
  "metadata": {}
}
```

---

## Compliance | الامتثال

### Standards Alignment
- **OWASP Top 10**: All vulnerabilities addressed
- **CIS Benchmarks**: Container and Kubernetes hardening
- **ISO 27001**: Information security management
- **GDPR**: Data protection (where applicable)
- **GlobalGAP**: Agricultural compliance tracking

### Security Testing
| Type | Frequency | Tool |
|------|-----------|------|
| SAST | Every commit | CodeQL, Bandit, Semgrep |
| DAST | Weekly | OWASP ZAP |
| Dependency Scan | Daily | Trivy, npm audit |
| Penetration Test | Annually | External vendor |
| Security Review | Per release | Internal team |

---

## Security Checklist | قائمة التحقق الأمني

### For Developers
- [ ] Never hardcode secrets
- [ ] Use parameterized queries
- [ ] Validate all inputs
- [ ] Escape all outputs
- [ ] Use HTTPS everywhere
- [ ] Implement proper error handling
- [ ] Follow least privilege principle
- [ ] Keep dependencies updated

### For Operations
- [ ] Enable TLS on all services
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Implement backup strategy
- [ ] Test disaster recovery
- [ ] Rotate secrets regularly
- [ ] Review access permissions
- [ ] Audit security logs

### For Code Review
- [ ] Check for hardcoded secrets
- [ ] Verify input validation
- [ ] Review authentication logic
- [ ] Check authorization rules
- [ ] Verify error handling
- [ ] Review logging (no sensitive data)
- [ ] Check dependency versions
- [ ] Verify TLS usage

---

## Contact | التواصل

| Type | Contact |
|------|---------|
| Security issues | security@kafaat.sa |
| Bug reports | bugs@kafaat.sa |
| General inquiries | dev@kafaat.sa |

---

_Last Updated: January 2026_
