"""Production-guard tests for src/config.py.

Verifies the 7-layer safety stack at the Settings level:

  1. ENVIRONMENT='production' → ValidationError
  2. Tenant prefix outside ('tenant_e2e_*', 'tenant_test_*') → ValidationError
  3. TEST_SEED_TOKEN < 32 chars → ValidationError
"""

from __future__ import annotations

import os
from contextlib import contextmanager

import pytest


@contextmanager
def _override_env(**kwargs):
    """Temporarily set/unset env vars."""
    saved = {}
    for k, v in kwargs.items():
        saved[k] = os.environ.get(k)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_production_environment_refused():
    """Pydantic must refuse ENVIRONMENT=production at construction."""
    from pydantic import ValidationError
    from src.config import Settings

    with _override_env(ENVIRONMENT="production"):
        with pytest.raises(ValidationError) as exc:
            Settings()
        # Message contains the explanation
        assert "production" in str(exc.value).lower()


def test_production_environment_case_insensitive():
    from pydantic import ValidationError
    from src.config import Settings

    with _override_env(ENVIRONMENT="PRODUCTION"):
        with pytest.raises(ValidationError):
            Settings()


def test_unsafe_tenant_prefix_refused():
    """Tenants must start with 'tenant_e2e_' or 'tenant_test_'."""
    from pydantic import ValidationError
    from src.config import Settings

    with _override_env(TEST_TENANT_WHITELIST='["tenant_real_production"]'):
        with pytest.raises(ValidationError) as exc:
            Settings()
        assert "tenant_e2e_" in str(exc.value) or "tenant_test_" in str(exc.value)


def test_short_seed_token_refused():
    """TEST_SEED_TOKEN must be at least 32 characters."""
    from pydantic import ValidationError
    from src.config import Settings

    with _override_env(TEST_SEED_TOKEN="short"):
        with pytest.raises(ValidationError):
            Settings()


def test_safe_tenant_prefix_accepted():
    from src.config import Settings

    with _override_env(TEST_TENANT_WHITELIST='["tenant_e2e_smoke", "tenant_test_unit"]'):
        s = Settings()
        assert "tenant_e2e_smoke" in s.TEST_TENANT_WHITELIST
        assert "tenant_test_unit" in s.TEST_TENANT_WHITELIST
