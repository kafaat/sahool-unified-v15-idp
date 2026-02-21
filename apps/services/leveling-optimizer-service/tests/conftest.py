"""
Pytest configuration and fixtures for Leveling Optimizer Service tests.

تكوين Pytest والتركيبات لاختبارات خدمة تحسين التسوية.
"""

import os

# Set test environment variables before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-only-32chars"
