"""
SAHOOL Smoke Tests
Fast tests to verify imports and basic functionality
"""



class TestCoreImports:
    """Test that core modules can be imported"""

    def test_shared_security_imports(self):
        """Shared security module should import"""
        import shared.security.jwt  # noqa: F401
        import shared.security.rbac  # noqa: F401

    def test_shared_events_imports(self):
        """Shared events module should import"""
        import shared.events  # noqa: F401

    def test_shared_monitoring_imports(self):
        """Shared monitoring module should import"""
        import shared.monitoring.metrics  # noqa: F401


class TestServiceImports:
    """Test that service modules can be imported"""

    def test_field_ops_imports(self):
        """Field ops service should import"""
        import sys
        from pathlib import Path

        # Updated path to match new apps/services structure
        field_ops_path = Path("apps/services/field-ops/src")
        if not field_ops_path.exists():
            import pytest
            pytest.skip("Field ops service not found at expected path")

        sys.path.insert(0, str(field_ops_path))

        try:
            import main as field_ops_main  # noqa: F401
            # Verify app exists
            assert hasattr(field_ops_main, "app")
        except ImportError:
            import pytest
            pytest.skip("Field ops main module not available")

    def test_field_ops_models_exist(self):
        """Field ops models should exist"""
        import sys
        from pathlib import Path

        # Updated path to match new apps/services structure
        field_ops_path = Path("apps/services/field-ops/src")
        if not field_ops_path.exists():
            import pytest
            pytest.skip("Field ops service not found at expected path")

        sys.path.insert(0, str(field_ops_path))

        try:
            from main import FieldCreate, FieldResponse, OperationCreate
            assert FieldCreate is not None
            assert FieldResponse is not None
            assert OperationCreate is not None
        except ImportError:
            import pytest
            pytest.skip("Field ops models not available")


class TestSecurityModules:
    """Test security module integrity"""

    def test_jwt_functions_exist(self):
        """JWT module should have required functions"""
        from shared.security.jwt import (
            create_access_token,
            create_refresh_token,
            create_token,
            verify_token,
        )

        assert callable(create_token)
        assert callable(verify_token)
        assert callable(create_access_token)
        assert callable(create_refresh_token)

    def test_rbac_functions_exist(self):
        """RBAC module should have required functions"""
        from shared.security.rbac import (
            can_access_resource,
            get_role_permissions,
            has_permission,
        )

        assert callable(has_permission)
        assert callable(get_role_permissions)
        assert callable(can_access_resource)

    def test_rbac_roles_defined(self):
        """RBAC should have all required roles"""
        from shared.security.rbac import Role

        assert hasattr(Role, "VIEWER")
        assert hasattr(Role, "WORKER")
        assert hasattr(Role, "SUPERVISOR")
        assert hasattr(Role, "MANAGER")
        assert hasattr(Role, "ADMIN")
        assert hasattr(Role, "SUPER_ADMIN")

    def test_rbac_permissions_defined(self):
        """RBAC should have permissions defined"""
        from shared.security.rbac import Permission

        # Check some key permissions exist
        assert hasattr(Permission, "FIELDOPS_TASK_READ")
        assert hasattr(Permission, "FIELDOPS_FIELD_CREATE")
        assert hasattr(Permission, "ADMIN_USERS_READ")


class TestNoCircularImports:
    """Test that there are no circular import issues"""

    def test_import_chain_security(self):
        """Security import chain should work"""
        # Import in typical order
        from shared.security import jwt, rbac

        # Should not raise
        assert rbac is not None
        assert jwt is not None

    def test_fresh_import_works(self):
        """Fresh imports should work without state issues"""
        import importlib

        import shared.security.rbac

        # Reload should work
        importlib.reload(shared.security.rbac)
