# SAHOOL Test Coverage Analysis Report

**Generated**: 2026-01-11
**Branch**: claude/analyze-test-coverage-LaKa7

---

## Executive Summary

| Category           | With Tests | Without Tests | Coverage % |
| ------------------ | ---------- | ------------- | ---------- |
| **Services**       | 39         | 15            | 72%        |
| **Shared Modules** | 7          | 13            | 35%        |
| **Kernel Modules** | 1          | 2             | 33%        |

---

## Services Test Coverage

### Services WITH Tests (39 services)

| Service                     | Test Files | Type    | Priority    |
| --------------------------- | ---------- | ------- | ----------- |
| ai-advisor                  | 12         | Python  | Core        |
| satellite-service           | 14         | Python  | Deprecated  |
| vegetation-analysis-service | 14         | Python  | Replacement |
| notification-service        | 10         | Python  | Core        |
| ai-agents-core              | 8          | Python  | Core        |
| iot-gateway                 | 6          | Python  | Core        |
| ws-gateway                  | 4          | Node.js | Core        |
| crop-intelligence-service   | 3          | Python  | Replacement |
| fertilizer-advisor          | 3          | Python  | Deprecated  |
| field-core                  | 3          | Node.js | Deprecated  |
| field-management-service    | 3          | Node.js | Replacement |
| inventory-service           | 3          | Python  | Core        |
| ndvi-processor              | 3          | Python  | Core        |
| weather-advanced            | 3          | Python  | Deprecated  |
| weather-service             | 3          | Python  | Replacement |
| advisory-service            | 2          | Python  | Replacement |
| agro-advisor                | 2          | Python  | Core        |
| agro-rules                  | 2          | Python  | Core        |
| equipment-service           | 2          | Node.js | Core        |
| field-chat                  | 2          | Python  | Core        |
| field-ops                   | 2          | Python  | Deprecated  |
| task-service                | 2          | Node.js | Core        |
| yield-engine                | 2          | Python  | Deprecated  |
| alert-service               | 3          | Python  | Core        |
| astronomical-calendar       | 1          | Python  | Core        |
| billing-core                | 1          | Node.js | Core        |
| code-fix-agent              | 1          | Python  | AI          |
| code-review-service         | 1          | Node.js | AI          |
| crop-health                 | 1          | Python  | Core        |
| crop-health-ai              | 1          | Python  | Deprecated  |
| field-service               | 1          | Node.js | Core        |
| indicators-service          | 1          | Python  | Core        |
| irrigation-smart            | 1          | Python  | Core        |
| mcp-server                  | 1          | Python  | Core        |
| ndvi-engine                 | 1          | Python  | Core        |
| provider-config             | 1          | Python  | Config      |
| shared                      | 1          | Python  | Shared      |
| virtual-sensors             | 1          | Python  | Core        |
| weather-core                | 1          | Python  | Core        |

### Services WITHOUT Tests (15 services)

| Service                  | Type    | Files | Status | Priority |
| ------------------------ | ------- | ----- | ------ | -------- |
| **agent-registry**       | Python  | 4     | FROZEN | Low      |
| **user-service**         | Node.js | 30    | FROZEN | Low      |
| **globalgap-compliance** | Python  | 17    | FROZEN | Low      |
| chat-service             | Node.js | 25    | Active | Medium   |
| community-chat           | Node.js | 92    | Active | High     |
| crop-growth-model        | Node.js | 35    | Active | High     |
| demo-data                | Unknown | 0     | Active | Low      |
| disaster-assessment      | Node.js | 99    | Active | High     |
| field-intelligence       | Python  | 10    | Active | Medium   |
| iot-service              | Node.js | 103   | Active | High     |
| lai-estimation           | Node.js | 134   | Active | High     |
| marketplace-service      | Node.js | 126   | Active | High     |
| research-core            | Node.js | 433   | Active | High     |
| yield-prediction         | Node.js | 99    | Active | Medium   |
| yield-prediction-service | Node.js | 185   | Active | High     |

**Note**: Services marked FROZEN are deprecated and do not require new tests.

---

## Shared Modules Test Coverage

### Modules WITH Tests (7 modules)

| Module     | Test File                                           | Coverage |
| ---------- | --------------------------------------------------- | -------- |
| cache      | test_cache_redis_sentinel.py                        | Partial  |
| events     | test_events_publisher.py, test_events_subscriber.py | Good     |
| guardrails | test_guardrails_input_filter.py                     | Partial  |
| middleware | test_request_tenant_middleware.py                   | Partial  |
| secrets    | test_secrets.py                                     | Good     |
| security   | test_security_middleware.py                         | Partial  |
| versioning | test_api_versioning.py                              | Good     |

### Modules WITHOUT Tests (13 modules)

| Module              | Priority | Reason                         |
| ------------------- | -------- | ------------------------------ |
| **auth**            | Critical | Core authentication - JWT, 2FA |
| **contracts**       | High     | API contracts validation       |
| **domain**          | High     | Domain models                  |
| **monitoring**      | High     | Prometheus metrics             |
| **observability**   | High     | Logging, tracing               |
| **mcp**             | Medium   | Model Context Protocol         |
| **file_validation** | Medium   | File upload security           |
| **telemetry**       | Medium   | OpenTelemetry                  |
| a2a                 | Low      | Agent-to-Agent protocol        |
| design-system       | Low      | Frontend components            |
| globalgap           | Low      | Compliance (deprecated?)       |
| libs                | Low      | Utility libraries              |
| templates           | Low      | Template files                 |

---

## Kernel Modules Test Coverage

| Module    | Has Tests | Priority |
| --------- | --------- | -------- |
| field_ops | Yes       | Core     |
| analytics | No        | High     |
| common    | No        | Critical |

---

## Test Infrastructure Summary

### Test Directories

```
tests/
├── a2a/          # Agent-to-Agent protocol tests
├── e2e/          # End-to-end tests (3 workflows)
├── evaluation/   # AI agent evaluation
├── factories/    # Test factories (field, user)
├── guardrails/   # Input validation tests
├── integration/  # Integration tests (27 tests)
├── load/         # Load tests (Locust)
├── simulation/   # Platform simulation
├── smoke/        # Import verification
└── unit/         # Unit tests (20+ tests)
```

### Test Statistics

| Category          | Count |
| ----------------- | ----- |
| Total test files  | 88    |
| Unit tests        | 20    |
| Integration tests | 27    |
| E2E tests         | 3     |
| Smoke tests       | 2     |
| Guardrails tests  | 2     |
| Evaluation tests  | 1     |

---

## Recommendations

### High Priority (Critical Path)

1. **Add tests for `shared/auth`**
   - JWT token validation
   - 2FA flow
   - Token revocation
   - RBAC permissions

2. **Add tests for `apps/kernel/common`**
   - Database middleware
   - Queue utilities
   - Monitoring setup

3. **Add tests for large Node.js services**:
   - `research-core` (433 files)
   - `yield-prediction-service` (185 files)
   - `lai-estimation` (134 files)
   - `marketplace-service` (126 files)

### Medium Priority

4. **Add tests for `shared/contracts`**
   - API contract validation
   - Event schema validation

5. **Add tests for `shared/monitoring`**
   - Prometheus metrics
   - Health checks

6. **Add tests for Python services without tests**:
   - `field-intelligence` (10 files)
   - `globalgap-compliance` (17 files) - if not deprecated

### Low Priority

7. **Add tests for utility modules**:
   - `shared/libs`
   - `shared/templates`

8. **Improve existing test coverage**:
   - Services with only 1 test file
   - Partial module coverage

---

## Test Coverage Targets

| Milestone   | Target | Services | Modules |
| ----------- | ------ | -------- | ------- |
| **Current** | 72%    | 39/54    | 7/20    |
| **Phase 1** | 80%    | 43/54    | 12/20   |
| **Phase 2** | 90%    | 49/54    | 18/20   |
| **Target**  | 95%    | 51/54    | 19/20   |

---

## Excluded from Coverage

These services are deprecated and excluded from coverage targets:

- `agent-registry` - FROZEN (port conflict)
- `user-service` - FROZEN (port conflict)
- `globalgap-compliance` - FROZEN (port conflict)
- `satellite-service` - DEPRECATED (replaced)
- `weather-advanced` - DEPRECATED (replaced)
- `crop-health-ai` - DEPRECATED (replaced)
- `fertilizer-advisor` - DEPRECATED (replaced)
- `field-core` - DEPRECATED (replaced)
- `field-ops` - DEPRECATED (replaced)
- `yield-engine` - DEPRECATED (replaced)

---

## Next Steps

1. Create test templates for Python and Node.js services
2. Set up CI coverage reporting
3. Add coverage gates to PR workflow
4. Prioritize critical path testing

---

_Last Updated: 2026-01-11_
