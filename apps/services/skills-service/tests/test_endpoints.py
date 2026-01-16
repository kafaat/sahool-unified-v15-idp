"""
Tests for Skills Service endpoints
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client"""
    import sys
    from pathlib import Path

    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from main import app

    return TestClient(app)


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
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["service"] == "skills_service"
        assert "endpoints" in data["data"]


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
        response = client.post("/compress", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "test-skill-1"
        assert data["original_size_kb"] > 0
        assert data["compressed_size_kb"] > 0
        assert data["compression_level"] == 6
        assert "compressed_data" in data

    @pytest.mark.unit
    def test_compress_invalid_data(self, client):
        """Test compression with empty skill data"""
        payload = {
            "skill_id": "test-skill",
            "skill_data": {},
            "compression_level": 5,
        }
        response = client.post("/compress", json=payload)
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    def test_compress_level_range(self, client):
        """Test compression level validation"""
        payload = {
            "skill_id": "test-skill",
            "skill_data": {"data": "test"},
            "compression_level": 10,  # Invalid: > 9
        }
        response = client.post("/compress", json=payload)
        assert response.status_code == 422


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
        response = client.post("/memory/store", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "memory-skill-1"
        assert data["namespace"] == "test"
        assert data["success"] is True
        assert data["ttl_seconds"] == 1800

    @pytest.mark.unit
    def test_store_missing_skill_id(self, client):
        """Test store without skill ID"""
        payload = {
            "skill_id": "",
            "namespace": "test",
            "skill_data": {"test": "data"},
        }
        response = client.post("/memory/store", json=payload)
        assert response.status_code == 422

    @pytest.mark.unit
    def test_recall_from_memory(self, client):
        """Test recalling skill from memory"""
        payload = {
            "skill_id": "memory-skill-1",
            "namespace": "test",
            "include_metadata": False,
        }
        response = client.post("/memory/recall", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "memory-skill-1"
        assert data["namespace"] == "test"
        assert "retrieved_at" in data

    @pytest.mark.unit
    def test_recall_with_metadata(self, client):
        """Test recall with metadata"""
        payload = {
            "skill_id": "memory-skill-1",
            "namespace": "test",
            "include_metadata": True,
        }
        response = client.post("/memory/recall", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "metadata" in data


class TestEvaluationEndpoint:
    """Test skill evaluation endpoint"""

    @pytest.mark.unit
    def test_evaluate_skill(self, client):
        """Test skill evaluation"""
        payload = {
            "skill_id": "eval-skill-1",
            "input_data": {"text": "test input"},
            "metrics": ["accuracy", "latency"],
        }
        response = client.post("/evaluate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["skill_id"] == "eval-skill-1"
        assert data["status"] == "completed"
        assert "metrics" in data
        assert "performance_score" in data
        assert 0 <= data["performance_score"] <= 1

    @pytest.mark.unit
    def test_evaluate_with_custom_metrics(self, client):
        """Test evaluation with custom metrics"""
        payload = {
            "skill_id": "eval-skill-2",
            "input_data": {"x": 1, "y": 2},
            "metrics": ["accuracy", "latency", "memory", "throughput"],
        }
        response = client.post("/evaluate", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "metrics" in data
        # Should have at least the requested metrics
        assert len(data["metrics"]) >= 1

    @pytest.mark.unit
    def test_evaluate_missing_input(self, client):
        """Test evaluation without input data"""
        payload = {
            "skill_id": "eval-skill-1",
            "input_data": {},
            "metrics": ["accuracy"],
        }
        response = client.post("/evaluate", json=payload)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
