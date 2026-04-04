# Integration Test Plan — SAHOOL v16.1 Stabilization
# خطة اختبارات التكامل — تثبيت سهول 16.1

> **Purpose**: Verify all stabilization fixes work together before staging/production
> **When**: Day 7 of the hardening sprint, after all 8 PRs are merged
> **Duration**: 1 full day (8 hours)
> **Environment**: `docker-compose.test.yml` + staging cluster

---

## Test Categories

### Category 1: Authentication & Authorization (2 hours)

#### 1.1 JWT Token Flow
```
TEST: Login → Access Token → Refresh → New Access Token
VERIFY:
  - httpOnly cookie is set by server (not JS)
  - No Cookies.set() in browser after refresh
  - Token uses HS256 only (not HS384/HS512)
  - Expired token → 401 → auto-refresh → retry succeeds
```

#### 1.2 Auth Bypass Prevention
```
TEST: Access protected endpoints without token
VERIFY:
  - GET /farmer/{id} → 401 (not 200 with data)
  - PUT /{id}/preferences → 401
  - PATCH /{id}/read → 401
  - All admin routes → redirect to /login
```

#### 1.3 Tenant Isolation
```
TEST: Tenant A user tries to access Tenant B data
VERIFY:
  - GET /farmer/{tenant_b_farmer_id} → 403
  - Marketplace products filtered by tenant
  - Vector store queries include tenant_id filter
  - Notifications isolated per tenant
```

#### 1.4 Open Redirect Prevention
```
TEST: Login with malicious returnTo parameter
VERIFY:
  - /login?returnTo=https://evil.com → redirects to /dashboard
  - /login?returnTo=//evil.com → redirects to /dashboard
  - /login?returnTo=/dashboard/settings → works correctly
```

#### 1.5 2FA Flow
```
TEST: Login with 2FA enabled account
VERIFY:
  - Initial login → requires_2fa response
  - Submit TOTP code → success
  - Invalid TOTP → error message (no crash)
```

---

### Category 2: Webhook Security (1 hour)

#### 2.1 WhatsApp Webhook HMAC
```
TEST: Send webhook without/with X-Hub-Signature-256
VERIFY:
  - No signature → 401
  - Wrong signature → 401
  - Valid signature → 200 (processes message)
  - GET /webhook (verification) still works
```

#### 2.2 USSD Callback Authentication
```
TEST: Send USSD callback from unauthorized IP
VERIFY:
  - Unknown IP + no HMAC → 401
  - Known IP + valid HMAC → 200
  - Development mode without config → passes (for local testing)
```

#### 2.3 Stripe Webhook Verification
```
TEST: Send fake Stripe webhook event
VERIFY:
  - No stripe-signature header → 400
  - Invalid signature → 400
  - Valid signature → processes event
```

#### 2.4 Tharwatt Webhook Verification
```
TEST: Send fake Tharwatt webhook event
VERIFY:
  - No X-Tharwatt-Signature → 401
  - Invalid signature → 401
  - Valid signature → processes event
```

---

### Category 3: Billing & Payments (1.5 hours)

#### 3.1 Server-Side Pricing
```
TEST: Create subscription with client-supplied price
VERIFY:
  - Custom price in payload → ignored, server price used
  - Invalid plan_id → 400
  - Valid plan_id → correct server-defined price applied
```

#### 3.2 Idempotency
```
TEST: Submit same payment twice with same idempotency key
VERIFY:
  - First request → creates payment
  - Second request (same key) → returns same result (no double charge)
  - Different key → creates new payment
```

#### 3.3 Startup Validation
```
TEST: Start billing-core without STRIPE_API_KEY in production
VERIFY:
  - ENVIRONMENT=production + no key → critical log warning
  - ENVIRONMENT=development + no key → starts normally
```

---

### Category 4: Infrastructure Security (1.5 hours)

#### 4.1 Vault Auto-Unseal
```
TEST: Restart Vault container
VERIFY:
  - Vault auto-unseals via KMS (no manual intervention)
  - Secrets accessible after restart
  - Health endpoint returns sealed=false
```

#### 4.2 Pre-Deploy Validation
```
TEST: Run pre-deploy validation script
VERIFY:
  - ./scripts/pre-deploy-validation.sh → PASS (no CHANGE_ME in critical files)
  - ./scripts/pre-deploy-validation.sh --strict → scans entire repo
```

#### 4.3 EKS Security Groups (Staging Only)
```
TEST: Verify EKS node egress rules after terraform apply
VERIFY:
  - HTTPS (443) outbound → allowed
  - DNS (53) outbound → allowed
  - NTP (123) outbound → allowed
  - Random port (e.g., 4444) outbound → blocked
  - ECR image pulls → work correctly
```

#### 4.4 Kong Configuration
```
TEST: Kong starts with all config files
VERIFY:
  - kong.yml loads without duplicate service errors
  - Prometheus metrics on 127.0.0.1:8100 (not 0.0.0.0)
  - AI/LLM services have JWT plugin enabled
  - Rate limiting uses Redis (not local)
```

#### 4.5 NDVI Production Guard
```
TEST: Request NDVI in ENVIRONMENT=production without sentinelhub
VERIFY:
  - Returns None (not mock data)
  - Logs error with hint to install sentinelhub
  - ENVIRONMENT=development → returns mock data with data_source="mock"
```

---

### Category 5: IoT & Device Security (30 min)

#### 5.1 Auto-Register Block
```
TEST: Unknown MQTT device sends data in ENVIRONMENT=production
VERIFY:
  - IOT_AUTO_REGISTER=true + ENVIRONMENT=production → device rejected
  - IOT_AUTO_REGISTER=true + ENVIRONMENT=development → device auto-registered
  - IOT_AUTO_REGISTER=false → device rejected with error log
```

---

### Category 6: Data Flow & Events (1 hour)

#### 6.1 NATS Event Publishing
```
TEST: Publish event and verify consumption
VERIFY:
  - Event published with correct subject pattern
  - Consumer receives and processes event
  - DLQ receives failed events
  - Duplicate event_id → deduplicated (if Redis dedup enabled)
```

#### 6.2 Rate Limiter
```
TEST: Exceed rate limit threshold
VERIFY:
  - Requests within limit → 200
  - Requests over limit → 429
  - Rate limit uses JWT tenant_id (not X-Tenant-ID header)
  - LRUDict handles max-size eviction correctly
```

---

### Category 7: Admin Portal (30 min)

#### 7.1 Critical Flows
```
TEST: Admin login → dashboard → farms → settings
VERIFY:
  - Login works with valid credentials
  - returnTo sanitized (no open redirect)
  - /api/auth/send-otp accessible pre-login
  - Token refresh preserves httpOnly (check cookie attributes)
  - Farms page shows error message on API failure
  - Middleware logs errors in production mode
```

---

## Test Execution Checklist

### Before Testing
- [ ] All 8 PRs merged to `stabilization/v16.1-hardening`
- [ ] `docker-compose up` starts cleanly (no errors)
- [ ] All services report healthy (`make health`)
- [ ] Test database seeded (`make db-seed`)
- [ ] Test environment variables configured

### During Testing
- [ ] Category 1: Auth & Authorization — PASS / FAIL
- [ ] Category 2: Webhook Security — PASS / FAIL
- [ ] Category 3: Billing & Payments — PASS / FAIL
- [ ] Category 4: Infrastructure Security — PASS / FAIL
- [ ] Category 5: IoT & Device Security — PASS / FAIL
- [ ] Category 6: Data Flow & Events — PASS / FAIL
- [ ] Category 7: Admin Portal — PASS / FAIL

### After Testing
- [ ] All categories PASS
- [ ] No new errors in logs (`docker-compose logs | grep ERROR`)
- [ ] Prometheus metrics collecting
- [ ] Test report documented
- [ ] Ready for staging deployment

## Pass/Fail Criteria

| Criteria | Threshold |
|----------|-----------|
| Category pass rate | **7/7 categories** must pass |
| Critical test failures | **0 allowed** |
| New error log entries | **0 new ERROR/CRITICAL** entries |
| Service health | **100%** services healthy |
| Response time regression | **< 10%** degradation from baseline |
