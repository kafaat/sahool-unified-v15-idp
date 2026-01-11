"""
Pytest configuration for weather-advanced tests
"""

import pytest

# Configure pytest-asyncio to use auto mode
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
