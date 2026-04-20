"""Configuration for test-harness-sidecar — Pydantic-validated.

PR 1 scope: lifecycle + RLS/field introspection only. Seed/events
pieces deliberately deferred to PR 2/3 (depend on shared modules
that don't exist yet).
"""

from __future__ import annotations

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


# Bumped every time openapi.yaml changes shape. Framework checks this
# via /version before running its suite — mismatch aborts.
CONTRACT_VERSION = "1.0.0"
SIDECAR_VERSION = "1.0.0"


class Settings(BaseSettings):
    # Refused at start (see _enforce_production_guard in main.py + Pydantic
    # validator below). PR 1 has NO override flag — production accidents
    # require renaming ENVIRONMENT in source.
    ENVIRONMENT: str = Field(default="local")

    # Outside production HTTP service ranges (8000-8199, 8200-8299 mostly used)
    PORT: int = Field(default=8299)

    # Bearer-style header for every protected endpoint
    TEST_SEED_TOKEN: str = Field(..., min_length=32)

    # Enforced on every request that takes a tenant_id. Strict prefix policy
    # keeps a typo from accidentally probing a real tenant.
    TEST_TENANT_WHITELIST: list[str] = Field(
        default_factory=lambda: ["tenant_e2e_staging", "tenant_test_local"],
    )

    # Same DSN production services use — introspection MUST see what
    # production sees. PgBouncer transaction-mode is fine here because
    # introspect queries are short-lived and don't rely on session state
    # beyond the SET LOCAL inside one transaction.
    POSTGRES_DSN: str = Field(...)

    # Versioning surfaced via /version
    SIDECAR_VERSION: str = SIDECAR_VERSION
    CONTRACT_VERSION: str = CONTRACT_VERSION

    @field_validator("ENVIRONMENT")
    @classmethod
    def _refuse_production(cls, v: str) -> str:
        if v.lower() == "production":
            raise ValueError(
                "ENVIRONMENT=production is not allowed for test-harness-sidecar. "
                "There is no override flag in this version."
            )
        return v

    @field_validator("TEST_TENANT_WHITELIST")
    @classmethod
    def _safe_tenant_prefix(cls, v: list[str]) -> list[str]:
        for tenant in v:
            if not (tenant.startswith("tenant_e2e_") or tenant.startswith("tenant_test_")):
                raise ValueError(
                    f"Tenant '{tenant}' must start with 'tenant_e2e_' or 'tenant_test_'"
                )
        return v

    class Config:
        env_file = ".env"
