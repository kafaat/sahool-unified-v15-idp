"""
Market Price Tracking Module
============================
وحدة تتبع أسعار السوق

A comprehensive module for tracking, analyzing, and managing agricultural
market prices across Saudi Arabia and Yemen.

Features:
- Crop price tracking by region and market
- Price trend analysis and predictions
- Threshold-based price alerts
- Best selling time recommendations
- Market price comparisons

Author: SAHOOL Platform Team
Updated: January 2026

Usage:
    from shared.market_prices import (
        MarketPriceTracker,
        PriceAnalyzer,
        CropPrice,
        PriceAlert,
        AlertType,
        Currency,
        PriceUnit,
    )

    # Initialize tracker
    tracker = MarketPriceTracker(tenant_id="farm_001")

    # Record a price
    price = await tracker.record_price(
        crop_id="wheat",
        market_id="riyadh_central",
        price=Decimal("2500"),
        unit=PriceUnit.TON,
    )

    # Create alert
    alert = await tracker.create_alert(
        crop_id="wheat",
        alert_type=AlertType.PRICE_ABOVE,
        threshold_value=Decimal("3000"),
    )

    # Analyze trends
    analyzer = PriceAnalyzer(tracker)
    trend = await analyzer.analyze_trend("wheat", days=30)

    # Get selling recommendation
    recommendation = await analyzer.get_selling_recommendation(
        crop_id="wheat",
        quantity=10.0,
    )

    # Compare markets
    comparison = await analyzer.compare_markets("wheat")
"""

# Models
from .models import (
    # Enums
    Currency,
    PriceUnit,
    PriceQuality,
    MarketType,
    AlertType,
    AlertStatus,
    TrendDirection,
    Season,
    Country,
    # Data classes
    Region,
    Market,
    CropType,
    CropPrice,
    PriceAlert,
    PriceTrend,
    MarketComparison,
    SellingRecommendation,
    # Predefined data
    SAUDI_REGIONS,
    YEMEN_REGIONS,
    ALL_REGIONS,
    MAJOR_MARKETS,
    CROP_TYPES,
    # Errors
    MarketPriceError,
    MarketPriceErrors,
    MarketPriceException,
)

# Tracker
from .tracker import (
    PriceStorage,
    AlertStorage,
    MarketPriceTracker,
    # Convenience functions
    get_price_tracker,
    record_price,
    get_latest_price,
    get_price_history,
    create_price_alert,
)

# Analyzer
from .analyzer import (
    PriceAnalyzer,
    # Convenience functions
    get_price_analyzer,
    analyze_price_trend,
    compare_crop_markets,
    get_selling_advice,
)

__all__ = [
    # Enums
    "Currency",
    "PriceUnit",
    "PriceQuality",
    "MarketType",
    "AlertType",
    "AlertStatus",
    "TrendDirection",
    "Season",
    "Country",
    # Data classes
    "Region",
    "Market",
    "CropType",
    "CropPrice",
    "PriceAlert",
    "PriceTrend",
    "MarketComparison",
    "SellingRecommendation",
    # Predefined data
    "SAUDI_REGIONS",
    "YEMEN_REGIONS",
    "ALL_REGIONS",
    "MAJOR_MARKETS",
    "CROP_TYPES",
    # Errors
    "MarketPriceError",
    "MarketPriceErrors",
    "MarketPriceException",
    # Tracker
    "PriceStorage",
    "AlertStorage",
    "MarketPriceTracker",
    "get_price_tracker",
    "record_price",
    "get_latest_price",
    "get_price_history",
    "create_price_alert",
    # Analyzer
    "PriceAnalyzer",
    "get_price_analyzer",
    "analyze_price_trend",
    "compare_crop_markets",
    "get_selling_advice",
]

__version__ = "16.0.0"
