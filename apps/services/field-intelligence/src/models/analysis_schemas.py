"""
Comprehensive Field Analysis Schemas
مخططات تحليل الحقول الشاملة

Request/response types for POST /api/v1/analyze/field/comprehensive
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Incoming data ──────────────────────────────────────────────────────────────


class IndiceStats(BaseModel):
    value: float | None = None
    min: float | None = None
    max: float | None = None
    std_dev: float | None = None
    cloud_cover: float | None = None


class AllIndicesPayload(BaseModel):
    """37 agricultural spectral indices from CDSE/Sentinel-2."""
    # Vegetation Vigor (10)
    NDVI: IndiceStats = Field(default_factory=IndiceStats)
    EVI: IndiceStats = Field(default_factory=IndiceStats)
    EVI2: IndiceStats = Field(default_factory=IndiceStats)
    GNDVI: IndiceStats = Field(default_factory=IndiceStats)
    WDRVI: IndiceStats = Field(default_factory=IndiceStats)
    ARVI: IndiceStats = Field(default_factory=IndiceStats)
    DVI: IndiceStats = Field(default_factory=IndiceStats)
    RVI: IndiceStats = Field(default_factory=IndiceStats)
    RDVI: IndiceStats = Field(default_factory=IndiceStats)
    NIRv: IndiceStats = Field(default_factory=IndiceStats)
    # Red Edge / Chlorophyll (8)
    NDRE: IndiceStats = Field(default_factory=IndiceStats)
    NDRE1: IndiceStats = Field(default_factory=IndiceStats)
    NDRE2: IndiceStats = Field(default_factory=IndiceStats)
    S2REP: IndiceStats = Field(default_factory=IndiceStats)
    IRECI: IndiceStats = Field(default_factory=IndiceStats)
    CIre: IndiceStats = Field(default_factory=IndiceStats)
    CIgreen: IndiceStats = Field(default_factory=IndiceStats)
    MCARI: IndiceStats = Field(default_factory=IndiceStats)
    # Soil-Adjusted (4)
    SAVI: IndiceStats = Field(default_factory=IndiceStats)
    OSAVI: IndiceStats = Field(default_factory=IndiceStats)
    MSAVI: IndiceStats = Field(default_factory=IndiceStats)
    TSAVI: IndiceStats = Field(default_factory=IndiceStats)
    # Water / Moisture (6)
    NDWI: IndiceStats = Field(default_factory=IndiceStats)
    NDMI: IndiceStats = Field(default_factory=IndiceStats)
    MNDWI: IndiceStats = Field(default_factory=IndiceStats)
    MSI: IndiceStats = Field(default_factory=IndiceStats)
    LSWI: IndiceStats = Field(default_factory=IndiceStats)
    DSWI: IndiceStats = Field(default_factory=IndiceStats)
    # Canopy Structure (3)
    LAI: IndiceStats = Field(default_factory=IndiceStats)
    FAPAR: IndiceStats = Field(default_factory=IndiceStats)
    SeLI: IndiceStats = Field(default_factory=IndiceStats)
    # Pigment / Senescence (3)
    PSRI: IndiceStats = Field(default_factory=IndiceStats)
    SIPI: IndiceStats = Field(default_factory=IndiceStats)
    ARI: IndiceStats = Field(default_factory=IndiceStats)
    # Soil (2)
    BSI: IndiceStats = Field(default_factory=IndiceStats)
    BI: IndiceStats = Field(default_factory=IndiceStats)
    # Phenology (1)
    NDPI: IndiceStats = Field(default_factory=IndiceStats)


class FarmHierarchy(BaseModel):
    governorate: str | None = None
    district: str | None = None
    sub_district: str | None = None


class FieldInfoFull(BaseModel):
    id: str
    name: str
    name_ar: str | None = None
    lat: float
    lng: float
    area_ha: float | None = None
    crop_type: str | None = None
    previous_crop: str | None = None
    soil_type: str | None = None
    irrigation_type: str | None = None
    seeding_date: str | None = None
    harvest_date: str | None = None
    bbox: list[float] | None = None
    farm_hierarchy: FarmHierarchy | None = None


class SoilMoisturePayload(BaseModel):
    depth_0_1cm: float | None = None
    depth_1_3cm: float | None = None
    depth_3_9cm: float | None = None
    depth_9_27cm: float | None = None
    depth_27_81cm: float | None = None


class SoilTemperaturePayload(BaseModel):
    surface: float | None = None
    depth_6cm: float | None = None
    depth_18cm: float | None = None
    depth_54cm: float | None = None


class DailyForecast(BaseModel):
    date: str | None = None
    temp_max: float | None = None
    temp_min: float | None = None
    precipitation_sum: float | None = None
    rain_sum: float | None = None
    et0: float | None = None
    radiation_sum: float | None = None
    sunshine_duration: float | None = None
    wind_speed_max: float | None = None
    wind_gusts_max: float | None = None
    wind_direction_dominant: float | None = None
    uv_index_max: float | None = None
    precipitation_probability_max: float | None = None
    weather_code: int | None = None


class WeatherPayload(BaseModel):
    temperature: float | None = None
    feels_like: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    precipitation: float | None = None
    cloud_cover: float | None = None
    description: str = ""
    pressure: float | None = None


class MeteoPayload(BaseModel):
    """Expanded Open-Meteo data with full agriculture parameters."""
    temperature_2m: float | None = None
    relative_humidity_2m: float | None = None
    apparent_temperature: float | None = None
    precipitation: float | None = None
    wind_speed_10m: float | None = None
    wind_direction_10m: float | None = None
    wind_gusts_10m: float | None = None
    cloud_cover: float | None = None
    pressure_msl: float | None = None
    is_day: int | None = None
    # Agriculture-specific
    vapour_pressure_deficit: float | None = None
    et0_fao_evapotranspiration: float | None = None
    shortwave_radiation: float | None = None
    direct_radiation: float | None = None
    diffuse_radiation: float | None = None
    sunshine_duration: float | None = None
    # Soil data
    soil_moisture: SoilMoisturePayload | None = None
    soil_temperature: SoilTemperaturePayload | None = None
    # 7-day forecast
    forecast_7day: list[DailyForecast] = Field(default_factory=list)
    # Legacy compat
    soil_moisture_0to1cm: float | None = None


class ImageryPayload(BaseModel):
    true_color: str | None = None
    ndvi_heatmap: str | None = None
    ndmi_heatmap: str | None = None
    ndre_heatmap: str | None = None


class ComprehensiveAnalysisRequest(BaseModel):
    field: FieldInfoFull
    indices: AllIndicesPayload = Field(default_factory=AllIndicesPayload)
    imagery: ImageryPayload | None = None
    primary_indice: str = "NDVI"
    weather: WeatherPayload | None = None
    meteo: MeteoPayload | None = None
    index_count: int | None = None
    satellite_date: str | None = None
    cloud_cover_pct: float | None = None
    data_source: str | None = None
    fetched_at: str = ""


# ── Response types (unified 13-section, no tabs) ─────────────────────────────


class ActionItem(BaseModel):
    priority: str  # "critical" | "this_week" | "this_month"
    text: str


class SectionContent(BaseModel):
    """Content for one analysis section."""
    title: str           # Arabic section title
    title_en: str        # English section title
    status: str          # "good" | "moderate" | "warning" | "critical"
    status_color: str    # "green" | "yellow" | "orange" | "red"
    summary: str         # 1-2 sentence Arabic summary
    details: list[str] = Field(default_factory=list)   # Bullet points
    metrics: dict | None = None  # Key numeric values
    confidence: float = 0.7      # 0-1


class AnalysisSections(BaseModel):
    """All 13 analysis sections."""
    health_overview: SectionContent
    vegetation_health: SectionContent
    water_stress: SectionContent
    growth_stage: SectionContent
    nutrient_status: SectionContent
    pest_disease_risk: SectionContent
    irrigation_recommendation: SectionContent
    weather_impact: SectionContent
    yield_prediction: SectionContent
    soil_health: SectionContent
    historical_trends: SectionContent
    action_plan: SectionContent
    economic_impact: SectionContent


class FieldAnalysisResponse(BaseModel):
    field_id: str
    analyzed_at: str
    cached: bool = False
    # Overall health
    health_score: int = 0          # 0-100 composite
    health_class: str = "moderate"  # healthy | moderate | stressed | critical
    health_confidence: float = 0.7
    # Satellite imagery
    imagery: ImageryPayload | None = None
    # 13 Analysis Sections
    sections: AnalysisSections | None = None
    # Raw index values for charts
    indices_summary: dict = Field(default_factory=dict)
    # Metadata
    satellite_date: str | None = None
    cloud_cover_pct: float | None = None
    data_sources: list[str] = Field(default_factory=list)
    indice: str = "NDVI"
    # Backward compat (populated from action_plan section)
    current_status: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    # Legacy tier fields (kept for backward compat with existing mobile)
    farmer: dict | None = None
    specialist: dict | None = None
