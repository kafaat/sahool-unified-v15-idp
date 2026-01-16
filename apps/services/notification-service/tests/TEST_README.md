# SAHOOL Notification Service - Test Suite

Comprehensive test coverage for the SAHOOL notification service, including unit tests, integration tests, and service layer tests.

## Test Files

### 1. `test_notification_controller.py`

Tests for FastAPI REST API endpoints:

- Health check endpoints
- Notification creation (custom, weather alerts, pest alerts, irrigation reminders)
- Notification retrieval (farmer notifications, broadcast notifications)
- Notification updates (mark as read)
- Farmer registration and preferences
- Statistics endpoints

**Coverage:**

- ✅ API endpoint validation
- ✅ Request/response handling
- ✅ Error handling and HTTP status codes
- ✅ Authentication and authorization
- ✅ Query parameter validation

### 2. `test_notification_service_comprehensive.py`

Tests for business logic and service layer:

- Notification creation with user preferences
- Multi-channel notification delivery
- Recipient targeting (by governorate, crop, farmer)
- Weather alert message generation
- NATS event integration
- Error handling and retry logic

**Coverage:**

- ✅ Notification creation logic
- ✅ User preference checking
- ✅ Channel delivery (SMS, Email, Push)
- ✅ Recipient determination
- ✅ Bilingual support (Arabic/English)
- ✅ Error handling and logging

### 3. `test_push_service.py`

Tests for Firebase Cloud Messaging integration:

- Client initialization (credentials file, dictionary, environment)
- Single device notifications
- Topic-based notifications
- Multicast notifications
- Topic subscription management
- Retry logic
- Priority handling (Android/iOS)

**Coverage:**

- ✅ Firebase client initialization
- ✅ Push notification sending
- ✅ Topic management
- ✅ Multicast operations
- ✅ Bilingual notifications
- ✅ Priority levels
- ✅ Error handling

### 4. `test_email_sms_services.py`

Tests for Email (SendGrid) and SMS (Twilio) integrations:

- Client initialization
- Email sending (HTML, plain text, templates)
- SMS sending (single, bulk)
- Phone number and email validation
- Retry logic
- Bilingual content selection

**Coverage:**

- ✅ Email client (SendGrid)
- ✅ SMS client (Twilio)
- ✅ Bulk operations
- ✅ Template emails
- ✅ Validation
- ✅ Error handling

### 5. `conftest.py`

Shared test fixtures and configurations:

- Mock objects (notifications, farmers, clients)
- Test clients (async, sync)
- Sample test data
- Pytest markers

## Running Tests

### Prerequisites

Install test dependencies:

```bash
cd apps/services/notification-service
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Run Specific Test Files

```bash
# Run controller tests only
pytest tests/test_notification_controller.py -v

# Run service tests only
pytest tests/test_notification_service_comprehensive.py -v

# Run push notification tests only
pytest tests/test_push_service.py -v

# Run email/SMS tests only
pytest tests/test_email_sms_services.py -v
```

### Run Specific Test Classes or Methods

```bash
# Run a specific test class
pytest tests/test_notification_controller.py::TestHealthEndpoint -v

# Run a specific test method
pytest tests/test_push_service.py::TestFirebaseClientInitialization::test_initialize_with_credentials_path -v
```

### Run Tests with Markers

```bash
# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run smoke tests
pytest tests/ -m smoke
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -n 4
```

## Coverage Report

Generate and view coverage report:

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Open coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Configuration

### pytest.ini

Create a `pytest.ini` file in the notification-service directory:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    smoke: Smoke tests
    slow: Slow running tests
```

### Environment Variables for Testing

Set these environment variables for integration tests:

```bash
# For SMS tests
export TWILIO_ACCOUNT_SID=your_test_account_sid
export TWILIO_AUTH_TOKEN=your_test_auth_token
export TWILIO_FROM_NUMBER=+1234567890

# For Email tests
export SENDGRID_API_KEY=your_test_api_key
export SENDGRID_FROM_EMAIL=noreply@test.com
export SENDGRID_FROM_NAME="Test Service"

# For Firebase tests
export FIREBASE_CREDENTIALS_PATH=/path/to/test-credentials.json
# OR
export FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'

# For Database tests
export DATABASE_URL=postgresql://user:password@localhost:5432/test_db
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Notification Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd apps/services/notification-service
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run tests
        run: |
          cd apps/services/notification-service
          pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Mocking and Test Doubles

All external services are mocked in tests:

- **Firebase**: Mocked with `unittest.mock`
- **Twilio**: Mocked with `unittest.mock`
- **SendGrid**: Mocked with `unittest.mock`
- **Database**: Mocked with `unittest.mock.AsyncMock`
- **NATS**: Mocked for event subscription tests

No real API calls are made during tests to ensure:

- Fast test execution
- No external dependencies
- No costs incurred
- Consistent, reproducible results

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on others
2. **Clarity**: Test names clearly describe what is being tested
3. **Coverage**: Aim for >80% code coverage
4. **Speed**: Tests should run quickly (< 5 seconds for unit tests)
5. **Mocking**: Mock external services to avoid real API calls
6. **Fixtures**: Use shared fixtures from `conftest.py`
7. **Assertions**: Use clear, specific assertions
8. **Cleanup**: Reset state after each test

## Troubleshooting

### Common Issues

1. **Import Errors**

   ```bash
   # Ensure you're in the correct directory
   cd apps/services/notification-service
   # Add src to Python path
   export PYTHONPATH="${PYTHONPATH}:${PWD}"
   ```

2. **Async Test Errors**

   ```bash
   # Install pytest-asyncio
   pip install pytest-asyncio
   ```

3. **Database Connection Errors**
   - Tests should mock database calls
   - Check that mocks are properly configured

4. **Module Not Found**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   ```

## Test Metrics

Current test coverage:

- **Total Tests**: 100+
- **Controller Tests**: 25+
- **Service Tests**: 30+
- **Push Service Tests**: 25+
- **Email/SMS Tests**: 20+
- **Code Coverage**: >85%

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests pass before committing
3. Maintain >80% code coverage
4. Update this README if adding new test files
5. Use descriptive test names
6. Add docstrings to test functions

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
