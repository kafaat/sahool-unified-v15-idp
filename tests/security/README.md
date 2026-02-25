# Security Tests

Tests that verify the platform's defenses against common attack vectors including authentication bypass, SQL injection, and CSRF exploits. These tests run without external services — all attack scenarios are simulated against local implementations.

## Running

```bash
# All security tests
pytest tests/security/ -v

# Individual test files
pytest tests/security/test_authentication_bypass.py -v
pytest tests/security/test_sql_injection.py -v
pytest tests/security/test_csrf_protection.py -v

# As part of full CI
make ci
```

## Test Files

### `test_authentication_bypass.py`

Tests JWT security against known bypass techniques:

- Expired token rejection
- Invalid signature detection
- Missing required claims (`exp`, `sub`, `tenant_id`)
- Algorithm confusion attacks (e.g., `alg: none`)
- Token revocation via JTI blocklist
- Token replay after revocation
- Malformed token formats (empty string, random bytes, truncated)

### `test_sql_injection.py`

Validates that query building uses parameterized queries and rejects injection payloads:

- 18 standard SQL injection payloads (DROP TABLE, UNION SELECT, SLEEP, etc.)
- Parameterized SELECT, INSERT, UPDATE, DELETE builders
- Table and column identifier validation (`.isidentifier()` guard)
- Batch insert protection
- Search query sanitization

### `test_csrf_protection.py`

Tests CSRF token lifecycle:

- Token generation tied to session ID
- HMAC-SHA256 signature validation
- Expiry enforcement
- Session mismatch rejection
- Double-submit cookie pattern
- Tampering detection (altered payload)

## Design

These tests use local mock implementations (no live services) so they can run in any CI environment. The mock classes mirror the actual platform patterns:

- `JWTAuthenticator` — mirrors `shared.auth.jwt_handler`
- `ParameterizedQueryBuilder` — mirrors asyncpg parameterized query patterns
- `CSRFTokenManager` — mirrors CSRF middleware behavior

## Related Tools

The platform also runs automated security scanning in CI:

```bash
make secrets-scan     # Gitleaks secret detection
make deps-audit       # npm security audit
# CI workflows: security-checks.yml, codeql-analysis.yml, security-audit.yml
```
