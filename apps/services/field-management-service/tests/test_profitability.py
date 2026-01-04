"""
Tests for Crop Profitability Analyzer
"""

import os
import sys

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from profitability_analyzer import (
    CropProfitability,
    ProfitabilityAnalyzer,
)


class TestProfitabilityAnalyzer:
    """Test suite for ProfitabilityAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return ProfitabilityAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_crop_with_regional_data(self, analyzer):
        """Test crop analysis using regional estimates"""
        result = await analyzer.analyze_crop(
            field_id="field-001",
            crop_season_id="season-2025-1",
            crop_code="wheat",
            area_ha=2.5,
        )

        assert isinstance(result, CropProfitability)
        assert result.field_id == "field-001"
        assert result.crop_code == "wheat"
        assert result.crop_name_en == "Wheat"
        assert result.crop_name_ar == "قمح"
        assert result.area_ha == 2.5
        assert result.total_costs > 0
        assert result.total_revenue > 0
        assert len(result.costs) > 0
        assert len(result.revenues) > 0

    @pytest.mark.asyncio
    async def test_analyze_crop_with_custom_costs(self, analyzer):
        """Test crop analysis with custom costs"""
        costs = [
            {
                "category": "seeds",
                "description": "Premium wheat seeds",
                "amount": 200000,
                "unit": "YER",
                "quantity": 75,
                "unit_cost": 2666.67,
            },
            {
                "category": "fertilizer",
                "description": "NPK fertilizer",
                "amount": 300000,
                "unit": "YER",
                "quantity": 1,
                "unit_cost": 300000,
            },
        ]

        result = await analyzer.analyze_crop(
            field_id="field-001",
            crop_season_id="season-2025-1",
            crop_code="wheat",
            area_ha=2.5,
            costs=costs,
        )

        assert result.total_costs == 500000
        assert len(result.costs) == 2

    @pytest.mark.asyncio
    async def test_analyze_crop_with_custom_revenues(self, analyzer):
        """Test crop analysis with custom revenues"""
        revenues = [
            {
                "description": "Wheat harvest - premium grade",
                "quantity": 7500,
                "unit": "kg",
                "unit_price": 600,
                "grade": "premium",
            }
        ]

        result = await analyzer.analyze_crop(
            field_id="field-001",
            crop_season_id="season-2025-1",
            crop_code="wheat",
            area_ha=2.5,
            revenues=revenues,
        )

        assert result.total_revenue == 4500000
        assert result.actual_yield == 3000  # 7500 / 2.5
        assert len(result.revenues) == 1
        assert result.revenues[0].grade == "premium"

    @pytest.mark.asyncio
    async def test_profitability_metrics(self, analyzer):
        """Test profitability metrics calculation"""
        result = await analyzer.analyze_crop(
            field_id="field-001",
            crop_season_id="season-2025-1",
            crop_code="tomato",
            area_ha=1.0,
        )

        # Check all metrics are calculated
        assert result.gross_profit == result.total_revenue - result.total_costs
        assert result.cost_per_ha == result.total_costs / result.area_ha
        assert result.revenue_per_ha == result.total_revenue / result.area_ha
        assert result.profit_per_ha == result.net_profit / result.area_ha

        # Check percentages
        if result.total_revenue > 0:
            expected_margin = result.gross_profit / result.total_revenue * 100
            assert abs(result.gross_margin_percent - expected_margin) < 0.01

        # Check ROI
        if result.total_costs > 0:
            expected_roi = result.net_profit / result.total_costs * 100
            assert abs(result.return_on_investment - expected_roi) < 0.01

    @pytest.mark.asyncio
    async def test_break_even_calculation(self, analyzer):
        """Test break-even yield calculation"""
        result = await analyzer.calculate_break_even(
            crop_code="wheat", area_ha=2.5, total_costs=670000, expected_price=550
        )

        assert "break_even_yield_kg" in result
        assert "break_even_yield_kg_ha" in result
        assert "break_even_price_yer_kg" in result
        assert result["break_even_yield_kg"] > 0
        assert result["area_ha"] == 2.5

        # Manual calculation check
        expected_be_yield = 670000 / 550
        assert abs(result["break_even_yield_kg"] - expected_be_yield) < 0.01

    @pytest.mark.asyncio
    async def test_compare_crops(self, analyzer):
        """Test crop comparison"""
        crops = ["wheat", "tomato", "potato"]
        result = await analyzer.compare_crops(
            crop_codes=crops, area_ha=1.0, region="sanaa"
        )

        assert len(result) == 3
        assert all("crop_code" in crop for crop in result)
        assert all("estimated_profit" in crop for crop in result)
        assert all("roi_percent" in crop for crop in result)

        # Results should be sorted by profit per hectare
        profits = [crop["profit_per_ha"] for crop in result]
        assert profits == sorted(profits, reverse=True)

    @pytest.mark.asyncio
    async def test_season_analysis(self, analyzer):
        """Test season analysis with multiple crops"""
        crops_data = [
            {"field_id": "field-001", "crop_code": "wheat", "area_ha": 2.5},
            {"field_id": "field-002", "crop_code": "tomato", "area_ha": 1.0},
            {"field_id": "field-003", "crop_code": "potato", "area_ha": 1.5},
        ]

        result = await analyzer.analyze_season(
            farmer_id="farmer-001", season_year="2025", crops_data=crops_data
        )

        assert result.season_year == "2025"
        assert result.total_area_ha == 5.0
        assert result.total_costs > 0
        assert result.total_revenue > 0
        assert result.total_profit == result.total_revenue - result.total_costs
        assert len(result.crops) == 3
        assert result.best_crop
        assert result.worst_crop
        assert len(result.recommendations_en) > 0
        assert len(result.recommendations_ar) > 0

        # Check rankings
        ranks = [crop.rank_in_portfolio for crop in result.crops]
        assert set(ranks) == {1, 2, 3}

    @pytest.mark.asyncio
    async def test_cost_breakdown(self, analyzer):
        """Test cost breakdown by category"""
        result = await analyzer.get_cost_breakdown(crop_code="wheat", area_ha=1.0)

        assert "total" in result
        assert "seeds" in result
        assert "fertilizer" in result
        assert "labor" in result

        # Check percentages are calculated
        assert "seeds_percent" in result
        assert "fertilizer_percent" in result

        # Verify percentages sum to 100
        total_pct = sum(v for k, v in result.items() if k.endswith("_percent"))
        assert abs(total_pct - 100) < 0.1

    @pytest.mark.asyncio
    async def test_regional_benchmarks(self, analyzer):
        """Test regional benchmark retrieval"""
        result = await analyzer.get_regional_benchmarks(
            crop_code="coffee", region="sanaa"
        )

        assert result["crop_code"] == "coffee"
        assert result["crop_name_en"] == "Coffee"
        assert result["crop_name_ar"] == "بن"
        assert "benchmarks" in result
        assert "costs_per_ha" in result["benchmarks"]
        assert "yield_kg_ha" in result["benchmarks"]
        assert "price_yer_kg" in result["benchmarks"]
        assert "profit_per_ha" in result["benchmarks"]

    @pytest.mark.asyncio
    async def test_historical_profitability(self, analyzer):
        """Test historical profitability retrieval"""
        result = await analyzer.get_historical_profitability(
            field_id="field-001", crop_code="wheat", years=5
        )

        assert len(result) == 5
        assert all("year" in item for item in result)
        assert all("profit" in item for item in result)
        assert all("roi_percent" in item for item in result)

    def test_generate_recommendations(self, analyzer):
        """Test recommendation generation"""
        # Create a mock analysis with low yield

        analysis = CropProfitability(
            field_id="field-001",
            crop_season_id="season-001",
            crop_code="wheat",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            area_ha=1.0,
            costs=[],
            total_costs=500000,
            cost_per_ha=500000,
            revenues=[],
            total_revenue=900000,
            revenue_per_ha=900000,
            gross_profit=400000,
            gross_margin_percent=44.4,
            net_profit=400000,
            net_margin_percent=44.4,
            profit_per_ha=400000,
            break_even_yield=1000,
            actual_yield=1800,  # Low yield
            return_on_investment=80,
            vs_regional_average=0,
            rank_in_portfolio=1,
        )

        result = analyzer.generate_recommendations(analysis)

        assert "english" in result
        assert "arabic" in result
        assert len(result["english"]) > 0
        assert len(result["arabic"]) > 0

    @pytest.mark.asyncio
    async def test_all_crops_have_data(self, analyzer):
        """Test that all crops in names dict have corresponding data"""
        for crop_code in analyzer.CROP_NAMES_EN.keys():
            assert crop_code in analyzer.CROP_NAMES_AR
            assert crop_code in analyzer.REGIONAL_COSTS
            assert crop_code in analyzer.REGIONAL_YIELDS
            assert crop_code in analyzer.REGIONAL_PRICES

    @pytest.mark.asyncio
    async def test_high_value_crops(self, analyzer):
        """Test that high-value crops like coffee and qat are profitable"""
        for crop_code in ["coffee", "qat"]:
            result = await analyzer.analyze_crop(
                field_id="field-001",
                crop_season_id="season-001",
                crop_code=crop_code,
                area_ha=1.0,
            )

            # High-value crops should have high revenue per ha
            assert result.revenue_per_ha > 1000000  # > 1M YER/ha
            # And should be profitable
            assert result.net_profit > 0

    @pytest.mark.asyncio
    async def test_negative_profit_scenario(self, analyzer):
        """Test handling of unprofitable scenarios"""
        # Create a scenario with high costs and low revenue
        costs = [
            {
                "category": "seeds",
                "description": "Expensive seeds",
                "amount": 500000,
                "unit": "YER",
                "quantity": 1,
                "unit_cost": 500000,
            },
            {
                "category": "fertilizer",
                "description": "Premium fertilizer",
                "amount": 600000,
                "unit": "YER",
                "quantity": 1,
                "unit_cost": 600000,
            },
        ]

        revenues = [
            {
                "description": "Poor harvest",
                "quantity": 500,  # Very low yield
                "unit": "kg",
                "unit_price": 400,
                "grade": "low",
            }
        ]

        result = await analyzer.analyze_crop(
            field_id="field-001",
            crop_season_id="season-001",
            crop_code="wheat",
            area_ha=1.0,
            costs=costs,
            revenues=revenues,
        )

        assert result.total_costs > result.total_revenue
        assert result.net_profit < 0
        assert result.gross_margin_percent < 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
