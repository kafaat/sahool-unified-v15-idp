"""
Pytest Configuration for Security Tests
ضبط اختبارات الأمان
"""

import os
import sys

# Set JWT test environment BEFORE any imports
# This must happen before pytest imports the test modules
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-minimum-32-chars"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ENVIRONMENT"] = "development"

# Force reload of jwt module if it was imported with wrong settings
if "shared.security.jwt" in sys.modules:
    del sys.modules["shared.security.jwt"]

import pytest


@pytest.fixture(autouse=True)
def setup_jwt_env():
    """Ensure JWT environment is set for all tests"""
    original_secret = os.environ.get("JWT_SECRET_KEY")
    original_algo = os.environ.get("JWT_ALGORITHM")
    original_env = os.environ.get("ENVIRONMENT")

    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-minimum-32-chars"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["ENVIRONMENT"] = "development"

    yield

    # Restore original values
    if original_secret:
        os.environ["JWT_SECRET_KEY"] = original_secret
    if original_algo:
        os.environ["JWT_ALGORITHM"] = original_algo
    if original_env:
        os.environ["ENVIRONMENT"] = original_env
