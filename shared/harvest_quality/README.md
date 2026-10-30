# Harvest Quality Module - وحدة جودة المحصول

Post-harvest quality grading, pricing, and trend analysis for the SAHOOL platform. Provides parameter-based grading against SASO-aligned standards for wheat, barley, dates, and vegetables, grade-based price calculation with premiums and penalties, buyer requirement matching, and longitudinal quality trend analysis.

**Version**: 1.0.0 | **Python**: 3.11+

## File Structure

```
shared/harvest_quality/
├── __init__.py    # Public API and re-exports
├── models.py      # QualityGrade, QualityStandard, QualityTestRecord, BuyerRequirement, pricing models
├── grading.py     # QualityGradingEngine, BuyerMatchingEngine, QualityTrendAnalyzer, built-in standards
└── pricing.py     # QualityPricingEngine, PricingConfig, built-in price matrices, adjustment rules
```

## Key Components

### Quality Grades (`QualityGrade`)
`PREMIUM`, `GRADE_1`, `GRADE_2`, `GRADE_3`, `REJECTED`

### Supported Crop Types

| Crop | Standard Getter | Key Parameters |
|------|----------------|----------------|
| Wheat | `get_wheat_standard()` | Moisture, protein, test weight, foreign matter, damaged kernels |
| Barley | `get_barley_standard()` | Moisture, protein, test weight, foreign matter |
| Date Palm | `get_date_standard()` | Moisture, sugar content, uniformity, defects, size |
| Vegetables | `get_vegetable_standard()` | Size, color, firmness, defects, shelf life |

### `QualityGradingEngine`
Scores each quality parameter against grade thresholds (0-100 scale) and returns the worst-failing grade as `overall_grade`. Also produces per-parameter `TestResult` (PASS, FAIL, BORDERLINE) and a weighted `grade_score`.

### `BuyerMatchingEngine`
Matches a grading result against a list of `BuyerRequirement` objects. Returns ranked `BuyerMatch` entries with `meets_requirements`, `price_premium_percent`, and `recommended_processing`.

### `QualityTrendAnalyzer`
Accepts a time-ordered list of `QualityTestRecord` objects and computes moving averages, grade distribution, and `TrendDirection` (IMPROVING, STABLE, DECLINING, VOLATILE) for each tracked parameter.

### `QualityPricingEngine`
Calculates final price from a `GradePriceMatrix` by applying grade base prices and parameter-specific adjustment rules (premiums for high protein, penalties for excess moisture, etc.). Returns a `PriceCalculation` with `base_price`, `adjustments`, and `final_price`.

## Usage Examples

### Grade a Wheat Sample

```python
from shared.harvest_quality import (
    QualityGradingEngine, QUALITY_STANDARDS,
    QualityGrade,
)

engine = QualityGradingEngine()
engine.set_standard(QUALITY_STANDARDS["wheat"])

result = engine.calculate_grade({
    "moisture":         12.5,   # % - target <= 12.5 for Grade 1
    "protein":          13.0,   # %
    "test_weight":      79.0,   # kg/hl
    "foreign_matter":    0.8,   # %
    "damaged_kernels":   1.5,   # %
})

print(f"Overall grade : {result.overall_grade.value}")   # e.g. "grade_1"
print(f"Score         : {result.grade_score:.1f}/100")
for param, test in result.parameter_results.items():
    print(f"  {param}: {test.result} (value={test.measured_value})")
```

### Calculate Grade-Based Price

```python
from shared.harvest_quality import (
    QualityPricingEngine, PRICE_MATRICES,
    calculate_quick_price, get_grade_price_breakdown,
    Currency,
)

pricing = QualityPricingEngine()
price_calc = pricing.calculate_price(
    grade=result.overall_grade,
    quantity=5000,          # kg
    test_values={"moisture": 12.5, "protein": 13.0},
    price_matrix=PRICE_MATRICES["wheat"],
)

print(f"Base price  : {price_calc.base_price} {price_calc.currency.value}")
print(f"Adjustments : {price_calc.total_adjustment}")
print(f"Final price : {price_calc.final_price} {price_calc.currency.value}")

# Quick estimate without building a full engine
quick = calculate_quick_price("wheat", result.overall_grade, quantity=5000)

# Per-grade breakdown for negotiation display
breakdown = get_grade_price_breakdown("wheat")
```

### Match Buyers to a Grade Result

```python
from shared.harvest_quality import BuyerMatchingEngine, BuyerRequirement, BuyerType

buyers = [
    BuyerRequirement(
        buyer_id="MILL-001",
        buyer_name="Al-Jazeera Flour Mill",
        buyer_type=BuyerType.PROCESSOR,
        minimum_grade=QualityGrade.GRADE_1,
        min_protein=12.5,
        max_moisture=13.0,
        price_premium_percent=8.0,
    ),
]

matcher = BuyerMatchingEngine()
matches = matcher.find_matches(result, buyers)
for m in matches:
    print(f"{m.buyer_name}: meets_requirements={m.meets_requirements}, "
          f"premium={m.price_premium_percent}%")
```

### Analyze Quality Trends

```python
from shared.harvest_quality import QualityTrendAnalyzer, QualityTestRecord

# Load historical records from DB
records: list[QualityTestRecord] = load_records_from_db(field_id="FIELD-003")

analyzer = QualityTrendAnalyzer()
trend = analyzer.analyze(records, window_size=5)

print(f"Direction  : {trend.trend_direction.value}")   # improving / stable / declining
print(f"Avg grade  : {trend.average_grade_score:.1f}/100")
for param, direction in trend.parameter_trends.items():
    print(f"  {param}: {direction.value}")
```

## Built-in Price Matrices

| Matrix | Getter |
|--------|--------|
| Wheat | `get_wheat_price_matrix()` / `PRICE_MATRICES["wheat"]` |
| Barley | `get_barley_price_matrix()` / `PRICE_MATRICES["barley"]` |
| Dates | `get_date_price_matrix()` / `PRICE_MATRICES["dates"]` |
| Vegetables | `get_vegetable_price_matrix()` / `PRICE_MATRICES["vegetables"]` |

## Integration Notes

- Standards are calibrated against SASO (Saudi Standards, Metrology and Quality Organization) thresholds.
- The `estimate_value_improvement()` helper calculates potential revenue gain from drying or cleaning to reach a higher grade.
- Connect quality records to the `traceability-service` (port 8123) to attach grade data to lot QR codes.
- Pricing currency defaults to SAR; set `Currency.USD` or `Currency.YER` in `PricingConfig` for cross-border transactions.
