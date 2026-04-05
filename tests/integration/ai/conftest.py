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


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    """Auto-skip AI integration tests when optional dependencies
    (structlog, fastapi, pydantic_settings, etc.) are not installed.

    This avoids the need to sprinkle ``pytest.importorskip`` or
    ``@pytest.mark.skipif`` on every individual test that may
    transitively import a heavy optional package.
    """
    try:
        item.runtest()
    except ModuleNotFoundError as exc:
        pytest.skip(f"{exc.name} not installed – skipping {item.nodeid}")
    except Exception:
        # Re-raise all other exceptions for normal pytest handling
        raise
