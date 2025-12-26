# SAHOOL Integration Tests
# اختبارات التكامل لمنصة سهول

Comprehensive integration tests for the SAHOOL agricultural platform covering all three service packages: Starter, Professional, and Enterprise.

## 📋 Overview

This test suite provides end-to-end integration testing for:

- **Starter Package** (حزمة المبتدئين):
  - Field CRUD operations
  - Weather forecast retrieval
  - Astronomical calendar
  - Agro advisor recommendations
  - Notifications

- **Professional Package** (الحزمة الاحترافية):
  - Satellite imagery retrieval
  - NDVI analysis
  - Crop health AI detection
  - Irrigation recommendations
  - Inventory management

- **Enterprise Package** (حزمة المؤسسات):
  - AI advisor multi-agent queries
  - IoT gateway data flow
  - Marketplace operations
  - Billing and subscriptions
  - Research core experiments

- **Event Flow Tests** (اختبارات تدفق الأحداث):
  - Field created → triggers satellite analysis
  - Weather alert → triggers notifications
  - Low stock → triggers alert
  - IoT reading → triggers irrigation recommendation

## 🚀 Quick Start

### Prerequisites

```bash
# Required software
- Docker & Docker Compose
- Python 3.11+
- pip
```

### Running Tests

```bash
# 1. Start test environment
docker-compose -f docker-compose.test.yml up -d

# 2. Run all integration tests
cd tests/integration
./run_tests.sh

# 3. Run specific package tests
./run_tests.sh starter           # Starter package only
./run_tests.sh professional      # Professional package only
./run_tests.sh enterprise        # Enterprise package only
./run_tests.sh events            # Event flow tests only

# 4. View results
open ../../test-results/report-*.html
```

### Using Make (if configured)

```bash
# From project root
make test-integration              # Run all integration tests
make test-integration-starter      # Run starter tests
make test-integration-professional # Run professional tests
make test-integration-enterprise   # Run enterprise tests
```

## 📁 File Structure

```
tests/integration/
├── conftest.py                      # Pytest fixtures and configuration
├── test_starter_package.py         # Starter package tests
├── test_professional_package.py    # Professional package tests
├── test_enterprise_package.py      # Enterprise package tests
├── test_event_flow.py              # NATS event flow tests
├── run_tests.sh                    # Test runner script
└── README.md                       # This file
```

## 🔧 Configuration

### Environment Variables

The tests use environment variables for configuration:

```bash
# Database
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=sahool_test
export POSTGRES_PASSWORD=test_password_123
export POSTGRES_DB=sahool_test

# Redis
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=test_redis_pass

# NATS
export NATS_HOST=localhost
export NATS_PORT=4222

# Qdrant
export QDRANT_HOST=localhost
export QDRANT_PORT=6333

# JWT
export JWT_SECRET_KEY=test-secret-key-for-tests-only-do-not-use-in-production-32chars
```

### Docker Compose Test Environment

The `docker-compose.test.yml` file in the project root provides:

- PostgreSQL with PostGIS (port 5433)
- Redis (port 6380)
- NATS (port 4223)
- Qdrant (port 6335)
- All SAHOOL services with `_test` suffix

## 📝 Test Data Factories

The `conftest.py` provides factory classes for generating test data:

```python
# Field data
field_data = field_factory.create(name="Test Field", crop_type="wheat")

# Weather query
weather_query = weather_factory.create(latitude=15.3694, longitude=44.1910)

# Notification
notification = notification_factory.create(user_id="user-123", notification_type="weather_alert")

# Inventory item
item = inventory_factory.create(item_type="fertilizer")

# AI query
query = ai_query_factory.create(language="ar")

# Payment
payment = payment_factory.create(amount=100.0, currency="YER")

# IoT reading
reading = iot_factory.create(sensor_type="soil_moisture")

# Research experiment
experiment = experiment_factory.create()
```

## 🎯 Test Markers

Tests use pytest markers for categorization:

```python
@pytest.mark.integration      # Integration test
@pytest.mark.event_flow        # Event flow test
@pytest.mark.asyncio           # Async test
```

Run tests by marker:

```bash
# Run only integration tests
pytest -m integration

# Run only event flow tests
pytest -m event_flow

# Run async tests
pytest -m asyncio
```

## 📊 Test Reports

Test results are generated in the `test-results/` directory:

- **HTML Report**: `report-{package}.html` - Human-readable test report
- **JUnit XML**: `junit-{package}.xml` - CI/CD compatible format
- **Coverage Report**: `coverage/index.html` - Code coverage analysis

## 🔍 Debugging Tests

### Verbose Output

```bash
# Enable verbose output
VERBOSE=1 ./run_tests.sh

# Or with pytest directly
pytest -vv tests/integration/test_starter_package.py
```

### Fail Fast

```bash
# Stop on first failure
FAIL_FAST=1 ./run_tests.sh

# Or with pytest
pytest -x tests/integration/
```

### Running Individual Tests

```bash
# Run single test file
pytest tests/integration/test_starter_package.py

# Run single test class
pytest tests/integration/test_starter_package.py::TestFieldOperations

# Run single test method
pytest tests/integration/test_starter_package.py::TestFieldOperations::test_create_field
```

## 🐛 Troubleshooting

### Services Not Ready

If tests fail with connection errors:

```bash
# Check service health
docker-compose -f docker-compose.test.yml ps

# View service logs
docker-compose -f docker-compose.test.yml logs field_ops_test
docker-compose -f docker-compose.test.yml logs weather_core_test

# Restart services
docker-compose -f docker-compose.test.yml restart
```

### Database Issues

```bash
# Connect to test database
docker exec -it sahool-postgres-test psql -U sahool_test -d sahool_test

# Check tables
\dt

# View data
SELECT * FROM fields LIMIT 10;
```

### Clean Up

```bash
# Stop and remove test containers
docker-compose -f docker-compose.test.yml down

# Remove volumes (complete cleanup)
docker-compose -f docker-compose.test.yml down -v
```

## 📚 Additional Resources

- [SAHOOL Testing Guide](../../docs/TESTING.md)
- [API Documentation](../../docs/API.md)
- [Architecture Overview](../../docs/ARCHITECTURE.md)
- [Docker Compose Guide](../../docker/README.md)

## 🤝 Contributing

When adding new integration tests:

1. Use the existing factory classes for test data
2. Follow the naming convention: `test_{feature}_*`
3. Add Arabic comments for test descriptions
4. Include proper assertions with error messages
5. Clean up test data in teardown
6. Update this README if adding new test files

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Contact the SAHOOL Platform Team
- Check the [Testing Documentation](../../docs/TESTING.md)

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Maintainer**: SAHOOL Platform Team
