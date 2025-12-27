# Inventory Service - Tests
# اختبارات خدمة المخزون

## Overview | نظرة عامة

Comprehensive test suite for agricultural inventory management and analytics.
مجموعة اختبارات شاملة لإدارة وتحليلات المخزون الزراعي.

## Test Structure | بنية الاختبارات

- `conftest.py`: Shared fixtures and test configuration
- `test_inventory_analytics.py`: Unit tests for analytics and forecasting
- `test_api_endpoints.py`: Integration tests for API endpoints

## Running Tests | تشغيل الاختبارات

### Run all tests | تشغيل جميع الاختبارات
```bash
pytest
```

### Run specific test file | تشغيل ملف محدد
```bash
pytest tests/test_inventory_analytics.py
pytest tests/test_api_endpoints.py
```

### Run with coverage | مع تغطية الكود
```bash
pytest --cov=src --cov-report=html
```

## Test Coverage | تغطية الاختبارات

The test suite covers:
- ✅ Consumption forecasting and predictions
- ✅ Inventory valuation (FIFO, weighted average)
- ✅ ABC/Pareto analysis
- ✅ Turnover ratio calculations
- ✅ Slow-moving and dead stock identification
- ✅ Reorder point optimization
- ✅ Cost analysis by field/crop
- ✅ Waste tracking and analysis
- ✅ Dashboard metrics generation
- ✅ API endpoints and input validation

## Requirements | المتطلبات

```
pytest==8.3.4
pytest-asyncio==0.24.0
aiosqlite  # For in-memory testing
```

## Database Testing | اختبار قاعدة البيانات

Tests use an in-memory SQLite database for fast, isolated testing.
No external database required for running tests.
