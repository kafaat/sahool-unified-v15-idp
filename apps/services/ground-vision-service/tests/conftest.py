"""Test configuration for ground-vision-service."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from src.main import app

    return TestClient(app)
