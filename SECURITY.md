# Security Policy / سياسة الأمان

## Supported Versions / الإصدارات المدعومة

| Version | Supported          |
| ------- | ------------------ |
| 15.3.x  | :white_check_mark: |
| 15.2.x  | :white_check_mark: |
| < 15.0  | :x:                |

## Reporting a Vulnerability / الإبلاغ عن ثغرة

**Please do not report security vulnerabilities through public GitHub issues.**

### How to Report / كيفية الإبلاغ

1. **Email**: Send details to security@sahool.io
2. **Subject**: `[SECURITY] Brief description`
3. **Include**:
   - Type of vulnerability
   - Full path of affected file(s)
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Time / وقت الاستجابة

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days (critical), 90 days (other)

### What to Expect / ما يمكن توقعه

1. Acknowledgment of your report
2. Assessment of the vulnerability
3. Regular updates on progress
4. Credit in security advisory (if desired)

## Security Best Practices / أفضل الممارسات الأمنية

### For Contributors / للمساهمين

- **Never commit secrets**: API keys, passwords, certificates
- **Use environment variables**: For all sensitive configuration
- **Validate input**: Sanitize all user input
- **Use parameterized queries**: Prevent SQL injection
- **Follow OWASP Top 10**: Review before submitting PR

### Sensitive Files (Never Commit) / الملفات الحساسة

```
.env
.env.*
*.pem
*.key
*.p12
*credentials*
*secrets*
config/local.yaml
```

### Security Tools Used / أدوات الأمان المستخدمة

- **Gitleaks**: Secret scanning
- **Trivy**: Container vulnerability scanning
- **Snyk**: Dependency scanning
- **CodeQL**: Static analysis

## Security Architecture / هندسة الأمان

### Authentication

- JWT tokens with short expiry
- Refresh token rotation
- Multi-factor authentication (optional)

### Authorization

- Role-based access control (RBAC)
- Tenant isolation (multi-tenant)
- API key authentication for services

### Data Protection

- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- PII redaction in logs

### Network Security

- Network policies in Kubernetes
- Service mesh (optional)
- API Gateway with rate limiting

## Security Documentation / توثيق الأمان

For detailed security documentation, see:

- [Threat Model (STRIDE)](docs/security/THREAT_MODEL_STRIDE.md)
- [Data Classification](docs/security/DATA_CLASSIFICATION.md)
- [Security Runbook](docs/runbook/SECURITY.md)

## Acknowledgments / شكر وتقدير

We thank the following individuals for responsibly disclosing vulnerabilities:

<!-- List will be updated as vulnerabilities are reported and fixed -->

---

_Last Updated: 2025-12-18_
