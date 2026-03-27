"""
Tests for Skills Service endpoints
"""

import sys

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

# Valid UUID for tenant header required by TenantContextMiddleware
TENANT_ID = "00000000-0000-0000-0000-000000000001"
TENANT_HEADERS = {"X-Tenant-ID": TENANT_ID}


@pytest.fixture
def client():
    """Create test client with auth dependency overridden.

    Uses raise_server_exceptions=False so that unhandled errors in endpoints
    (e.g. AttributeError from missing ErrorCode.INVALID_INPUT, or Pydantic
    ValidationError from type mismatches) return a 500 response instead of
    crashing the test process.
    """
    from pathlib import Path

    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from main import app, get_current_user

    # Override auth dependency so endpoints don't require a real JWT
    app.dependency_overrides[get_current_user] = lambda: None

    yield TestClient(app, raise_server_exceptions=False)

    # Clean up overrides
    app.dependency_overrides.clear()


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.mark.unit
    def test_healthz(self, client):
        """Test liveness probe"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "skills_service"

    @pytest.mark.unit
    def test_readyz(self, client):
        """Test readiness probe"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @pytest.mark.unit
    def test_root(self, client):
        """Test root endpoint returns service info wrapped in success response"""
        response = client.get("/", headers=TENANT_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["service"] == "skills_service"
        assert "endpoints" in data["data"]

    @pytest.mark.unit
    def test_root_without_tenant_returns_400(self, client):
        """Root endpoint requires tenant context via X-Tenant-ID header"""
        response = client.get("/")
        assert response.status_code == 400


class TestCompressionEndpoint:
    """Test skill compression endpoint"""

    @pytest.mark.unit
    def test_compress_valid(self, client):
        """Test compression with valid data"""
        payload = {
            "skill_id": "test-skill-1",
            "skill_data": {
                "weights": [0.1, 0.2, 0.3],
                "config": {"layers": 3},
            },
            "compression_level": 6,
        }
        response = client.post("/compress", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "test-skill-1"
        assert data["original_size_kb"] > 0
        assert data["compressed_size_kb"] > 0
        assert data["compression_level"] == 6
        assert "compressed_data" in data

    @pytest.mark.unit
    def test_compress_empty_skill_data_returns_validation_error(self, client):
        """Empty skill_data triggers a code path using ErrorCode.INVALID_INPUT
        which does not exist in ErrorCode enum, resulting in a 500 error."""
        payload = {
            "skill_id": "test-skill",
            "skill_data": {},
            "compression_level": 5,
        }
        response = client.post("/compress", json=payload, headers=TENANT_HEADERS)
        assert response.status_code in (400, 422)

    @pytest.mark.unit
    def test_compress_level_out_of_range(self, client):
        """Pydantic validates compression_level le=9, so 10 returns 422"""
        payload = {
            "skill_id": "test-skill",
            "skill_data": {"data": "test"},
            "compression_level": 10,  # Invalid: > 9
        }
        response = client.post("/compress", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_compress_missing_required_fields(self, client):
        """Missing required fields (skill_id, skill_data) returns 422"""
        payload = {
            "compression_level": 5,
        }
        response = client.post("/compress", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_compress_default_level(self, client):
        """Compression level defaults to 1 when not specified"""
        payload = {
            "skill_id": "test-skill-default",
            "skill_data": {"key": "value"},
        }
        response = client.post("/compress", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["compression_level"] == 1

    @pytest.mark.unit
    def test_compress_ratio_is_positive(self, client):
        """Compression ratio should be between 0 and 1"""
        payload = {
            "skill_id": "test-ratio",
            "skill_data": {"a": 1, "b": 2, "c": [1, 2, 3]},
            "compression_level": 5,
        }
        response = client.post("/compress", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert 0 < data["compression_ratio"] < 1


class TestMemoryEndpoints:
    """Test memory storage and recall endpoints"""

    @pytest.mark.unit
    def test_store_in_memory(self, client):
        """Test storing skill in memory"""
        payload = {
            "skill_id": "memory-skill-1",
            "namespace": "test",
            "skill_data": {"test": "data"},
            "ttl_seconds": 1800,
        }
        response = client.post("/memory/store", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "memory-skill-1"
        assert data["namespace"] == "test"
        assert data["success"] is True
        assert data["ttl_seconds"] == 1800

    @pytest.mark.unit
    def test_store_default_namespace(self, client):
        """Default namespace is 'default'"""
        payload = {
            "skill_id": "memory-skill-2",
            "skill_data": {"test": "data"},
        }
        response = client.post("/memory/store", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["namespace"] == "default"

    @pytest.mark.unit
    def test_store_empty_skill_id_returns_validation_error(self, client):
        """Empty skill_id triggers ErrorCode.INVALID_INPUT path which errors at runtime"""
        payload = {
            "skill_id": "",
            "namespace": "test",
            "skill_data": {"test": "data"},
        }
        response = client.post("/memory/store", json=payload, headers=TENANT_HEADERS)
        assert response.status_code in (400, 422)

    @pytest.mark.unit
    def test_store_missing_required_fields(self, client):
        """Missing required fields returns 422"""
        payload = {
            "namespace": "test",
        }
        response = client.post("/memory/store", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_recall_from_memory_returns_result(self, client):
        """Recall returns memory data (Pydantic type fix allows None values)."""
        payload = {
            "skill_id": "memory-skill-1",
            "namespace": "test",
            "include_metadata": False,
        }
        response = client.post("/memory/recall", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200

    @pytest.mark.unit
    def test_recall_with_metadata(self, client):
        """Recall with metadata=True returns enriched result."""
        payload = {
            "skill_id": "memory-skill-1",
            "namespace": "test",
            "include_metadata": True,
        }
        response = client.post("/memory/recall", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200


class TestEvaluationEndpoint:
    """Test skill evaluation endpoint"""

    @pytest.mark.unit
    def test_evaluate_skill(self, client):
        """Test skill evaluation with valid input"""
        payload = {
            "skill_id": "eval-skill-1",
            "input_data": {"text": "test input"},
            "metrics": ["accuracy", "latency"],
        }
        response = client.post("/evaluate", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "eval-skill-1"
        assert data["status"] == "completed"
        assert "metrics" in data
        assert "performance_score" in data
        assert 0 <= data["performance_score"] <= 1

    @pytest.mark.unit
    def test_evaluate_with_custom_metrics(self, client):
        """Test evaluation with multiple custom metrics"""
        payload = {
            "skill_id": "eval-skill-2",
            "input_data": {"x": 1, "y": 2},
            "metrics": ["accuracy", "latency", "memory", "throughput"],
        }
        response = client.post("/evaluate", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "metrics" in data
        assert len(data["metrics"]) >= 1

    @pytest.mark.unit
    def test_evaluate_empty_input_data_returns_validation_error(self, client):
        """Empty input_data triggers ErrorCode.INVALID_INPUT path which errors at runtime"""
        payload = {
            "skill_id": "eval-skill-1",
            "input_data": {},
            "metrics": ["accuracy"],
        }
        response = client.post("/evaluate", json=payload, headers=TENANT_HEADERS)
        assert response.status_code in (400, 422)

    @pytest.mark.unit
    def test_evaluate_missing_required_fields(self, client):
        """Missing required fields returns 422"""
        payload = {
            "metrics": ["accuracy"],
        }
        response = client.post("/evaluate", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_evaluate_has_timestamp(self, client):
        """Evaluation response includes a timestamp"""
        payload = {
            "skill_id": "eval-skill-ts",
            "input_data": {"data": "test"},
            "metrics": ["accuracy"],
        }
        response = client.post("/evaluate", json=payload, headers=TENANT_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
