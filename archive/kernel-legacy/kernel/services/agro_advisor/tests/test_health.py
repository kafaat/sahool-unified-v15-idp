"""
Health Check Tests - Agro Advisor
"""

import pytest
from fastapi.testclient import TestClient
from kernel.services.agro_advisor.src.main import app


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
    assert data["service"] == "agro_advisor"
    assert "version" in data


def test_list_crops(client):
    """Test crops listing"""
    response = client.get("/crops")
    assert response.status_code == 200
    data = response.json()
    assert "crops" in data
    assert "tomato" in data["crops"]
    assert "wheat" in data["crops"]


def test_get_crop_stages(client):
    """Test crop stages endpoint"""
    response = client.get("/crops/tomato/stages")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "tomato"
    assert "stages" in data
    assert len(data["stages"]) > 0


def test_get_crop_requirements(client):
    """Test crop requirements endpoint"""
    response = client.get("/crops/tomato/requirements")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "tomato"
    assert "total_needs" in data
    assert "N" in data["total_needs"]


def test_get_disease_info(client):
    """Test disease info endpoint"""
    response = client.get("/disease/tomato_late_blight")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "tomato_late_blight"
    assert "name_ar" in data
    assert "name_en" in data
    assert "actions" in data


def test_get_disease_not_found(client):
    """Test disease not found"""
    response = client.get("/disease/nonexistent_disease")
    assert response.status_code == 404


def test_get_crop_diseases(client):
    """Test diseases by crop"""
    response = client.get("/disease/crop/tomato")
    assert response.status_code == 200
    data = response.json()
    assert data["crop"] == "tomato"
    assert "diseases" in data
    assert len(data["diseases"]) > 0


def test_search_diseases(client):
    """Test disease search"""
    response = client.get("/disease/search?q=لفحة")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_get_fertilizer_info(client):
    """Test fertilizer info endpoint"""
    response = client.get("/fertilizer/urea")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "urea"
    assert "analysis" in data
    assert data["analysis"]["N"] == 46


def test_get_fertilizers_by_nutrient(client):
    """Test fertilizers by nutrient"""
    response = client.get("/fertilizer/nutrient/N")
    assert response.status_code == 200
    data = response.json()
    assert data["nutrient"] == "N"
    assert "fertilizers" in data
    assert len(data["fertilizers"]) > 0


def test_get_action_details(client):
    """Test action details endpoint"""
    response = client.get("/actions/spray_copper")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "spray_copper"
    assert "instructions_ar" in data
    assert "task_type" in data
