# SAHOOL Platform - Comprehensive Test Automation System
# نظام الاختبار الآلي الشامل لمنصة سهول

## Overview - نظرة عامة

This directory contains a comprehensive automated testing system for the SAHOOL agricultural platform. The test suite covers all 41+ microservices and ensures platform reliability, performance, and correctness.

يحتوي هذا الدليل على نظام اختبار آلي شامل لمنصة سهول الزراعية. تغطي مجموعة الاختبارات جميع الخدمات الصغيرة (41+) وتضمن موثوقية المنصة وأدائها ودقتها.

## Test Structure - هيكل الاختبارات

```
tests/
├── integration/              # Integration tests - اختبارات التكامل
│   ├── conftest.py          # Service fixtures - تهيئة الخدمات
│   ├── test_service_health.py    # Health checks for all 41 services
│   ├── test_api_endpoints.py     # API endpoint testing
│   └── test_data_flow.py         # Data flow between services
│
├── e2e/                     # End-to-end workflow tests - اختبارات سير العمل الكاملة
│   ├── conftest.py          # E2E fixtures - تهيئة E2E
│   ├── test_field_workflow.py    # Field creation → NDVI → Weather → Recommendations
│   ├── test_payment_workflow.py  # Billing → Tharwatt → Invoice
│   └── test_ai_advisor_workflow.py  # Question → Multi-Agent → Answer
│
├── unit/                    # Unit tests - اختبارات الوحدة
├── smoke/                   # Smoke tests - اختبارات الدخان
├── simulation/              # Simulation tests - اختبارات المحاكاة
└── factories/               # Test data factories - مصانع بيانات الاختبار
```

## Test Categories - فئات الاختبارات

### 1. Integration Tests (tests/integration/)

#### Service Health Tests
- Tests all 41+ services for health and availability
- Validates infrastructure services (PostgreSQL, Redis, NATS, Qdrant, Kong, etc.)
- Validates application services (Field Ops, Weather, NDVI, AI Advisor, etc.)
- **File**: `test_service_health.py`

#### API Endpoint Tests
- Tests RESTful API endpoints
- Validates request/response formats
- Tests authentication and authorization
- Tests error handling
- **File**: `test_api_endpoints.py`

#### Data Flow Tests
- Tests NATS messaging between services
- Tests Redis caching behavior
- Tests PostgreSQL database operations
- Tests Qdrant vector search
- Tests service-to-service communication
- **File**: `test_data_flow.py`

### 2. End-to-End Workflow Tests (tests/e2e/)

#### Field Workflow Test
Complete agricultural field management workflow:
1. Create field in Field Ops
2. Request NDVI analysis
3. Get weather data for field location
4. Receive agricultural recommendations
5. Verify data consistency across services

**File**: `test_field_workflow.py`

#### Payment Workflow Test
Complete payment and billing workflow:
1. Create subscription
2. Create payment intent
3. Process payment via Tharwatt (Yemen payment gateway)
4. Verify payment status
5. Generate and retrieve invoice

**File**: `test_payment_workflow.py`

#### AI Advisor Workflow Test
Complete AI advisor multi-agent workflow:
1. Submit agricultural question (Arabic/English)
2. Multi-agent coordination:
   - Weather Agent
   - Crop Health Agent
   - Satellite Agent
   - Agro Advisor Agent
3. RAG (Retrieval-Augmented Generation) from Qdrant
4. Claude AI generates comprehensive answer
5. Receive and validate response

**File**: `test_ai_advisor_workflow.py`

## Running Tests - تشغيل الاختبارات

### Quick Start - البدء السريع

```bash
# Run all tests
./scripts/run-tests.sh --all

# Run health checks only
./scripts/run-tests.sh --health

# Run integration tests with coverage
./scripts/run-tests.sh --integration --coverage

# Run E2E tests in Docker
./scripts/run-tests.sh --e2e --docker

# Run fast tests (skip slow tests)
./scripts/run-tests.sh --fast
```

### Test Options - خيارات الاختبار

| Option | Description | الوصف |
|--------|-------------|-------|
| `--unit` | Run unit tests only | تشغيل اختبارات الوحدة فقط |
| `--integration` | Run integration tests only | تشغيل اختبارات التكامل فقط |
| `--e2e` | Run E2E workflow tests only | تشغيل اختبارات سير العمل فقط |
| `--health` | Run health check tests only | تشغيل اختبارات الصحة فقط |
| `--all` | Run all tests (default) | تشغيل جميع الاختبارات |
| `--fast` | Skip slow tests | تخطي الاختبارات البطيئة |
| `--verbose` | Verbose output | مخرجات مفصلة |
| `--coverage` | Generate coverage report | إنشاء تقرير التغطية |
| `--docker` | Run in Docker containers | تشغيل في حاويات Docker |
| `--clean` | Clean test environment first | تنظيف بيئة الاختبار أولاً |

### Direct pytest Commands

```bash
# Run specific test file
pytest tests/integration/test_service_health.py -v

# Run tests with specific marker
pytest -m health  # Run health check tests
pytest -m e2e     # Run E2E tests
pytest -m integration  # Run integration tests

# Run tests and generate HTML report
pytest tests/ --html=test-results/report.html

# Run tests with coverage
pytest tests/ --cov=apps --cov-report=html
```

## Docker Test Environment - بيئة اختبار Docker

The test suite includes a Docker Compose configuration for isolated test environments.

### Starting Test Environment

```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Run tests in container
docker-compose -f docker-compose.test.yml exec test_runner pytest tests/

# Stop test environment
docker-compose -f docker-compose.test.yml down
```

### Test Environment Services

The test environment includes:
- PostgreSQL (test database)
- Redis (test cache)
- NATS (test messaging)
- Qdrant (test vector DB)
- Field Ops (test instance)
- NDVI Engine (test instance)
- Weather Core (test instance)
- Billing Core (test instance)
- AI Advisor (test instance)

All services run on different ports to avoid conflicts with development environment.

## Test Configuration - تكوين الاختبارات

### Environment Variables

Test configuration uses environment variables:

```bash
# Database
POSTGRES_USER=sahool_test
POSTGRES_PASSWORD=test_password_123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sahool_test

# Redis
REDIS_PASSWORD=test_redis_pass
REDIS_HOST=localhost
REDIS_PORT=6379

# NATS
NATS_HOST=localhost
NATS_PORT=4222

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# JWT
JWT_SECRET_KEY=test-secret-key-for-tests-only
TEST_JWT_TOKEN=test-jwt-token-for-e2e-tests
```

### pytest Configuration

Test behavior is configured in `pytest.ini`:

```ini
[pytest]
testpaths = tests apps/services
markers =
    integration: Integration tests
    e2e: End-to-end workflow tests
    unit: Unit tests
    health: Health check tests
    slow: Slow tests
```

## Test Coverage - تغطية الاختبارات

### Services Tested (41+ Services)

#### Infrastructure Services (8)
- ✓ PostgreSQL (PostGIS)
- ✓ Kong API Gateway
- ✓ NATS Messaging
- ✓ Redis Cache
- ✓ Qdrant Vector DB
- ✓ MQTT Broker
- ✓ Prometheus
- ✓ Grafana

#### Core Application Services (33+)
- ✓ Field Core
- ✓ Field Operations
- ✓ NDVI Engine
- ✓ Weather Core
- ✓ Field Chat
- ✓ IoT Gateway
- ✓ Agro Advisor
- ✓ WebSocket Gateway
- ✓ Crop Health
- ✓ Task Service
- ✓ Equipment Service
- ✓ Provider Config
- ✓ Crop Health AI
- ✓ Virtual Sensors
- ✓ Community Chat
- ✓ Yield Engine
- ✓ Irrigation Smart
- ✓ Fertilizer Advisor
- ✓ Indicators Service
- ✓ Satellite Service
- ✓ Weather Advanced
- ✓ Notification Service
- ✓ Research Core
- ✓ Disaster Assessment
- ✓ Yield Prediction
- ✓ LAI Estimation
- ✓ Crop Growth Model
- ✓ Marketplace Service
- ✓ Admin Dashboard
- ✓ Billing Core
- ✓ AI Advisor (Multi-Agent System)
- ✓ Astronomical Calendar
- ✓ Agro Rules Worker

### Test Metrics

Generate coverage report:

```bash
./scripts/run-tests.sh --all --coverage
```

View coverage report:
```bash
open htmlcov/index.html
```

## CI/CD Integration - تكامل CI/CD

### GitHub Actions

Add to `.github/workflows/tests.yml`:

```yaml
name: SAHOOL Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: ./scripts/run-tests.sh --all --docker
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitLab CI

Add to `.gitlab-ci.yml`:

```yaml
test:
  script:
    - ./scripts/run-tests.sh --all --docker
  artifacts:
    reports:
      junit: test-results/junit.xml
      coverage: test-results/coverage.xml
```

## Best Practices - أفضل الممارسات

### Writing Tests

1. **Use descriptive test names** - استخدم أسماء وصفية للاختبارات
   ```python
   async def test_field_creation_with_valid_data():
       # Test implementation
   ```

2. **Use fixtures for setup** - استخدم التهيئة للإعداد
   ```python
   @pytest.fixture
   async def test_field():
       return {"name": "Test Field", "area": 10.5}
   ```

3. **Test both success and failure cases** - اختبر حالات النجاح والفشل
   ```python
   async def test_valid_field_creation():
       # Test valid case

   async def test_invalid_field_creation():
       # Test invalid case
   ```

4. **Use markers for categorization** - استخدم العلامات للتصنيف
   ```python
   @pytest.mark.integration
   @pytest.mark.slow
   async def test_complete_workflow():
       # Test implementation
   ```

5. **Add bilingual comments** - أضف تعليقات ثنائية اللغة
   ```python
   # Test field creation workflow
   # اختبار سير عمل إنشاء الحقل
   ```

## Troubleshooting - حل المشكلات

### Common Issues

#### Tests failing due to services not running
```bash
# Start services first
docker-compose up -d

# Or run in Docker test environment
./scripts/run-tests.sh --docker
```

#### Port conflicts
```bash
# Clean environment
./scripts/run-tests.sh --clean

# Use Docker test environment (different ports)
./scripts/run-tests.sh --docker
```

#### Slow tests timing out
```bash
# Skip slow tests
./scripts/run-tests.sh --fast
```

## Contributing - المساهمة

When adding new services or features:

1. Add service health check to `test_service_health.py`
2. Add API endpoint tests to `test_api_endpoints.py`
3. Add integration tests to `test_data_flow.py`
4. Add E2E workflow tests if applicable
5. Update this README with new test coverage

## Resources - المصادر

- [pytest Documentation](https://docs.pytest.org/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SAHOOL Platform Documentation](../docs/)

## Contact - التواصل

For questions or issues with the test suite:
- Open an issue in the repository
- Contact the SAHOOL Platform Team

---

**Last Updated**: 2024-12-24
**Test Suite Version**: 1.0.0
**SAHOOL Platform Version**: 15.3.2
