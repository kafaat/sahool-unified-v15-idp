"""
SAHOOL Terrain Events
======================
أحداث تحليل التضاريس - تحليل الارتفاعات والمياه والتآكل

Terrain analysis events for elevation modeling, water flow, erosion risk,
and land leveling recommendations.

Event subjects follow pattern: sahool.terrain.{event_type}
For tenant-scoped: sahool.tenant.{tenant_id}.terrain.{event_type}

Usage:
    from shared.events.terrain_events import (
        TerrainAnalysisCompletedEvent,
        HighErosionRiskEvent,
        TerrainSubjects,
    )

    event = TerrainAnalysisCompletedEvent(
        field_id=field_uuid,
        analysis_id=analysis_uuid,
        elevation_min=120.5,
        elevation_max=135.2,
        slope_mean=3.5,
        ...
    )
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────────────
# Terrain Subject Constants - ثوابت موضوعات التضاريس
# ─────────────────────────────────────────────────────────────────────────────


class TerrainSubjects:
    """
    NATS subject constants for terrain analysis events.
    ثوابت موضوعات NATS لأحداث تحليل التضاريس
    """

    # Analysis events
    ANALYSIS_STARTED = "sahool.terrain.analysis_started"
    ANALYSIS_COMPLETED = "sahool.terrain.analysis_completed"
    ANALYSIS_FAILED = "sahool.terrain.analysis_failed"

    # Risk alerts
    HIGH_EROSION_RISK = "sahool.terrain.high_erosion_risk"
    WATERLOGGING_DETECTED = "sahool.terrain.waterlogging_detected"
    DRAINAGE_ISSUE = "sahool.terrain.drainage_issue"

    # Recommendations
    LEVELING_RECOMMENDED = "sahool.terrain.leveling_recommended"
    DRAINAGE_RECOMMENDED = "sahool.terrain.drainage_recommended"
    CONTOUR_FARMING_RECOMMENDED = "sahool.terrain.contour_farming_recommended"

    # Data updates
    DEM_UPDATED = "sahool.terrain.dem_updated"
    FLOW_ACCUMULATION_COMPUTED = "sahool.terrain.flow_accumulation_computed"

    # Wildcards
    ALL = "sahool.terrain.*"
    RISKS_ALL = "sahool.terrain.*_risk"
    RECOMMENDATIONS_ALL = "sahool.terrain.*_recommended"

    @staticmethod
    def tenant_scoped(tenant_id: str, event_type: str) -> str:
        """
        Get tenant-scoped subject for terrain events.

        Args:
            tenant_id: Tenant identifier
            event_type: Event type (e.g., "analysis_completed")

        Returns:
            Tenant-scoped subject (e.g., "sahool.tenant.org_123.terrain.analysis_completed")
        """
        return f"sahool.tenant.{tenant_id}.terrain.{event_type}"


# Convenience constants for direct import
SAHOOL_TERRAIN_ANALYSIS_STARTED = TerrainSubjects.ANALYSIS_STARTED
SAHOOL_TERRAIN_ANALYSIS_COMPLETED = TerrainSubjects.ANALYSIS_COMPLETED
SAHOOL_TERRAIN_ANALYSIS_FAILED = TerrainSubjects.ANALYSIS_FAILED
SAHOOL_TERRAIN_HIGH_EROSION_RISK = TerrainSubjects.HIGH_EROSION_RISK
SAHOOL_TERRAIN_WATERLOGGING_DETECTED = TerrainSubjects.WATERLOGGING_DETECTED
SAHOOL_TERRAIN_DRAINAGE_ISSUE = TerrainSubjects.DRAINAGE_ISSUE
SAHOOL_TERRAIN_LEVELING_RECOMMENDED = TerrainSubjects.LEVELING_RECOMMENDED
SAHOOL_TERRAIN_DRAINAGE_RECOMMENDED = TerrainSubjects.DRAINAGE_RECOMMENDED
SAHOOL_TERRAIN_DEM_UPDATED = TerrainSubjects.DEM_UPDATED
SAHOOL_TERRAIN_ALL = TerrainSubjects.ALL


# ─────────────────────────────────────────────────────────────────────────────
# Enums - التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class ErosionRiskLevel(StrEnum):
    """Erosion risk levels"""

    NEGLIGIBLE = "negligible"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class WaterloggingRisk(StrEnum):
    """Waterlogging risk levels"""

    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SlopeClass(StrEnum):
    """Slope classification for agricultural use"""

    FLAT = "flat"  # 0-2%
    GENTLE = "gentle"  # 2-5%
    MODERATE = "moderate"  # 5-10%
    STEEP = "steep"  # 10-15%
    VERY_STEEP = "very_steep"  # >15%


class TerrainDataSource(StrEnum):
    """Source of terrain data"""

    DRONE_PHOTOGRAMMETRY = "drone_photogrammetry"
    LIDAR = "lidar"
    SATELLITE_DEM = "satellite_dem"
    SURVEY_RTK = "survey_rtk"
    INTERPOLATED = "interpolated"


class LevelingMethod(StrEnum):
    """Land leveling methods"""

    LASER_GUIDED = "laser_guided"
    GPS_GUIDED = "gps_guided"
    CONVENTIONAL = "conventional"
    PRECISION = "precision"


# ─────────────────────────────────────────────────────────────────────────────
# Base Terrain Event - النموذج الأساسي لأحداث التضاريس
# ─────────────────────────────────────────────────────────────────────────────


class BaseTerrainEvent(BaseModel):
    """
    Base class for all terrain analysis events.
    النموذج الأساسي لجميع أحداث تحليل التضاريس
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")
    source_service: str = Field(default="terrain-analysis-service", description="Service that emitted the event")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")

    @property
    def event_type(self) -> str:
        """Return the event type name (class name)"""
        return self.__class__.__name__

    model_config = ConfigDict(populate_by_name=True)


# ─────────────────────────────────────────────────────────────────────────────
# Supporting Models - النماذج الداعمة
# ─────────────────────────────────────────────────────────────────────────────


class ElevationStatistics(BaseModel):
    """
    Elevation statistics for a field.
    إحصائيات الارتفاع للحقل
    """

    min_m: float = Field(..., description="Minimum elevation in meters")
    max_m: float = Field(..., description="Maximum elevation in meters")
    mean_m: float = Field(..., description="Mean elevation in meters")
    std_dev_m: float = Field(..., ge=0, description="Standard deviation in meters")
    range_m: float = Field(..., ge=0, description="Elevation range in meters")
    datum: str = Field(default="WGS84", description="Vertical datum reference")


class SlopeStatistics(BaseModel):
    """
    Slope statistics for a field.
    إحصائيات الميل للحقل
    """

    min_percent: float = Field(..., ge=0, description="Minimum slope percentage")
    max_percent: float = Field(..., ge=0, description="Maximum slope percentage")
    mean_percent: float = Field(..., ge=0, description="Mean slope percentage")
    std_dev_percent: float = Field(..., ge=0, description="Standard deviation")
    dominant_direction: str | None = Field(
        None,
        pattern="^(N|NE|E|SE|S|SW|W|NW)$",
        description="Dominant slope direction",
    )
    slope_class: str = Field(
        ...,
        pattern="^(flat|gentle|moderate|steep|very_steep)$",
        description="Overall slope classification",
    )


class DrainageZone(BaseModel):
    """
    Drainage zone information.
    معلومات منطقة الصرف
    """

    zone_id: str = Field(..., description="Zone identifier")
    area_sqm: float = Field(..., ge=0, description="Zone area in m2")
    flow_accumulation: float = Field(..., ge=0, description="Flow accumulation value")
    is_depression: bool = Field(default=False, description="Is a depression/sink")
    waterlogging_risk: str = Field(..., pattern="^(none|low|moderate|high|critical)$", description="Waterlogging risk")
    centroid_lat: float = Field(..., ge=-90, le=90, description="Zone centroid latitude")
    centroid_lon: float = Field(..., ge=-180, le=180, description="Zone centroid longitude")


class ErosionZone(BaseModel):
    """
    Erosion risk zone information.
    معلومات منطقة خطر التآكل
    """

    zone_id: str = Field(..., description="Zone identifier")
    area_sqm: float = Field(..., ge=0, description="Zone area in m2")
    risk_level: str = Field(
        ...,
        pattern="^(negligible|low|moderate|high|severe)$",
        description="Erosion risk level",
    )
    erosion_type: str | None = Field(
        None,
        pattern="^(sheet|rill|gully|wind)$",
        description="Type of erosion risk",
    )
    slope_percent: float = Field(..., ge=0, description="Zone slope percentage")
    soil_loss_tons_per_ha_year: float | None = Field(None, ge=0, description="Estimated soil loss (RUSLE)")
    centroid_lat: float = Field(..., ge=-90, le=90, description="Zone centroid latitude")
    centroid_lon: float = Field(..., ge=-180, le=180, description="Zone centroid longitude")


class LevelingZone(BaseModel):
    """
    Land leveling zone recommendation.
    توصية منطقة تسوية الأرض
    """

    zone_id: str = Field(..., description="Zone identifier")
    area_sqm: float = Field(..., ge=0, description="Zone area in m2")
    cut_volume_m3: float = Field(..., ge=0, description="Volume to cut in m3")
    fill_volume_m3: float = Field(..., ge=0, description="Volume to fill in m3")
    target_elevation_m: float = Field(..., description="Target elevation in meters")
    priority: int = Field(..., ge=1, le=5, description="Priority (1=highest)")
    estimated_cost: float | None = Field(None, ge=0, description="Estimated leveling cost")
    currency: str = Field(default="SAR", description="Currency code")


# ─────────────────────────────────────────────────────────────────────────────
# Terrain Analysis Events - أحداث تحليل التضاريس
# ─────────────────────────────────────────────────────────────────────────────


class TerrainAnalysisStartedEvent(BaseTerrainEvent):
    """
    Event emitted when terrain analysis job starts.
    حدث يُطلق عند بدء مهمة تحليل التضاريس
    """

    analysis_id: UUID = Field(default_factory=uuid4, description="Analysis job identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    analysis_type: str = Field(
        ...,
        pattern="^(full|elevation_only|slope_only|drainage|erosion|leveling)$",
        description="Type of analysis",
    )
    data_source: str = Field(
        ...,
        pattern="^(drone_photogrammetry|lidar|satellite_dem|survey_rtk|interpolated)$",
        description="Terrain data source",
    )
    resolution_m: float | None = Field(None, gt=0, description="DEM resolution in meters")
    requested_by: UUID | None = Field(None, description="User who requested analysis")


class TerrainAnalysisCompletedEvent(BaseTerrainEvent):
    """
    Event emitted when terrain analysis is completed.
    حدث يُطلق عند اكتمال تحليل التضاريس
    """

    analysis_id: UUID = Field(..., description="Analysis job identifier")
    field_id: UUID = Field(..., description="Analyzed field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Data source information
    data_source: str = Field(
        ...,
        pattern="^(drone_photogrammetry|lidar|satellite_dem|survey_rtk|interpolated)$",
        description="Terrain data source",
    )
    resolution_m: float = Field(..., gt=0, description="DEM resolution in meters")
    capture_date: datetime | None = Field(None, description="Data capture date")

    # Elevation statistics
    elevation: ElevationStatistics = Field(..., description="Elevation statistics")

    # Slope statistics
    slope: SlopeStatistics = Field(..., description="Slope statistics")

    # Aspect (slope direction) distribution
    aspect_distribution: dict[str, float] | None = Field(None, description="Aspect distribution by direction (%)")

    # Derived indices
    topographic_wetness_index_mean: float | None = Field(None, description="Mean Topographic Wetness Index (TWI)")
    stream_power_index_mean: float | None = Field(None, description="Mean Stream Power Index (SPI)")
    sediment_transport_index_mean: float | None = Field(None, description="Mean Sediment Transport Index (STI)")

    # Drainage analysis
    drainage_density: float | None = Field(None, ge=0, description="Drainage density (km/km2)")
    depression_count: int | None = Field(None, ge=0, description="Number of depressions")
    depression_total_area_sqm: float | None = Field(None, ge=0, description="Total depression area")

    # Erosion risk summary
    erosion_risk_level: str = Field(
        ...,
        pattern="^(negligible|low|moderate|high|severe)$",
        description="Overall erosion risk",
    )
    high_risk_area_sqm: float | None = Field(None, ge=0, description="High erosion risk area")
    high_risk_area_percentage: float | None = Field(None, ge=0, le=100, description="High risk area percentage")

    # Waterlogging risk
    waterlogging_risk: str = Field(
        ...,
        pattern="^(none|low|moderate|high|critical)$",
        description="Overall waterlogging risk",
    )
    waterlogging_area_sqm: float | None = Field(None, ge=0, description="Area at risk of waterlogging")

    # Suitability for irrigation
    irrigation_suitability: str | None = Field(
        None,
        pattern="^(excellent|good|moderate|poor|unsuitable)$",
        description="Irrigation suitability",
    )
    leveling_required: bool = Field(default=False, description="Whether leveling is recommended")

    # Processing metadata
    started_at: datetime = Field(..., description="Analysis start time")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Completion time")
    processing_duration_ms: int = Field(..., ge=0, description="Processing duration")

    # Output URLs
    dem_url: str | None = Field(None, description="DEM GeoTIFF URL")
    slope_map_url: str | None = Field(None, description="Slope map URL")
    aspect_map_url: str | None = Field(None, description="Aspect map URL")
    flow_accumulation_url: str | None = Field(None, description="Flow accumulation URL")
    erosion_risk_map_url: str | None = Field(None, description="Erosion risk map URL")
    report_url: str | None = Field(None, description="Analysis report URL")


class TerrainAnalysisFailedEvent(BaseTerrainEvent):
    """
    Event emitted when terrain analysis fails.
    حدث يُطلق عند فشل تحليل التضاريس
    """

    analysis_id: UUID = Field(..., description="Analysis job identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")

    # Partial results
    completed_steps: list[str] = Field(default_factory=list, description="Successfully completed steps")
    failed_step: str | None = Field(None, description="Step that failed")

    # Timing
    started_at: datetime = Field(..., description="Analysis start time")
    failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Failure time")

    # Retry info
    retry_count: int = Field(default=0, ge=0, description="Retry attempts")
    is_retriable: bool = Field(default=True, description="Can be retried")


# ─────────────────────────────────────────────────────────────────────────────
# Risk Alert Events - أحداث تنبيهات المخاطر
# ─────────────────────────────────────────────────────────────────────────────


class HighErosionRiskEvent(BaseTerrainEvent):
    """
    Event emitted when high erosion risk is detected.
    حدث يُطلق عند اكتشاف خطر تآكل مرتفع
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Alert identifier")
    field_id: UUID = Field(..., description="Affected field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Risk assessment
    risk_level: str = Field(..., pattern="^(high|severe)$", description="Erosion risk level")
    erosion_type: str = Field(
        ...,
        pattern="^(sheet|rill|gully|wind|combined)$",
        description="Type of erosion risk",
    )

    # Affected area
    affected_area_sqm: float = Field(..., ge=0, description="Affected area in m2")
    affected_area_percentage: float = Field(..., ge=0, le=100, description="Percentage of field")
    erosion_zones: list[ErosionZone] = Field(default_factory=list, description="Erosion zones")

    # Estimated impact
    estimated_soil_loss_tons_per_ha_year: float | None = Field(
        None, ge=0, description="Estimated annual soil loss (RUSLE)"
    )
    nutrient_loss_risk: str | None = Field(None, pattern="^(low|moderate|high)$", description="Nutrient loss risk")

    # Environmental factors
    contributing_factors: list[str] = Field(default_factory=list, description="Contributing factors")
    slope_factor: float | None = Field(None, ge=0, description="RUSLE slope factor (S)")
    rainfall_erosivity: float | None = Field(None, ge=0, description="Rainfall erosivity (R factor)")

    # Recommendations
    recommended_actions: list[str] = Field(default_factory=list, description="Recommended actions")
    recommended_actions_ar: list[str] = Field(default_factory=list, description="Arabic recommendations")
    urgency: str = Field(..., pattern="^(immediate|soon|seasonal)$", description="Action urgency")

    # Cost-benefit
    estimated_prevention_cost: float | None = Field(None, ge=0, description="Prevention cost estimate")
    estimated_damage_if_untreated: float | None = Field(None, ge=0, description="Potential damage cost")
    currency: str = Field(default="SAR", description="Currency code")

    # Evidence
    erosion_map_url: str | None = Field(None, description="Erosion risk map URL")
    report_url: str | None = Field(None, description="Detailed report URL")


class WaterloggingDetectedEvent(BaseTerrainEvent):
    """
    Event emitted when waterlogging risk is detected.
    حدث يُطلق عند اكتشاف خطر التشبع المائي
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Alert identifier")
    field_id: UUID = Field(..., description="Affected field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Risk assessment
    risk_level: str = Field(..., pattern="^(moderate|high|critical)$", description="Waterlogging risk level")
    waterlogging_type: str = Field(
        ...,
        pattern="^(surface|subsurface|perched|seasonal)$",
        description="Type of waterlogging",
    )

    # Affected area
    affected_area_sqm: float = Field(..., ge=0, description="Affected area in m2")
    affected_area_percentage: float = Field(..., ge=0, le=100, description="Percentage of field")
    drainage_zones: list[DrainageZone] = Field(default_factory=list, description="Problem drainage zones")

    # Depression analysis
    depression_count: int = Field(..., ge=0, description="Number of depressions")
    max_depression_depth_m: float | None = Field(None, ge=0, description="Maximum depression depth")
    total_depression_volume_m3: float | None = Field(None, ge=0, description="Total depression volume")

    # Contributing factors
    soil_drainage_class: str | None = Field(
        None,
        pattern="^(well_drained|moderately_drained|poorly_drained|very_poorly_drained)$",
        description="Soil drainage class",
    )
    water_table_depth_m: float | None = Field(None, ge=0, description="Water table depth if known")
    contributing_factors: list[str] = Field(default_factory=list, description="Contributing factors")

    # Crop impact
    crop_at_risk: str | None = Field(None, description="Crop at risk")
    crop_at_risk_ar: str | None = Field(None, description="Arabic crop name")
    yield_loss_risk_percentage: float | None = Field(None, ge=0, le=100, description="Yield loss risk")

    # Recommendations
    recommended_actions: list[str] = Field(default_factory=list, description="Recommended actions")
    recommended_actions_ar: list[str] = Field(default_factory=list, description="Arabic recommendations")
    drainage_solution: str | None = Field(
        None,
        pattern="^(surface_drains|subsurface_drains|raised_beds|grading|pumping)$",
        description="Recommended drainage solution",
    )
    urgency: str = Field(..., pattern="^(immediate|before_planting|seasonal)$", description="Action urgency")

    # Cost estimates
    estimated_remediation_cost: float | None = Field(None, ge=0, description="Remediation cost estimate")
    currency: str = Field(default="SAR", description="Currency code")

    # Evidence
    waterlogging_map_url: str | None = Field(None, description="Waterlogging risk map")
    report_url: str | None = Field(None, description="Detailed report URL")


class DrainageIssueEvent(BaseTerrainEvent):
    """
    Event emitted when drainage issues are detected.
    حدث يُطلق عند اكتشاف مشاكل في الصرف
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Alert identifier")
    field_id: UUID = Field(..., description="Affected field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Issue classification
    issue_type: str = Field(
        ...,
        pattern="^(poor_natural_drainage|blocked_outlet|insufficient_slope|ponding)$",
        description="Type of drainage issue",
    )
    severity: str = Field(..., pattern="^(low|moderate|high|critical)$", description="Issue severity")

    # Affected area
    affected_area_sqm: float = Field(..., ge=0, description="Affected area in m2")
    affected_zones: list[DrainageZone] = Field(default_factory=list, description="Affected drainage zones")

    # Issue details
    description: str = Field(..., description="Issue description")
    description_ar: str | None = Field(None, description="Arabic description")

    # Recommendations
    recommended_solution: str = Field(..., description="Recommended solution")
    recommended_solution_ar: str | None = Field(None, description="Arabic recommendation")
    estimated_cost: float | None = Field(None, ge=0, description="Solution cost estimate")
    currency: str = Field(default="SAR", description="Currency code")


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Events - أحداث التوصيات
# ─────────────────────────────────────────────────────────────────────────────


class LevelingRecommendedEvent(BaseTerrainEvent):
    """
    Event emitted when land leveling is recommended.
    حدث يُطلق عند التوصية بتسوية الأرض
    """

    recommendation_id: UUID = Field(default_factory=uuid4, description="Recommendation identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Leveling assessment
    leveling_required: bool = Field(default=True, description="Leveling is required")
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$", description="Leveling priority")
    leveling_method: str = Field(
        ...,
        pattern="^(laser_guided|gps_guided|conventional|precision)$",
        description="Recommended leveling method",
    )

    # Current state
    current_slope_mean_percent: float = Field(..., ge=0, description="Current mean slope")
    current_elevation_range_m: float = Field(..., ge=0, description="Current elevation range")
    unevenness_index: float | None = Field(None, ge=0, description="Field unevenness index")

    # Target state
    target_slope_percent: float = Field(..., ge=0, description="Target slope")
    target_elevation_range_m: float = Field(..., ge=0, description="Target elevation range")

    # Earthwork calculation
    total_cut_volume_m3: float = Field(..., ge=0, description="Total cut volume")
    total_fill_volume_m3: float = Field(..., ge=0, description="Total fill volume")
    net_earthwork_m3: float = Field(..., description="Net earthwork (cut-fill)")
    earthwork_balance: str = Field(
        ..., pattern="^(balanced|cut_excess|fill_required)$", description="Earthwork balance"
    )

    # Zones
    leveling_zones: list[LevelingZone] = Field(default_factory=list, description="Leveling zones with details")
    cut_zones_count: int = Field(default=0, ge=0, description="Number of cut zones")
    fill_zones_count: int = Field(default=0, ge=0, description="Number of fill zones")

    # Benefits
    expected_benefits: list[str] = Field(default_factory=list, description="Expected benefits")
    expected_benefits_ar: list[str] = Field(default_factory=list, description="Arabic benefits")
    irrigation_efficiency_improvement_percent: float | None = Field(
        None, ge=0, le=100, description="Expected irrigation efficiency improvement"
    )
    water_savings_percent: float | None = Field(None, ge=0, le=100, description="Expected water savings")
    yield_improvement_percent: float | None = Field(None, ge=0, le=100, description="Expected yield improvement")

    # Cost-benefit analysis
    estimated_cost: float = Field(..., ge=0, description="Estimated leveling cost")
    currency: str = Field(default="SAR", description="Currency code")
    estimated_annual_savings: float | None = Field(None, ge=0, description="Estimated annual savings")
    payback_period_years: float | None = Field(None, ge=0, description="Payback period in years")

    # Implementation
    recommended_timing: str | None = Field(None, description="Recommended implementation timing")
    recommended_timing_ar: str | None = Field(None, description="Arabic timing recommendation")
    estimated_duration_days: int | None = Field(None, ge=1, description="Estimated duration in days")

    # Supporting data
    cut_fill_map_url: str | None = Field(None, description="Cut/fill map URL")
    design_surface_url: str | None = Field(None, description="Design surface URL")
    report_url: str | None = Field(None, description="Detailed report URL")


class DrainageRecommendedEvent(BaseTerrainEvent):
    """
    Event emitted when drainage improvements are recommended.
    حدث يُطلق عند التوصية بتحسينات الصرف
    """

    recommendation_id: UUID = Field(default_factory=uuid4, description="Recommendation identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Drainage assessment
    current_drainage_rating: str = Field(
        ...,
        pattern="^(adequate|poor|very_poor|critical)$",
        description="Current drainage rating",
    )
    recommended_drainage_type: str = Field(
        ...,
        pattern="^(surface|subsurface|combined|raised_beds)$",
        description="Recommended drainage type",
    )
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$", description="Implementation priority")

    # Drainage design
    main_drain_length_m: float | None = Field(None, ge=0, description="Main drain length")
    lateral_drain_length_m: float | None = Field(None, ge=0, description="Total lateral drain length")
    drain_spacing_m: float | None = Field(None, ge=0, description="Drain spacing")
    drain_depth_m: float | None = Field(None, ge=0, description="Drain depth")
    outlet_location_lat: float | None = Field(None, ge=-90, le=90, description="Outlet latitude")
    outlet_location_lon: float | None = Field(None, ge=-180, le=180, description="Outlet longitude")

    # Expected improvements
    expected_improvements: list[str] = Field(default_factory=list, description="Expected improvements")
    expected_improvements_ar: list[str] = Field(default_factory=list, description="Arabic improvements")
    waterlogging_reduction_percent: float | None = Field(
        None, ge=0, le=100, description="Expected waterlogging reduction"
    )

    # Cost-benefit
    estimated_cost: float = Field(..., ge=0, description="Estimated installation cost")
    currency: str = Field(default="SAR", description="Currency code")
    estimated_annual_benefit: float | None = Field(None, ge=0, description="Estimated annual benefit")
    payback_period_years: float | None = Field(None, ge=0, description="Payback period")

    # Supporting data
    drainage_design_url: str | None = Field(None, description="Drainage design URL")
    report_url: str | None = Field(None, description="Detailed report URL")


class ContourFarmingRecommendedEvent(BaseTerrainEvent):
    """
    Event emitted when contour farming practices are recommended.
    حدث يُطلق عند التوصية بممارسات الزراعة الكنتورية
    """

    recommendation_id: UUID = Field(default_factory=uuid4, description="Recommendation identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Assessment
    slope_mean_percent: float = Field(..., ge=0, description="Mean field slope")
    erosion_risk_current: str = Field(
        ...,
        pattern="^(low|moderate|high|severe)$",
        description="Current erosion risk",
    )
    erosion_risk_with_contours: str = Field(
        ...,
        pattern="^(negligible|low|moderate|high)$",
        description="Erosion risk with contour farming",
    )

    # Contour design
    contour_interval_m: float = Field(..., gt=0, description="Contour line interval")
    contour_lines_count: int = Field(..., ge=1, description="Number of contour lines")
    contour_lines_url: str | None = Field(None, description="Contour lines GeoJSON URL")

    # Expected benefits
    erosion_reduction_percent: float = Field(..., ge=0, le=100, description="Expected erosion reduction")
    water_retention_improvement_percent: float | None = Field(
        None, ge=0, le=100, description="Water retention improvement"
    )
    expected_benefits: list[str] = Field(default_factory=list, description="Expected benefits")
    expected_benefits_ar: list[str] = Field(default_factory=list, description="Arabic benefits")

    # Implementation
    implementation_notes: str | None = Field(None, description="Implementation notes")
    implementation_notes_ar: str | None = Field(None, description="Arabic implementation notes")
    compatible_crops: list[str] = Field(default_factory=list, description="Compatible crops")

    # Supporting data
    report_url: str | None = Field(None, description="Detailed report URL")


# ─────────────────────────────────────────────────────────────────────────────
# DEM Update Event - حدث تحديث نموذج الارتفاع الرقمي
# ─────────────────────────────────────────────────────────────────────────────


class DEMUpdatedEvent(BaseTerrainEvent):
    """
    Event emitted when Digital Elevation Model is updated.
    حدث يُطلق عند تحديث نموذج الارتفاع الرقمي
    """

    field_id: UUID = Field(..., description="Field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # DEM metadata
    data_source: str = Field(
        ...,
        pattern="^(drone_photogrammetry|lidar|satellite_dem|survey_rtk|interpolated)$",
        description="Data source",
    )
    resolution_m: float = Field(..., gt=0, description="DEM resolution in meters")
    accuracy_m: float | None = Field(None, gt=0, description="Vertical accuracy")
    capture_date: datetime = Field(..., description="Data capture date")
    processing_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Processing date")

    # Coverage
    coverage_percentage: float = Field(..., ge=0, le=100, description="Field coverage percentage")
    points_count: int | None = Field(None, ge=0, description="Number of elevation points")

    # Statistics summary
    elevation_min_m: float = Field(..., description="Minimum elevation")
    elevation_max_m: float = Field(..., description="Maximum elevation")
    elevation_mean_m: float = Field(..., description="Mean elevation")

    # Previous comparison
    previous_dem_date: datetime | None = Field(None, description="Previous DEM date")
    elevation_change_detected: bool = Field(default=False, description="Significant elevation change detected")
    max_elevation_change_m: float | None = Field(None, description="Maximum elevation change since last DEM")

    # Output URLs
    dem_url: str = Field(..., description="DEM GeoTIFF URL")
    hillshade_url: str | None = Field(None, description="Hillshade visualization URL")
    metadata_url: str | None = Field(None, description="Metadata JSON URL")


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Subject constants
    "TerrainSubjects",
    "SAHOOL_TERRAIN_ANALYSIS_STARTED",
    "SAHOOL_TERRAIN_ANALYSIS_COMPLETED",
    "SAHOOL_TERRAIN_ANALYSIS_FAILED",
    "SAHOOL_TERRAIN_HIGH_EROSION_RISK",
    "SAHOOL_TERRAIN_WATERLOGGING_DETECTED",
    "SAHOOL_TERRAIN_DRAINAGE_ISSUE",
    "SAHOOL_TERRAIN_LEVELING_RECOMMENDED",
    "SAHOOL_TERRAIN_DRAINAGE_RECOMMENDED",
    "SAHOOL_TERRAIN_DEM_UPDATED",
    "SAHOOL_TERRAIN_ALL",
    # Enums
    "ErosionRiskLevel",
    "WaterloggingRisk",
    "SlopeClass",
    "TerrainDataSource",
    "LevelingMethod",
    # Supporting models
    "ElevationStatistics",
    "SlopeStatistics",
    "DrainageZone",
    "ErosionZone",
    "LevelingZone",
    # Base event
    "BaseTerrainEvent",
    # Analysis events
    "TerrainAnalysisStartedEvent",
    "TerrainAnalysisCompletedEvent",
    "TerrainAnalysisFailedEvent",
    # Risk alert events
    "HighErosionRiskEvent",
    "WaterloggingDetectedEvent",
    "DrainageIssueEvent",
    # Recommendation events
    "LevelingRecommendedEvent",
    "DrainageRecommendedEvent",
    "ContourFarmingRecommendedEvent",
    # DEM update event
    "DEMUpdatedEvent",
]
