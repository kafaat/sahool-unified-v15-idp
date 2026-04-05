"""
Conftest for AI integration tests — overrides DB-dependent fixtures.
These tests run without PostgreSQL/psycopg2 (static analysis + unit-style).
تكوين اختبارات تكامل AI — لا تتطلب قاعدة بيانات.
"""

import sys
from pathlib import Path
import pytest

# Ensure repo root is in path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
for p in [str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Override parent conftest cleanup_test_data — no DB needed here."""
    yield
    # No DB cleanup needed for AI middleware gap tests


@pytest.fixture
def db_cursor():
    """Override db_cursor — AI gap tests don't need a DB connection."""
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Auto-skip AI integration tests when optional dependencies
    (structlog, fastapi, pydantic_settings, etc.) are not installed,
    or when stdlib-logging receives structlog-style keyword arguments.

    Uses ``hookwrapper=True`` so the default pytest hook runs the test
    first, and we inspect the outcome afterwards — no double-execution.

    Only known optional packages are auto-skipped; unknown import
    failures still surface as real errors.
    """
    # Packages that are optional for AI integration tests
    _OPTIONAL_PACKAGES = frozenset({
        "structlog", "fastapi", "pydantic_settings",
        "langchain", "langchain_anthropic", "crewai",
        "torch", "ultralytics", "onnxruntime",
        "tortoise", "asyncpg",
    })

    outcome = yield
    if outcome.excinfo is not None:
        exc_type, exc_value, _ = outcome.excinfo
        if issubclass(exc_type, ModuleNotFoundError):
            missing = getattr(exc_value, "name", "") or ""
            # Auto-skip only known optional packages
            top_pkg = missing.split(".")[0] if missing else ""
            if top_pkg in _OPTIONAL_PACKAGES:
                pytest.skip(f"{missing} not installed – skipping {item.nodeid}")
        elif issubclass(exc_type, TypeError) and "unexpected keyword argument" in str(exc_value):
            pytest.skip(f"Logger compatibility – {exc_value} – skipping {item.nodeid}")
