# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Test Configuration and Fixtures for LLM Orchestrator Service.
إعدادات الاختبار والتجهيزات لخدمة تنسيق نماذج اللغة الكبيرة.
"""

import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]
from unittest.mock import AsyncMock

import pytest

# Set test environment variables before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["LOG_LEVEL"] = "WARNING"

try:
    from src.main import app
except ImportError:
    pytest.skip("llm-orchestrator-service dependencies not installed", allow_module_level=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before all tests run."""
    yield


@pytest.fixture
def client(setup_test_environment):
    """Create test client."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("fastapi not installed")
    return TestClient(app)


@pytest.fixture
def sample_user_intent():
    """Sample user intent for testing."""
    return {
        "text": "What disease is affecting my wheat crop?",
        "language": "en",
        "field_id": "field_001",
        "tenant_id": "tenant_001",
    }


@pytest.fixture
def sample_user_intent_arabic():
    """Sample Arabic user intent for testing."""
    return {
        "text": "ما هو المرض الذي يصيب محصول القمح الخاص بي؟",
        "language": "ar",
        "field_id": "field_001",
        "tenant_id": "tenant_001",
    }


@pytest.fixture
def sample_irrigation_intent():
    """Sample irrigation query intent."""
    return {
        "text": "When should I irrigate my field?",
        "language": "en",
        "field_id": "field_002",
    }


@pytest.fixture
def sample_image_intent():
    """Sample image analysis intent."""
    return {
        "text": "Analyze this image for pests",
        "language": "en",
        "image_base64": "base64_encoded_image_data_here",
        "field_id": "field_001",
    }


@pytest.fixture
def mock_agent_executor():
    """Mock agent executor for testing."""
    executor = AsyncMock()
    executor.execute_plan = AsyncMock(return_value=[])
    executor.call_single_agent = AsyncMock(
        return_value={
            "agent_name": "test-agent",
            "success": True,
            "result": {"status": "ok"},
            "latency_ms": 100,
        }
    )
    return executor


@pytest.fixture
def sample_agent_result():
    """Sample agent result for testing."""
    return {
        "agent_name": "crop-intelligence",
        "success": True,
        "result": {
            "overall_health": {"status_en": "good", "status_ar": "جيد"},
            "detection_count": 0,
            "detections": [],
        },
        "latency_ms": 150,
        "cached": False,
    }


@pytest.fixture
def sample_execution_plan():
    """Sample execution plan for testing."""
    return {
        "plan_id": "plan_test_001",
        "agents": [
            {
                "agent_name": "crop-intelligence",
                "endpoint": "http://localhost:8095/api/v1/disease/detect",
                "method": "POST",
                "params": {},
                "priority": 1,
                "timeout": 30,
            }
        ],
        "execution_mode": "parallel",
        "intent": {
            "intent_type": "crop_disease",
            "confidence": 0.85,
            "entities": {},
            "language_detected": "en",
        },
    }
