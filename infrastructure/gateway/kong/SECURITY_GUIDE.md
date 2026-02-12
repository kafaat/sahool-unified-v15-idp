# Kong API Gateway Security Best Practices
# أفضل ممارسات أمان بوابة Kong API

**SAHOOL Platform - Agricultural Intelligence Platform**
**Version:** v16.1.0
**Last Updated:** 2026-02-11

---

## Security Checklist | قائمة التحقق الأمنية

### Pre-Production Security Checklist

- [ ] **CORS Configuration**
  - [ ] Replace wildcard `*` with specific domains
  - [ ] Set `credentials: true` for authenticated endpoints
  - [ ] Use `kong-cors-production.yml` template

- [ ] **Admin API Security**
  - [ ] Admin API bound to `127.0.0.1` only (✅ Already configured)
  - [ ] Admin API not exposed to internet
  - [ ] Strong authentication on Admin API
  - [ ] Audit logging enabled for Admin operations

- [ ] **Authentication**
  - [ ] JWT secrets are 32+ characters
  - [ ] Secrets stored in environment variables (not hardcoded)
  - [ ] Token expiration configured (default: 1 hour)
  - [ ] Refresh token rotation enabled
  - [ ] Consider RS256 for enhanced security

- [ ] **Rate Limiting**
  - [ ] Redis-based rate limiting for distributed clusters
  - [ ] Different tiers for different user types
  - [ ] Stricter limits on auth endpoints (login, register)
  - [ ] Extra strict on sensitive operations (billing, payments)

- [ ] **IP Restrictions**
  - [ ] Billing endpoints restricted to internal networks (✅ Configured)
  - [ ] IoT gateway restricted to device networks (✅ Configured)
  - [ ] Admin endpoints restricted to office IPs
  - [ ] Metrics endpoints restricted to monitoring tools

- [ ] **Security Headers**
  - [ ] `X-Content-Type-Options: nosniff` (✅ Configured)
  - [ ] `X-Frame-Options: DENY` (✅ Configured)
  - [ ] `X-XSS-Protection: 1; mode=block` (✅ Configured)
  - [ ] `Strict-Transport-Security` with HSTS (✅ Configured)
  - [ ] `Content-Security-Policy` configured
  - [ ] Remove `Server` and `X-Powered-By` headers (✅ Configured)

- [ ] **Bot Protection**
  - [ ] Bot detection plugin enabled (✅ Configured)
  - [ ] Scanner tools blocked (sqlmap, Nikto, etc.)
  - [ ] Legitimate bots allowed (Googlebot, etc.)

- [ ] **TLS/SSL**
  - [ ] Valid SSL certificates installed
  - [ ] TLS 1.2+ only (disable TLS 1.0, 1.1)
  - [ ] Strong cipher suites configured
  - [ ] HTTPS redirect enabled

- [ ] **Request Validation**
  - [ ] Request size limiting enabled (10MB default) (✅ Configured)
  - [ ] Input validation on all POST/PUT endpoints
  - [ ] SQL injection protection
  - [ ] XSS protection

- [ ] **Monitoring & Logging**
  - [ ] Prometheus metrics enabled (✅ Configured)
  - [ ] Error logs to centralized logging (Loki)
  - [ ] Security events logged and alerted
  - [ ] Audit trail for sensitive operations

---

## Security Configurations | التكوينات الأمنية

### 1. Production CORS Configuration

**File:** `kong-cors-production.yml`

```yaml
- name: cors
  config:
    origins:
      - "https://app.sahool.com"
      - "https://admin.sahool.com"
      - "https://mobile.sahool.com"
    credentials: true
    max_age: 86400
```

**Implementation:**
```bash
# Update kong.yml CORS plugin with production domains
# Reload Kong
docker compose exec kong-dbless kong reload
```

---

### 2. IP Restriction for Sensitive Services

**Already Configured:**
- ✅ **billing-core**: Internal networks only
- ✅ **iot-gateway**: Internal networks only

**Add for:**
```yaml
# Admin dashboard (example)
- name: admin-dashboard
  routes:
    - name: admin-route
      paths: ["/admin"]
  plugins:
    - name: ip-restriction
      config:
        allow:
          - "10.0.0.0/8"      # Internal
          - "192.168.0.0/16"  # Office network
          - "203.0.113.0/24"  # VPN range (example)
        status: 403
        message: "Access denied. Admin access restricted."
```

---

### 3. JWT Configuration Best Practices

**Current Setup:**
- Algorithm: HS256 (HMAC with SHA-256)
- Secrets: Environment variables

**Recommended Upgrade (RS256):**
```yaml
jwt_secrets:
  - key: sahool-jwt-rsa
    algorithm: RS256
    rsa_public_key: |
      -----BEGIN PUBLIC KEY-----
      <Your RSA Public Key>
      -----END PUBLIC KEY-----
```

**Benefits:**
- Public key for verification (no shared secret)
- Private key never leaves auth service
- Better for microservices architecture

**Generate Keys:**
```bash
# Generate RSA key pair
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -outform PEM -pubout -out public.pem

# Use private key in auth service
# Use public key in Kong JWT consumer
```

---

### 4. Rate Limiting Tiers (Already Configured)

**File:** `kong-rate-limiting-tiers.yml`

| Tier | Requests/Min | Requests/Hour | Use Case |
|------|--------------|---------------|----------|
| **Trial** | 10 | 100 | Free tier users |
| **Starter** | 30 | 500 | Basic subscription |
| **Professional** | 60 | 2000 | Pro users |
| **Enterprise** | 120 | 5000 | Enterprise customers |
| **Research** | 60 | 1000 | Research institutions |
| **Internal** | 1000 | 50000 | Service-to-service |

**Additional Auth Endpoint Limits:**
```yaml
# Login endpoint (prevent brute force)
- name: rate-limiting
  config:
    minute: 5
    hour: 20
    policy: redis
    redis_host: kong-redis
```

---

### 5. Security Headers (Already Configured)

**Global Plugin:**
```yaml
- name: response-transformer
  config:
    add:
      headers:
        - "X-Content-Type-Options: nosniff"
        - "X-Frame-Options: DENY"
        - "X-XSS-Protection: 1; mode=block"
        - "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
        - "Referrer-Policy: strict-origin-when-cross-origin"
        - "Permissions-Policy: geolocation=(), microphone=(), camera=()"
    remove:
      headers:
        - "Server"
        - "X-Powered-By"
```

**CSP Header (Add for production):**
```yaml
# Content Security Policy
- "Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.sahool.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.sahool.com; frame-ancestors 'none'"
```

---

### 6. Bot Detection (Already Configured)

**Global Plugin:**
```yaml
- name: bot-detection
  config:
    deny:
      - "sqlmap"
      - "Nikto"
      - "masscan"
      - "nuclei"
      - "nmap"
    allow:
      - "Googlebot"
      - "bingbot"
```

**Add More Protection:**
```yaml
# Additional malicious patterns
deny:
  - ".*sql.*inject.*"
  - ".*union.*select.*"
  - ".*drop.*table.*"
  - ".*xss.*"
  - ".*script.*alert.*"
```

---

### 7. TLS/SSL Configuration

**Current:** HTTP only (development)

**Production Setup:**
```yaml
# In docker-compose.yml
KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
KONG_SSL_CERT: /etc/kong/ssl/sahool.com.crt
KONG_SSL_CERT_KEY: /etc/kong/ssl/sahool.com.key

# Force HTTPS redirect
- name: request-termination
  route:
    protocols: ["http"]
  config:
    status_code: 301
    message: "Redirecting to HTTPS"
```

**Certificate Management:**
```bash
# Using Let's Encrypt
certbot certonly --standalone -d api.sahool.com

# Copy to Kong
cp /etc/letsencrypt/live/api.sahool.com/fullchain.pem infrastructure/gateway/kong/ssl/
cp /etc/letsencrypt/live/api.sahool.com/privkey.pem infrastructure/gateway/kong/ssl/

# Reload Kong
docker compose exec kong-dbless kong reload
```

---

## Security Monitoring | مراقبة الأمان

### Prometheus Alerts (Already Configured)

**File:** `alerts/kong-alerts.yml`

```yaml
groups:
  - name: kong_security
    rules:
      # High error rate (potential attack)
      - alert: HighErrorRate
        expr: rate(kong_http_requests_total{code=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      # Excessive rate limiting triggers
      - alert: ExcessiveRateLimiting
        expr: rate(kong_rate_limiting_exceeded[5m]) > 100
        for: 2m
        annotations:
          summary: "Potential DDoS attack"

      # Suspicious 403 responses
      - alert: HighForbiddenRate
        expr: rate(kong_http_requests_total{code="403"}[5m]) > 10
        for: 3m
        annotations:
          summary: "High rate of forbidden requests"
```

### Security Event Logging

```yaml
# Add file-log plugin for security events
- name: file-log
  config:
    path: /var/log/kong/security.log
    custom_fields_by_lua:
      ip: "return ngx.var.remote_addr"
      user_agent: "return ngx.req.get_headers()['user-agent']"
      method: "return ngx.req.get_method()"
      path: "return ngx.var.request_uri"
```

---

## Incident Response | الاستجابة للحوادث

### 1. DDoS Attack

**Detection:**
- Sudden spike in request rate
- High rate limiting triggers
- Service degradation

**Response:**
```bash
# 1. Identify attacker IP
docker compose logs kong-dbless | grep -E "429|403" | awk '{print $1}' | sort | uniq -c | sort -nr

# 2. Block IP immediately
# Add to kong.yml > ip-restriction > deny
- name: ip-restriction
  config:
    deny:
      - "1.2.3.4"  # Attacker IP

# 3. Reload Kong
docker compose exec kong-dbless kong reload

# 4. Enable CDN/WAF protection (Cloudflare)
```

### 2. SQL Injection Attempt

**Detection:**
- Logs contain SQL keywords (UNION, SELECT, DROP)
- Bot detection triggers on sqlmap

**Response:**
```bash
# 1. Review logs
docker compose logs kong-dbless | grep -iE "sql|union|select|drop"

# 2. Block offending IPs
# 3. Audit database for unauthorized access
# 4. Implement parameterized queries in services
```

### 3. JWT Compromise

**Detection:**
- Unusual usage patterns for a token
- Token used from multiple IPs

**Response:**
```bash
# 1. Revoke specific token (add to blocklist)
# 2. Rotate JWT secret immediately
# 3. Invalidate all existing tokens
# 4. Force re-authentication

# Rotate secret
# Update .env
JWT_SECRET_KEY=$(openssl rand -base64 32)
# Restart services
docker compose restart kong-dbless user-service
```

---

## Compliance | الامتثال

### GDPR Compliance

- [ ] Data encryption in transit (TLS)
- [ ] Data encryption at rest (database)
- [ ] Access logging for audit trail
- [ ] Right to deletion implemented
- [ ] Data breach notification process

### PCI-DSS (for payment processing)

- [ ] TLS 1.2+ only
- [ ] Strong cryptography
- [ ] Secure key management
- [ ] Access controls
- [ ] Monitoring and logging

### SAHOOL Security Standards

- [ ] All sensitive data encrypted
- [ ] Authentication on all endpoints
- [ ] Rate limiting on all endpoints
- [ ] Audit logging for sensitive operations
- [ ] Security headers on all responses

---

## Testing Security | اختبار الأمان

### Security Testing Checklist

```bash
# 1. Test CORS
curl -I -X OPTIONS http://localhost:8000/api/v1/fields \
  -H "Origin: https://evil.com"
# Should return 403 or no CORS headers

# 2. Test rate limiting
for i in {1..100}; do 
  curl http://localhost:8000/api/v1/weather
done
# Should return 429 after limit

# 3. Test IP restriction
curl http://localhost:8000/api/v1/billing \
  -H "X-Forwarded-For: 1.2.3.4"
# Should return 403

# 4. Test security headers
curl -I http://localhost:8000/api/v1/health
# Check for X-Content-Type-Options, X-Frame-Options, etc.

# 5. Test bot detection
curl http://localhost:8000/api/v1/fields \
  -H "User-Agent: sqlmap/1.0"
# Should return 403
```

### Penetration Testing

**Recommended Tools:**
- OWASP ZAP
- Burp Suite
- Nikto (test blocking)
- sqlmap (test protection)

**Annual Security Audit:**
- External penetration testing
- Code review
- Configuration audit
- Compliance verification

---

## Updates and Patching | التحديثات والتصحيحات

### Kong Updates

```bash
# Check current version
docker exec kong-dbless kong version

# Check for updates
docker pull kong:latest

# Review release notes
# https://github.com/Kong/kong/releases

# Update docker-compose.yml
# Test in staging first
# Apply to production during maintenance window
```

### Security Patches

**Immediate (Critical):**
- Zero-day vulnerabilities
- Remote code execution
- Authentication bypass

**Scheduled (High/Medium):**
- Denial of service
- Information disclosure
- Security improvements

**Process:**
1. Monitor Kong security advisories
2. Test patch in staging
3. Schedule maintenance window
4. Apply patch to production
5. Verify functionality
6. Monitor for issues

---

## Contact and Escalation | الاتصال والتصعيد

**Security Team:** security@sahool.com
**Incident Response:** incidents@sahool.com
**24/7 On-Call:** +966-XX-XXXX-XXXX

**Escalation Path:**
1. Level 1: DevOps Engineer
2. Level 2: Security Team
3. Level 3: CISO
4. Level 4: CTO

**Incident Severity:**
- **P0 (Critical)**: Active breach, system compromised
- **P1 (High)**: Vulnerability exploited, data at risk
- **P2 (Medium)**: Security control bypassed
- **P3 (Low)**: Configuration issue, no active threat

---

## Additional Resources | موارد إضافية

- [Kong Security Best Practices](https://docs.konghq.com/gateway/latest/production/security-update-process/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SAHOOL Security Policy](../../governance/SECURITY_POLICY.md)
- [Kong Security Audit Report](../../tests/middleware/KONG_SECURITY_AUDIT.md)

---

**Document Version:** 1.0
**Maintained By:** Security Team & Platform Engineering
**Review Cycle:** Quarterly
**Next Review:** 2026-05-11
