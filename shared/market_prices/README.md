# shared/market_prices

Market price tracking and analysis for the SAHOOL platform. Monitors crop prices across
wholesale and retail markets in Saudi Arabia and Yemen, detects price trends and volatility,
fires configurable price alerts (SMS/push/email), and generates data-driven selling
recommendations for farmers.

## File Structure

```
shared/market_prices/
├── __init__.py    # Public API exports
├── models.py      # All data models, predefined regions, markets, crop types
├── tracker.py     # Price ingestion, storage, alert evaluation
└── analyzer.py    # Trend analysis, market comparison, selling recommendations
```

## Key Components

### models.py

Data models and pre-seeded reference data for Saudi Arabia and Yemen.

**Enumerations:**

| Enum | Values |
|------|--------|
| `Currency` | SAR (Saudi Riyal), YER (Yemeni Rial), USD |
| `PriceUnit` | KG, TON, QUINTAL, SACK, BOX, PIECE |
| `PriceQuality` | PREMIUM, GRADE_A, GRADE_B, GRADE_C, STANDARD, MIXED |
| `MarketType` | WHOLESALE, RETAIL, FARM_GATE, EXPORT, IMPORT, FUTURES |
| `AlertType` | PRICE_ABOVE, PRICE_BELOW, PRICE_CHANGE_PCT, PRICE_DROP, PRICE_SPIKE, BEST_SELLING_TIME, MARKET_OPPORTUNITY |
| `AlertStatus` | ACTIVE, TRIGGERED, EXPIRED, DISABLED, ACKNOWLEDGED |
| `TrendDirection` | RISING, FALLING, STABLE, VOLATILE, UNKNOWN |

**Core data classes:**

| Class | Purpose |
|-------|---------|
| `Region` | Geographic region with country, coordinates, timezone |
| `Market` | Agricultural market with type, location, operating hours, supported crops |
| `CropType` | Crop with category, default price unit, seasonal availability |
| `CropPrice` | Price record with market, quality grade, date, source, verification status |
| `PriceAlert` | Alert configuration with threshold, notification channels, trigger history |
| `PriceTrend` | Trend analysis result with direction, strength, statistics, prediction |
| `MarketComparison` | Cross-market comparison with best/worst price and recommendation |
| `SellingRecommendation` | Sell/hold/wait recommendation with expected revenue and risk factors |

**Pre-seeded reference data:**

| Constant | Contents |
|----------|---------|
| `SAUDI_REGIONS` | 10 regions: Riyadh, Jeddah, Dammam, Al-Ahsa, Qassim, Tabuk, Hail, Madinah, Jizan, Asir |
| `YEMEN_REGIONS` | 8 regions: Sana'a, Aden, Taiz, Hodeidah, Ibb, Hadramaut, Dhamar, Lahij |
| `ALL_REGIONS` | Combined dict of all 18 regions |
| `MAJOR_MARKETS` | 8 key markets: Riyadh Central, Jeddah Wholesale, Dammam Agricultural, Qassim Dates, Al-Ahsa Agricultural, Sana'a Central, Aden Port, Hodeidah Agricultural |
| `CROP_TYPES` | 15 crops: wheat, barley, dates, tomatoes, potatoes, onions, cucumbers, watermelon, grapes, coffee, alfalfa, corn, sorghum, mangoes, bananas |

`PriceAlert.check_trigger(current_price, previous_price)` evaluates configured alert
logic inline without external dependencies.

### tracker.py

Price ingestion and alert evaluation service.

| Class | Description |
|-------|-------------|
| `PriceStorage` | File-based price storage (JSON, partitioned by date) |
| `MarketPriceTracker` | Manages price records, alert registration, and notification dispatch |

**Key methods:**
- `record_price(crop_id, market_id, price, currency, unit, quality, ...)` - stores a new price
- `get_latest_price(crop_id, market_id)` - returns most recent `CropPrice`
- `get_price_history(crop_id, market_id, start_date, end_date)` - returns sorted list
- `register_alert(alert)` / `delete_alert(alert_id)` - manage price alerts
- `check_alerts(crop_id, current_price)` - evaluates all active alerts; fires notifications
- `get_recent_prices(crop_id, region_id, days)` - prices across all region markets

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `get_price_tracker(tenant_id)` | Returns tenant-scoped tracker singleton |
| `record_price(crop_id, market_id, price, ...)` | Quick price record ingestion |

### analyzer.py

Statistical analysis and recommendation engine.

| Class | Description |
|-------|-------------|
| `PriceAnalyzer` | Full analysis suite backed by a `MarketPriceTracker` |

**Key methods:**

| Method | Returns |
|--------|---------|
| `analyze_trend(crop_id, market_id, days)` | `PriceTrend` with direction, strength, statistics |
| `compare_markets(crop_id, region_ids, date)` | `MarketComparison` with ranked market list |
| `get_selling_recommendation(crop_id, farmer_id, quantity, ...)` | `SellingRecommendation` |
| `detect_market_opportunities(crop_id, region_id)` | List of opportunity signals |

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `get_price_analyzer(tenant_id)` | Returns analyzer paired with tenant tracker |
| `analyze_price_trend(crop_id, market_id, tenant_id, days)` | Quick trend call |
| `get_best_selling_opportunity(crop_id, tenant_id, ...)` | Quick recommendation call |

## Usage Example

```python
from datetime import date
from decimal import Decimal
from shared.market_prices import (
    get_price_tracker,
    get_price_analyzer,
    MAJOR_MARKETS,
    CROP_TYPES,
    PriceAlert,
    AlertType,
    PriceUnit,
    Currency,
)

tracker = get_price_tracker("tenant_001")

# Record a price observation
await tracker.record_price(
    crop_id="wheat",
    market_id="riyadh_central",
    price=Decimal("950"),
    currency=Currency.SAR,
    unit=PriceUnit.TON,
    source="market_report",
)

# Set a price alert (notify when wheat > 1100 SAR/ton)
alert = PriceAlert(
    tenant_id="tenant_001",
    farmer_id="farmer_001",
    crop_id="wheat",
    crop_name="Wheat",
    crop_name_ar="قمح",
    market_id="riyadh_central",
    alert_type=AlertType.PRICE_ABOVE,
    threshold_value=Decimal("1100"),
    threshold_unit=PriceUnit.TON,
    notify_sms=True,
    phone_number="+966501234567",
    name="Wheat High Price",
    name_ar="سعر القمح مرتفع",
)
await tracker.register_alert(alert)

# Trend analysis
analyzer = get_price_analyzer("tenant_001")
trend = await analyzer.analyze_trend("wheat", "riyadh_central", days=30)
print(f"Trend: {trend.direction}, Change: {trend.price_change_percent:.1f}%")

# Cross-market comparison
comparison = await analyzer.compare_markets(
    crop_id="dates",
    region_ids=["qassim", "al_ahsa", "riyadh"],
)
print(f"Best market: {comparison.best_price_market_name_ar}")
print(f"Potential gain vs average: {comparison.potential_gain_percent:.1f}%")

# Selling recommendation
rec = await analyzer.get_selling_recommendation(
    crop_id="wheat",
    farmer_id="farmer_001",
    quantity_tons=42.5,
)
print(f"Advice: {rec.action_ar}")  # "بيع" / "انتظر" / "احتفظ"
print(f"Expected revenue: {rec.estimated_revenue} SAR")
```

## Alert Types Reference

| Alert Type | Trigger Condition |
|------------|------------------|
| PRICE_ABOVE | Current price >= threshold value |
| PRICE_BELOW | Current price <= threshold value |
| PRICE_CHANGE_PCT | Absolute % change >= percentage_threshold in time_window_days |
| PRICE_DROP | Current price < previous price |
| PRICE_SPIKE | % increase >= percentage_threshold vs. previous price |
