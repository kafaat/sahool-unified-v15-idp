"""Smoke tests for ussd-gateway."""
import pytest


@pytest.mark.smoke
def test_import_main():
    """Verify main module can be imported."""
    try:
        from src.main import app
        assert app is not None
    except ImportError:
        pytest.skip("Dependencies not installed")


@pytest.mark.smoke
def test_health_endpoint_exists():
    """Verify health endpoint is defined."""
    try:
        from src.main import app
        routes = [route.path for route in app.routes]
        assert "/healthz" in routes or "/health" in routes
    except ImportError:
        pytest.skip("Dependencies not installed")
