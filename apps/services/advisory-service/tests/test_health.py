"""
Health Check Tests - Advisory Service
"""

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

try:
    from src.main import app
except ImportError:
    pytest.skip("advisory-service src not available", allow_module_level=True)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "advisory_service"
    assert "version" in data


def test_list_crops(client):
    """Test crops listing"""
    response = client.get("/api/v1/crops")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "total_crops" in data
    assert data["total_crops"] > 0


def test_get_crop_stages(client):
    """Test crop stages endpoint"""
    response = client.get("/api/v1/crops/tomato/stages")
    assert response.status_code == 200
    data = response.json()
    # Response is wrapped in create_success_response
    inner = data.get("data", data)
    assert inner["crop"] == "tomato"
    assert "stages" in inner
    assert len(inner["stages"]) > 0


def test_get_crop_requirements(client):
    """Test crop requirements endpoint"""
    response = client.get("/api/v1/crops/tomato/requirements")
    assert response.status_code == 200
    data = response.json()
    inner = data.get("data", data)
    assert inner["crop"] == "tomato"
    assert "total_needs" in inner
    assert "N" in inner["total_needs"]


def test_get_disease_info(client):
    """Test disease info endpoint"""
    response = client.get("/api/v1/disease/tomato_late_blight")
    assert response.status_code == 200
    data = response.json()
    inner = data.get("data", data)
    assert inner["id"] == "tomato_late_blight"
    assert "name_ar" in inner
    assert "name_en" in inner
    assert "actions" in inner


def test_get_disease_not_found(client):
    """Test disease not found"""
    response = client.get("/api/v1/disease/nonexistent_disease")
    assert response.status_code == 404


def test_get_crop_diseases(client):
    """Test diseases by crop"""
    response = client.get("/api/v1/disease/crop/tomato")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "tomato"
    assert "diseases" in data
    assert len(data["diseases"]) > 0


def test_search_diseases(client):
    """Test disease search"""
    response = client.get("/api/v1/disease/search?q=لفحة")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_get_fertilizer_info(client):
    """Test fertilizer info endpoint"""
    response = client.get("/api/v1/fertilizer/urea")
    assert response.status_code == 200
    data = response.json()
    inner = data.get("data", data)
    assert inner["id"] == "urea"
    assert "analysis" in inner
    assert inner["analysis"]["N"] == 46


def test_get_fertilizers_by_nutrient(client):
    """Test fertilizers by nutrient"""
    response = client.get("/api/v1/fertilizer/nutrient/N")
    assert response.status_code == 200
    data = response.json()
    assert data["nutrient"] == "N"
    assert "fertilizers" in data
    assert len(data["fertilizers"]) > 0


def test_get_action_details(client):
    """Test action details endpoint"""
    response = client.get("/api/v1/actions/spray_copper")
    assert response.status_code == 200
    data = response.json()
    inner = data.get("data", data)
    assert inner["id"] == "spray_copper"
    assert "instructions_ar" in inner
    assert "task_type" in inner
