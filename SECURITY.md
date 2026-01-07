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

## Security Measures | إجراءات الأمان

### Code Security | أمان الكود

- **CodeQL**: Automated semantic code analysis for Python and TypeScript
- **Bandit**: Python-specific security linter
- **Semgrep**: Pattern-based security scanning
- **Trivy**: Vulnerability scanning for dependencies and containers

### Infrastructure Security | أمان البنية التحتية

- All services run as non-root users
- Container images are scanned for vulnerabilities
- Secrets are managed through environment variables
- Database connections use encrypted channels

### Authentication & Authorization | المصادقة والتفويض

- JWT-based authentication
- Role-based access control (RBAC)
- Rate limiting on all API endpoints
- Token expiration and refresh mechanisms

## Security Best Practices | أفضل الممارسات الأمنية

1. Never commit secrets or credentials to the repository
2. Use environment variables for sensitive configuration
3. Keep dependencies up to date
4. Follow the principle of least privilege
5. Enable branch protection rules
6. Require code reviews for all changes

## Contact | التواصل

- Security issues: security@kafaat.sa
- General inquiries: dev@kafaat.sa
