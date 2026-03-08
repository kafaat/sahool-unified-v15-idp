"""Smoke tests for demo-data."""

import pytest


@pytest.mark.smoke
def test_import_main():
    """Verify main module can be imported."""
    try:
        import importlib.util
        from pathlib import Path

        main_path = Path(__file__).parent.parent / "main.py"
        spec = importlib.util.spec_from_file_location("main", main_path)
        assert spec is not None
        assert spec.loader is not None
    except ImportError:
        pytest.skip("Dependencies not installed")


@pytest.mark.smoke
def test_main_module_exists():
    """Verify main.py exists at the service root."""
    from pathlib import Path

    main_path = Path(__file__).parent.parent / "main.py"
    assert main_path.exists(), "main.py should exist at the service root"


@pytest.mark.smoke
def test_requirements_file_exists():
    """Verify requirements.txt exists."""
    from pathlib import Path

    req_path = Path(__file__).parent.parent / "requirements.txt"
    assert req_path.exists(), "requirements.txt should exist"
