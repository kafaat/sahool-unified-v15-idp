# WS Gateway Service - Tests

# اختبارات خدمة بوابة WebSocket

## Overview | نظرة عامة

Comprehensive test suite for the WebSocket gateway service.
مجموعة اختبارات شاملة لخدمة بوابة WebSocket.

## Test Structure | بنية الاختبارات

- `conftest.py`: Shared fixtures and test configuration
- `test_rooms.py`: Unit tests for room management
- `test_api_endpoints.py`: Integration tests for API endpoints

## Running Tests | تشغيل الاختبارات

### Run all tests | تشغيل جميع الاختبارات

```bash
pytest
```

### Run specific test file | تشغيل ملف محدد

```bash
pytest tests/test_rooms.py
pytest tests/test_api_endpoints.py
```

### Run with coverage | مع تغطية الكود

```bash
pytest --cov=src --cov-report=html
```

## Test Coverage | تغطية الاختبارات

The test suite covers:

- ✅ Room creation and management
- ✅ WebSocket connection handling
- ✅ Multi-room subscriptions
- ✅ Broadcast functionality
- ✅ User/tenant/field targeted messaging
- ✅ JWT authentication and validation
- ✅ Authorization and tenant isolation
- ✅ API endpoints (health, stats, broadcast)
- ✅ Connection lifecycle management

## Requirements | المتطلبات

```
pytest==8.3.4
pytest-asyncio==0.24.0
PyJWT  # For JWT testing
```

## Security Testing | اختبار الأمان

Tests include security scenarios:

- Invalid JWT tokens
- Expired tokens
- Cross-tenant access prevention
- Admin privilege verification
