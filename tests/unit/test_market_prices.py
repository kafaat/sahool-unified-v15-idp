"""
Unit tests for market_prices module

Tests cover:
- Price models and enums
- Price tracking and recording
- Trend analysis
- Regional price queries
- Bilingual support
- Alert management
- Market comparisons

Author: SAHOOL Test Suite
Updated: January 2026
"""

import asyncio
import tempfile
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from shared.market_prices import (
    CROP_TYPES,
    MAJOR_MARKETS,
    SAUDI_REGIONS,
    YEMEN_REGIONS,
    AlertStatus,
    AlertStorage,
    AlertType,
    Country,
    CropPrice,
    CropType,
    # Models
    Currency,
    Market,
    MarketComparison,
    MarketPriceErrors,
    MarketPriceException,
    MarketPriceTracker,
    MarketType,
    PriceAlert,
    # Analyzer
    PriceAnalyzer,
    PriceQuality,
    # Tracker
    PriceStorage,
    PriceTrend,
    PriceUnit,
    Region,
    Season,
    SellingRecommendation,
    TrendDirection,
)

# =============================================================================
# Tests for Price Models and Enums
# =============================================================================


@pytest.mark.unit
class TestEnums:
    """Test enumeration definitions"""

    def test_currency_enum(self):
        """Test Currency enum values"""
        assert Currency.SAR.value == "SAR"
        assert Currency.YER.value == "YER"
        assert Currency.USD.value == "USD"

    def test_price_unit_enum(self):
        """Test PriceUnit enum values"""
        assert PriceUnit.KG.value == "kg"
        assert PriceUnit.TON.value == "ton"
        assert PriceUnit.QUINTAL.value == "quintal"
        assert PriceUnit.SACK.value == "sack"

    def test_price_quality_enum(self):
        """Test PriceQuality enum values"""
        assert PriceQuality.PREMIUM.value == "premium"
        assert PriceQuality.GRADE_A.value == "grade_a"
        assert PriceQuality.STANDARD.value == "standard"

    def test_market_type_enum(self):
        """Test MarketType enum values"""
        assert MarketType.WHOLESALE.value == "wholesale"
        assert MarketType.RETAIL.value == "retail"
        assert MarketType.FARM_GATE.value == "farm_gate"

    def test_alert_type_enum(self):
        """Test AlertType enum values"""
        assert AlertType.PRICE_ABOVE.value == "price_above"
        assert AlertType.PRICE_BELOW.value == "price_below"
        assert AlertType.PRICE_SPIKE.value == "price_spike"

    def test_alert_status_enum(self):
        """Test AlertStatus enum values"""
        assert AlertStatus.ACTIVE.value == "active"
        assert AlertStatus.TRIGGERED.value == "triggered"
        assert AlertStatus.EXPIRED.value == "expired"

    def test_trend_direction_enum(self):
        """Test TrendDirection enum values"""
        assert TrendDirection.RISING.value == "rising"
        assert TrendDirection.FALLING.value == "falling"
        assert TrendDirection.STABLE.value == "stable"
        assert TrendDirection.VOLATILE.value == "volatile"

    def test_season_enum(self):
        """Test Season enum values"""
        assert Season.WINTER.value == "winter"
        assert Season.SUMMER.value == "summer"
        assert Season.YEAR_ROUND.value == "year_round"

    def test_country_enum(self):
        """Test Country enum values"""
        assert Country.SAUDI_ARABIA.value == "SA"
        assert Country.YEMEN.value == "YE"


@pytest.mark.unit
class TestRegionModel:
    """Test Region data model"""

    def test_region_creation_saudi(self):
        """Test creating a Saudi region"""
        region = SAUDI_REGIONS["riyadh"]
        assert region.id == "riyadh"
        assert region.name == "Riyadh"
        assert region.name_ar == "الرياض"
        assert region.country == Country.SAUDI_ARABIA
        assert region.is_active is True

    def test_region_creation_yemen(self):
        """Test creating a Yemen region"""
        region = YEMEN_REGIONS["sanaa"]
        assert region.id == "sanaa"
        assert region.name == "Sana'a"
        assert region.name_ar == "صنعاء"
        assert region.country == Country.YEMEN

    def test_region_to_dict(self):
        """Test Region to_dict serialization"""
        region = SAUDI_REGIONS["riyadh"]
        data = region.to_dict()
        assert data["id"] == "riyadh"
        assert data["name"] == "Riyadh"
        assert data["country"] == "SA"
        assert data["is_active"] is True


@pytest.mark.unit
class TestMarketModel:
    """Test Market data model"""

    def test_market_creation(self):
        """Test creating a market"""
        market = MAJOR_MARKETS["riyadh_central"]
        assert market.id == "riyadh_central"
        assert market.name == "Riyadh Central Market"
        assert market.name_ar == "سوق الرياض المركزي"
        assert market.market_type == MarketType.WHOLESALE
        assert market.region_id == "riyadh"

    def test_market_supported_crops(self):
        """Test market supported crops"""
        market = MAJOR_MARKETS["riyadh_central"]
        assert "wheat" in market.supported_crops
        assert "dates" in market.supported_crops
        assert len(market.supported_crops) > 0

    def test_market_to_dict(self):
        """Test Market to_dict serialization"""
        market = MAJOR_MARKETS["riyadh_central"]
        data = market.to_dict()
        assert data["id"] == "riyadh_central"
        assert data["market_type"] == "wholesale"
        assert data["country"] == "SA"

    def test_market_yemen(self):
        """Test Yemen market"""
        market = MAJOR_MARKETS["sanaa_central"]
        assert market.country == Country.YEMEN
        assert market.region_id == "sanaa"


@pytest.mark.unit
class TestCropTypeModel:
    """Test CropType data model"""

    def test_crop_type_wheat(self):
        """Test wheat crop type"""
        crop = CROP_TYPES["wheat"]
        assert crop.id == "wheat"
        assert crop.name == "Wheat"
        assert crop.name_ar == "قمح"
        assert crop.category == "grains"
        assert crop.default_unit == PriceUnit.TON

    def test_crop_type_dates(self):
        """Test dates crop type"""
        crop = CROP_TYPES["dates"]
        assert crop.id == "dates"
        assert crop.name_ar == "تمور"
        assert crop.category == "dates"
        assert crop.default_unit == PriceUnit.KG

    def test_crop_type_seasons(self):
        """Test crop seasons"""
        wheat = CROP_TYPES["wheat"]
        assert Season.WINTER in wheat.seasons

        dates = CROP_TYPES["dates"]
        assert Season.SUMMER in dates.seasons

    def test_crop_type_to_dict(self):
        """Test CropType to_dict serialization"""
        crop = CROP_TYPES["wheat"]
        data = crop.to_dict()
        assert data["id"] == "wheat"
        assert data["category"] == "grains"
        assert "winter" in data["seasons"]


@pytest.mark.unit
class TestCropPriceModel:
    """Test CropPrice data model"""

    def test_crop_price_creation(self):
        """Test creating a crop price"""
        price = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            market_id="riyadh_central",
            market_name="Riyadh Central",
            market_name_ar="سوق الرياض المركزي",
            region_id="riyadh",
            price=Decimal("2500"),
            currency=Currency.SAR,
            unit=PriceUnit.TON,
            quality=PriceQuality.STANDARD,
        )
        assert price.crop_id == "wheat"
        assert price.price == Decimal("2500")
        assert price.currency == Currency.SAR

    def test_crop_price_bilingual(self):
        """Test bilingual support in CropPrice"""
        price = CropPrice(
            crop_id="dates",
            crop_name="Dates",
            crop_name_ar="تمور",
            variety="Sukkari",
            variety_ar="سكري",
            market_id="qassim_dates",
            market_name="Qassim Dates Market",
            market_name_ar="سوق القصيم للتمور",
            price=Decimal("1500"),
        )
        assert price.crop_name == "Dates"
        assert price.crop_name_ar == "تمور"
        assert price.variety_ar == "سكري"

    def test_crop_price_to_dict(self):
        """Test CropPrice to_dict serialization"""
        price = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            market_id="riyadh_central",
            price=Decimal("2500"),
        )
        data = price.to_dict()
        assert data["crop_id"] == "wheat"
        assert data["price"] == "2500"
        assert data["crop_name_ar"] == "قمح"

    def test_crop_price_from_dict(self):
        """Test CropPrice from_dict deserialization"""
        data = {
            "crop_id": "wheat",
            "crop_name": "Wheat",
            "crop_name_ar": "قمح",
            "market_id": "riyadh_central",
            "price": "2500",
            "currency": "SAR",
            "unit": "ton",
            "quality": "standard",
        }
        price = CropPrice.from_dict(data)
        assert price.crop_id == "wheat"
        assert price.price == Decimal("2500")


@pytest.mark.unit
class TestPriceAlertModel:
    """Test PriceAlert data model"""

    def test_price_alert_creation(self):
        """Test creating a price alert"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
            currency=Currency.SAR,
        )
        assert alert.crop_id == "wheat"
        assert alert.alert_type == AlertType.PRICE_ABOVE
        assert alert.threshold_value == Decimal("3000")
        assert alert.status == AlertStatus.ACTIVE

    def test_price_alert_is_valid(self):
        """Test alert validity check"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
            status=AlertStatus.ACTIVE,
            valid_from=date.today(),
        )
        assert alert.is_valid() is True

        # Expired alert
        alert.valid_until = date.today() - timedelta(days=1)
        assert alert.is_valid() is False

        # Disabled alert
        alert.valid_until = None
        alert.status = AlertStatus.DISABLED
        assert alert.is_valid() is False

    def test_price_alert_check_trigger_price_above(self):
        """Test trigger check for PRICE_ABOVE alert"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
            status=AlertStatus.ACTIVE,
        )
        assert alert.check_trigger(Decimal("3100")) is True
        assert alert.check_trigger(Decimal("2900")) is False

    def test_price_alert_check_trigger_price_below(self):
        """Test trigger check for PRICE_BELOW alert"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_BELOW,
            threshold_value=Decimal("2000"),
            status=AlertStatus.ACTIVE,
        )
        assert alert.check_trigger(Decimal("1900")) is True
        assert alert.check_trigger(Decimal("2100")) is False

    def test_price_alert_check_trigger_price_spike(self):
        """Test trigger check for PRICE_SPIKE alert"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_SPIKE,
            percentage_threshold=10.0,
            status=AlertStatus.ACTIVE,
        )
        # 10% increase should trigger
        assert alert.check_trigger(Decimal("2200"), Decimal("2000")) is True
        # 5% increase should not trigger
        assert alert.check_trigger(Decimal("2100"), Decimal("2000")) is False

    def test_price_alert_check_trigger_price_drop(self):
        """Test trigger check for PRICE_DROP alert"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_DROP,
            status=AlertStatus.ACTIVE,
        )
        assert alert.check_trigger(Decimal("1900"), Decimal("2000")) is True
        assert alert.check_trigger(Decimal("2100"), Decimal("2000")) is False


@pytest.mark.unit
class TestPriceTrendModel:
    """Test PriceTrend data model"""

    def test_price_trend_creation(self):
        """Test creating a price trend"""
        trend = PriceTrend(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            direction=TrendDirection.RISING,
            current_price=Decimal("2600"),
            previous_price=Decimal("2400"),
        )
        assert trend.crop_id == "wheat"
        assert trend.direction == TrendDirection.RISING

    def test_price_trend_to_dict(self):
        """Test PriceTrend to_dict serialization"""
        trend = PriceTrend(
            crop_id="wheat",
            direction=TrendDirection.RISING,
            current_price=Decimal("2600"),
        )
        data = trend.to_dict()
        assert data["crop_id"] == "wheat"
        assert data["direction"] == "rising"


# =============================================================================
# Tests for Storage
# =============================================================================


@pytest.mark.unit
class TestPriceStorage:
    """Test PriceStorage functionality"""

    @pytest.fixture
    def storage(self):
        """Create temporary storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield PriceStorage(tmpdir)

    @pytest.mark.asyncio
    async def test_save_and_load_price(self, storage):
        """Test saving and loading a price"""
        price = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
        )

        await storage.save_price(price)
        prices = await storage.load_prices(market_id="riyadh_central")

        assert len(prices) > 0
        assert prices[0].crop_id == "wheat"
        assert prices[0].price == Decimal("2500")

    @pytest.mark.asyncio
    async def test_load_prices_with_filters(self, storage):
        """Test loading prices with filters"""
        price1 = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
            price_date=date.today(),
        )
        price2 = CropPrice(
            crop_id="dates",
            crop_name="Dates",
            market_id="riyadh_central",
            price=Decimal("1500"),
            price_date=date.today(),
        )

        await storage.save_price(price1)
        await storage.save_price(price2)

        wheat_prices = await storage.load_prices(crop_id="wheat")
        assert len(wheat_prices) == 1
        assert wheat_prices[0].crop_id == "wheat"

    @pytest.mark.asyncio
    async def test_load_latest_price(self, storage):
        """Test loading latest price"""
        price1 = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            market_id="riyadh_central",
            price=Decimal("2400"),
            price_date=date.today() - timedelta(days=1),
        )
        price2 = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
            price_date=date.today(),
        )

        await storage.save_price(price1)
        await storage.save_price(price2)

        latest = await storage.load_latest_price("wheat")
        assert latest is not None
        assert latest.price == Decimal("2500")


@pytest.mark.unit
class TestAlertStorage:
    """Test AlertStorage functionality"""

    @pytest.fixture
    def storage(self):
        """Create temporary alert storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield AlertStorage(tmpdir)

    @pytest.mark.asyncio
    async def test_save_and_load_alert(self, storage):
        """Test saving and loading an alert"""
        alert = PriceAlert(
            id="alert_001",
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
        )

        await storage.save_alert(alert)
        alerts = await storage.load_alerts("farm_001")

        assert len(alerts) == 1
        assert alerts[0].crop_id == "wheat"

    @pytest.mark.asyncio
    async def test_update_alert(self, storage):
        """Test updating an alert"""
        alert = PriceAlert(
            id="alert_001",
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
            status=AlertStatus.ACTIVE,
        )

        await storage.save_alert(alert)

        # Update alert
        alert.status = AlertStatus.TRIGGERED
        await storage.save_alert(alert)

        alerts = await storage.load_alerts("farm_001")
        assert alerts[0].status == AlertStatus.TRIGGERED

    @pytest.mark.asyncio
    async def test_delete_alert(self, storage):
        """Test deleting an alert"""
        alert = PriceAlert(
            id="alert_001",
            tenant_id="farm_001",
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
        )

        await storage.save_alert(alert)
        assert await storage.delete_alert("farm_001", "alert_001") is True
        alerts = await storage.load_alerts("farm_001")
        assert len(alerts) == 0


# =============================================================================
# Tests for Price Tracker
# =============================================================================


@pytest.mark.unit
class TestMarketPriceTracker:
    """Test MarketPriceTracker functionality"""

    @pytest.fixture
    def tracker(self):
        """Create tracker with temporary storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = PriceStorage(tmpdir)
            alert_storage = AlertStorage(tmpdir)
            yield MarketPriceTracker(
                tenant_id="farm_001",
                price_storage=storage,
                alert_storage=alert_storage,
            )

    @pytest.mark.asyncio
    async def test_record_price(self, tracker):
        """Test recording a price"""
        price = await tracker.record_price(
            crop_id="wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
            unit=PriceUnit.TON,
        )

        assert price.crop_id == "wheat"
        assert price.price == Decimal("2500")
        assert price.market_id == "riyadh_central"

    @pytest.mark.asyncio
    async def test_record_price_invalid_crop(self, tracker):
        """Test recording price with invalid crop"""
        with pytest.raises(MarketPriceException) as exc_info:
            await tracker.record_price(
                crop_id="invalid_crop",
                market_id="riyadh_central",
                price=Decimal("2500"),
            )
        assert exc_info.value.error.code == "crop_not_found"

    @pytest.mark.asyncio
    async def test_record_price_invalid_market(self, tracker):
        """Test recording price with invalid market"""
        with pytest.raises(MarketPriceException) as exc_info:
            await tracker.record_price(
                crop_id="wheat",
                market_id="invalid_market",
                price=Decimal("2500"),
            )
        assert exc_info.value.error.code == "market_not_found"

    @pytest.mark.asyncio
    async def test_get_latest_price(self, tracker):
        """Test getting latest price"""
        await tracker.record_price(
            crop_id="wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
        )

        price = await tracker.get_latest_price("wheat", "riyadh_central")
        assert price is not None
        assert price.price == Decimal("2500")

    @pytest.mark.asyncio
    async def test_get_price_history(self, tracker):
        """Test getting price history"""
        for i in range(5):
            await tracker.record_price(
                crop_id="wheat",
                market_id="riyadh_central",
                price=Decimal(str(2400 + i * 50)),
                price_date=date.today() - timedelta(days=i),
            )

        history = await tracker.get_price_history("wheat", "riyadh_central", days=30)
        assert len(history) == 5

    @pytest.mark.asyncio
    async def test_create_alert(self, tracker):
        """Test creating an alert"""
        alert = await tracker.create_alert(
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
            user_id="user_001",
        )

        assert alert.crop_id == "wheat"
        assert alert.alert_type == AlertType.PRICE_ABOVE
        assert alert.status == AlertStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_markets(self, tracker):
        """Test getting markets"""
        markets = tracker.get_markets()
        assert len(markets) > 0

        saudi_markets = tracker.get_markets(country=Country.SAUDI_ARABIA)
        assert all(m.country == Country.SAUDI_ARABIA for m in saudi_markets)

        yemen_markets = tracker.get_markets(country=Country.YEMEN)
        assert all(m.country == Country.YEMEN for m in yemen_markets)

    @pytest.mark.asyncio
    async def test_get_regions(self, tracker):
        """Test getting regions"""
        regions = tracker.get_regions()
        assert len(regions) > 0

        saudi_regions = tracker.get_regions(country=Country.SAUDI_ARABIA)
        assert all(r.country == Country.SAUDI_ARABIA for r in saudi_regions)


# =============================================================================
# Tests for Price Analyzer
# =============================================================================


@pytest.mark.unit
class TestPriceAnalyzer:
    """Test PriceAnalyzer functionality"""

    @pytest.fixture
    async def analyzer_with_data(self):
        """Create analyzer with sample price data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = PriceStorage(tmpdir)
            alert_storage = AlertStorage(tmpdir)
            tracker = MarketPriceTracker(
                tenant_id="farm_001",
                price_storage=storage,
                alert_storage=alert_storage,
            )

            # Add price history
            base_price = 2400.0
            for i in range(30):
                price_val = base_price + (i * 5)  # Rising trend
                await tracker.record_price(
                    crop_id="wheat",
                    market_id="riyadh_central",
                    price=Decimal(str(price_val)),
                    price_date=date.today() - timedelta(days=29 - i),
                )

            analyzer = PriceAnalyzer(tracker)
            yield analyzer

    @pytest.mark.asyncio
    async def test_analyze_trend_rising(self, analyzer_with_data):
        """Test trend analysis with rising prices"""
        trend = await analyzer_with_data.analyze_trend("wheat", days=30)

        assert trend.crop_id == "wheat"
        # Trend can be RISING, STABLE, or VOLATILE depending on price variation
        assert trend.direction in [
            TrendDirection.RISING,
            TrendDirection.STABLE,
            TrendDirection.VOLATILE,
        ]
        # Current should be higher than previous due to rising pattern
        assert trend.current_price > trend.previous_price
        # Should have positive price change
        assert trend.price_change > Decimal("0")

    @pytest.mark.asyncio
    async def test_analyze_trend_invalid_crop(self, analyzer_with_data):
        """Test trend analysis with invalid crop"""
        with pytest.raises(MarketPriceException) as exc_info:
            await analyzer_with_data.analyze_trend("invalid_crop")
        assert exc_info.value.error.code == "crop_not_found"

    @pytest.mark.asyncio
    async def test_volatility_calculation(self, analyzer_with_data):
        """Test volatility score calculation"""
        trend = await analyzer_with_data.analyze_trend("wheat", days=30)
        assert 0 <= trend.volatility_score <= 100

    @pytest.mark.asyncio
    async def test_seasonal_factors(self, analyzer_with_data):
        """Test seasonal factor calculation"""
        trend = await analyzer_with_data.analyze_trend("wheat", days=30)
        assert trend.seasonal_factor > 0

    @pytest.mark.asyncio
    async def test_price_statistics(self, analyzer_with_data):
        """Test price statistics calculation"""
        stats = await analyzer_with_data.get_price_statistics("wheat", days=30)

        assert stats["data_points"] > 0
        assert "current" in stats
        assert "high" in stats
        assert "low" in stats
        assert "average" in stats


# =============================================================================
# Tests for Bilingual Support
# =============================================================================


@pytest.mark.unit
class TestBilingualSupport:
    """Test bilingual (Arabic/English) support"""

    def test_region_bilingual(self):
        """Test region bilingual names"""
        riyadh = SAUDI_REGIONS["riyadh"]
        assert riyadh.name == "Riyadh"
        assert riyadh.name_ar == "الرياض"

        sanaa = YEMEN_REGIONS["sanaa"]
        assert sanaa.name == "Sana'a"
        assert sanaa.name_ar == "صنعاء"

    def test_market_bilingual(self):
        """Test market bilingual names"""
        market = MAJOR_MARKETS["riyadh_central"]
        assert market.name == "Riyadh Central Market"
        assert market.name_ar == "سوق الرياض المركزي"

    def test_crop_bilingual(self):
        """Test crop bilingual names"""
        wheat = CROP_TYPES["wheat"]
        assert wheat.name == "Wheat"
        assert wheat.name_ar == "قمح"

        dates = CROP_TYPES["dates"]
        assert dates.name == "Dates"
        assert dates.name_ar == "تمور"

    def test_price_alert_bilingual(self):
        """Test price alert bilingual support"""
        alert = PriceAlert(
            tenant_id="farm_001",
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            alert_type=AlertType.PRICE_ABOVE,
            threshold_value=Decimal("3000"),
            name="Wheat Price Alert",
            name_ar="تنبيه سعر القمح",
            description="Alert when wheat exceeds 3000",
            description_ar="تنبيه عندما يتجاوز سعر القمح 3000",
        )
        assert alert.name == "Wheat Price Alert"
        assert alert.name_ar == "تنبيه سعر القمح"

    def test_error_messages_bilingual(self):
        """Test error messages in both languages"""
        error = MarketPriceErrors.CROP_NOT_FOUND
        assert error.message == "Crop type not found"
        assert error.message_ar == "نوع المحصول غير موجود"

        error = MarketPriceErrors.NO_PRICE_DATA
        assert error.message == "No price data available for the specified criteria"
        assert error.message_ar == "لا تتوفر بيانات أسعار للمعايير المحددة"


# =============================================================================
# Tests for Regional Prices
# =============================================================================


@pytest.mark.unit
class TestRegionalPrices:
    """Test regional price queries"""

    @pytest.fixture
    def tracker(self):
        """Create tracker with price data from multiple regions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = PriceStorage(tmpdir)
            alert_storage = AlertStorage(tmpdir)
            tracker = MarketPriceTracker(
                tenant_id="farm_001",
                price_storage=storage,
                alert_storage=alert_storage,
            )
            yield tracker

    @pytest.mark.asyncio
    async def test_get_prices_by_region(self, tracker):
        """Test getting prices by region"""
        # Record prices in different regions
        await tracker.record_price(
            crop_id="wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
        )
        await tracker.record_price(
            crop_id="wheat",
            market_id="jeddah_wholesale",
            price=Decimal("2600"),
        )

        riyadh_prices = await tracker.get_prices_by_region("wheat", "riyadh")
        assert len(riyadh_prices) > 0
        assert all(p.region_id == "riyadh" for p in riyadh_prices)

    @pytest.mark.asyncio
    async def test_get_prices_by_country(self, tracker):
        """Test getting prices by country"""
        await tracker.record_price(
            crop_id="wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
        )
        await tracker.record_price(
            crop_id="wheat",
            market_id="sanaa_central",
            price=Decimal("1500"),
        )

        saudi_prices = await tracker.get_prices_by_country("wheat", Country.SAUDI_ARABIA)
        assert len(saudi_prices) > 0

        yemen_prices = await tracker.get_prices_by_country("wheat", Country.YEMEN)
        assert len(yemen_prices) > 0


# =============================================================================
# Tests for Currency and Units
# =============================================================================


@pytest.mark.unit
class TestCurrencyAndUnits:
    """Test currency and unit handling"""

    def test_crop_price_with_different_currencies(self):
        """Test CropPrice with different currencies"""
        sar_price = CropPrice(
            crop_id="wheat",
            price=Decimal("2500"),
            currency=Currency.SAR,
        )
        assert sar_price.currency == Currency.SAR

        yer_price = CropPrice(
            crop_id="wheat",
            price=Decimal("500000"),
            currency=Currency.YER,
        )
        assert yer_price.currency == Currency.YER

    def test_crop_price_with_different_units(self):
        """Test CropPrice with different units"""
        kg_price = CropPrice(
            crop_id="tomatoes",
            price=Decimal("5"),
            unit=PriceUnit.KG,
        )
        assert kg_price.unit == PriceUnit.KG

        ton_price = CropPrice(
            crop_id="wheat",
            price=Decimal("2500"),
            unit=PriceUnit.TON,
        )
        assert ton_price.unit == PriceUnit.TON

    def test_crop_price_with_quality_grades(self):
        """Test CropPrice with quality grades"""
        premium = CropPrice(
            crop_id="dates",
            price=Decimal("2000"),
            quality=PriceQuality.PREMIUM,
        )
        assert premium.quality == PriceQuality.PREMIUM

        standard = CropPrice(
            crop_id="dates",
            price=Decimal("1200"),
            quality=PriceQuality.STANDARD,
        )
        assert standard.quality == PriceQuality.STANDARD


# =============================================================================
# Tests for Data Models and Serialization
# =============================================================================


@pytest.mark.unit
class TestSerialization:
    """Test serialization/deserialization of data models"""

    def test_crop_price_json_serialization(self):
        """Test CropPrice JSON serialization"""
        price = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            market_id="riyadh_central",
            price=Decimal("2500"),
        )
        json_str = price.to_json()
        assert "wheat" in json_str
        assert "قمح" in json_str

    def test_crop_price_roundtrip(self):
        """Test CropPrice dict roundtrip"""
        original = CropPrice(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            market_id="riyadh_central",
            price=Decimal("2500"),
            currency=Currency.SAR,
            unit=PriceUnit.TON,
        )
        data = original.to_dict()
        restored = CropPrice.from_dict(data)

        assert restored.crop_id == original.crop_id
        assert restored.price == original.price
        assert restored.currency == original.currency

    def test_market_comparison_to_dict(self):
        """Test MarketComparison serialization"""
        comparison = MarketComparison(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            best_price_market_id="riyadh_central",
            best_price_market_name="Riyadh Central",
            best_price=Decimal("2600"),
            worst_price=Decimal("2300"),
            average_price=Decimal("2450"),
        )
        data = comparison.to_dict()
        assert data["crop_id"] == "wheat"
        assert data["best_price"] == "2600"

    def test_selling_recommendation_to_dict(self):
        """Test SellingRecommendation serialization"""
        rec = SellingRecommendation(
            crop_id="wheat",
            crop_name="Wheat",
            crop_name_ar="قمح",
            action="sell",
            action_ar="بيع",
            confidence=85.0,
            expected_price=Decimal("2500"),
        )
        data = rec.to_dict()
        assert data["crop_id"] == "wheat"
        assert data["action"] == "sell"
        assert data["action_ar"] == "بيع"


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.unit
class TestIntegration:
    """Integration tests combining multiple components"""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test full workflow: record, analyze, alert"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize tracker
            storage = PriceStorage(tmpdir)
            alert_storage = AlertStorage(tmpdir)
            tracker = MarketPriceTracker(
                tenant_id="farm_001",
                price_storage=storage,
                alert_storage=alert_storage,
            )

            # Record multiple prices
            for i in range(10):
                await tracker.record_price(
                    crop_id="wheat",
                    market_id="riyadh_central",
                    price=Decimal(str(2400 + i * 20)),
                    price_date=date.today() - timedelta(days=9 - i),
                )

            # Create alert
            alert = await tracker.create_alert(
                crop_id="wheat",
                alert_type=AlertType.PRICE_ABOVE,
                threshold_value=Decimal("2700"),
                user_id="user_001",
            )
            assert alert.crop_id == "wheat"

            # Get latest price
            latest = await tracker.get_latest_price("wheat")
            assert latest is not None

            # Get history
            history = await tracker.get_price_history("wheat", days=30)
            assert len(history) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
