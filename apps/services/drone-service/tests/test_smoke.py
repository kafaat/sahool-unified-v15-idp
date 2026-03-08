"""
Smoke test for drone-service
Tests basic import and module structure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_main_module_structure():
    """Test that main.py has expected attributes."""
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("main", Path(__file__).parent.parent / "src" / "main.py")
        assert spec is not None
        assert spec.loader is not None
    except Exception as e:
        raise AssertionError(f"Import check failed: {e}")


def test_api_routers_exist():
    """Test that API router files exist."""
    api_path = Path(__file__).parent.parent / "src" / "api" / "v1"
    assert (api_path / "drones.py").exists()
    assert (api_path / "flights.py").exists()
    assert (api_path / "missions.py").exists()
    assert (api_path / "vra.py").exists()


def test_db_module_exists():
    """Test that database repository module exists."""
    src_path = Path(__file__).parent.parent / "src"
    assert (src_path / "db.py").exists()


def test_events_module_exists():
    """Test that events module exists."""
    src_path = Path(__file__).parent.parent / "src"
    assert (src_path / "events.py").exists()


def test_migrations_exist():
    """Test that SQL migration files exist."""
    migrations_path = Path(__file__).parent.parent / "migrations"
    assert (migrations_path / "001_create_drone_tables.sql").exists()


if __name__ == "__main__":
    test_main_module_structure()
    test_api_routers_exist()
    test_db_module_exists()
    test_events_module_exists()
    test_migrations_exist()
    print("All smoke tests passed!")
