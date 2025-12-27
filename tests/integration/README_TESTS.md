# SAHOOL Integration Tests
# اختبارات التكامل لمنصة سهول

## Overview / نظرة عامة

This directory contains comprehensive integration tests for the SAHOOL agricultural platform. These tests validate the interaction between multiple services and ensure the system works correctly as a whole.

تحتوي هذا الدليل على اختبارات تكامل شاملة لمنصة سهول الزراعية. تتحقق هذه الاختبارات من التفاعل بين الخدمات المتعددة وتضمن عمل النظام بشكل صحيح ككل.

## Test Categories / فئات الاختبارات

### 1. Workflow Tests / اختبارات سير العمل

- **`test_alert_workflow.py`** - Alert system workflows (weather, pest, IoT alerts)
  - اختبارات سير عمل نظام التنبيهات (الطقس، الآفات، تنبيهات IoT)

- **`test_billing_workflow.py`** - Subscription and payment workflows
  - اختبارات سير عمل الاشتراكات والدفع

- **`test_field_workflow.py`** - Field management workflows
  - اختبارات سير عمل إدارة الحقول

- **`test_iot_workflow.py`** - IoT device and sensor workflows
  - اختبارات سير عمل أجهزة ومستشعرات IoT

- **`test_marketplace_workflow.py`** - E-commerce marketplace workflows
  - اختبارات سير عمل السوق الإلكترونية

- **`test_notification_workflow.py`** - Notification delivery workflows
  - اختبارات سير عمل توصيل الإشعارات

- **`test_user_journey.py`** - Complete end-to-end user journeys
  - رحلات المستخدم الكاملة من البداية للنهاية

### 2. Service Integration Tests / اختبارات تكامل الخدمات

- **`test_api_endpoints.py`** - REST API endpoint tests
  - اختبارات نقاط نهاية REST API

- **`test_data_flow.py`** - Data flow between services (NATS, Redis, PostgreSQL)
  - تدفق البيانات بين الخدمات

- **`test_identity_flows.py`** - Authentication and authorization flows
  - تدفقات المصادقة والتفويض

- **`test_service_health.py`** - Service health check tests
  - اختبارات فحص صحة الخدمات

### 3. Package Tests / اختبارات الحزم

- **`test_starter_package.py`** - Starter plan features
- **`test_professional_package.py`** - Professional plan features
- **`test_enterprise_package.py`** - Enterprise plan features

## Running Tests / تشغيل الاختبارات

### Prerequisites / المتطلبات الأساسية

1. **Docker and Docker Compose** installed
2. **Python 3.11+** with pytest
3. **Environment variables** configured

### Quick Start / بداية سريعة

```bash
# 1. Start test environment
docker-compose -f docker-compose.test.yml up -d

# 2. Wait for services to be ready (30 seconds)
sleep 30

# 3. Run all integration tests
pytest tests/integration/ -v

# 4. Run specific test file
pytest tests/integration/test_alert_workflow.py -v

# 5. Run tests with specific markers
pytest tests/integration/ -m "not slow" -v

# 6. Stop test environment
docker-compose -f docker-compose.test.yml down
```

### Running Tests in CI/CD / تشغيل الاختبارات في CI/CD

```bash
# Run with coverage report
pytest tests/integration/ \
  --cov=apps/services \
  --cov-report=html \
  --cov-report=term \
  --junit-xml=test-results/junit.xml \
  -v
```

## Test Markers / علامات الاختبارات

Tests are organized using pytest markers:

- `@pytest.mark.integration` - Integration test
- `@pytest.mark.asyncio` - Async test (requires pytest-asyncio)
- `@pytest.mark.slow` - Slow test (may take >10 seconds)
- `@pytest.mark.api` - API endpoint test
- `@pytest.mark.dataflow` - Data flow test

### Running Specific Categories / تشغيل فئات محددة

```bash
# Run only fast tests
pytest tests/integration/ -m "not slow"

# Run only API tests
pytest tests/integration/ -m api

# Run only data flow tests
pytest tests/integration/ -m dataflow
```

## Test Fixtures / إعدادات الاختبارات

### Available Fixtures / الإعدادات المتاحة

The `conftest.py` file provides comprehensive fixtures:

#### Service Clients / عملاء الخدمات

- `http_client` - Generic async HTTP client with retries
- `field_ops_client` - Field operations service client
- `weather_client` - Weather service client
- `billing_client` - Billing service client
- `ai_advisor_client` - AI advisor client

#### Data Factories / مصانع البيانات

- `field_factory` - Create test field data
- `notification_factory` - Create notification data
- `iot_factory` - Create IoT sensor data
- `payment_factory` - Create payment data
- `alert_factory` - Create alert data
- `marketplace_factory` - Create marketplace product data
- `task_factory` - Create task data
- `device_factory` - Create IoT device data
- `order_factory` - Create order data
- `review_factory` - Create review data

#### Utilities / أدوات مساعدة

- `auth_headers` - Authentication headers
- `service_urls` - Service URL mappings
- `test_config` - Test configuration
- `wait_for_services` - Wait for service availability

### Example Usage / مثال على الاستخدام

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_example(
    http_client,
    service_urls,
    field_factory,
    auth_headers
):
    # Create test field data
    field_data = field_factory.create(name="Test Field", crop_type="wheat")

    # Get service URL
    field_url = service_urls["field_ops"]

    # Make API request
    response = await http_client.post(
        f"{field_url}/api/v1/fields",
        json=field_data,
        headers=auth_headers
    )

    assert response.status_code == 201
```

## Writing New Tests / كتابة اختبارات جديدة

### Test Structure / بنية الاختبار

Follow the Arrange-Act-Assert pattern:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_new_workflow(http_client, service_urls, auth_headers):
    """
    اختبار سير عمل جديد

    Test new workflow:
    1. Setup initial state
    2. Perform action
    3. Verify results
    """
    # Arrange - إعداد
    url = service_urls["service_name"]
    test_data = {"key": "value"}

    # Act - تنفيذ
    response = await http_client.post(
        f"{url}/api/endpoint",
        json=test_data,
        headers=auth_headers
    )

    # Assert - التحقق
    assert response.status_code == 200
    result = response.json()
    assert "expected_field" in result
```

### Best Practices / أفضل الممارسات

1. **Use descriptive test names** in both English and Arabic
2. **Document test steps** in docstrings
3. **Use factories** for test data generation
4. **Clean up** resources after tests
5. **Handle timeouts** gracefully
6. **Test both success and failure** scenarios
7. **Use appropriate markers** (@pytest.mark.slow, etc.)
8. **Mock external services** when necessary

## Test Data Management / إدارة بيانات الاختبار

### Database Cleanup / تنظيف قاعدة البيانات

The `cleanup_test_data` fixture automatically cleans up test data after each test:

```python
@pytest.fixture(autouse=True)
def cleanup_test_data(db_cursor):
    """Auto-cleanup after each test"""
    yield
    # Cleanup happens here
```

### Isolation / العزل

Each test should be independent and not rely on other tests' data.

## Troubleshooting / استكشاف الأخطاء

### Common Issues / المشاكل الشائعة

1. **Services not ready**
   ```bash
   # Wait longer for services
   sleep 60
   # Or check service logs
   docker-compose -f docker-compose.test.yml logs service_name
   ```

2. **Database connection errors**
   ```bash
   # Restart PostgreSQL
   docker-compose -f docker-compose.test.yml restart postgres_test
   ```

3. **NATS connection errors**
   ```bash
   # Check NATS health
   curl http://localhost:8223/healthz
   ```

4. **Port conflicts**
   ```bash
   # Check which ports are in use
   netstat -tuln | grep LISTEN
   # Update port mappings in docker-compose.test.yml
   ```

### Debug Mode / وضع التصحيح

Run tests with verbose output and keep containers:

```bash
# Run with debug output
pytest tests/integration/ -vv --log-cli-level=DEBUG

# Keep containers after test failure
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Coverage Goals / أهداف التغطية

Target coverage for integration tests:

- **Workflow Coverage**: 80%+ of user journeys
- **API Coverage**: 70%+ of endpoints
- **Service Integration**: 75%+ of service interactions
- **Error Handling**: 60%+ of error scenarios

## Continuous Integration / التكامل المستمر

### GitHub Actions

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start test environment
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Wait for services
        run: sleep 60

      - name: Run integration tests
        run: |
          docker-compose -f docker-compose.test.yml run test_runner \
            pytest tests/integration/ -v --junit-xml=test-results/junit.xml

      - name: Cleanup
        run: docker-compose -f docker-compose.test.yml down -v
```

## Performance Testing / اختبار الأداء

Some tests include performance benchmarks:

```bash
# Run with timing information
pytest tests/integration/ -v --durations=10
```

## Contributing / المساهمة

When adding new integration tests:

1. Create tests in appropriate workflow file
2. Use existing fixtures and factories
3. Add Arabic documentation
4. Update this README if adding new categories
5. Ensure tests pass in CI/CD

## Resources / موارد

- [Pytest Documentation](https://docs.pytest.org/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [SAHOOL Platform Docs](../../docs/README.md)

## Support / الدعم

For issues or questions:
- Create an issue in the repository
- Contact the platform team
- Check existing test examples

---

**Last Updated**: 2025-12-27
**Version**: 1.0.0
**Maintained by**: SAHOOL Platform Team
