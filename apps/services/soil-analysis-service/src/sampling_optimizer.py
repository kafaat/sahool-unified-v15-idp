"""
Soil Sampling Optimizer — محسّن نقاط أخذ عينات التربة
Calculates optimal soil sampling locations based on productivity zones,
reducing the number of samples while maintaining accuracy.

Inspired by OneSoil Pro's zone-based sampling algorithm.
"""

from __future__ import annotations

import math
import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

import structlog

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------
Coordinate: TypeAlias = tuple[float, float]  # (lat, lng)
Polygon: TypeAlias = list[Coordinate]  # closed ring of coordinates


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class ZoneType(str, Enum):
    """Productivity zone classification — تصنيف مناطق الإنتاجية"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def label_ar(self) -> str:
        return {
            ZoneType.HIGH: "إنتاجية عالية",
            ZoneType.MEDIUM: "إنتاجية متوسطة",
            ZoneType.LOW: "إنتاجية منخفضة",
        }[self]

    @property
    def label_en(self) -> str:
        return {
            ZoneType.HIGH: "High productivity",
            ZoneType.MEDIUM: "Medium productivity",
            ZoneType.LOW: "Low productivity",
        }[self]


class SamplingStrategy(str, Enum):
    """Sampling strategy — استراتيجية أخذ العينات"""

    ZONE_CENTROID = "zone_centroid"
    STRATIFIED_RANDOM = "stratified_random"
    GRID_BASED = "grid_based"
    HYBRID = "hybrid"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class SamplePoint:
    """A single soil sample location — نقطة أخذ عينة تربة واحدة"""

    lat: float
    lng: float
    zone_id: str
    zone_type: str  # high / medium / low
    priority: int  # 1=must (يجب), 2=recommended (موصى به), 3=optional (اختياري)

    @property
    def priority_label_ar(self) -> str:
        return {1: "يجب", 2: "موصى به", 3: "اختياري"}.get(self.priority, "غير محدد")

    @property
    def priority_label_en(self) -> str:
        return {1: "Must sample", 2: "Recommended", 3: "Optional"}.get(self.priority, "Unknown")

    def to_dict(self) -> dict:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "zone_id": self.zone_id,
            "zone_type": self.zone_type,
            "priority": self.priority,
            "priority_ar": self.priority_label_ar,
            "priority_en": self.priority_label_en,
        }


@dataclass
class NDVIZone:
    """An NDVI-derived productivity zone — منطقة إنتاجية مشتقة من مؤشر الغطاء النباتي"""

    zone_id: str
    zone_type: ZoneType
    boundary: Polygon  # list of (lat, lng) forming a closed polygon
    area_hectares: float
    mean_ndvi: float
    ndvi_std: float  # standard deviation – proxy for within-zone variability


@dataclass
class SamplingPlan:
    """Complete sampling plan for a field — خطة أخذ العينات الكاملة للحقل"""

    field_id: str
    total_samples: int
    points: list[SamplePoint]
    estimated_cost_sar: float
    coverage_pct: float
    accuracy_score: float
    plan_ar: str  # Arabic description

    # Metadata
    strategy: str = "hybrid"
    hectares_per_sample: float = 5.0

    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "total_samples": self.total_samples,
            "points": [p.to_dict() for p in self.points],
            "estimated_cost_sar": round(self.estimated_cost_sar, 2),
            "coverage_pct": round(self.coverage_pct, 2),
            "accuracy_score": round(self.accuracy_score, 4),
            "plan_ar": self.plan_ar,
            "strategy": self.strategy,
            "hectares_per_sample": self.hectares_per_sample,
        }


# ---------------------------------------------------------------------------
# Cost estimates (Yemen / Saudi market, SAR)
# ---------------------------------------------------------------------------
# Per-sample cost breakdown (approximate, SAR)
_COST_PER_SAMPLE_SAR = 250.0  # lab analysis fee — رسوم التحليل المخبري
_COST_TRAVEL_PER_SAMPLE_SAR = 35.0  # field travel overhead — تكلفة التنقل
_COST_EQUIPMENT_PER_SAMPLE_SAR = 15.0  # consumables (bags, auger) — المستهلكات
_TOTAL_COST_PER_SAMPLE_SAR = (
    _COST_PER_SAMPLE_SAR + _COST_TRAVEL_PER_SAMPLE_SAR + _COST_EQUIPMENT_PER_SAMPLE_SAR
)

# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def _polygon_area_hectares(polygon: Polygon) -> float:
    """
    Approximate polygon area in hectares using the Shoelace formula on
    lat/lng coordinates.  Applies a cos(lat) correction for longitude
    distortion.  Accurate enough for field-scale polygons (< 100 ha).
    """
    if len(polygon) < 3:
        return 0.0

    # Ensure the ring is closed
    ring = list(polygon)
    if ring[0] != ring[-1]:
        ring.append(ring[0])

    # Approximate meters per degree at the centroid latitude
    mean_lat = sum(p[0] for p in ring[:-1]) / (len(ring) - 1)
    lat_rad = math.radians(mean_lat)
    meters_per_deg_lat = 111_320.0
    meters_per_deg_lng = 111_320.0 * math.cos(lat_rad)

    # Shoelace in projected coordinates (meters)
    area_m2 = 0.0
    n = len(ring) - 1
    for i in range(n):
        x0 = ring[i][1] * meters_per_deg_lng
        y0 = ring[i][0] * meters_per_deg_lat
        x1 = ring[(i + 1) % n][1] * meters_per_deg_lng
        y1 = ring[(i + 1) % n][0] * meters_per_deg_lat
        area_m2 += x0 * y1 - x1 * y0

    area_m2 = abs(area_m2) / 2.0
    return area_m2 / 10_000.0  # m² → hectares


def _polygon_centroid(polygon: Polygon) -> Coordinate:
    """Return the centroid (average) of polygon vertices."""
    if not polygon:
        return (0.0, 0.0)
    ring = polygon if polygon[0] != polygon[-1] else polygon[:-1]
    n = len(ring)
    avg_lat = sum(p[0] for p in ring) / n
    avg_lng = sum(p[1] for p in ring) / n
    return (avg_lat, avg_lng)


def _point_in_polygon(point: Coordinate, polygon: Polygon) -> bool:
    """Ray-casting algorithm to check if a point lies inside a polygon."""
    lat, lng = point
    ring = list(polygon)
    if ring[0] != ring[-1]:
        ring.append(ring[0])

    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        yi, xi = ring[i]
        yj, xj = ring[j]
        if ((yi > lat) != (yj > lat)) and (lng < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _bounding_box(polygon: Polygon) -> tuple[float, float, float, float]:
    """Return (min_lat, min_lng, max_lat, max_lng)."""
    lats = [p[0] for p in polygon]
    lngs = [p[1] for p in polygon]
    return (min(lats), min(lngs), max(lats), max(lngs))


def _random_point_in_polygon(polygon: Polygon, max_attempts: int = 200) -> Coordinate | None:
    """Generate a uniformly random point inside a polygon via rejection sampling."""
    min_lat, min_lng, max_lat, max_lng = _bounding_box(polygon)
    for _ in range(max_attempts):
        lat = random.uniform(min_lat, max_lat)
        lng = random.uniform(min_lng, max_lng)
        if _point_in_polygon((lat, lng), polygon):
            return (lat, lng)
    # Fallback to centroid if rejection sampling fails (very narrow polygon)
    return _polygon_centroid(polygon)


# ---------------------------------------------------------------------------
# Main optimizer class
# ---------------------------------------------------------------------------
class SoilSamplingOptimizer:
    """
    Determines optimal soil sampling locations for a field based on
    NDVI-derived productivity zones.

    محسّن أخذ عينات التربة - يحدد المواقع المثلى لأخذ العينات
    بناءً على مناطق الإنتاجية المشتقة من مؤشر الغطاء النباتي

    Algorithm:
        1. Divide field into productivity zones (from NDVI)
        2. Allocate samples proportionally to zone area + variability
        3. Place samples at zone centroids + random stratified points
        4. Ensure minimum 1 sample per zone
        5. Default: 1 sample per 5 hectares (configurable)
    """

    # Default configuration
    DEFAULT_HECTARES_PER_SAMPLE = 5.0
    MIN_SAMPLES_PER_ZONE = 1
    MAX_SAMPLES_TOTAL = 200
    MIN_SAMPLES_TOTAL = 3

    # Variability weight: zones with higher NDVI std deviation get more samples
    VARIABILITY_WEIGHT = 0.4  # 40% variability, 60% area

    def __init__(
        self,
        hectares_per_sample: float = DEFAULT_HECTARES_PER_SAMPLE,
        cost_per_sample_sar: float = _TOTAL_COST_PER_SAMPLE_SAR,
        seed: int | None = None,
    ):
        """
        Initialize the optimizer.

        Args:
            hectares_per_sample: Target density (default 5 ha/sample — ١ عينة لكل ٥ هكتار)
            cost_per_sample_sar: Cost per sample in SAR (default ~300 SAR)
            seed: Random seed for reproducibility
        """
        self.hectares_per_sample = max(1.0, hectares_per_sample)
        self.cost_per_sample_sar = cost_per_sample_sar
        if seed is not None:
            random.seed(seed)

    def optimize(
        self,
        field_boundary: Polygon,
        ndvi_zones: list[NDVIZone],
        target_samples: int | None = None,
        strategy: SamplingStrategy = SamplingStrategy.HYBRID,
    ) -> SamplingPlan:
        """
        Generate an optimal sampling plan for a field.

        تحسين خطة أخذ العينات للحقل

        Args:
            field_boundary: List of (lat, lng) coordinates defining the field boundary
            ndvi_zones: Productivity zones derived from NDVI analysis
            target_samples: Override auto-calculated sample count (optional)
            strategy: Sampling strategy to use (default: hybrid)

        Returns:
            SamplingPlan with optimized sample locations
        """
        field_area_ha = _polygon_area_hectares(field_boundary)
        if field_area_ha <= 0:
            logger.warning("Field area is zero or negative, using zone areas")
            field_area_ha = sum(z.area_hectares for z in ndvi_zones) or 1.0

        # --- Step 1: Determine total sample count ---
        if target_samples is not None:
            total_samples = max(self.MIN_SAMPLES_TOTAL, min(target_samples, self.MAX_SAMPLES_TOTAL))
        else:
            total_samples = max(
                self.MIN_SAMPLES_TOTAL,
                min(
                    math.ceil(field_area_ha / self.hectares_per_sample),
                    self.MAX_SAMPLES_TOTAL,
                ),
            )

        logger.info(
            "sampling_optimization_start",
            field_area_ha=round(field_area_ha, 2),
            total_samples=total_samples,
            num_zones=len(ndvi_zones),
            strategy=strategy.value,
        )

        # --- Step 2: Generate sample points based on strategy ---
        if strategy == SamplingStrategy.ZONE_CENTROID:
            points = self._zone_centroid(ndvi_zones)
        elif strategy == SamplingStrategy.GRID_BASED:
            grid_size_m = math.sqrt((field_area_ha * 10_000) / total_samples)
            points = self._grid_based(field_boundary, grid_size_m)
        elif strategy == SamplingStrategy.STRATIFIED_RANDOM:
            allocation = self._allocate_samples(ndvi_zones, total_samples, field_area_ha)
            points = self._stratified_random(ndvi_zones, allocation)
        else:
            # Hybrid: centroids (priority 1) + stratified random fill (priority 2/3)
            points = self._hybrid(ndvi_zones, total_samples, field_area_ha)

        # Enforce bounds
        if len(points) > self.MAX_SAMPLES_TOTAL:
            points = sorted(points, key=lambda p: p.priority)[:self.MAX_SAMPLES_TOTAL]

        actual_samples = len(points)

        # --- Step 3: Compute plan metrics ---
        estimated_cost = actual_samples * self.cost_per_sample_sar

        # Coverage: fraction of total zone area represented by at least 1 sample
        zones_with_samples = {p.zone_id for p in points}
        covered_area = sum(z.area_hectares for z in ndvi_zones if z.zone_id in zones_with_samples)
        total_zone_area = sum(z.area_hectares for z in ndvi_zones) or 1.0
        coverage_pct = min(100.0, (covered_area / total_zone_area) * 100.0)

        # Accuracy score: based on sample density and zone coverage
        density_score = min(1.0, actual_samples / max(1, math.ceil(field_area_ha / self.hectares_per_sample)))
        zone_coverage_score = len(zones_with_samples) / max(1, len(ndvi_zones))
        # Penalise if any high-variability zone is missing
        variability_penalty = 0.0
        for z in ndvi_zones:
            if z.zone_id not in zones_with_samples and z.ndvi_std > 0.1:
                variability_penalty += 0.05
        accuracy_score = max(0.0, min(1.0, 0.5 * density_score + 0.5 * zone_coverage_score - variability_penalty))

        # --- Step 4: Arabic plan description ---
        plan_ar = self._generate_plan_ar(
            field_area_ha=field_area_ha,
            total_samples=actual_samples,
            num_zones=len(ndvi_zones),
            coverage_pct=coverage_pct,
            cost_sar=estimated_cost,
            strategy=strategy,
        )

        field_id = f"FIELD-{uuid.uuid4().hex[:8].upper()}"

        plan = SamplingPlan(
            field_id=field_id,
            total_samples=actual_samples,
            points=points,
            estimated_cost_sar=estimated_cost,
            coverage_pct=coverage_pct,
            accuracy_score=accuracy_score,
            plan_ar=plan_ar,
            strategy=strategy.value,
            hectares_per_sample=self.hectares_per_sample,
        )

        logger.info(
            "sampling_optimization_complete",
            field_id=plan.field_id,
            total_samples=plan.total_samples,
            coverage_pct=round(plan.coverage_pct, 1),
            accuracy_score=round(plan.accuracy_score, 4),
            estimated_cost_sar=round(plan.estimated_cost_sar, 2),
        )

        return plan

    # -----------------------------------------------------------------------
    # Sampling strategies
    # -----------------------------------------------------------------------

    def _allocate_samples(
        self,
        zones: list[NDVIZone],
        total_samples: int,
        field_area_ha: float,
    ) -> dict[str, int]:
        """
        Allocate samples to zones proportionally based on area and variability.

        توزيع العينات على المناطق بنسبة المساحة والتباين

        Formula per zone:
            weight = (1 - w) * (zone_area / total_area) + w * (zone_std / max_std)
            samples = max(1, round(weight * total_samples / sum(weights)))
        """
        if not zones:
            return {}

        total_area = sum(z.area_hectares for z in zones) or 1.0
        max_std = max((z.ndvi_std for z in zones), default=0.01) or 0.01
        w = self.VARIABILITY_WEIGHT

        # Compute raw weights
        weights: dict[str, float] = {}
        for z in zones:
            area_ratio = z.area_hectares / total_area
            std_ratio = z.ndvi_std / max_std
            weights[z.zone_id] = (1.0 - w) * area_ratio + w * std_ratio

        total_weight = sum(weights.values()) or 1.0

        # Allocate with minimum 1 per zone
        allocation: dict[str, int] = {}
        remaining = total_samples

        for z in zones:
            n = max(self.MIN_SAMPLES_PER_ZONE, round((weights[z.zone_id] / total_weight) * total_samples))
            allocation[z.zone_id] = n
            remaining -= n

        # Redistribute surplus/deficit
        if remaining != 0:
            # Sort zones by weight descending to add/remove from most important first
            sorted_zones = sorted(zones, key=lambda z: weights[z.zone_id], reverse=True)
            idx = 0
            while remaining > 0:
                zone = sorted_zones[idx % len(sorted_zones)]
                allocation[zone.zone_id] += 1
                remaining -= 1
                idx += 1
            while remaining < 0:
                zone = sorted_zones[-(idx % len(sorted_zones)) - 1]
                if allocation[zone.zone_id] > self.MIN_SAMPLES_PER_ZONE:
                    allocation[zone.zone_id] -= 1
                    remaining += 1
                idx += 1
                if idx > len(sorted_zones) * 2:
                    break  # safety valve

        return allocation

    def _stratified_random(
        self,
        zones: list[NDVIZone],
        samples_per_zone: dict[str, int],
    ) -> list[SamplePoint]:
        """
        Generate stratified random sample points within each zone.

        نقاط أخذ عينات عشوائية طبقية داخل كل منطقة

        Each zone gets its allocated number of random points placed
        uniformly inside the zone polygon.
        """
        points: list[SamplePoint] = []

        for zone in zones:
            n = samples_per_zone.get(zone.zone_id, self.MIN_SAMPLES_PER_ZONE)
            for i in range(n):
                coord = _random_point_in_polygon(zone.boundary)
                if coord is None:
                    coord = _polygon_centroid(zone.boundary)
                # First point in each zone is priority 2, rest are 3
                priority = 2 if i == 0 else 3
                points.append(
                    SamplePoint(
                        lat=round(coord[0], 7),
                        lng=round(coord[1], 7),
                        zone_id=zone.zone_id,
                        zone_type=zone.zone_type.value,
                        priority=priority,
                    )
                )

        return points

    def _grid_based(
        self,
        boundary: Polygon,
        grid_size_m: float,
    ) -> list[SamplePoint]:
        """
        Generate sample points on a regular grid clipped to the field boundary.

        نقاط أخذ عينات على شبكة منتظمة مقتصة على حدود الحقل

        Args:
            boundary: Field boundary polygon
            grid_size_m: Grid spacing in meters
        """
        min_lat, min_lng, max_lat, max_lng = _bounding_box(boundary)
        centroid = _polygon_centroid(boundary)
        lat_rad = math.radians(centroid[0])

        meters_per_deg_lat = 111_320.0
        meters_per_deg_lng = 111_320.0 * math.cos(lat_rad)

        lat_step = grid_size_m / meters_per_deg_lat
        lng_step = grid_size_m / meters_per_deg_lng

        if lat_step <= 0 or lng_step <= 0:
            return []

        points: list[SamplePoint] = []
        lat = min_lat + lat_step / 2.0  # offset grid by half step
        idx = 0
        while lat <= max_lat:
            lng = min_lng + lng_step / 2.0
            while lng <= max_lng:
                if _point_in_polygon((lat, lng), boundary):
                    idx += 1
                    points.append(
                        SamplePoint(
                            lat=round(lat, 7),
                            lng=round(lng, 7),
                            zone_id=f"GRID-{idx:03d}",
                            zone_type=ZoneType.MEDIUM.value,
                            priority=2,
                        )
                    )
                lng += lng_step
            lat += lat_step

        return points

    def _zone_centroid(self, zones: list[NDVIZone]) -> list[SamplePoint]:
        """
        Place one sample point at the centroid of each zone.

        وضع نقطة عينة واحدة في مركز كل منطقة

        All centroid points receive priority 1 (must sample).
        """
        points: list[SamplePoint] = []
        for zone in zones:
            centroid = _polygon_centroid(zone.boundary)
            points.append(
                SamplePoint(
                    lat=round(centroid[0], 7),
                    lng=round(centroid[1], 7),
                    zone_id=zone.zone_id,
                    zone_type=zone.zone_type.value,
                    priority=1,
                )
            )
        return points

    def _hybrid(
        self,
        zones: list[NDVIZone],
        total_samples: int,
        field_area_ha: float,
    ) -> list[SamplePoint]:
        """
        Hybrid strategy combining centroid + stratified random.

        استراتيجية مختلطة تجمع بين مركز المنطقة والعشوائية الطبقية

        1. Place one centroid point per zone (priority 1 — must)
        2. Fill remaining quota with stratified random points (priority 2/3)
        """
        # Phase 1: centroids
        centroid_points = self._zone_centroid(zones)

        # Phase 2: remaining quota via stratified random
        remaining = max(0, total_samples - len(centroid_points))
        if remaining > 0 and zones:
            allocation = self._allocate_samples(zones, remaining, field_area_ha)
            random_points = self._stratified_random(zones, allocation)
        else:
            random_points = []

        return centroid_points + random_points

    # -----------------------------------------------------------------------
    # Arabic plan description
    # -----------------------------------------------------------------------

    @staticmethod
    def _generate_plan_ar(
        field_area_ha: float,
        total_samples: int,
        num_zones: int,
        coverage_pct: float,
        cost_sar: float,
        strategy: SamplingStrategy,
    ) -> str:
        """Generate a human-readable Arabic description of the sampling plan."""
        strategy_names = {
            SamplingStrategy.ZONE_CENTROID: "مركز المنطقة",
            SamplingStrategy.STRATIFIED_RANDOM: "عشوائية طبقية",
            SamplingStrategy.GRID_BASED: "شبكة منتظمة",
            SamplingStrategy.HYBRID: "مختلطة (مركز + عشوائية)",
        }
        strategy_ar = strategy_names.get(strategy, "مختلطة")

        return (
            f"خطة أخذ عينات التربة\n"
            f"المساحة الإجمالية: {field_area_ha:.1f} هكتار\n"
            f"عدد العينات: {total_samples}\n"
            f"عدد المناطق: {num_zones}\n"
            f"نسبة التغطية: {coverage_pct:.1f}%\n"
            f"التكلفة التقديرية: {cost_sar:,.0f} ريال سعودي\n"
            f"الاستراتيجية: {strategy_ar}\n"
            f"---\n"
            f"ملاحظة: يُنصح بأخذ العينات في الصباح الباكر عندما تكون رطوبة التربة مستقرة.\n"
            f"يجب أخذ العينات من عمق ٣٠ سم باستخدام مثقاب التربة القياسي."
        )
