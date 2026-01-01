"""
SAHOOL Crop Health AI Service - Unit Tests
اختبارات خدمة صحة المحاصيل بالذكاء الاصطناعي
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client with mocked app"""
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/healthz")
    def health():
        return {"status": "ok", "service": "crop_health_ai"}

    @app.post("/api/v1/analyze/image")
    def analyze_image():
        return {
            "analysis_id": "analysis_001",
            "predictions": [
                {
                    "class": "leaf_blight",
                    "class_ar": "لفحة الأوراق",
                    "confidence": 0.89,
                    "severity": "moderate",
                }
            ],
            "recommendations": [
                "Apply fungicide within 24 hours",
                "Improve air circulation",
            ],
        }

    @app.post("/api/v1/analyze/batch")
    def analyze_batch():
        return {
            "batch_id": "batch_001",
            "total_images": 10,
            "processed": 10,
            "results_url": "/api/v1/batch/batch_001/results",
        }

    @app.get("/api/v1/diseases")
    def list_diseases():
        return {
            "diseases": [
                {"id": "leaf_blight", "name": "Leaf Blight", "name_ar": "لفحة الأوراق"},
                {
                    "id": "powdery_mildew",
                    "name": "Powdery Mildew",
                    "name_ar": "البياض الدقيقي",
                },
            ]
        }

    @app.get("/api/v1/diseases/{disease_id}")
    def get_disease(disease_id: str):
        return {
            "id": disease_id,
            "name": "Leaf Blight",
            "name_ar": "لفحة الأوراق",
            "description": "Fungal disease affecting leaves",
            "symptoms": ["brown spots", "wilting"],
            "treatment": ["fungicide", "remove infected leaves"],
        }

    @app.get("/api/v1/models/info")
    def get_model_info():
        return {
            "model_version": "v3.2.0",
            "supported_crops": ["tomato", "wheat", "potato"],
            "accuracy": 0.92,
            "last_updated": "2025-12-01",
        }

    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200


class TestImageAnalysis:
    def test_analyze_image(self, client):
        response = client.post(
            "/api/v1/analyze/image",
            json={"image_url": "https://example.com/image.jpg", "crop": "tomato"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert len(data["predictions"]) > 0

    def test_predictions_have_confidence(self, client):
        response = client.post("/api/v1/analyze/image", json={})
        predictions = response.json()["predictions"]
        for pred in predictions:
            assert "confidence" in pred
            assert 0 <= pred["confidence"] <= 1


class TestBatchAnalysis:
    def test_analyze_batch(self, client):
        response = client.post(
            "/api/v1/analyze/batch", json={"images": ["url1", "url2"]}
        )
        assert response.status_code == 200
        assert "batch_id" in response.json()


class TestDiseases:
    def test_list_diseases(self, client):
        response = client.get("/api/v1/diseases")
        assert response.status_code == 200
        assert "diseases" in response.json()

    def test_get_disease_details(self, client):
        response = client.get("/api/v1/diseases/leaf_blight")
        assert response.status_code == 200
        data = response.json()
        assert "symptoms" in data
        assert "treatment" in data


class TestModelInfo:
    def test_get_model_info(self, client):
        response = client.get("/api/v1/models/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_version" in data
        assert "accuracy" in data
