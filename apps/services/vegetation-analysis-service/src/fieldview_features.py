"""
🔬 SAHOOL FieldView-Inspired Features (Reverse-Engineered)
ميزات مستوحاة من FieldView — هندسة عكسية

5 features reverse-engineered from Climate FieldView:
1. Field Comparison — مقارنة الحقول جنباً لجنب
2. Performance Benchmark — قياس الأداء مقابل المنطقة
3. True Color Imagery — صور RGB حقيقية
4. Seed Advisor — مستشار الأصناف
5. A/B Split Test — اختبار تقسيم الحقل

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from enum import StrEnum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Field Comparison — مقارنة الحقول جنباً لجنب
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class FieldSnapshot:
    """Snapshot of a field's state at a point in time."""

    field_id: str
    field_name: str
    field_name_ar: str
    date: date
    ndvi: float
    evi: float | None = None
    savi: float | None = None
    lai: float | None = None
    soil_moisture_pct: float | None = None
    crop_type: str = ""
    area_hectares: float = 0.0
    health_status: str = ""
    irrigation_type: str = ""


@dataclass
class ComparisonMetric:
    """Single metric comparison between two fields."""

    metric_name: str
    metric_name_ar: str
    unit: str
    field_a_value: float | None
    field_b_value: float | None
    difference: float | None = None
    difference_pct: float | None = None
    winner: str = ""  # "a", "b", or "tie"
    significance: str = "low"  # low, medium, high


@dataclass
class FieldComparisonResult:
    """Complete comparison between two fields."""

    field_a: FieldSnapshot
    field_b: FieldSnapshot
    metrics: list[ComparisonMetric] = field(default_factory=list)
    overall_winner: str = ""
    summary_ar: str = ""
    summary_en: str = ""


class FieldComparator:
    """
    Compare two fields side-by-side across multiple dimensions.
    مقارنة حقلين جنباً لجنب عبر أبعاد متعددة

    FieldView equivalent: Field Region Reports + Side-by-Side comparison
    """

    def compare(self, field_a: FieldSnapshot, field_b: FieldSnapshot) -> FieldComparisonResult:
        metrics = []

        # NDVI comparison
        metrics.append(
            self._compare_metric(
                "NDVI",
                "مؤشر الغطاء النباتي",
                "",
                field_a.ndvi,
                field_b.ndvi,
                higher_is_better=True,
            )
        )

        # EVI
        if field_a.evi is not None and field_b.evi is not None:
            metrics.append(
                self._compare_metric(
                    "EVI",
                    "مؤشر الغطاء المحسّن",
                    "",
                    field_a.evi,
                    field_b.evi,
                    higher_is_better=True,
                )
            )

        # LAI
        if field_a.lai is not None and field_b.lai is not None:
            metrics.append(
                self._compare_metric(
                    "LAI",
                    "مؤشر مساحة الورقة",
                    "m²/m²",
                    field_a.lai,
                    field_b.lai,
                    higher_is_better=True,
                )
            )

        # Soil moisture
        if field_a.soil_moisture_pct is not None and field_b.soil_moisture_pct is not None:
            metrics.append(
                self._compare_metric(
                    "Soil Moisture",
                    "رطوبة التربة",
                    "%",
                    field_a.soil_moisture_pct,
                    field_b.soil_moisture_pct,
                    higher_is_better=True,
                )
            )

        # Area
        metrics.append(
            self._compare_metric(
                "Area",
                "المساحة",
                "ha",
                field_a.area_hectares,
                field_b.area_hectares,
                higher_is_better=None,  # Neutral
            )
        )

        # Determine overall winner
        a_wins = sum(1 for m in metrics if m.winner == "a")
        b_wins = sum(1 for m in metrics if m.winner == "b")
        overall = "a" if a_wins > b_wins else "b" if b_wins > a_wins else "tie"

        winner_name = field_a.field_name_ar if overall == "a" else field_b.field_name_ar if overall == "b" else "تعادل"

        return FieldComparisonResult(
            field_a=field_a,
            field_b=field_b,
            metrics=metrics,
            overall_winner=overall,
            summary_ar=f"الأفضل أداءً: {winner_name} ({a_wins} مقابل {b_wins} مؤشرات)",
            summary_en=f"Better performer: {field_a.field_name if overall == 'a' else field_b.field_name} ({a_wins} vs {b_wins} metrics)",
        )

    def _compare_metric(
        self,
        name: str,
        name_ar: str,
        unit: str,
        val_a: float | None,
        val_b: float | None,
        higher_is_better: bool | None = True,
    ) -> ComparisonMetric:
        if val_a is None or val_b is None:
            return ComparisonMetric(name, name_ar, unit, val_a, val_b)

        diff = val_a - val_b
        diff_pct = (diff / val_b * 100) if val_b != 0 else 0

        if higher_is_better is None:
            winner = "tie"
        elif higher_is_better:
            winner = "a" if diff > 0.01 else "b" if diff < -0.01 else "tie"
        else:
            winner = "b" if diff > 0.01 else "a" if diff < -0.01 else "tie"

        sig = "high" if abs(diff_pct) > 15 else "medium" if abs(diff_pct) > 5 else "low"

        return ComparisonMetric(
            metric_name=name,
            metric_name_ar=name_ar,
            unit=unit,
            field_a_value=round(val_a, 4),
            field_b_value=round(val_b, 4),
            difference=round(diff, 4),
            difference_pct=round(diff_pct, 1),
            winner=winner,
            significance=sig,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Performance Benchmark — قياس الأداء مقابل المنطقة
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class BenchmarkResult:
    """Field performance relative to regional average."""

    field_id: str
    field_name_ar: str
    metric: str
    metric_ar: str
    field_value: float
    regional_avg: float
    regional_min: float
    regional_max: float
    percentile: float  # 0-100
    deviation_pct: float
    rating: str  # "excellent", "above_average", "average", "below_average", "poor"
    rating_ar: str


class PerformanceBenchmark:
    """
    Compare a field's performance against regional averages.
    قياس أداء الحقل مقابل متوسط المنطقة

    FieldView equivalent: Performance Benchmark + Regional Analysis
    """

    RATINGS = {
        "excellent": {"ar": "ممتاز", "min_percentile": 80},
        "above_average": {"ar": "فوق المتوسط", "min_percentile": 60},
        "average": {"ar": "متوسط", "min_percentile": 40},
        "below_average": {"ar": "تحت المتوسط", "min_percentile": 20},
        "poor": {"ar": "ضعيف", "min_percentile": 0},
    }

    def benchmark(
        self,
        field_value: float,
        regional_values: list[float],
        metric: str = "NDVI",
        metric_ar: str = "مؤشر الغطاء النباتي",
        field_id: str = "",
        field_name_ar: str = "",
    ) -> BenchmarkResult:
        if not regional_values:
            regional_values = [field_value]

        sorted_vals = sorted(regional_values)
        avg = sum(sorted_vals) / len(sorted_vals)
        rank = sum(1 for v in sorted_vals if v <= field_value)
        percentile = (rank / len(sorted_vals)) * 100
        deviation = ((field_value - avg) / avg * 100) if avg != 0 else 0

        # Determine rating
        rating = "poor"
        rating_ar = "ضعيف"
        for r, info in self.RATINGS.items():
            if percentile >= info["min_percentile"]:
                rating = r
                rating_ar = info["ar"]
                break

        return BenchmarkResult(
            field_id=field_id,
            field_name_ar=field_name_ar,
            metric=metric,
            metric_ar=metric_ar,
            field_value=round(field_value, 4),
            regional_avg=round(avg, 4),
            regional_min=round(sorted_vals[0], 4),
            regional_max=round(sorted_vals[-1], 4),
            percentile=round(percentile, 1),
            deviation_pct=round(deviation, 1),
            rating=rating,
            rating_ar=rating_ar,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. True Color Imagery — صور RGB حقيقية
# ═══════════════════════════════════════════════════════════════════════════════


class ImageryType(StrEnum):
    """FieldView-inspired imagery types."""

    VEGETATION = "vegetation"  # NDVI false color (existing)
    TRUE_COLOR = "true_color"  # RGB natural color (B04, B03, B02)
    FALSE_COLOR_IR = "false_color_ir"  # NIR false color (B08, B04, B03)
    AGRICULTURE = "agriculture"  # SWIR composite (B11, B08, B02)
    MOISTURE = "moisture"  # Moisture emphasis (B8A, B11, B04)
    SCOUTING = "scouting"  # NDVI + field boundaries + markers overlay


# Sentinel-2 evalscripts for each imagery type
EVALSCRIPTS = {
    ImageryType.TRUE_COLOR: """
//VERSION=3
function setup() { return { input: ["B04","B03","B02"], output: { bands: 3 } }; }
function evaluatePixel(s) { return [2.5*s.B04, 2.5*s.B03, 2.5*s.B02]; }
""",
    ImageryType.FALSE_COLOR_IR: """
//VERSION=3
function setup() { return { input: ["B08","B04","B03"], output: { bands: 3 } }; }
function evaluatePixel(s) { return [2.5*s.B08, 2.5*s.B04, 2.5*s.B03]; }
""",
    ImageryType.AGRICULTURE: """
//VERSION=3
function setup() { return { input: ["B11","B08","B02"], output: { bands: 3 } }; }
function evaluatePixel(s) { return [2.5*s.B11, 2.5*s.B08, 2.5*s.B02]; }
""",
    ImageryType.MOISTURE: """
//VERSION=3
function setup() { return { input: ["B8A","B11","B04"], output: { bands: 3 } }; }
function evaluatePixel(s) { return [2.5*s.B8A, 2.5*s.B11, 2.5*s.B04]; }
""",
    ImageryType.VEGETATION: """
//VERSION=3
function setup() { return { input: ["B08","B04"], output: { bands: 3 } }; }
function evaluatePixel(s) {
  var ndvi = (s.B08-s.B04)/(s.B08+s.B04);
  if (ndvi < 0.2) return [0.8, 0.2, 0.2];
  if (ndvi < 0.4) return [0.9, 0.6, 0.2];
  if (ndvi < 0.6) return [0.9, 0.9, 0.3];
  return [0.1, 0.5+ndvi*0.5, 0.1];
}
""",
}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Seed Advisor — مستشار الأصناف
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class VarietyRecommendation:
    """Single variety recommendation."""

    variety_name: str
    variety_name_ar: str
    crop_type: str
    match_score: float  # 0-100
    expected_yield_tons_ha: float
    drought_tolerance: str  # low, medium, high
    disease_resistance: list[str]
    optimal_planting_date: str
    seed_rate_kg_ha: float
    rationale_ar: str
    rationale_en: str


@dataclass
class SeedAdvisorResult:
    """Complete seed advisory for a field."""

    field_id: str
    crop_type: str
    recommendations: list[VarietyRecommendation]
    soil_suitability: str
    climate_zone: str
    timestamp: str


# Yemen crop variety database
YEMEN_VARIETIES = {
    "wheat": [
        {
            "name": "Sakha 95",
            "name_ar": "سخا 95",
            "yield": 4.5,
            "drought": "medium",
            "diseases": ["rust", "blight"],
            "seed_rate": 120,
            "planting": "Nov-Dec",
            "soil": ["loamy", "clay"],
            "temp_range": [10, 30],
            "water_need": 450,
        },
        {
            "name": "Giza 171",
            "name_ar": "جيزة 171",
            "yield": 5.0,
            "drought": "low",
            "diseases": ["rust", "fusarium"],
            "seed_rate": 130,
            "planting": "Nov",
            "soil": ["loamy", "silt"],
            "temp_range": [12, 28],
            "water_need": 500,
        },
        {
            "name": "Misr 3",
            "name_ar": "مصر 3",
            "yield": 4.2,
            "drought": "high",
            "diseases": ["rust"],
            "seed_rate": 110,
            "planting": "Nov-Jan",
            "soil": ["sandy-loam", "loamy"],
            "temp_range": [8, 35],
            "water_need": 380,
        },
    ],
    "barley": [
        {
            "name": "Giza 136",
            "name_ar": "جيزة 136",
            "yield": 3.8,
            "drought": "high",
            "diseases": ["powdery_mildew"],
            "seed_rate": 100,
            "planting": "Oct-Nov",
            "soil": ["sandy", "loamy"],
            "temp_range": [5, 32],
            "water_need": 300,
        },
    ],
    "sorghum": [
        {
            "name": "Local Red",
            "name_ar": "أحمر محلي",
            "yield": 2.5,
            "drought": "high",
            "diseases": [],
            "seed_rate": 8,
            "planting": "Jun-Jul",
            "soil": ["clay", "loamy"],
            "temp_range": [20, 45],
            "water_need": 350,
        },
    ],
    "date_palm": [
        {
            "name": "Sukkari",
            "name_ar": "سكري",
            "yield": 8.0,
            "drought": "high",
            "diseases": ["rpw"],
            "seed_rate": 0,
            "planting": "Mar-Apr",
            "soil": ["sandy", "sandy-loam"],
            "temp_range": [15, 50],
            "water_need": 600,
        },
        {
            "name": "Khalas",
            "name_ar": "خلاص",
            "yield": 7.0,
            "drought": "high",
            "diseases": ["rpw", "bayoud"],
            "seed_rate": 0,
            "planting": "Mar-Apr",
            "soil": ["sandy", "loamy"],
            "temp_range": [18, 48],
            "water_need": 550,
        },
    ],
}


class SeedAdvisor:
    """
    Recommend optimal crop varieties based on field conditions.
    توصية الأصناف المثلى بناءً على ظروف الحقل

    FieldView equivalent: Seed Advisor (predictive seed placement)
    Uses: soil type, climate zone, water availability, disease history
    """

    def recommend(
        self,
        crop_type: str,
        soil_type: str = "loamy",
        climate_zone: str = "highlands",
        water_available_mm: float = 400,
        temperature_avg: float = 25,
        disease_history: list[str] | None = None,
        field_id: str = "",
    ) -> SeedAdvisorResult:
        varieties = YEMEN_VARIETIES.get(crop_type, [])
        if not varieties:
            return SeedAdvisorResult(
                field_id=field_id,
                crop_type=crop_type,
                recommendations=[],
                soil_suitability="unknown",
                climate_zone=climate_zone,
                timestamp=datetime.now(UTC).isoformat(),
            )

        scored = []
        for v in varieties:
            score = self._score_variety(v, soil_type, water_available_mm, temperature_avg, disease_history or [])
            scored.append((v, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        recommendations = []
        for v, score in scored:
            rationale_parts_ar = []
            rationale_parts_en = []

            if soil_type in v.get("soil", []):
                rationale_parts_ar.append(f"التربة مناسبة ({soil_type})")
                rationale_parts_en.append(f"Soil compatible ({soil_type})")

            if water_available_mm >= v.get("water_need", 0) * 0.8:
                rationale_parts_ar.append("المياه كافية")
                rationale_parts_en.append("Water sufficient")
            else:
                rationale_parts_ar.append("⚠️ قد يحتاج ري إضافي")
                rationale_parts_en.append("May need supplemental irrigation")

            if v.get("drought") == "high":
                rationale_parts_ar.append("مقاوم للجفاف")
                rationale_parts_en.append("Drought tolerant")

            recommendations.append(
                VarietyRecommendation(
                    variety_name=v["name"],
                    variety_name_ar=v["name_ar"],
                    crop_type=crop_type,
                    match_score=round(score, 1),
                    expected_yield_tons_ha=v["yield"],
                    drought_tolerance=v.get("drought", "medium"),
                    disease_resistance=v.get("diseases", []),
                    optimal_planting_date=v.get("planting", ""),
                    seed_rate_kg_ha=v.get("seed_rate", 0),
                    rationale_ar=" • ".join(rationale_parts_ar),
                    rationale_en=" • ".join(rationale_parts_en),
                )
            )

        return SeedAdvisorResult(
            field_id=field_id,
            crop_type=crop_type,
            recommendations=recommendations,
            soil_suitability="good" if any(soil_type in v.get("soil", []) for v in varieties) else "marginal",
            climate_zone=climate_zone,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def _score_variety(
        self,
        v: dict,
        soil: str,
        water: float,
        temp: float,
        diseases: list[str],
    ) -> float:
        score = 50.0  # Base

        # Soil match (+20)
        if soil in v.get("soil", []):
            score += 20
        else:
            score -= 10

        # Water match (+15)
        need = v.get("water_need", 400)
        if water >= need:
            score += 15
        elif water >= need * 0.7:
            score += 5
        else:
            score -= 15

        # Temperature match (+15)
        t_min, t_max = v.get("temp_range", [10, 35])
        if t_min <= temp <= t_max:
            score += 15
        else:
            score -= 20

        # Drought tolerance bonus for Yemen (+10)
        if v.get("drought") == "high":
            score += 10
        elif v.get("drought") == "medium":
            score += 5

        # Disease resistance bonus (+10)
        resists = set(v.get("diseases", []))
        history = set(diseases)
        if history and resists.intersection(history):
            score += 10

        # Yield potential (+10)
        score += min(10, v.get("yield", 0) * 2)

        return max(0, min(100, score))


# ═══════════════════════════════════════════════════════════════════════════════
# 5. A/B Split Test — اختبار تقسيم الحقل
# ═══════════════════════════════════════════════════════════════════════════════


class SplitMethod(StrEnum):
    HORIZONTAL = "horizontal"  # Split east-west
    VERTICAL = "vertical"  # Split north-south
    CHECKERBOARD = "checkerboard"  # Alternating grid
    CUSTOM = "custom"  # User-defined zones


@dataclass
class SplitZone:
    """One zone in an A/B split test."""

    zone_id: str
    zone_label: str  # "A" or "B"
    treatment: str
    treatment_ar: str
    bbox: tuple[float, float, float, float]  # minLng, minLat, maxLng, maxLat
    area_hectares: float
    ndvi_before: float | None = None
    ndvi_after: float | None = None
    yield_tons_ha: float | None = None


@dataclass
class ABTestResult:
    """Complete A/B split test result."""

    field_id: str
    test_name: str
    test_name_ar: str
    split_method: str
    zone_a: SplitZone
    zone_b: SplitZone
    start_date: date
    end_date: date | None = None
    ndvi_difference: float | None = None
    yield_difference: float | None = None
    winner: str = ""  # "a", "b", "inconclusive"
    confidence_pct: float = 0.0
    conclusion_ar: str = ""
    conclusion_en: str = ""


class ABSplitTest:
    """
    Split a field into A/B zones to compare different practices.
    تقسيم حقل إلى منطقتين لمقارنة ممارسات مختلفة

    FieldView equivalent: A/B Testing / Split-field comparison
    Examples:
    - Zone A: drip irrigation, Zone B: sprinkler → compare NDVI after 30 days
    - Zone A: Urea 46%, Zone B: DAP → compare yield at harvest
    """

    def create_split(
        self,
        field_id: str,
        field_bbox: tuple[float, float, float, float],
        treatment_a: str,
        treatment_a_ar: str,
        treatment_b: str,
        treatment_b_ar: str,
        split_method: SplitMethod = SplitMethod.HORIZONTAL,
        test_name: str = "A/B Test",
        test_name_ar: str = "اختبار أ/ب",
    ) -> ABTestResult:
        min_lng, min_lat, max_lng, max_lat = field_bbox
        mid_lat = (min_lat + max_lat) / 2
        mid_lng = (min_lng + max_lng) / 2

        if split_method == SplitMethod.HORIZONTAL:
            bbox_a = (min_lng, mid_lat, max_lng, max_lat)
            bbox_b = (min_lng, min_lat, max_lng, mid_lat)
        elif split_method == SplitMethod.VERTICAL:
            bbox_a = (min_lng, min_lat, mid_lng, max_lat)
            bbox_b = (mid_lng, min_lat, max_lng, max_lat)
        else:
            bbox_a = (min_lng, min_lat, mid_lng, mid_lat)
            bbox_b = (mid_lng, mid_lat, max_lng, max_lat)

        # Approximate area per zone
        width_km = abs(max_lng - min_lng) * 111.32 * math.cos(math.radians(mid_lat))
        height_km = abs(max_lat - min_lat) * 111.32
        total_ha = width_km * height_km * 100
        zone_ha = total_ha / 2

        zone_a = SplitZone(
            zone_id=f"{field_id}_A",
            zone_label="A",
            treatment=treatment_a,
            treatment_ar=treatment_a_ar,
            bbox=bbox_a,
            area_hectares=round(zone_ha, 2),
        )
        zone_b = SplitZone(
            zone_id=f"{field_id}_B",
            zone_label="B",
            treatment=treatment_b,
            treatment_ar=treatment_b_ar,
            bbox=bbox_b,
            area_hectares=round(zone_ha, 2),
        )

        return ABTestResult(
            field_id=field_id,
            test_name=test_name,
            test_name_ar=test_name_ar,
            split_method=split_method,
            zone_a=zone_a,
            zone_b=zone_b,
            start_date=date.today(),
        )

    def evaluate(self, test: ABTestResult) -> ABTestResult:
        """Evaluate A/B test results after observation period."""
        if test.zone_a.ndvi_after is not None and test.zone_b.ndvi_after is not None:
            diff = test.zone_a.ndvi_after - test.zone_b.ndvi_after
            test.ndvi_difference = round(diff, 4)

            # Statistical significance approximation
            # (simplified — real implementation would use t-test)
            if abs(diff) > 0.05:
                test.confidence_pct = min(95, abs(diff) * 500)
                test.winner = "a" if diff > 0 else "b"
                winner_treatment_ar = test.zone_a.treatment_ar if test.winner == "a" else test.zone_b.treatment_ar
                test.conclusion_ar = f"المعاملة الأفضل: {winner_treatment_ar} (فرق NDVI: {abs(diff):.3f}، ثقة: {test.confidence_pct:.0f}%)"
                test.conclusion_en = f"Better treatment: {test.zone_a.treatment if test.winner == 'a' else test.zone_b.treatment} (NDVI diff: {abs(diff):.3f}, confidence: {test.confidence_pct:.0f}%)"
            else:
                test.winner = "inconclusive"
                test.confidence_pct = abs(diff) * 500
                test.conclusion_ar = "النتائج غير حاسمة — الفرق صغير جداً"
                test.conclusion_en = "Inconclusive — difference too small"

        if test.zone_a.yield_tons_ha is not None and test.zone_b.yield_tons_ha is not None:
            test.yield_difference = round(test.zone_a.yield_tons_ha - test.zone_b.yield_tons_ha, 2)

        return test
