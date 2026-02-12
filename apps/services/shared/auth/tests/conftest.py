"""
SAHOOL Authentication Tests - Pytest Configuration
تكوين الاختبارات لوحدة المصادقة

Provides pytest fixtures and configuration for authentication rate limiting tests.
"""

import os
import sys

import pytest

# Add the parent module to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiters between tests to ensure isolation."""
    # This fixture runs before each test to ensure clean state
    yield
    # Cleanup after test if needed
