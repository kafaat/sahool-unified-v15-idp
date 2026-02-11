# ===============================================================================
# GEERAGProvider - Google Earth Engine & Satellite Imagery Integration
# مزود RAG للأقمار الصناعية - تكامل صور الأقمار الصناعية
#
# Integrates UltraRAG with Tri-RAG for satellite imagery analysis:
# - NDVI time series analysis | تحليل السلاسل الزمنية لـ NDVI
# - Change detection | كشف التغيرات
# - Land cover classification | تصنيف الغطاء الأرضي
# - Vegetation indices | مؤشرات الغطاء النباتي
#
# Based on research: "GEE Toolkit for Visual Interpretation and Land Cover Analysis"
# ===============================================================================

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import StrEnum
from typing import Any

import structlog

from ..mcp_tools import RAGMCPTools
from ..models import (
    EntityType,
    RelationType,
    RetrievalStrategy,
    TriRAGConfig,
)
from ..retriever import (
    DenseRetriever,
    KnowledgeGraphRetriever,
    RetrievalConfig,
    SparseRetriever,
    TriRAGRetriever,
)

logger = structlog.get_logger(__name__)


# ===============================================================================
# Enums - التعدادات
# ===============================================================================


class SatelliteSource(StrEnum):
    """مصادر الأقمار الصناعية - Satellite data sources"""

    SENTINEL_2 = "sentinel_2"
    LANDSAT_8 = "landsat_8"
    LANDSAT_9 = "landsat_9"
    MODIS = "modis"
    VIIRS = "viirs"


class VegetationIndex(StrEnum):
    """مؤشرات الغطاء النباتي - Vegetation indices"""

    NDVI = "ndvi"  # Normalized Difference Vegetation Index
    EVI = "evi"  # Enhanced Vegetation Index
    SAVI = "savi"  # Soil Adjusted Vegetation Index
    NDWI = "ndwi"  # Normalized Difference Water Index
    NDMI = "ndmi"  # Normalized Difference Moisture Index
    LAI = "lai"  # Leaf Area Index
    GNDVI = "gndvi"  # Green NDVI
    MSAVI = "msavi"  # Modified SAVI


class LandCoverClass(StrEnum):
    """فئات الغطاء الأرضي - Land cover classes"""

    CROPLAND = "cropland"  # أرض زراعية
    FOREST = "forest"  # غابة
    GRASSLAND = "grassland"  # مراعي
    BARE_SOIL = "bare_soil"  # تربة عارية
    URBAN = "urban"  # حضري
    WATER = "water"  # ماء
    WETLAND = "wetland"  # أرض رطبة
    DESERT = "desert"  # صحراء


class ChangeType(StrEnum):
    """أنواع التغيرات - Types of changes"""

    VEGETATION_INCREASE = "vegetation_increase"
    VEGETATION_DECREASE = "vegetation_decrease"
    WATER_STRESS = "water_stress"
    HARVEST = "harvest"
    PLANTING = "planting"
    DROUGHT = "drought"
    FLOODING = "flooding"
    LAND_CLEARING = "land_clearing"


class AnalysisType(StrEnum):
    """أنواع التحليل - Analysis types"""

    TIME_SERIES = "time_series"
    CHANGE_DETECTION = "change_detection"
    LAND_COVER = "land_cover"
    PHENOLOGY = "phenology"
    ANOMALY = "anomaly"


# ===============================================================================
# Data Models - نماذج البيانات
# ===============================================================================


@dataclass
class GEEQueryContext:
    """سياق استعلام صور الأقمار الصناعية"""

    field_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    bbox: tuple[float, float, float, float] | None = None  # minx, miny, maxx, maxy
    start_date: date | None = None
    end_date: date | None = None
    satellite: SatelliteSource = SatelliteSource.SENTINEL_2
    indices: list[VegetationIndex] = field(default_factory=lambda: [VegetationIndex.NDVI])
    cloud_cover_max: float = 30.0
    tenant_id: str | None = None
    language: str = "both"  # en, ar, both


@dataclass
class TimeSeriesPoint:
    """نقطة في السلسلة الزمنية"""

    date: date
    value: float
    index_type: VegetationIndex
    quality: float = 1.0
    cloud_cover: float = 0.0
    satellite: SatelliteSource = SatelliteSource.SENTINEL_2

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "value": round(self.value, 4),
            "index_type": self.index_type.value,
            "quality": round(self.quality, 2),
            "cloud_cover": round(self.cloud_cover, 1),
            "satellite": self.satellite.value,
        }


@dataclass
class TimeSeriesAnalysis:
    """نتيجة تحليل السلسلة الزمنية"""

    field_id: str
    index_type: VegetationIndex
    start_date: date
    end_date: date
    data_points: list[TimeSeriesPoint]
    mean: float
    std: float
    min_value: float
    max_value: float
    trend_slope: float
    trend_direction: str  # increasing, decreasing, stable
    anomalies: list[dict[str, Any]]
    phenology: dict[str, Any] | None = None
    description_ar: str = ""
    description_en: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "index_type": self.index_type.value,
            "period": {
                "start_date": self.start_date.isoformat(),
                "end_date": self.end_date.isoformat(),
            },
            "statistics": {
                "mean": round(self.mean, 4),
                "std": round(self.std, 4),
                "min": round(self.min_value, 4),
                "max": round(self.max_value, 4),
            },
            "trend": {
                "slope": round(self.trend_slope, 6),
                "direction": self.trend_direction,
            },
            "data_points": [p.to_dict() for p in self.data_points],
            "anomalies": self.anomalies,
            "phenology": self.phenology,
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


@dataclass
class ChangeDetectionResult:
    """نتيجة كشف التغيرات"""

    field_id: str
    date1: date
    date2: date
    change_type: ChangeType
    ndvi_before: float
    ndvi_after: float
    change_magnitude: float
    change_percent: float
    severity: str  # low, medium, high, critical
    confidence: float
    affected_area_ha: float | None = None
    description_ar: str = ""
    description_en: str = ""
    recommendation_ar: str = ""
    recommendation_en: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "period": {
                "date1": self.date1.isoformat(),
                "date2": self.date2.isoformat(),
            },
            "change_type": self.change_type.value,
            "ndvi": {
                "before": round(self.ndvi_before, 4),
                "after": round(self.ndvi_after, 4),
                "change": round(self.change_magnitude, 4),
                "change_percent": round(self.change_percent, 1),
            },
            "severity": self.severity,
            "confidence": round(self.confidence, 2),
            "affected_area_ha": self.affected_area_ha,
            "description_ar": self.description_ar,
            "description_en": self.description_en,
            "recommendation_ar": self.recommendation_ar,
            "recommendation_en": self.recommendation_en,
        }


@dataclass
class LandCoverResult:
    """نتيجة تصنيف الغطاء الأرضي"""

    field_id: str
    analysis_date: date
    classification: dict[LandCoverClass, float]  # Class -> percentage
    dominant_class: LandCoverClass
    vegetation_fraction: float
    bare_soil_fraction: float
    water_fraction: float
    confidence: float
    description_ar: str = ""
    description_en: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "field_id": self.field_id,
            "analysis_date": self.analysis_date.isoformat(),
            "classification": {k.value: round(v, 2) for k, v in self.classification.items()},
            "dominant_class": self.dominant_class.value,
            "fractions": {
                "vegetation": round(self.vegetation_fraction, 2),
                "bare_soil": round(self.bare_soil_fraction, 2),
                "water": round(self.water_fraction, 2),
            },
            "confidence": round(self.confidence, 2),
            "description_ar": self.description_ar,
            "description_en": self.description_en,
        }


@dataclass
class GEEAnalysisResult:
    """نتيجة تحليل شاملة"""

    query: str
    analysis_type: AnalysisType
    time_series: TimeSeriesAnalysis | None = None
    change_detection: ChangeDetectionResult | None = None
    land_cover: LandCoverResult | None = None
    related_entities: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


# ===============================================================================
# GEERAGProvider - مزود RAG للأقمار الصناعية
# ===============================================================================


class GEERAGProvider:
    """
    Google Earth Engine RAG Provider for SAHOOL Platform
    مزود RAG للأقمار الصناعية لمنصة سهول

    Provides Tri-RAG capabilities for satellite imagery analysis
    using Knowledge Graph for satellite-index-landcover relationships.
    """

    # NDVI thresholds for classification
    NDVI_THRESHOLDS = {
        "water": -0.1,
        "bare_soil": 0.1,
        "sparse_vegetation": 0.2,
        "moderate_vegetation": 0.4,
        "dense_vegetation": 0.6,
        "very_dense": 0.8,
    }

    def __init__(
        self,
        config: TriRAGConfig | None = None,
        embedding_service: Any | None = None,
        vector_store: Any | None = None,
    ):
        self.config = config or TriRAGConfig()
        self.embedding_service = embedding_service
        self.vector_store = vector_store

        # Initialize retrievers
        self._kg_retriever = KnowledgeGraphRetriever(embedding_service)
        self._dense_retriever: DenseRetriever | None = None
        self._sparse_retriever: SparseRetriever | None = None
        self._tri_rag: TriRAGRetriever | None = None

        self._initialized = False

    async def initialize(self):
        """Initialize the provider with satellite knowledge"""
        if self._initialized:
            return

        # Initialize dense/sparse retrievers if services available
        if self.vector_store and self.embedding_service:
            self._dense_retriever = DenseRetriever(self.vector_store, self.embedding_service)
            self._sparse_retriever = SparseRetriever(self.vector_store)
        else:
            # Use mock for testing
            self._dense_retriever = _MockRetriever()
            self._sparse_retriever = _MockRetriever()

        # Create Tri-RAG retriever
        self._tri_rag = TriRAGRetriever(
            dense_retriever=self._dense_retriever,
            sparse_retriever=self._sparse_retriever,
            kg_retriever=self._kg_retriever,
            config=self.config,
        )

        # Load satellite knowledge graph
        await self._load_satellite_knowledge()

        self._initialized = True
        logger.info("gee_rag_provider_initialized")

    async def _load_satellite_knowledge(self):
        """Load satellite imagery knowledge into the knowledge graph"""

        # ===================================================================
        # Satellite Entities - كيانات الأقمار الصناعية
        # ===================================================================
        satellites = [
            {
                "id": "sat_sentinel2",
                "name": "Sentinel-2",
                "name_ar": "سنتينل-2",
                "entity_type": EntityType.SENSOR.value,
                "properties": {
                    "resolution": 10,
                    "revisit_days": 5,
                    "bands": 13,
                    "agency": "ESA",
                },
            },
            {
                "id": "sat_landsat8",
                "name": "Landsat-8",
                "name_ar": "لاندسات-8",
                "entity_type": EntityType.SENSOR.value,
                "properties": {
                    "resolution": 30,
                    "revisit_days": 16,
                    "bands": 11,
                    "agency": "NASA/USGS",
                },
            },
            {
                "id": "sat_landsat9",
                "name": "Landsat-9",
                "name_ar": "لاندسات-9",
                "entity_type": EntityType.SENSOR.value,
                "properties": {
                    "resolution": 30,
                    "revisit_days": 16,
                    "bands": 11,
                    "agency": "NASA/USGS",
                },
            },
            {
                "id": "sat_modis",
                "name": "MODIS",
                "name_ar": "موديس",
                "entity_type": EntityType.SENSOR.value,
                "properties": {
                    "resolution": 250,
                    "revisit_days": 1,
                    "bands": 36,
                    "agency": "NASA",
                },
            },
        ]

        # ===================================================================
        # Vegetation Index Entities - مؤشرات الغطاء النباتي
        # ===================================================================
        indices = [
            {
                "id": "idx_ndvi",
                "name": "NDVI",
                "name_ar": "مؤشر الغطاء النباتي الطبيعي",
                "entity_type": EntityType.INDICATOR.value,
                "properties": {
                    "formula": "(NIR - RED) / (NIR + RED)",
                    "range": [-1, 1],
                    "use": "vegetation_health",
                },
            },
            {
                "id": "idx_evi",
                "name": "EVI",
                "name_ar": "مؤشر الغطاء النباتي المحسن",
                "entity_type": EntityType.INDICATOR.value,
                "properties": {
                    "formula": "2.5 * (NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1)",
                    "range": [-1, 1],
                    "use": "vegetation_health_improved",
                },
            },
            {
                "id": "idx_savi",
                "name": "SAVI",
                "name_ar": "مؤشر الغطاء النباتي المعدل للتربة",
                "entity_type": EntityType.INDICATOR.value,
                "properties": {
                    "formula": "(NIR - RED) / (NIR + RED + L) * (1 + L)",
                    "range": [-1, 1],
                    "use": "vegetation_sparse_areas",
                },
            },
            {
                "id": "idx_ndwi",
                "name": "NDWI",
                "name_ar": "مؤشر الفرق الطبيعي للماء",
                "entity_type": EntityType.INDICATOR.value,
                "properties": {
                    "formula": "(GREEN - NIR) / (GREEN + NIR)",
                    "range": [-1, 1],
                    "use": "water_content",
                },
            },
            {
                "id": "idx_ndmi",
                "name": "NDMI",
                "name_ar": "مؤشر الرطوبة",
                "entity_type": EntityType.INDICATOR.value,
                "properties": {
                    "formula": "(NIR - SWIR) / (NIR + SWIR)",
                    "range": [-1, 1],
                    "use": "moisture_content",
                },
            },
            {
                "id": "idx_lai",
                "name": "LAI",
                "name_ar": "مؤشر مساحة الورقة",
                "entity_type": EntityType.INDICATOR.value,
                "properties": {
                    "formula": "derived_from_ndvi",
                    "range": [0, 10],
                    "use": "leaf_area",
                },
            },
        ]

        # ===================================================================
        # Land Cover Entities - كيانات الغطاء الأرضي
        # ===================================================================
        land_covers = [
            {
                "id": "lc_cropland",
                "name": "Cropland",
                "name_ar": "أرض زراعية",
                "entity_type": EntityType.LOCATION.value,
                "properties": {
                    "ndvi_range": [0.3, 0.9],
                    "seasonal": True,
                },
            },
            {
                "id": "lc_forest",
                "name": "Forest",
                "name_ar": "غابة",
                "entity_type": EntityType.LOCATION.value,
                "properties": {
                    "ndvi_range": [0.6, 0.95],
                    "seasonal": False,
                },
            },
            {
                "id": "lc_grassland",
                "name": "Grassland",
                "name_ar": "مراعي",
                "entity_type": EntityType.LOCATION.value,
                "properties": {
                    "ndvi_range": [0.2, 0.5],
                    "seasonal": True,
                },
            },
            {
                "id": "lc_bare_soil",
                "name": "Bare Soil",
                "name_ar": "تربة عارية",
                "entity_type": EntityType.LOCATION.value,
                "properties": {
                    "ndvi_range": [0.0, 0.15],
                    "seasonal": False,
                },
            },
            {
                "id": "lc_water",
                "name": "Water",
                "name_ar": "ماء",
                "entity_type": EntityType.LOCATION.value,
                "properties": {
                    "ndvi_range": [-1.0, 0.0],
                    "seasonal": False,
                },
            },
            {
                "id": "lc_desert",
                "name": "Desert",
                "name_ar": "صحراء",
                "entity_type": EntityType.LOCATION.value,
                "properties": {
                    "ndvi_range": [-0.1, 0.1],
                    "seasonal": False,
                },
            },
        ]

        # ===================================================================
        # Change Type Entities - كيانات أنواع التغيرات
        # ===================================================================
        changes = [
            {
                "id": "chg_veg_increase",
                "name": "Vegetation Increase",
                "name_ar": "زيادة الغطاء النباتي",
                "entity_type": EntityType.EVENT.value,
                "properties": {
                    "ndvi_change": ">0.1",
                    "cause": "growth_or_planting",
                },
            },
            {
                "id": "chg_veg_decrease",
                "name": "Vegetation Decrease",
                "name_ar": "انخفاض الغطاء النباتي",
                "entity_type": EntityType.EVENT.value,
                "properties": {
                    "ndvi_change": "<-0.1",
                    "cause": "harvest_or_stress",
                },
            },
            {
                "id": "chg_water_stress",
                "name": "Water Stress",
                "name_ar": "إجهاد مائي",
                "entity_type": EntityType.EVENT.value,
                "properties": {
                    "ndvi_change": "<-0.15",
                    "ndwi_change": "<-0.1",
                },
            },
            {
                "id": "chg_drought",
                "name": "Drought",
                "name_ar": "جفاف",
                "entity_type": EntityType.EVENT.value,
                "properties": {
                    "ndvi_change": "<-0.25",
                    "duration": ">30_days",
                },
            },
            {
                "id": "chg_harvest",
                "name": "Harvest",
                "name_ar": "حصاد",
                "entity_type": EntityType.EVENT.value,
                "properties": {
                    "ndvi_change": "<-0.3",
                    "initial_ndvi": ">0.5",
                },
            },
            {
                "id": "chg_planting",
                "name": "Planting",
                "name_ar": "زراعة",
                "entity_type": EntityType.EVENT.value,
                "properties": {
                    "ndvi_change": ">0.2",
                    "initial_ndvi": "<0.2",
                },
            },
        ]

        # ===================================================================
        # Analysis Method Entities - طرق التحليل
        # ===================================================================
        methods = [
            {
                "id": "meth_time_series",
                "name": "Time Series Analysis",
                "name_ar": "تحليل السلاسل الزمنية",
                "entity_type": EntityType.METHOD.value,
                "properties": {
                    "input": "ndvi_sequence",
                    "output": "trend_anomalies",
                },
            },
            {
                "id": "meth_change_detect",
                "name": "Change Detection",
                "name_ar": "كشف التغيرات",
                "entity_type": EntityType.METHOD.value,
                "properties": {
                    "input": "two_dates",
                    "output": "change_map",
                },
            },
            {
                "id": "meth_classification",
                "name": "Land Cover Classification",
                "name_ar": "تصنيف الغطاء الأرضي",
                "entity_type": EntityType.METHOD.value,
                "properties": {
                    "input": "multi_spectral",
                    "output": "land_cover_map",
                },
            },
            {
                "id": "meth_phenology",
                "name": "Phenology Detection",
                "name_ar": "كشف مراحل النمو",
                "entity_type": EntityType.METHOD.value,
                "properties": {
                    "input": "ndvi_curve",
                    "output": "growth_stages",
                },
            },
        ]

        # Add all entities
        all_entities = satellites + indices + land_covers + changes + methods
        for entity in all_entities:
            await self._kg_retriever.add_entity(entity)

        # ===================================================================
        # Relations - العلاقات
        # ===================================================================
        relations = [
            # Satellite-Index relations
            {
                "source_id": "sat_sentinel2",
                "target_id": "idx_ndvi",
                "relation_type": RelationType.PROVIDES.value,
            },
            {
                "source_id": "sat_sentinel2",
                "target_id": "idx_evi",
                "relation_type": RelationType.PROVIDES.value,
            },
            {
                "source_id": "sat_sentinel2",
                "target_id": "idx_ndwi",
                "relation_type": RelationType.PROVIDES.value,
            },
            {
                "source_id": "sat_landsat8",
                "target_id": "idx_ndvi",
                "relation_type": RelationType.PROVIDES.value,
            },
            {
                "source_id": "sat_landsat8",
                "target_id": "idx_ndmi",
                "relation_type": RelationType.PROVIDES.value,
            },
            {
                "source_id": "sat_modis",
                "target_id": "idx_ndvi",
                "relation_type": RelationType.PROVIDES.value,
            },
            # Index-LandCover relations
            {
                "source_id": "idx_ndvi",
                "target_id": "lc_cropland",
                "relation_type": RelationType.INDICATES.value,
            },
            {
                "source_id": "idx_ndvi",
                "target_id": "lc_forest",
                "relation_type": RelationType.INDICATES.value,
            },
            {
                "source_id": "idx_ndwi",
                "target_id": "lc_water",
                "relation_type": RelationType.INDICATES.value,
            },
            {
                "source_id": "idx_savi",
                "target_id": "lc_bare_soil",
                "relation_type": RelationType.INDICATES.value,
            },
            # Index-Change relations
            {
                "source_id": "idx_ndvi",
                "target_id": "chg_veg_increase",
                "relation_type": RelationType.DETECTS.value,
            },
            {
                "source_id": "idx_ndvi",
                "target_id": "chg_veg_decrease",
                "relation_type": RelationType.DETECTS.value,
            },
            {
                "source_id": "idx_ndwi",
                "target_id": "chg_water_stress",
                "relation_type": RelationType.DETECTS.value,
            },
            {
                "source_id": "idx_ndvi",
                "target_id": "chg_drought",
                "relation_type": RelationType.DETECTS.value,
            },
            {
                "source_id": "idx_ndvi",
                "target_id": "chg_harvest",
                "relation_type": RelationType.DETECTS.value,
            },
            # Method-Analysis relations
            {
                "source_id": "meth_time_series",
                "target_id": "idx_ndvi",
                "relation_type": RelationType.ANALYZES.value,
            },
            {
                "source_id": "meth_change_detect",
                "target_id": "chg_veg_decrease",
                "relation_type": RelationType.PRODUCES.value,
            },
            {
                "source_id": "meth_classification",
                "target_id": "lc_cropland",
                "relation_type": RelationType.CLASSIFIES.value,
            },
            {
                "source_id": "meth_phenology",
                "target_id": "lc_cropland",
                "relation_type": RelationType.ANALYZES.value,
            },
            # LandCover-Change relations
            {
                "source_id": "lc_cropland",
                "target_id": "chg_harvest",
                "relation_type": RelationType.EXHIBITS.value,
            },
            {
                "source_id": "lc_cropland",
                "target_id": "chg_planting",
                "relation_type": RelationType.EXHIBITS.value,
            },
            {
                "source_id": "lc_cropland",
                "target_id": "chg_water_stress",
                "relation_type": RelationType.EXHIBITS.value,
            },
        ]

        for relation in relations:
            await self._kg_retriever.add_relation(relation)

        logger.info(
            "satellite_knowledge_loaded",
            entities=len(all_entities),
            relations=len(relations),
        )

    # =========================================================================
    # Analysis Methods - طرق التحليل
    # =========================================================================

    async def analyze_time_series(
        self,
        field_id: str,
        start_date: date,
        end_date: date,
        index_type: VegetationIndex = VegetationIndex.NDVI,
        data_points: list[TimeSeriesPoint] | None = None,
        context: GEEQueryContext | None = None,
    ) -> GEEAnalysisResult:
        """
        Analyze NDVI time series for a field
        تحليل السلسلة الزمنية لـ NDVI للحقل

        Args:
            field_id: Field identifier
            start_date: Start date for analysis
            end_date: End date for analysis
            index_type: Vegetation index to analyze
            data_points: Optional pre-fetched time series data
            context: Query context

        Returns:
            GEEAnalysisResult with time series analysis
        """
        await self.initialize()

        query = f"Time series analysis for field {field_id} from {start_date} to {end_date}"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # If no data points provided, generate sample data
        if not data_points:
            data_points = self._generate_sample_timeseries(start_date, end_date, index_type)

        # Calculate statistics
        values = [p.value for p in data_points]
        if not values:
            values = [0.0]

        import statistics as stats

        mean = stats.mean(values) if values else 0.0
        std = stats.stdev(values) if len(values) > 1 else 0.0
        min_val = min(values)
        max_val = max(values)

        # Calculate trend
        trend_slope = self._calculate_trend_slope(values)
        if trend_slope > 0.001:
            trend_direction = "increasing"
        elif trend_slope < -0.001:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        # Detect anomalies
        anomalies = self._detect_anomalies(data_points)

        # Create time series analysis
        time_series = TimeSeriesAnalysis(
            field_id=field_id,
            index_type=index_type,
            start_date=start_date,
            end_date=end_date,
            data_points=data_points,
            mean=mean,
            std=std,
            min_value=min_val,
            max_value=max_val,
            trend_slope=trend_slope,
            trend_direction=trend_direction,
            anomalies=anomalies,
            description_ar=f"تحليل السلسلة الزمنية لـ {index_type.value} للحقل {field_id}",
            description_en=f"Time series analysis of {index_type.value} for field {field_id}",
        )

        return GEEAnalysisResult(
            query=query,
            analysis_type=AnalysisType.TIME_SERIES,
            time_series=time_series,
            sources=[r.to_dict() for r in results[:5]],
            confidence=0.85,
            metadata={
                "field_id": field_id,
                "index_type": index_type.value,
            },
        )

    async def detect_changes(
        self,
        field_id: str,
        date1: date,
        date2: date,
        ndvi1: float | None = None,
        ndvi2: float | None = None,
        context: GEEQueryContext | None = None,
    ) -> GEEAnalysisResult:
        """
        Detect changes between two dates
        كشف التغيرات بين تاريخين

        Args:
            field_id: Field identifier
            date1: First date
            date2: Second date
            ndvi1: NDVI value at date1
            ndvi2: NDVI value at date2
            context: Query context

        Returns:
            GEEAnalysisResult with change detection
        """
        await self.initialize()

        query = f"Change detection for field {field_id} between {date1} and {date2}"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Use provided values or generate sample
        if ndvi1 is None:
            ndvi1 = 0.65
        if ndvi2 is None:
            ndvi2 = 0.45

        change_magnitude = ndvi2 - ndvi1
        change_percent = (change_magnitude / ndvi1 * 100) if ndvi1 != 0 else 0
        days_between = (date2 - date1).days

        # Classify change type
        change_type = self._classify_change(ndvi1, ndvi2, days_between)

        # Determine severity
        severity = self._determine_severity(abs(change_percent), days_between)

        # Calculate confidence
        confidence = min(0.5 + abs(change_percent) / 60, 0.95)

        # Generate descriptions and recommendations
        desc_ar, desc_en = self._generate_change_description(
            change_type, change_magnitude, change_percent
        )
        rec_ar, rec_en = self._generate_recommendation(change_type, severity)

        change_result = ChangeDetectionResult(
            field_id=field_id,
            date1=date1,
            date2=date2,
            change_type=change_type,
            ndvi_before=ndvi1,
            ndvi_after=ndvi2,
            change_magnitude=change_magnitude,
            change_percent=change_percent,
            severity=severity,
            confidence=confidence,
            description_ar=desc_ar,
            description_en=desc_en,
            recommendation_ar=rec_ar,
            recommendation_en=rec_en,
        )

        return GEEAnalysisResult(
            query=query,
            analysis_type=AnalysisType.CHANGE_DETECTION,
            change_detection=change_result,
            sources=[r.to_dict() for r in results[:5]],
            confidence=confidence,
            metadata={
                "field_id": field_id,
                "days_between": days_between,
            },
        )

    async def classify_land_cover(
        self,
        field_id: str,
        analysis_date: date,
        ndvi: float | None = None,
        ndwi: float | None = None,
        context: GEEQueryContext | None = None,
    ) -> GEEAnalysisResult:
        """
        Classify land cover for a field
        تصنيف الغطاء الأرضي للحقل

        Args:
            field_id: Field identifier
            analysis_date: Date of analysis
            ndvi: NDVI value (optional)
            ndwi: NDWI value (optional)
            context: Query context

        Returns:
            GEEAnalysisResult with land cover classification
        """
        await self.initialize()

        query = f"Land cover classification for field {field_id} on {analysis_date}"

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Use provided values or generate sample
        if ndvi is None:
            ndvi = 0.55
        if ndwi is None:
            ndwi = 0.1

        # Classify based on NDVI/NDWI thresholds
        classification = self._classify_land_cover(ndvi, ndwi)
        dominant_class = max(classification, key=classification.get)

        # Calculate fractions
        vegetation_classes = [
            LandCoverClass.CROPLAND,
            LandCoverClass.FOREST,
            LandCoverClass.GRASSLAND,
        ]
        vegetation_fraction = sum(classification.get(c, 0) for c in vegetation_classes)
        bare_soil_fraction = classification.get(LandCoverClass.BARE_SOIL, 0) + classification.get(
            LandCoverClass.DESERT, 0
        )
        water_fraction = classification.get(LandCoverClass.WATER, 0) + classification.get(
            LandCoverClass.WETLAND, 0
        )

        land_cover = LandCoverResult(
            field_id=field_id,
            analysis_date=analysis_date,
            classification=classification,
            dominant_class=dominant_class,
            vegetation_fraction=vegetation_fraction,
            bare_soil_fraction=bare_soil_fraction,
            water_fraction=water_fraction,
            confidence=0.8,
            description_ar=f"تصنيف الغطاء الأرضي: {dominant_class.value}",
            description_en=f"Land cover classification: {dominant_class.value}",
        )

        return GEEAnalysisResult(
            query=query,
            analysis_type=AnalysisType.LAND_COVER,
            land_cover=land_cover,
            sources=[r.to_dict() for r in results[:5]],
            confidence=0.8,
            metadata={
                "field_id": field_id,
                "ndvi": ndvi,
                "ndwi": ndwi,
            },
        )

    async def general_query(
        self,
        query: str,
        context: GEEQueryContext | None = None,
    ) -> GEEAnalysisResult:
        """
        General satellite imagery query using Tri-RAG
        استعلام عام عن صور الأقمار الصناعية
        """
        await self.initialize()

        config = RetrievalConfig(
            strategy=RetrievalStrategy.TRI_RAG,
            top_k=10,
            filters={"kg_max_hops": 2},
        )

        results = await self._tri_rag.retrieve(query, config)

        # Extract related entities
        related = []
        for r in results:
            if r.chunk.metadata.get("entity_type"):
                related.append(
                    {
                        "name": r.chunk.text,
                        "type": r.chunk.metadata.get("entity_type"),
                        "score": r.score,
                    }
                )

        return GEEAnalysisResult(
            query=query,
            analysis_type=AnalysisType.TIME_SERIES,  # Default
            related_entities=related,
            sources=[r.to_dict() for r in results[:5]],
            confidence=results[0].score if results else 0.0,
            metadata={"query": query},
        )

    # =========================================================================
    # Helper Methods - دوال مساعدة
    # =========================================================================

    def _generate_sample_timeseries(
        self,
        start_date: date,
        end_date: date,
        index_type: VegetationIndex,
    ) -> list[TimeSeriesPoint]:
        """Generate sample time series data for testing"""
        import math
        import random

        points = []
        current = start_date
        day_index = 0

        while current <= end_date:
            # Sinusoidal pattern with noise
            seasonal = 0.5 + 0.25 * math.sin(2 * math.pi * day_index / 120)
            noise = random.gauss(0, 0.03)
            value = max(0, min(1, seasonal + noise))

            points.append(
                TimeSeriesPoint(
                    date=current,
                    value=value,
                    index_type=index_type,
                    quality=random.uniform(0.8, 1.0),
                    cloud_cover=random.uniform(0, 30),
                )
            )

            current += timedelta(days=8)  # ~weekly
            day_index += 8

        return points

    def _calculate_trend_slope(self, values: list[float]) -> float:
        """Calculate linear trend slope"""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))

        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, values))
        sum_x2 = sum(xi**2 for xi in x)

        denominator = n * sum_x2 - sum_x**2
        if denominator == 0:
            return 0.0

        return (n * sum_xy - sum_x * sum_y) / denominator

    def _detect_anomalies(
        self,
        data_points: list[TimeSeriesPoint],
        threshold: float = 2.0,
    ) -> list[dict[str, Any]]:
        """Detect anomalies in time series using Z-score"""
        if len(data_points) < 3:
            return []

        import statistics as stats

        values = [p.value for p in data_points]
        mean = stats.mean(values)
        std = stats.stdev(values) if len(values) > 1 else 0.01

        anomalies = []
        for i, point in enumerate(data_points):
            z_score = abs((point.value - mean) / std) if std > 0 else 0

            if z_score > threshold:
                anomalies.append(
                    {
                        "index": i,
                        "date": point.date.isoformat(),
                        "value": point.value,
                        "z_score": round(z_score, 2),
                        "deviation": round(point.value - mean, 4),
                        "type": "high" if point.value > mean else "low",
                    }
                )

        return anomalies

    def _classify_change(
        self,
        ndvi_before: float,
        ndvi_after: float,
        days_between: int,
    ) -> ChangeType:
        """Classify the type of change"""
        change = ndvi_after - ndvi_before
        abs_change = abs(change)

        # No significant change
        if abs_change < 0.1:
            return ChangeType.VEGETATION_INCREASE if change > 0 else ChangeType.VEGETATION_DECREASE

        # Harvest detection
        if ndvi_before > 0.5 and ndvi_after < 0.3 and change < -0.3:
            return ChangeType.HARVEST

        # Planting detection
        if ndvi_before < 0.25 and ndvi_after > 0.35 and change > 0.2:
            return ChangeType.PLANTING

        # Drought
        if change < -0.25 and days_between > 30:
            return ChangeType.DROUGHT

        # Water stress
        if change < -0.15:
            return ChangeType.WATER_STRESS

        # General vegetation change
        if change > 0:
            return ChangeType.VEGETATION_INCREASE
        else:
            return ChangeType.VEGETATION_DECREASE

    def _determine_severity(
        self,
        change_percent: float,
        days_between: int,
    ) -> str:
        """Determine severity of change"""
        daily_change = change_percent / max(days_between, 1)

        if change_percent > 30 or daily_change > 2.0:
            return "critical"
        elif change_percent > 20 or daily_change > 1.0:
            return "high"
        elif change_percent > 10 or daily_change > 0.5:
            return "medium"
        else:
            return "low"

    def _classify_land_cover(
        self,
        ndvi: float,
        ndwi: float,
    ) -> dict[LandCoverClass, float]:
        """Classify land cover based on spectral indices"""
        classification = {}

        # Water detection
        if ndwi > 0.3 or ndvi < -0.1:
            classification[LandCoverClass.WATER] = 0.9
            return classification

        # Bare soil / Desert (ndvi < 0.15)
        if ndvi < 0.15:
            classification[LandCoverClass.BARE_SOIL] = 0.5
            classification[LandCoverClass.DESERT] = 0.4
            return classification

        # Sparse vegetation / grassland (0.15 <= ndvi < 0.35)
        if ndvi < 0.35:
            classification[LandCoverClass.GRASSLAND] = 0.6
            classification[LandCoverClass.BARE_SOIL] = 0.3
            return classification

        # Moderate vegetation / cropland (0.35 <= ndvi < 0.6)
        if ndvi < 0.6:
            classification[LandCoverClass.CROPLAND] = 0.7
            classification[LandCoverClass.GRASSLAND] = 0.2
            return classification

        # Dense vegetation / forest (ndvi >= 0.6)
        classification[LandCoverClass.FOREST] = 0.5
        classification[LandCoverClass.CROPLAND] = 0.4
        return classification

    def _generate_change_description(
        self,
        change_type: ChangeType,
        change_magnitude: float,
        change_percent: float,
    ) -> tuple[str, str]:
        """Generate bilingual change description"""
        descriptions = {
            ChangeType.VEGETATION_INCREASE: (
                f"زيادة في الغطاء النباتي بنسبة {abs(change_percent):.1f}%",
                f"Vegetation increase of {abs(change_percent):.1f}%",
            ),
            ChangeType.VEGETATION_DECREASE: (
                f"انخفاض في الغطاء النباتي بنسبة {abs(change_percent):.1f}%",
                f"Vegetation decrease of {abs(change_percent):.1f}%",
            ),
            ChangeType.WATER_STRESS: (
                f"إجهاد مائي مكتشف - انخفاض NDVI بنسبة {abs(change_percent):.1f}%",
                f"Water stress detected - NDVI decreased by {abs(change_percent):.1f}%",
            ),
            ChangeType.HARVEST: (
                "حصاد مكتشف - انخفاض سريع في الغطاء النباتي",
                "Harvest detected - rapid vegetation decline",
            ),
            ChangeType.PLANTING: (
                "زراعة جديدة مكتشفة - زيادة في الغطاء النباتي",
                "New planting detected - vegetation increase",
            ),
            ChangeType.DROUGHT: (
                "جفاف محتمل - انخفاض حاد ومستمر",
                "Possible drought - severe and sustained decline",
            ),
        }

        return descriptions.get(
            change_type,
            (f"تغيير بنسبة {change_percent:.1f}%", f"Change of {change_percent:.1f}%"),
        )

    def _generate_recommendation(
        self,
        change_type: ChangeType,
        severity: str,
    ) -> tuple[str, str]:
        """Generate bilingual recommendation"""
        recommendations = {
            ChangeType.VEGETATION_INCREASE: (
                "استمر في الممارسات الحالية - نمو جيد",
                "Continue current practices - good growth",
            ),
            ChangeType.VEGETATION_DECREASE: (
                "تحقق من حالة الري والتسميد",
                "Check irrigation and fertilization status",
            ),
            ChangeType.WATER_STRESS: (
                "زد كمية الري فوراً",
                "Increase irrigation immediately",
            ),
            ChangeType.HARVEST: (
                "خطط للزراعة القادمة",
                "Plan for next planting",
            ),
            ChangeType.PLANTING: (
                "حافظ على رطوبة التربة للإنبات",
                "Maintain soil moisture for germination",
            ),
            ChangeType.DROUGHT: (
                "ري عاجل - خطر فقدان المحصول",
                "Urgent irrigation - crop loss risk",
            ),
        }

        return recommendations.get(
            change_type,
            ("مراقبة مستمرة موصى بها", "Continued monitoring recommended"),
        )

    def get_mcp_tools(self) -> RAGMCPTools:
        """Get MCP tools for this provider"""
        return RAGMCPTools(
            rag_pipeline=None,
            knowledge_base=None,
        )

    @property
    def knowledge_graph(self) -> KnowledgeGraphRetriever:
        """Access the knowledge graph retriever"""
        return self._kg_retriever


class _MockRetriever:
    """Mock retriever for testing without vector store"""

    async def retrieve(self, query: str, config: RetrievalConfig) -> list:
        return []

    async def add_documents(self, chunks: list, collection: str = "default") -> bool:
        return True


# Export
__all__ = [
    "GEERAGProvider",
    "GEEQueryContext",
    "GEEAnalysisResult",
    "TimeSeriesPoint",
    "TimeSeriesAnalysis",
    "ChangeDetectionResult",
    "LandCoverResult",
    "SatelliteSource",
    "VegetationIndex",
    "LandCoverClass",
    "ChangeType",
    "AnalysisType",
]
