"""Health check tests for demo-data.

Note: demo-data is a standalone data generation script, not a FastAPI service.
These tests verify the module structure rather than HTTP endpoints.
"""
import pytest


@pytest.mark.smoke
def test_main_module_loadable():
    """Verify main module file can be located."""
    from pathlib import Path

    main_path = Path(__file__).parent.parent / "main.py"
    assert main_path.exists(), "main.py should exist at the service root"
    assert main_path.stat().st_size > 0, "main.py should not be empty"


@pytest.mark.smoke
def test_dockerfile_exists():
    """Verify Dockerfile exists for container deployment."""
    from pathlib import Path

    dockerfile = Path(__file__).parent.parent / "Dockerfile"
    assert dockerfile.exists(), "Dockerfile should exist"
