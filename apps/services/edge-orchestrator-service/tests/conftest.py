# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Pytest configuration and fixtures for Edge Orchestrator Service tests.

تكوين Pytest والتركيبات لاختبارات خدمة تنسيق الحافة.
"""

import asyncio
import os
import sys
from collections.abc import Generator
from uuid import uuid4

import pytest

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src module to avoid cross-service contamination in CI
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]

# Set test environment variables before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client():
    """Create test client for the FastAPI application."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("fastapi not installed")
    from src.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def default_tenant_id() -> str:
    """Default tenant ID for tests."""
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def auth_headers(default_tenant_id: str) -> dict[str, str]:
    """Authentication headers for requests."""
    return {
        "X-Tenant-ID": default_tenant_id,
        "Content-Type": "application/json",
    }


@pytest.fixture
def sample_device_data() -> dict:
    """Sample edge device data for testing."""
    return {
        "name": "Test Jetson Device",
        "name_ar": "جهاز جيتسون للاختبار",
        "description": "A test edge device",
        "description_ar": "جهاز حافة للاختبار",
        "device_type": "jetson_orin_nano",
        "farm_id": str(uuid4()),
        "ip_address": "192.168.1.100",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "serial_number": f"TEST-{uuid4().hex[:8].upper()}",
        "tags": ["test", "edge", "jetson"],
        "metadata": {
            "location": "test_field",
            "purpose": "testing",
        },
    }


@pytest.fixture
def sample_job_data(sample_device_data: dict) -> dict:
    """Sample job data for testing."""
    return {
        "job_type": "inference",
        "device_id": str(uuid4()),  # Will be replaced with actual device ID
        "priority": "normal",
        "config": {
            "model_name": "yolo26-s",
            "confidence_threshold": 0.5,
            "max_detections": 100,
            "timeout_seconds": 300,
        },
        "metadata": {
            "test": True,
        },
    }


@pytest.fixture
def sample_sync_request() -> dict:
    """Sample sync request data for testing."""
    return {
        "direction": "upload",
        "data_types": ["inference_results", "sensor_data"],
        "force": False,
    }


@pytest.fixture
def sample_deploy_request() -> dict:
    """Sample deploy request data for testing."""
    return {
        "model_name": "yolo26-s",
        "model_version": "latest",
        "model_format": "tensorrt",
        "force_update": False,
        "validate_after_deploy": True,
    }
