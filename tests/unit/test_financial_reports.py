"""Tests for financial reports module."""
import pytest
from shared.financial_reports import (
    FinancialReportGenerator,
    CostEntry,
    RevenueEntry,
    CostCategory,
    Season,
    FieldFinancialReport,
)

class TestFinancialReportGenerator:
    def setup_method(self):
        self.gen = FinancialReportGenerator()

    def test_break_even_calculation(self):
        be = self.gen.calculate_break_even(42000, 1850, 10)
        assert be > 0
        assert be < 5  # Should be around 2.27 t/ha

    def test_break_even_zero_price(self):
        assert self.gen.calculate_break_even(42000, 0, 10) == 0.0

    def test_recommendation_roi(self):
        roi = self.gen.estimate_recommendation_roi(
            recommendation_type="fertilizer",
            investment_sar=1150,
            crop_type="wheat",
            area_hectares=10,
            expected_yield_increase_percent=15,
            current_yield_ton_ha=4.0,
        )
        assert roi.expected_roi_percent > 0
        assert roi.recommendation_type_ar == "تسميد"

    def test_generate_field_report(self):
        costs = [
            CostEntry(category=CostCategory.SEED, amount_sar=5000),
            CostEntry(category=CostCategory.FERTILIZER, amount_sar=8000),
            CostEntry(category=CostCategory.IRRIGATION, amount_sar=3000),
        ]
        revenues = [
            RevenueEntry(crop_type="wheat", yield_ton=40, price_per_ton_sar=1850, total_revenue_sar=74000),
        ]

        report = self.gen.generate_field_report(
            field_id="FIELD-001",
            field_name="North Field",
            field_name_ar="الحقل الشمالي",
            tenant_id="tenant-001",
            area_hectares=10,
            crop_type="wheat",
            crop_type_ar="قمح",
            season=Season.WINTER,
            costs=costs,
            revenues=revenues,
        )

        assert report.total_costs_sar == 16000
        assert report.total_revenue_sar == 74000
        assert report.profit_sar == 58000
        assert report.roi_percent > 0

    def test_season_comparison(self):
        current = FieldFinancialReport(
            field_id="F1",
            total_costs_sar=16000,
            total_revenue_sar=74000,
            profit_sar=58000,
            roi_percent=362.5,
            season=Season.WINTER,
            generated_at="2026-01-01",
        )
        previous = FieldFinancialReport(
            field_id="F1",
            total_costs_sar=18000,
            total_revenue_sar=65000,
            profit_sar=47000,
            roi_percent=261.1,
            season=Season.WINTER,
            generated_at="2025-01-01",
        )

        comparison = self.gen.compare_seasons(current, previous)
        assert comparison.cost_change_percent < 0  # Costs decreased
        assert comparison.revenue_change_percent > 0  # Revenue increased

    def test_crop_prices_exist(self):
        assert "wheat" in self.gen.CROP_PRICES
        assert "date_palm" in self.gen.CROP_PRICES
        assert self.gen.CROP_PRICES["wheat"] > 0
