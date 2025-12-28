"""
Pytest configuration for agent evaluation tests
تكوين pytest لاختبارات تقييم الوكلاء
"""

import pytest
import os


def pytest_configure(config):
    """Configure pytest for evaluation tests"""
    config.addinivalue_line(
        "markers", "evaluation: marks tests as evaluation tests (deselect with '-m \"not evaluation\"')"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


@pytest.fixture(scope="session")
def evaluation_mode():
    """Check if running in evaluation mode"""
    return os.getenv("EVALUATION_MODE", "false").lower() == "true"


@pytest.fixture(scope="session")
def api_endpoint():
    """Get API endpoint for testing"""
    return os.getenv("API_ENDPOINT", "http://localhost:8000")
