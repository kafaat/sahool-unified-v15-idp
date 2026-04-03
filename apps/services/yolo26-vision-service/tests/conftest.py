"""Pytest configuration and fixtures for YOLO26 Vision Service tests."""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure the service source is importable
SERVICE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SERVICE_ROOT))
sys.path.insert(0, str(SERVICE_ROOT.parent.parent.parent))  # repo root


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    """Set test environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("NATS_URL", "")
    monkeypatch.setenv("REDIS_URL", "")
    monkeypatch.setenv("MODEL_BASE_PATH", "/tmp/yolo26-test-models")  # nosec B108 - test env var for model path
    monkeypatch.setenv("DEVICE", "cpu")
    monkeypatch.setenv("HALF_PRECISION", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")


@pytest.fixture
def mock_torch():
    """Mock torch module for tests without GPU."""
    with patch("torch.cuda.is_available", return_value=False), patch("torch.cuda.device_count", return_value=0):
        yield


@pytest.fixture
def mock_model_manager():
    """Mock YOLO26 model manager for unit tests."""
    manager = MagicMock()
    manager.load_model = AsyncMock()
    manager.get_loaded_models = MagicMock(return_value=[])
    manager.clear_cache = MagicMock()
    manager.gpu_memory_info = None
    return manager
