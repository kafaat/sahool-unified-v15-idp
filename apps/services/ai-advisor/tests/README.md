# AI Advisor Service - Tests
# اختبارات خدمة المستشار الذكي

## Overview | نظرة عامة

Comprehensive test suite for the AI Advisor multi-agent system.
مجموعة اختبارات شاملة لنظام المستشار الذكي متعدد الوكلاء.

## Test Structure | بنية الاختبارات

- `conftest.py`: Shared fixtures and test configuration
- `test_base_agent.py`: Unit tests for BaseAgent class
- `test_multi_provider.py`: Unit tests for multi-provider LLM service
- `test_api_endpoints.py`: Integration tests for API endpoints

## Running Tests | تشغيل الاختبارات

### Run all tests | تشغيل جميع الاختبارات
```bash
pytest
```

### Run specific test file | تشغيل ملف اختبار محدد
```bash
pytest tests/test_base_agent.py
pytest tests/test_multi_provider.py
pytest tests/test_api_endpoints.py
```

### Run with coverage | تشغيل مع تغطية الكود
```bash
pytest --cov=src --cov-report=html
```

### Run only unit tests | تشغيل اختبارات الوحدة فقط
```bash
pytest -m unit
```

### Run only integration tests | تشغيل اختبارات التكامل فقط
```bash
pytest -m integration
```

## Test Coverage | تغطية الاختبارات

The test suite covers:
- ✅ BaseAgent initialization and core methods
- ✅ Multi-provider LLM service (Anthropic, OpenAI, Google)
- ✅ Automatic fallback between providers
- ✅ RAG knowledge retrieval
- ✅ API endpoints (ask, diagnose, recommend, analyze-field)
- ✅ Input validation
- ✅ Error handling
- ✅ External tool mocking

## Requirements | المتطلبات

Tests use the following packages (already in requirements.txt):
```
pytest==8.3.4
pytest-asyncio==0.24.0
```

## Mock Strategy | استراتيجية المحاكاة

External dependencies are mocked:
- Anthropic API client
- OpenAI API client
- Google Gemini API client
- RAG embeddings and retriever
- Agricultural tools (crop health, weather, satellite)

This ensures tests run quickly and don't require API keys.
