"""
API endpoint tests for Knowledge Graph Service
اختبارات نقاط نهاية API لخدمة الرسم البياني للمعرفة

Tests the FastAPI endpoints in api/v1/entities.py, api/v1/graphs.py, api/v1/relationships.py, and main.py
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import AsyncMock, MagicMock, patch

# Mock shared modules before importing the app
sys.modules.setdefault("shared.errors_py", MagicMock(
    add_request_id_middleware=MagicMock(),
    setup_exception_handlers=MagicMock(),
))
sys.modules.setdefault("shared.middleware.tenant_context", MagicMock(
    TenantContextMiddleware=type("FakeMiddleware", (), {"__init__": lambda *a, **kw: None}),
))
sys.modules.setdefault("shared.cors_config", MagicMock(
    setup_cors_middleware=MagicMock(),
))
sys.modules.setdefault("shared.auth.dependencies", MagicMock(
    get_current_user=MagicMock(return_value={"id": "test-user"}),
))

try:
    from fastapi.testclient import TestClient
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from models import Crop, Disease, RelationshipType, Treatment
from services import EntityService, KnowledgeGraphService, RelationshipService


@pytest.fixture
async def initialized_app():
    """Create a FastAPI app with initialized services."""
    # Patch shared builder to use fallback data
    with patch("services.graph_service._HAS_SHARED_KG", False):
        graph_service = KnowledgeGraphService()
        await graph_service._load_fallback_data()

    entity_service = EntityService(graph_service)
    relationship_service = RelationshipService(graph_service)

    # Add a disease and treatment so we can test relationships
    await graph_service.add_disease(Disease(
        id="leaf-rust",
        name_en="Leaf Rust",
        name_ar="صدأ الأوراق",
        pathogen_type="fungal",
        severity_level=7,
    ))
    await graph_service.add_treatment(Treatment(
        id="sulfur-spray",
        name_en="Sulfur Spray",
        name_ar="رش الكبريت",
        treatment_type="fungicide",
    ))
    await graph_service.add_relationship(
        source_type="disease",
        source_id="leaf-rust",
        target_type="crop",
        target_id="wheat",
        relationship_type=RelationshipType.AFFECTS,
        confidence=0.9,
    )
    await graph_service.add_relationship(
        source_type="disease",
        source_id="leaf-rust",
        target_type="treatment",
        target_id="sulfur-spray",
        relationship_type=RelationshipType.TREATED_BY,
    )

    # Import app and set state
    from main import app
    app.state.graph_service = graph_service
    app.state.entity_service = entity_service
    app.state.relationship_service = relationship_service

    return app


@pytest.mark.skipif(not HAS_FASTAPI, reason="fastapi not installed")
@pytest.mark.asyncio
class TestKGAPIEndpoints:
    """Tests for KG API endpoints via TestClient."""

    @pytest.fixture
    async def client(self, initialized_app):
        return TestClient(initialized_app)

    # ---- Health endpoints ----

    async def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "knowledge-graph"
        assert "endpoints" in data

    async def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["database"] is True

    async def test_readyz(self, client):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"

    async def test_health_combined(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "graph_stats" in data
        assert data["graph_stats"]["total_nodes"] > 0

    # ---- Entity endpoints ----

    async def test_list_crops(self, client):
        resp = client.get("/api/v1/entities/crops", headers={"Authorization": "Bearer testtoken"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["total"] >= 2

    async def test_get_crop(self, client):
        resp = client.get("/api/v1/entities/crops/wheat")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == "wheat"

    async def test_get_crop_not_found(self, client):
        resp = client.get("/api/v1/entities/crops/nonexistent")
        assert resp.status_code == 404

    async def test_create_crop(self, client):
        resp = client.post("/api/v1/entities/crops", json={
            "id": "barley",
            "name_en": "Barley",
            "name_ar": "الشعير",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    async def test_list_diseases(self, client):
        resp = client.get("/api/v1/entities/diseases")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    async def test_get_disease(self, client):
        resp = client.get("/api/v1/entities/diseases/leaf-rust")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["id"] == "leaf-rust"

    async def test_get_disease_not_found(self, client):
        resp = client.get("/api/v1/entities/diseases/nonexistent")
        assert resp.status_code == 404

    async def test_create_disease(self, client):
        resp = client.post("/api/v1/entities/diseases", json={
            "id": "blight",
            "name_en": "Blight",
            "name_ar": "اللفحة",
        })
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    async def test_list_treatments(self, client):
        resp = client.get("/api/v1/entities/treatments")
        assert resp.status_code == 200

    async def test_get_treatment(self, client):
        resp = client.get("/api/v1/entities/treatments/sulfur-spray")
        assert resp.status_code == 200

    async def test_get_treatment_not_found(self, client):
        resp = client.get("/api/v1/entities/treatments/nonexistent")
        assert resp.status_code == 404

    async def test_create_treatment(self, client):
        resp = client.post("/api/v1/entities/treatments", json={
            "id": "neem",
            "name_en": "Neem Oil",
            "name_ar": "زيت النيم",
        })
        assert resp.status_code == 200

    async def test_search_entities(self, client):
        resp = client.get("/api/v1/entities/search", params={"q": "wheat"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    # ---- Graph endpoints ----

    async def test_graph_stats(self, client):
        resp = client.get("/api/v1/graphs/stats", headers={"Authorization": "Bearer testtoken"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total_nodes"] > 0

    async def test_graph_search(self, client):
        resp = client.get("/api/v1/graphs/search", params={"q": "wheat"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_results"] >= 1

    async def test_graph_path(self, client):
        resp = client.get("/api/v1/graphs/path", params={
            "source_type": "disease",
            "source_id": "leaf-rust",
            "target_type": "crop",
            "target_id": "wheat",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["length"] == 1

    async def test_graph_path_not_found(self, client):
        resp = client.get("/api/v1/graphs/path", params={
            "source_type": "crop",
            "source_id": "tomato",
            "target_type": "treatment",
            "target_id": "sulfur-spray",
        })
        assert resp.status_code == 404

    # ---- Relationship endpoints ----

    async def test_affected_crops(self, client):
        resp = client.get("/api/v1/relationships/affected-crops/leaf-rust",
                          headers={"Authorization": "Bearer testtoken"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["affected_crops_count"] >= 1

    async def test_disease_treatments(self, client):
        resp = client.get("/api/v1/relationships/disease-treatments/leaf-rust")
        assert resp.status_code == 200
        data = resp.json()
        assert data["treatments_count"] >= 1

    async def test_compatible_treatments(self, client):
        resp = client.get("/api/v1/relationships/crop-compatible-treatments/wheat")
        assert resp.status_code == 200

    async def test_diseases_by_crop(self, client):
        resp = client.get("/api/v1/relationships/diseases-by-crop/wheat")
        assert resp.status_code == 200

    async def test_preventive_treatments(self, client):
        resp = client.get("/api/v1/relationships/preventive-treatments/leaf-rust")
        assert resp.status_code == 200

    async def test_all_related(self, client):
        resp = client.get("/api/v1/relationships/related/disease/leaf-rust")
        assert resp.status_code == 200
        data = resp.json()
        assert data["related_count"] >= 1

    async def test_relationship_path(self, client):
        resp = client.get("/api/v1/relationships/path/disease/leaf-rust/crop/wheat")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["length"] == 1

    async def test_relationship_path_not_found(self, client):
        resp = client.get("/api/v1/relationships/path/crop/tomato/treatment/sulfur-spray")
        assert resp.status_code == 404

    async def test_validate_relationship_exists(self, client):
        resp = client.post("/api/v1/relationships/validate", params={
            "source_type": "disease",
            "source_id": "leaf-rust",
            "target_type": "crop",
            "target_id": "wheat",
            "relationship_type": "affects",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["exists"] is True

    async def test_validate_relationship_not_exists(self, client):
        resp = client.post("/api/v1/relationships/validate", params={
            "source_type": "crop",
            "source_id": "wheat",
            "target_type": "disease",
            "target_id": "leaf-rust",
            "relationship_type": "prevents",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["exists"] is False

    async def test_add_relationship(self, client):
        resp = client.post("/api/v1/relationships/add", params={
            "source_type": "disease",
            "source_id": "leaf-rust",
            "target_type": "treatment",
            "target_id": "sulfur-spray",
            "relationship_type": "prevents",
            "confidence": 0.8,
        })
        assert resp.status_code == 200

    async def test_404_handler(self, client):
        resp = client.get("/nonexistent-path")
        assert resp.status_code == 404
        data = resp.json()
        assert data["status"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
