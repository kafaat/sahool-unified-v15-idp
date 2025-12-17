# Security Testing Guide
# دليل اختبار الأمان

This guide provides instructions for testing the security fixes and running security audits on the SAHOOL platform.

## Quick Security Checks

### 1. Test CORS Configuration

Test that CORS is properly configured and rejects unauthorized origins:

```bash
# Test with unauthorized origin (should be rejected)
curl -H "Origin: https://malicious-site.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8095/api/v1/diagnose

# Expected response: No CORS headers or error

# Test with authorized origin (should be accepted)
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS http://localhost:8095/api/v1/diagnose

# Expected response: CORS headers present
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
```

Test all three services:
- crop-health-ai: `http://localhost:8095`
- yield-engine: `http://localhost:8098`
- virtual-sensors: `http://localhost:8096`

### 2. Test Password Requirements

Verify that services fail without proper passwords:

```bash
# Should fail without .env file
docker-compose config

# Should show error like:
# Error: POSTGRES_PASSWORD not set in .env file

# Create .env file
./scripts/security/generate-env.sh

# Should now work
docker-compose config
```

### 3. Verify Environment Variables

Check that no default passwords are being used:

```bash
# Check docker-compose configuration
docker-compose config | grep -E "PASSWORD"

# Should NOT see:
# - "sahool" (old default postgres password)
# - "changeme" (old default redis password)

# Should see environment variable references like:
# - ${POSTGRES_PASSWORD:?Error...}
# - ${REDIS_PASSWORD:?Error...}
```

## Automated Security Scanning

### Python Dependencies

```bash
# Install security audit tools
pip install safety pip-audit

# Run safety check
cd kernel-services-v15.3/crop-health-ai
safety check --json > ../../reports/security/safety-crop-health-ai.json

# Run pip-audit
pip-audit --format json > ../../reports/security/pip-audit-crop-health-ai.json
```

### Node.js Dependencies

```bash
# Check for vulnerabilities
cd web_admin
npm audit

# Get JSON report
npm audit --json > ../reports/security/npm-audit-web-admin.json

# Fix automatically (if possible)
npm audit fix

# For breaking changes
npm audit fix --force
```

### Flutter Dependencies

```bash
cd mobile/sahool_field_app
flutter pub audit
```

### Docker Image Scanning

```bash
# Install Trivy
# On macOS:
brew install trivy

# On Linux:
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Scan images
trivy image postgis/postgis:15-3.3
trivy image redis:7-alpine
trivy image kong:3.4

# Scan custom images (after building)
docker-compose build
trivy image sahool-crop-health-ai:latest
trivy image sahool-yield-engine:latest
```

## Manual Security Testing

### 1. SQL Injection Testing

Test database query parameters:

```bash
# Test field search with SQL injection attempt
curl -X GET "http://localhost:8080/api/v1/fields?name=test' OR '1'='1"

# Should NOT:
# - Return all fields
# - Cause database error

# Should:
# - Treat as literal string
# - Return empty or proper filtered results
```

### 2. XSS Testing

Test input sanitization:

```bash
# Test with XSS payload
curl -X POST http://localhost:8095/api/v1/fields \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<script>alert(\"XSS\")</script>",
    "crop_type": "wheat"
  }'

# Response should:
# - Escape/sanitize the script tags
# - Not execute JavaScript
```

### 3. Authentication Testing

Test JWT validation:

```bash
# Test without token (should fail)
curl -X GET http://localhost:8095/api/v1/diagnose

# Expected: 401 Unauthorized

# Test with invalid token (should fail)
curl -X GET http://localhost:8095/api/v1/diagnose \
  -H "Authorization: Bearer invalid_token"

# Expected: 401 Unauthorized

# Test with expired token (should fail)
# (Create a token with exp in the past)
```

### 4. Rate Limiting Testing

Test API rate limits (if implemented):

```bash
# Send multiple requests quickly
for i in {1..100}; do
  curl -X GET http://localhost:8095/health &
done
wait

# Should see rate limit responses after threshold
# Expected: 429 Too Many Requests
```

## Security Test Automation

Create a security test suite:

```python
# tests/security/test_cors.py
import pytest
import requests

BASE_URLS = [
    "http://localhost:8095",  # crop-health-ai
    "http://localhost:8098",  # yield-engine
    "http://localhost:8096",  # virtual-sensors
]

@pytest.mark.parametrize("base_url", BASE_URLS)
def test_cors_rejects_unauthorized_origin(base_url):
    """Test that CORS rejects unauthorized origins."""
    headers = {
        "Origin": "https://malicious-site.com",
        "Access-Control-Request-Method": "POST",
    }
    
    response = requests.options(
        f"{base_url}/api/v1/diagnose",
        headers=headers
    )
    
    # Should not have CORS headers for unauthorized origin
    assert "Access-Control-Allow-Origin" not in response.headers or \
           response.headers["Access-Control-Allow-Origin"] != "https://malicious-site.com"

@pytest.mark.parametrize("base_url", BASE_URLS)
def test_cors_accepts_authorized_origin(base_url):
    """Test that CORS accepts authorized origins."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    }
    
    response = requests.options(
        f"{base_url}/api/v1/diagnose",
        headers=headers
    )
    
    # Should have CORS headers for authorized origin
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"
    assert response.headers.get("Access-Control-Allow-Credentials") == "true"

def test_cors_does_not_allow_wildcard():
    """Ensure no service uses wildcard CORS."""
    for base_url in BASE_URLS:
        response = requests.options(base_url)
        assert response.headers.get("Access-Control-Allow-Origin") != "*"
```

Run security tests:

```bash
# Run security test suite
pytest tests/security/ -v

# Run with coverage
pytest tests/security/ -v --cov=src --cov-report=html
```

## OWASP ZAP Scanning

Run automated security scanning with OWASP ZAP:

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run ZAP baseline scan
docker run --rm -v $(pwd)/reports/security:/zap/wrk/:rw \
  --network="host" \
  owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8095 \
  -J zap-crop-health-ai.json \
  -r zap-crop-health-ai.html

# Scan other services
docker run --rm -v $(pwd)/reports/security:/zap/wrk/:rw \
  --network="host" \
  owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8098 \
  -J zap-yield-engine.json

docker run --rm -v $(pwd)/reports/security:/zap/wrk/:rw \
  --network="host" \
  owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8096 \
  -J zap-virtual-sensors.json
```

## Security Checklist

Before marking security as "complete", verify:

### CORS Security
- [ ] No wildcard (`*`) origins in any service
- [ ] Origins are explicitly listed in configuration
- [ ] Development origins only enabled in development environment
- [ ] CORS tested with unauthorized and authorized origins
- [ ] All three services (crop-health-ai, yield-engine, virtual-sensors) updated

### Password Security
- [ ] No default passwords in docker-compose.yml
- [ ] Password generation script creates strong passwords (32+ chars)
- [ ] .env.template exists with clear instructions
- [ ] .env file is in .gitignore
- [ ] Services fail to start without proper .env file
- [ ] JWT secret is 64+ characters

### Code Security
- [ ] No hardcoded secrets in code
- [ ] All user inputs validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] Error messages don't expose sensitive information
- [ ] Authentication required for protected endpoints
- [ ] Authorization checks in place

### Dependency Security
- [ ] Python: `safety check` passes
- [ ] Node.js: `npm audit` shows no high/critical issues
- [ ] Flutter: `flutter pub audit` passes
- [ ] Docker images scanned with Trivy

### Documentation
- [ ] SECURITY_FIXES.md created and complete
- [ ] CONTRIBUTING.md includes security guidelines
- [ ] .env.template documented
- [ ] Security testing guide created

## Continuous Security Monitoring

### GitHub Actions

Add security scanning to CI/CD:

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Python Security Scan
        run: |
          pip install safety
          safety check --json > safety-report.json
      
      - name: Node.js Security Scan
        run: |
          cd web_admin
          npm audit --json > npm-audit-report.json
```

### Scheduled Reviews

- **Weekly:** Automated dependency scanning
- **Monthly:** Manual security review
- **Quarterly:** Penetration testing
- **Annually:** Full security audit

## Incident Response

If a security issue is found:

1. **DO NOT** create a public issue
2. **DO** email security@sahool.io immediately
3. **DO** create a private security advisory on GitHub
4. **WAIT** for security team response before disclosing

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [CWE/SANS Top 25](https://www.sans.org/top25-software-errors/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Security is everyone's responsibility!** 🔒
