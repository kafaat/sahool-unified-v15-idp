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
