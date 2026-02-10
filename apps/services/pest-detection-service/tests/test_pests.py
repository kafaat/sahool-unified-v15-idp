"""
Tests for Pests API.
اختبارات واجهة برمجة الآفات.
"""

import pytest


class TestPestsAPI:
    """Test cases for pests endpoints."""

    def test_list_pests(self, client):
        """Test listing all pests."""
        response = client.get("/api/v1/pests")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 10  # We have 10 pests in database

    def test_list_pests_by_category(self, client):
        """Test filtering pests by category."""
        response = client.get("/api/v1/pests?category=insect")
        assert response.status_code == 200
        data = response.json()
        assert all(p["category"] == "insect" for p in data)

    def test_list_pests_by_crop(self, client):
        """Test filtering pests by crop."""
        response = client.get("/api/v1/pests?crop=date_palm")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # All returned pests should affect date_palm
        for pest in data:
            assert "date_palm" in [c.lower() for c in pest["affected_crops"]]

    def test_list_quarantine_pests(self, client):
        """Test filtering quarantine pests only."""
        response = client.get("/api/v1/pests?quarantine_only=true")
        assert response.status_code == 200
        data = response.json()
        assert all(p["is_quarantine"] for p in data)

    def test_get_pest_by_id(self, client):
        """Test getting specific pest by ID."""
        response = client.get("/api/v1/pests/rpw")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "rpw"
        assert data["name_en"] == "Red Palm Weevil"
        assert data["name_ar"] == "سوسة النخيل الحمراء"
        assert data["is_quarantine"] is True

    def test_get_pest_not_found(self, client):
        """Test getting non-existent pest."""
        response = client.get("/api/v1/pests/nonexistent")
        assert response.status_code == 404

    def test_search_pests_english(self, client):
        """Test searching pests by English name."""
        response = client.get("/api/v1/pests/search?q=palm")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Should find Red Palm Weevil
        pest_ids = [p["id"] for p in data]
        assert "rpw" in pest_ids

    def test_search_pests_arabic(self, client):
        """Test searching pests by Arabic name."""
        response = client.get("/api/v1/pests/search?q=سوسة")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_search_pests_scientific(self, client):
        """Test searching pests by scientific name."""
        response = client.get("/api/v1/pests/search?q=Rhynchophorus")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["id"] == "rpw"

    def test_search_pests_min_length(self, client):
        """Test search requires minimum 2 characters."""
        response = client.get("/api/v1/pests/search?q=a")
        assert response.status_code == 422  # Validation error

    def test_get_pests_by_crop(self, client):
        """Test getting pests for specific crop."""
        response = client.get("/api/v1/pests/crop/wheat")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        # Aphids should be in the list
        pest_ids = [p["id"] for p in data]
        assert "aphids" in pest_ids

    def test_get_quarantine_pests_endpoint(self, client):
        """Test dedicated quarantine pests endpoint."""
        response = client.get("/api/v1/pests/quarantine")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4  # RPW, Locust, Tuta, Fruit Fly
        assert all(p["is_quarantine"] for p in data)

    def test_get_seasonal_predictions(self, client):
        """Test seasonal pest predictions."""
        response = client.get("/api/v1/pests/seasonal?month=6")
        assert response.status_code == 200
        data = response.json()
        assert data["season"] == "summer"
        assert data["season_ar"] == "الصيف"
        assert "predicted_pests" in data

    def test_get_seasonal_predictions_with_crop(self, client):
        """Test seasonal predictions filtered by crop."""
        response = client.get("/api/v1/pests/seasonal?month=3&crop=wheat")
        assert response.status_code == 200
        data = response.json()
        assert data["season"] == "spring"

    def test_identify_by_symptoms(self, client):
        """Test symptom-based pest identification."""
        response = client.post(
            "/api/v1/pests/identify/symptoms",
            json={
                "crop": "wheat",
                "symptoms": ["yellowing", "curled leaves"],
                "region": "middle_east",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert data["crop"] == "wheat"


class TestPestDataIntegrity:
    """Test pest database data integrity."""

    def test_all_pests_have_required_fields(self, client):
        """Test all pests have required fields."""
        response = client.get("/api/v1/pests")
        data = response.json()

        required_fields = [
            "id",
            "name_en",
            "name_ar",
            "scientific_name",
            "category",
            "description_en",
            "description_ar",
            "affected_crops",
            "symptoms_en",
            "symptoms_ar",
        ]

        for pest in data:
            for field in required_fields:
                assert field in pest, f"Missing field {field} in pest {pest.get('id')}"

    def test_all_pests_have_bilingual_content(self, client):
        """Test all pests have both English and Arabic content."""
        response = client.get("/api/v1/pests")
        data = response.json()

        for pest in data:
            pest_id = pest["id"]
            assert pest["name_ar"], f"Missing Arabic name for {pest_id}"
            assert pest["description_ar"], f"Missing Arabic description for {pest_id}"
            assert len(pest["symptoms_ar"]) > 0, f"Missing Arabic symptoms for {pest_id}"

    def test_rpw_pest_details(self, client):
        """Test Red Palm Weevil has complete details."""
        response = client.get("/api/v1/pests/rpw")
        data = response.json()

        assert data["scientific_name"] == "Rhynchophorus ferrugineus"
        assert "date_palm" in data["affected_crops"]
        assert data["is_quarantine"] is True
        assert len(data["symptoms_en"]) >= 3
        assert len(data["symptoms_ar"]) >= 3
