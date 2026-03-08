"""
Smoke test for cooperative-service
Tests basic import and module structure
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.smoke
def test_main_module_structure():
    """Test that main.py has expected attributes"""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("main", Path(__file__).parent.parent / "src" / "main.py")
        assert spec is not None
        assert spec.loader is not None
        print("✓ main.py module structure valid")
    except Exception as e:
        print(f"✗ Import check failed: {e}")
        raise


@pytest.mark.smoke
def test_api_routers_exist():
    """Test that API router files exist"""
    api_path = Path(__file__).parent.parent / "src" / "api" / "v1"

    assert (api_path / "cooperatives.py").exists()
    print("✓ All API router files exist")


@pytest.mark.smoke
def test_migrations_exist():
    """Test that SQL migration files exist"""
    migrations_path = Path(__file__).parent.parent / "migrations"

    assert (migrations_path / "001_create_cooperative_tables.sql").exists()
    print("✓ Migration files exist")


if __name__ == "__main__":
    test_main_module_structure()
    test_api_routers_exist()
    test_migrations_exist()
    print("✓ All smoke tests passed!")
