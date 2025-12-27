# Notification Service - Extended Tests
# اختبارات موسعة لخدمة الإشعارات

## Overview | نظرة عامة

Extended test suite for personalized notification service.
مجموعة اختبارات موسعة لخدمة الإشعارات المخصصة.

## Test Structure | بنية الاختبارات

- `test_notifications.py`: Existing notification tests
- `test_notification_service_extended.py`: Extended tests for types, enums, and database

## Running Tests | تشغيل الاختبارات

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_notification_service_extended.py

# With coverage
pytest --cov=src --cov-report=html
```

## Test Coverage | تغطية الاختبارات

- ✅ Notification types and enums
- ✅ Geographic enumerations (Governorates, Crops)
- ✅ Priority levels
- ✅ Communication channels
- ✅ Database initialization and health checks
- ✅ Arabic translations
