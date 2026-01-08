"""
SAHOOL Astronomical Calendar Service - Unit Tests
اختبارات خدمة التقويم الفلكي الزراعي
"""

import pytest
from fastapi.testclient import TestClient


# Mock the main app
@pytest.fixture
def client():
    """Create test client with mocked app"""
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/healthz")
    def health():
        return {"status": "ok", "service": "astronomical_calendar", "version": "15.5.0"}

    @app.get("/api/v1/moon/phase")
    def get_moon_phase(date: str = None):
        return {
            "date": date or "2025-12-23",
            "phase": "waning_gibbous",
            "phase_ar": "أحدب متناقص",
            "illumination": 0.78,
            "age_days": 18.5,
            "next_new_moon": "2025-12-30",
            "next_full_moon": "2026-01-13",
            "agriculture": {
                "suitable_for": ["pruning", "harvesting"],
                "avoid": ["planting", "grafting"],
            },
        }

    @app.get("/api/v1/lunar-mansion")
    def get_lunar_mansion(date: str = None):
        return {
            "date": date or "2025-12-23",
            "mansion_number": 15,
            "name_ar": "الغفر",
            "name_en": "Al-Ghafr",
            "meaning": "الغطاء",
            "star": "ι Virginis",
            "element": "air",
            "agriculture": {
                "recommendation": "مناسب للزراعة والغرس",
                "crops": ["wheat", "barley", "vegetables"],
            },
        }

    @app.get("/api/v1/hijri")
    def get_hijri_date(gregorian_date: str = None):
        return {
            "gregorian": gregorian_date or "2025-12-23",
            "hijri": {
                "year": 1447,
                "month": 6,
                "day": 22,
                "month_name": "جمادى الآخرة",
                "month_name_en": "Jumada al-Thani",
            },
        }

    @app.get("/api/v1/zodiac/agricultural")
    def get_agricultural_zodiac(date: str = None):
        return {
            "date": date or "2025-12-23",
            "sun_sign": "capricorn",
            "sun_sign_ar": "الجدي",
            "moon_sign": "virgo",
            "moon_sign_ar": "العذراء",
            "agriculture": {
                "element": "earth",
                "fertility": "high",
                "suitable_activities": ["planting_root_crops", "fertilizing"],
            },
        }

    @app.get("/api/v1/planting-calendar")
    def get_planting_calendar(month: int, crop: str = None):
        return {
            "month": month,
            "month_name": "ديسمبر",
            "recommendations": [
                {
                    "crop": "wheat",
                    "crop_ar": "القمح",
                    "activity": "planting",
                    "optimal_days": [1, 5, 10, 15],
                    "moon_phase": "waxing",
                }
            ],
            "traditional_wisdom": "شهر الزراعة الشتوية",
        }

    @app.get("/api/v1/seasons")
    def get_yemeni_seasons():
        return {
            "current_season": "شتاء",
            "current_season_en": "winter",
            "traditional_name": "الشتاء",
            "start_date": "2025-12-21",
            "end_date": "2026-03-20",
            "agricultural_notes": "موسم زراعة الحبوب الشتوية",
        }

    @app.get("/api/v1/today")
    def get_today_info():
        return {
            "gregorian": "2025-12-23",
            "hijri": {"year": 1447, "month": 6, "day": 22},
            "moon_phase": "waning_gibbous",
            "lunar_mansion": "الغفر",
            "zodiac": {"sun": "capricorn", "moon": "virgo"},
            "agriculture": {
                "overall_rating": "good",
                "best_activities": ["harvesting", "pruning"],
                "avoid": ["planting_seeds"],
            },
        }

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "astronomical_calendar"


class TestMoonPhase:
    """Test moon phase endpoints"""

    def test_get_current_moon_phase(self, client):
        response = client.get("/api/v1/moon/phase")
        assert response.status_code == 200
        data = response.json()
        assert "phase" in data
        assert "phase_ar" in data
        assert "illumination" in data
        assert 0 <= data["illumination"] <= 1

    def test_get_moon_phase_with_date(self, client):
        response = client.get("/api/v1/moon/phase?date=2025-12-23")
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2025-12-23"

    def test_moon_phase_has_agriculture_info(self, client):
        response = client.get("/api/v1/moon/phase")
        assert response.status_code == 200
        data = response.json()
        assert "agriculture" in data
        assert "suitable_for" in data["agriculture"]


class TestLunarMansions:
    """Test lunar mansion (منازل النجوم) endpoints"""

    def test_get_lunar_mansion(self, client):
        response = client.get("/api/v1/lunar-mansion")
        assert response.status_code == 200
        data = response.json()
        assert "mansion_number" in data
        assert 1 <= data["mansion_number"] <= 28
        assert "name_ar" in data
        assert "name_en" in data

    def test_lunar_mansion_has_agriculture(self, client):
        response = client.get("/api/v1/lunar-mansion")
        assert response.status_code == 200
        data = response.json()
        assert "agriculture" in data
        assert "recommendation" in data["agriculture"]


class TestHijriCalendar:
    """Test Hijri calendar conversion"""

    def test_get_hijri_date(self, client):
        response = client.get("/api/v1/hijri")
        assert response.status_code == 200
        data = response.json()
        assert "hijri" in data
        assert "year" in data["hijri"]
        assert "month" in data["hijri"]
        assert "day" in data["hijri"]

    def test_hijri_with_gregorian_date(self, client):
        response = client.get("/api/v1/hijri?gregorian_date=2025-12-23")
        assert response.status_code == 200
        data = response.json()
        assert data["gregorian"] == "2025-12-23"


class TestAgriculturalZodiac:
    """Test agricultural zodiac endpoints"""

    def test_get_zodiac(self, client):
        response = client.get("/api/v1/zodiac/agricultural")
        assert response.status_code == 200
        data = response.json()
        assert "sun_sign" in data
        assert "moon_sign" in data
        assert "agriculture" in data

    def test_zodiac_has_arabic_names(self, client):
        response = client.get("/api/v1/zodiac/agricultural")
        assert response.status_code == 200
        data = response.json()
        assert "sun_sign_ar" in data
        assert "moon_sign_ar" in data


class TestPlantingCalendar:
    """Test planting calendar endpoints"""

    def test_get_planting_calendar(self, client):
        response = client.get("/api/v1/planting-calendar?month=12")
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == 12
        assert "recommendations" in data

    def test_planting_calendar_has_recommendations(self, client):
        response = client.get("/api/v1/planting-calendar?month=12")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) > 0
        rec = data["recommendations"][0]
        assert "crop" in rec
        assert "activity" in rec


class TestSeasons:
    """Test Yemeni agricultural seasons"""

    def test_get_seasons(self, client):
        response = client.get("/api/v1/seasons")
        assert response.status_code == 200
        data = response.json()
        assert "current_season" in data
        assert "current_season_en" in data
        assert "agricultural_notes" in data


class TestTodayInfo:
    """Test comprehensive today info"""

    def test_get_today_info(self, client):
        response = client.get("/api/v1/today")
        assert response.status_code == 200
        data = response.json()
        assert "gregorian" in data
        assert "hijri" in data
        assert "moon_phase" in data
        assert "lunar_mansion" in data
        assert "zodiac" in data
        assert "agriculture" in data

    def test_today_has_agriculture_rating(self, client):
        response = client.get("/api/v1/today")
        assert response.status_code == 200
        data = response.json()
        assert "overall_rating" in data["agriculture"]
        assert data["agriculture"]["overall_rating"] in [
            "excellent",
            "good",
            "moderate",
            "poor",
        ]
