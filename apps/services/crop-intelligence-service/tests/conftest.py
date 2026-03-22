"""
Test Configuration and Fixtures
إعدادات الاختبار والتجهيزات
"""

import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]

import pytest

# Set test environment before any service imports
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")

try:
    from src.main import OBSERVATIONS, ZONES, _init_sample_data, app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except Exception:
    get_current_user = None
    User = None
    OBSERVATIONS = None
    ZONES = None
    _init_sample_data = None
    app = None


def _fake_current_user():
    return User(
        id="test-user-001",
        email="test@sahool.sa",
        roles=["farmer"],
        tenant_id="00000000-0000-0000-0000-000000000001",
        hashed_password="$2b$12$test_hashed_password_placeholder",
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    """Initialize sample data before all tests run"""
    if app is None:
        yield
        return
    # Clear any existing data
    ZONES.clear()
    OBSERVATIONS.clear()

    # Initialize sample data
    _init_sample_data()

    yield

    # Cleanup after all tests
    ZONES.clear()
    OBSERVATIONS.clear()


@pytest.fixture
def client(setup_test_data):
    """Create test client with sample data initialized and auth overridden"""
    if app is None or get_current_user is None or User is None:
        pytest.skip("crop-intelligence-service src not available")

    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    TestClient = fastapi_testclient.TestClient

    app.dependency_overrides[get_current_user] = _fake_current_user
    test_client = TestClient(app)
    test_client.headers["X-Tenant-ID"] = "00000000-0000-0000-0000-000000000001"
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_observation_data():
    """Sample observation data for testing"""
    return {
        "captured_at": "2025-12-27T10:00:00Z",
        "source": "sentinel-2",
        "growth_stage": "mid",
        "indices": {
            "ndvi": 0.75,
            "evi": 0.60,
            "ndre": 0.25,
            "lci": 0.30,
            "ndwi": -0.05,
            "savi": 0.65,
        },
        "cloud_pct": 5.0,
    }
