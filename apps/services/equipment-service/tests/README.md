# Equipment Service - Extended Tests

# اختبارات موسعة لخدمة المعدات

## Overview | نظرة عامة

Extended test suite for agricultural equipment management service.
مجموعة اختبارات موسعة لخدمة إدارة المعدات الزراعية.

## Test Structure | بنية الاختبارات

- `test_equipment.py`: Existing equipment tests
- `test_equipment_extended.py`: Extended tests for models, enums, and validation

## Running Tests | تشغيل الاختبارات

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_equipment_extended.py

# With coverage
pytest --cov=src --cov-report=html
```

## Test Coverage | تغطية الاختبارات

- ✅ Equipment types (tractor, pump, drone, etc.)
- ✅ Equipment status tracking
- ✅ Maintenance priority levels
- ✅ Maintenance types
- ✅ Data model validation
- ✅ Equipment creation and updates
- ✅ Business logic tests (placeholders for extension)
