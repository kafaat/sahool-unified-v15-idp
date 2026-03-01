"""Tests for enhanced marketplace module."""
import pytest
from shared.marketplace_enhanced import (
    MarketplaceEngine,
    QualityGrade,
    OrderType,
    ListingStatus,
)


class TestMarketplaceEngine:
    def setup_method(self):
        self.engine = MarketplaceEngine()

    def test_get_market_prices(self):
        prices = self.engine.get_market_prices()
        assert len(prices) > 0
        wheat_prices = [p for p in prices if p.crop_type == "wheat"]
        assert len(wheat_prices) == 1
        assert wheat_prices[0].price_sar_per_ton > 0

    def test_create_listing(self):
        listing = self.engine.create_listing(
            seller_id="seller-001",
            tenant_id="tenant-001",
            crop_type="wheat",
            quantity_tons=50,
            price_sar_per_ton=1900,
            quality_grade=QualityGrade.GRADE_A,
        )
        assert listing.status == ListingStatus.ACTIVE
        assert listing.crop_type_ar == "قمح"

    def test_market_summary(self):
        self.engine.create_listing(
            seller_id="s1", tenant_id="t1",
            crop_type="wheat", quantity_tons=100,
            price_sar_per_ton=1850,
        )
        self.engine.create_listing(
            seller_id="s2", tenant_id="t1",
            crop_type="tomato", quantity_tons=50,
            price_sar_per_ton=2500,
        )
        summary = self.engine.get_market_summary()
        assert summary.active_listings == 2
        assert summary.total_volume_tons == 150
        assert summary.total_value_sar > 0

    def test_listing_has_arabic(self):
        listing = self.engine.create_listing(
            seller_id="s1", tenant_id="t1",
            crop_type="date_premium", quantity_tons=10,
            price_sar_per_ton=12000,
        )
        assert listing.crop_type_ar == "تمور ممتازة"
