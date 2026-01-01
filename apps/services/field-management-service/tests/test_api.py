"""
Integration tests for Profitability API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import app

client = TestClient(app)


class TestProfitabilityAPI:
    """Test suite for Profitability API endpoints"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "field_core"

    def test_readiness_check(self):
        """Test readiness check endpoint"""
        response = client.get("/readyz")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_list_crops(self):
        """Test list available crops endpoint"""
        response = client.get("/v1/crops/list")
        assert response.status_code == 200

        data = response.json()
        assert "crops" in data
        assert "total" in data
        assert data["total"] > 0
        assert len(data["crops"]) == data["total"]

        # Check crop structure
        crop = data["crops"][0]
        assert "crop_code" in crop
        assert "name_en" in crop
        assert "name_ar" in crop
        assert "has_regional_data" in crop

    def test_list_cost_categories(self):
        """Test list cost categories endpoint"""
        response = client.get("/v1/costs/categories")
        assert response.status_code == 200

        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 9  # All cost categories

        # Check category structure
        category = data["categories"][0]
        assert "code" in category
        assert "name_en" in category
        assert "name_ar" in category

    def test_get_crop_profitability(self):
        """Test get crop profitability with regional data"""
        response = client.get(
            "/v1/profitability/crop/season-2025-1",
            params={"field_id": "field-001", "crop_code": "wheat", "area_ha": 2.5},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["field_id"] == "field-001"
        assert data["crop_code"] == "wheat"
        assert data["crop_name_en"] == "Wheat"
        assert data["crop_name_ar"] == "قمح"
        assert data["area_ha"] == 2.5
        assert "total_costs" in data
        assert "total_revenue" in data
        assert "net_profit" in data
        assert "roi" in data or "return_on_investment" in data

    def test_analyze_profitability_with_costs(self):
        """Test analyze profitability with custom costs"""
        request_data = {
            "field_id": "field-001",
            "crop_season_id": "season-2025-1",
            "crop_code": "wheat",
            "area_ha": 2.5,
            "costs": [
                {
                    "category": "seeds",
                    "description": "Premium wheat seeds",
                    "amount": 200000,
                    "unit": "YER",
                    "quantity": 75,
                },
                {
                    "category": "fertilizer",
                    "description": "NPK fertilizer",
                    "amount": 300000,
                    "unit": "YER",
                    "quantity": 1,
                },
            ],
            "revenues": [
                {
                    "description": "Wheat harvest",
                    "quantity": 7500,
                    "unit": "kg",
                    "unit_price": 550,
                }
            ],
        }

        response = client.post("/v1/profitability/analyze", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "analysis" in data
        assert "recommendations" in data

        analysis = data["analysis"]
        assert analysis["total_costs"] == 500000
        assert analysis["total_revenue"] == 4125000

        recommendations = data["recommendations"]
        assert "english" in recommendations
        assert "arabic" in recommendations

    def test_season_summary(self):
        """Test season summary analysis"""
        request_data = {
            "farmer_id": "farmer-001",
            "season_year": "2025",
            "crops": [
                {"field_id": "field-001", "crop_code": "wheat", "area_ha": 2.5},
                {"field_id": "field-002", "crop_code": "tomato", "area_ha": 1.0},
                {"field_id": "field-003", "crop_code": "potato", "area_ha": 1.5},
            ],
        }

        response = client.post("/v1/profitability/season", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["season_year"] == "2025"
        assert data["total_area_ha"] == 5.0
        assert "total_costs" in data
        assert "total_revenue" in data
        assert "total_profit" in data
        assert "overall_margin" in data
        assert len(data["crops"]) == 3
        assert "best_crop" in data
        assert "worst_crop" in data
        assert "recommendations_en" in data
        assert "recommendations_ar" in data

    def test_compare_crops(self):
        """Test crop comparison"""
        response = client.get(
            "/v1/profitability/compare",
            params={
                "crops": "wheat,tomato,potato,coffee",
                "area_ha": 1.0,
                "region": "sanaa",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["region"] == "sanaa"
        assert data["area_ha"] == 1.0
        assert len(data["crops"]) == 4
        assert "best_crop" in data
        assert "worst_crop" in data

        # Check crops are sorted by profitability
        profits = [crop["profit_per_ha"] for crop in data["crops"]]
        assert profits == sorted(profits, reverse=True)

    def test_calculate_break_even(self):
        """Test break-even calculation"""
        response = client.get(
            "/v1/profitability/break-even",
            params={
                "crop_code": "wheat",
                "area_ha": 2.5,
                "total_costs": 670000,
                "expected_price": 550,
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["crop_code"] == "wheat"
        assert data["area_ha"] == 2.5
        assert "break_even_yield_kg" in data
        assert "break_even_yield_kg_ha" in data
        assert "break_even_price_yer_kg" in data
        assert "yield_gap_percent" in data

    def test_get_benchmarks(self):
        """Test regional benchmarks"""
        response = client.get(
            "/v1/profitability/benchmarks/coffee", params={"region": "sanaa"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["crop_code"] == "coffee"
        assert data["region"] == "sanaa"
        assert "benchmarks" in data
        assert "costs_per_ha" in data["benchmarks"]
        assert "yield_kg_ha" in data["benchmarks"]
        assert "price_yer_kg" in data["benchmarks"]

    def test_get_benchmarks_invalid_crop(self):
        """Test benchmarks with invalid crop"""
        response = client.get(
            "/v1/profitability/benchmarks/invalid_crop", params={"region": "sanaa"}
        )
        assert response.status_code == 404

    def test_cost_breakdown(self):
        """Test cost breakdown"""
        response = client.get(
            "/v1/profitability/cost-breakdown/wheat", params={"area_ha": 2.5}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["crop_code"] == "wheat"
        assert data["area_ha"] == 2.5
        assert "breakdown" in data
        assert "total" in data["breakdown"]
        assert "seeds" in data["breakdown"]
        assert "fertilizer" in data["breakdown"]

    def test_historical_profitability(self):
        """Test historical profitability"""
        response = client.get(
            "/v1/profitability/history/field-001/wheat", params={"years": 3}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["field_id"] == "field-001"
        assert data["crop_code"] == "wheat"
        assert data["years_analyzed"] == 3
        assert len(data["history"]) == 3

    def test_invalid_area_negative(self):
        """Test validation of negative area"""
        response = client.get(
            "/v1/profitability/crop/season-001",
            params={"field_id": "field-001", "crop_code": "wheat", "area_ha": -1.0},
        )
        assert response.status_code == 422  # Validation error

    def test_invalid_area_zero(self):
        """Test validation of zero area"""
        response = client.get(
            "/v1/profitability/crop/season-001",
            params={"field_id": "field-001", "crop_code": "wheat", "area_ha": 0},
        )
        assert response.status_code == 422  # Validation error


class TestProfitabilityEdgeCases:
    """Test edge cases and error handling"""

    def test_very_large_area(self):
        """Test with very large area"""
        response = client.get(
            "/v1/profitability/crop/season-001",
            params={
                "field_id": "field-001",
                "crop_code": "wheat",
                "area_ha": 10000,  # Very large
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["area_ha"] == 10000

    def test_very_small_area(self):
        """Test with very small area"""
        response = client.get(
            "/v1/profitability/crop/season-001",
            params={
                "field_id": "field-001",
                "crop_code": "wheat",
                "area_ha": 0.01,  # Very small
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["area_ha"] == 0.01

    def test_all_available_crops(self):
        """Test profitability for all available crops"""
        # Get list of crops
        crops_response = client.get("/v1/crops/list")
        crops = crops_response.json()["crops"]

        # Test each crop
        for crop in crops:
            if crop["has_regional_data"]:
                response = client.get(
                    f"/v1/profitability/crop/season-001",
                    params={
                        "field_id": "field-001",
                        "crop_code": crop["crop_code"],
                        "area_ha": 1.0,
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert data["crop_code"] == crop["crop_code"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
