"""
SAHOOL Test Configuration
Centralized pytest configuration for consistent imports across all tests
"""

import sys
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent

# Add all package paths to Python path for consistent imports
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "packages"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "field_suite"))
sys.path.insert(0, str(REPO_ROOT / "archive" / "kernel-legacy"))

# pytest configuration
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no I/O)")
    config.addinivalue_line("markers", "integration: Integration tests (API, database)")
    config.addinivalue_line("markers", "smoke: Smoke tests (import verification)")
    config.addinivalue_line("markers", "slow: Slow running tests")
