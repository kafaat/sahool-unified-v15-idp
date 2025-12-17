"""
SAHOOL Architecture Import Smoke Tests
Tests that all domain packages can be imported without circular dependencies.
"""

from __future__ import annotations

import importlib
import sys
from typing import TYPE_CHECKING

import pytest


class TestDomainImports:
    """Test that domain packages import cleanly"""

    def test_kernel_domain_imports(self):
        """kernel_domain package imports without errors"""
        # Main package
        import kernel_domain

        assert hasattr(kernel_domain, "__version__")

        # Submodules
        from kernel_domain import auth, tenancy, users

        # Key exports
        from kernel_domain.auth import create_access_token, hash_password
        from kernel_domain.tenancy import Tenant, TenantService
        from kernel_domain.users import User, UserService

    def test_field_suite_imports(self):
        """field_suite package imports without errors"""
        # Main package
        import field_suite

        assert hasattr(field_suite, "__version__")

        # Submodules
        from field_suite import farms, fields, crops

        # Key exports
        from field_suite.farms import Farm, FarmService
        from field_suite.fields import Field, FieldService
        from field_suite.crops import Crop, CropService

    def test_advisor_imports(self):
        """advisor package imports without errors"""
        # Main package
        import advisor

        assert hasattr(advisor, "__version__")

        # Submodules
        from advisor import ai, rag, context, feedback

        # Key exports
        from advisor.ai import AdvisorAI, AdvisorResponse
        from advisor.rag import RAGService, Document
        from advisor.context import ContextBuilder, FieldContext
        from advisor.feedback import FeedbackService, AdvisorFeedback


class TestLegacyCompatibility:
    """Test that legacy imports work with deprecation warnings"""

    def test_legacy_auth_import(self):
        """legacy.auth re-exports kernel_domain.auth"""
        with pytest.warns(DeprecationWarning, match="deprecated"):
            from legacy import auth

    def test_legacy_tenancy_import(self):
        """legacy.tenancy re-exports kernel_domain.tenancy"""
        with pytest.warns(DeprecationWarning, match="deprecated"):
            from legacy import tenancy

    def test_legacy_users_import(self):
        """legacy.users re-exports kernel_domain.users"""
        with pytest.warns(DeprecationWarning, match="deprecated"):
            from legacy import users

    def test_legacy_field_import(self):
        """legacy.field re-exports field_suite"""
        with pytest.warns(DeprecationWarning, match="deprecated"):
            from legacy import field

    def test_legacy_advisor_import(self):
        """legacy.advisor re-exports advisor"""
        with pytest.warns(DeprecationWarning, match="deprecated"):
            from legacy import advisor


class TestNoCircularImports:
    """Test for circular import detection"""

    @pytest.mark.parametrize("module_name", [
        "kernel_domain",
        "kernel_domain.auth",
        "kernel_domain.tenancy",
        "kernel_domain.users",
        "field_suite",
        "field_suite.farms",
        "field_suite.fields",
        "field_suite.crops",
        "advisor",
        "advisor.ai",
        "advisor.rag",
        "advisor.context",
        "advisor.feedback",
    ])
    def test_module_imports_cleanly(self, module_name: str):
        """Each module can be imported independently without circular import errors"""
        # Remove from cache to ensure fresh import
        modules_to_remove = [
            key for key in sys.modules
            if key == module_name or key.startswith(f"{module_name}.")
        ]
        for mod in modules_to_remove:
            sys.modules.pop(mod, None)

        # Attempt import
        try:
            module = importlib.import_module(module_name)
            assert module is not None
        except ImportError as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected in {module_name}: {e}")
            raise


class TestArchitectureRules:
    """Test architecture import rules using the checker"""

    def test_run_architecture_checker(self):
        """Architecture checker runs without finding violations"""
        from pathlib import Path
        import subprocess

        root = Path(__file__).parent.parent.parent
        checker_path = root / "tools" / "arch" / "check_imports.py"

        if not checker_path.exists():
            pytest.skip("Architecture checker not found")

        result = subprocess.run(
            [sys.executable, str(checker_path), "--root", str(root)],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            pytest.fail(
                f"Architecture violations found:\n{result.stdout}\n{result.stderr}"
            )
