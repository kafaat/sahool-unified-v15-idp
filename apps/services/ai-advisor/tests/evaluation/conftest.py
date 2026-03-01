"""
Pytest configuration for agent evaluation tests
تكوين pytest لاختبارات تقييم الوكلاء
"""

import os

import pytest



@pytest.fixture(scope="session")
def evaluation_mode():
    """Check if running in evaluation mode"""
    return os.getenv("EVALUATION_MODE", "false").lower() == "true"


@pytest.fixture(scope="session")
def api_endpoint():
    """Get API endpoint for testing"""
    return os.getenv("API_ENDPOINT", "http://localhost:8000")
