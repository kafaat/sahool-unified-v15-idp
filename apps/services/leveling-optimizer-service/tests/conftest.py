"""
Pytest configuration and fixtures for Leveling Optimizer Service tests.

تكوين Pytest والتركيبات لاختبارات خدمة تحسين التسوية.
"""

import os
import sys

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
