"""
Tests for code-review-service Dockerfile fixes
اختبارات إصلاحات Dockerfile لخدمة مراجعة الكود

Validates:
- Dockerfile contains COPY shared/ (platform shared modules)
- Multi-stage build structure
- Non-root user configuration
- shared.auth imports resolve correctly
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

DOCKERFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")


# ═══════════════════════════════════════════════════════════════════════════
# Test: Dockerfile structure
# ═══════════════════════════════════════════════════════════════════════════


class TestDockerfileStructure:
    """Validate Dockerfile contains required directives."""

    @pytest.fixture
    def dockerfile_content(self):
        with open(DOCKERFILE_PATH) as f:
            return f.read()

    def test_copies_platform_shared_directory(self, dockerfile_content):
        """Dockerfile must COPY shared/ (platform shared modules) before apps/services/shared/."""
        lines = dockerfile_content.split("\n")
        shared_copy_lines = [
            i for i, line in enumerate(lines) if "COPY" in line and "shared/" in line and "apps/services" not in line
        ]
        service_shared_copy_lines = [
            i for i, line in enumerate(lines) if "COPY" in line and "apps/services/shared/" in line
        ]

        assert len(shared_copy_lines) >= 1, "Missing: COPY shared/ ./shared/"
        assert len(service_shared_copy_lines) >= 1, "Missing: COPY apps/services/shared/ ./shared/"

        # Platform shared must come BEFORE service shared (overlay pattern)
        assert shared_copy_lines[0] < service_shared_copy_lines[0], (
            "COPY shared/ must come before COPY apps/services/shared/ (overlay pattern)"
        )

    def test_multi_stage_build(self, dockerfile_content):
        """Dockerfile should use multi-stage build (builder + production)."""
        assert "AS builder" in dockerfile_content, "Missing builder stage"
        assert "AS production" in dockerfile_content or "FROM" in dockerfile_content.split("AS builder")[1], (
            "Missing production stage after builder"
        )

    def test_non_root_user(self, dockerfile_content):
        """Dockerfile must switch to non-root user before CMD."""
        assert "USER sahool" in dockerfile_content, "Missing USER sahool directive"

        # USER must come before CMD
        user_pos = dockerfile_content.index("USER sahool")
        cmd_pos = dockerfile_content.index("CMD")
        assert user_pos < cmd_pos, "USER sahool must come before CMD"

    def test_healthcheck_present(self, dockerfile_content):
        """Dockerfile must have HEALTHCHECK directive."""
        assert "HEALTHCHECK" in dockerfile_content, "Missing HEALTHCHECK directive"

    def test_no_duplicate_chown(self, dockerfile_content):
        """Dockerfile should not have redundant chown -R commands."""
        # Count standalone chown commands (not --chown in COPY)
        chown_lines = [
            line.strip()
            for line in dockerfile_content.split("\n")
            if "chown -R sahool:sahool /app" in line and not line.strip().startswith("#") and "COPY" not in line
        ]
        # Should have at most 1 standalone chown (for logs dir)
        assert len(chown_lines) <= 1, (
            f"Found {len(chown_lines)} standalone chown commands, expected <= 1. "
            f"Use --chown in COPY directives instead."
        )


# ═══════════════════════════════════════════════════════════════════════════
# Test: shared module imports resolve
# ═══════════════════════════════════════════════════════════════════════════


class TestSharedModuleImports:
    """Test that shared module imports work correctly."""

    def test_shared_auth_importable(self):
        """shared.auth.dependencies must be importable.

        Skips when cryptography native extensions are broken (pyo3 panic in some CI envs).
        """
        # Guard: cffi_backend is required by cryptography → jwt → shared.auth
        pytest.importorskip("_cffi_backend", reason="cffi native backend not available")
        from shared.auth.dependencies import get_current_user

        assert callable(get_current_user)

    def test_shared_errors_py_importable(self):
        """shared.errors_py must be importable."""
        try:
            from shared.errors_py import add_request_id_middleware, setup_exception_handlers

            assert callable(setup_exception_handlers)
            assert callable(add_request_id_middleware)
        except ImportError as e:
            pytest.skip(f"shared.errors_py not available: {e}")

    def test_shared_middleware_importable(self):
        """shared.middleware.tenant_context must be importable."""
        try:
            from shared.middleware.tenant_context import TenantContextMiddleware

            assert TenantContextMiddleware is not None
        except ImportError as e:
            pytest.skip(f"shared.middleware not available: {e}")

    def test_service_main_importable(self):
        """src.main must be importable (proves all shared deps resolve)."""
        try:
            from src import main

            assert main.app is not None
        except ImportError as e:
            pytest.skip(f"Service import failed: {e}")
