# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Domain Models - Pydantic v2
# نماذج بيانات المعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Structured data models for agricultural knowledge following:
# - FRESH framework (Format, Relevance, Expiration, Sensitivity, Hierarchy)
# - FAIR principles (Findable, Accessible, Interoperable, Reusable)
# - AgriRegion pattern (geospatial metadata injection)
# - FAO AGROVOC linking (standardized terminology)
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import uuid
from datetime import date, datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeDomain(StrEnum):
    """Agricultural knowledge domains | مجالات المعرفة الزراعية"""

    CROPS = "crops"
    SOIL = "soil"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST_DISEASE = "pest_disease"
    WEATHER = "weather"
    REMOTE_SENSING = "remote_sensing"
    SMART_AGRICULTURE = "smart_agriculture"
    PRECISION_FARMING = "precision_farming"
    DIGITAL_TWIN = "digital_twin"
    GENERAL = "general"


class VerificationStatus(StrEnum):
    """Document verification status | حالة التحقق"""

    PENDING = "pending"
    APPROVED = "approved"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"


class SourceCredibilityLevel(int, Enum):
    """Source credibility levels | مستويات مصداقية المصدر"""

    COMMUNITY = 1  # مدونات/منتديات
    SPECIALIZED_WEBSITE = 2  # مواقع متخصصة
    LOCAL_RESEARCH = 3  # مراكز بحثية محلية
    GOVERNMENT_UNIVERSITY = 4  # وزارات/جامعات
    INTERNATIONAL_ORGANIZATION = 5  # FAO, ICARDA, WHO


class HierarchyLevel(StrEnum):
    """Content hierarchy level | مستوى التسلسل الهرمي"""

    OVERVIEW = "overview"  # نظرة عامة
    DETAILED = "detailed"  # تفصيلي
    EXPERT = "expert"  # متخصص


class Sensitivity(StrEnum):
    """Data sensitivity level | مستوى حساسية البيانات"""

    PUBLIC = "public"
    INTERNAL = "internal"
    RESTRICTED = "restricted"


# ─────────────────────────────────────────────────────────────────────────────
# Core Metadata Models (FRESH + FAIR + AgriRegion)
# ─────────────────────────────────────────────────────────────────────────────


class SeasonalRelevance(StrEnum):
    """Seasonal relevance for time-sensitive advice (AgriSaathi pattern).
    ملاءمة موسمية للنصائح الحساسة للوقت"""

    ALL_YEAR = "all_year"
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    PLANTING = "planting"
    GROWING = "growing"
    HARVEST = "harvest"


class FRESHMetadata(BaseModel):
    """FRESH framework metadata for knowledge organization.
    إطار FRESH لتنظيم بيانات قاعدة المعرفة"""

    format: str = "md"
    relevance_domains: list[KnowledgeDomain] = Field(default_factory=list)
    expiration_date: date | None = None
    sensitivity: Sensitivity = Sensitivity.PUBLIC
    hierarchy_level: HierarchyLevel = HierarchyLevel.DETAILED
    seasonal_relevance: SeasonalRelevance = SeasonalRelevance.ALL_YEAR


class GeospatialMetadata(BaseModel):
    """AgriRegion-style geospatial metadata for region-aware RAG.
    بيانات جغرافية وصفية على نمط AgriRegion"""

    applicable_regions: list[str] = Field(default_factory=list)
    climate_zones: list[str] = Field(default_factory=list)
    altitude_range_m: tuple[int, int] | None = None
    latitude_range: tuple[float, float] | None = None
    soil_types: list[str] = Field(default_factory=list)


class KnowledgeSourceMeta(BaseModel):
    """Metadata about the knowledge source with credibility scoring.
    بيانات المصدر مع تقييم المصداقية"""

    source_name: str = ""
    source_name_ar: str = ""
    source_url: str = ""
    credibility: SourceCredibilityLevel = SourceCredibilityLevel.SPECIALIZED_WEBSITE
    publication_date: date | None = None
    author: str = ""
    language: str = "both"
    agrovoc_concepts: list[str] = Field(default_factory=list)
    research_paper_id: str = ""
    doi: str = ""
    citation: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Domain Knowledge Document Models
# ─────────────────────────────────────────────────────────────────────────────


class BaseKnowledgeDocument(BaseModel):
    """Base class for all agricultural knowledge documents.
    فئة أساسية لجميع وثائق المعرفة الزراعية"""

    id: str = Field(default_factory=lambda: f"kb_{uuid.uuid4().hex[:12]}")
    title: str
    title_ar: str = ""
    content: str = ""
    content_ar: str = ""
    domain: KnowledgeDomain
    tags: list[str] = Field(default_factory=list)
    fresh: FRESHMetadata = Field(default_factory=FRESHMetadata)
    geospatial: GeospatialMetadata = Field(default_factory=GeospatialMetadata)
    source: KnowledgeSourceMeta = Field(default_factory=KnowledgeSourceMeta)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

    def to_knowledge_document(self) -> dict[str, Any]:
        """Convert to UltraRAG KnowledgeDocument-compatible dict.
        تحويل لتنسيق متوافق مع UltraRAG KnowledgeDocument"""
        return {
            "id": self.id,
            "title": self.title,
            "title_ar": self.title_ar,
            "content": self.content,
            "content_ar": self.content_ar,
            "source": self.source.source_url or self.source.source_name,
            "collection": self._get_collection(),
            "metadata": {
                "domain": self.domain.value,
                "tags": self.tags,
                "fresh": self.fresh.model_dump(),
                "geospatial": self.geospatial.model_dump(),
                "source_credibility": self.source.credibility.value,
                "agrovoc_concepts": self.source.agrovoc_concepts,
                "verification_status": self.verification_status.value,
                "version": self.version,
            },
        }

    def _get_collection(self) -> str:
        """Map domain to collection name."""
        from .collections import (
            CROP_KNOWLEDGE,
            FERTILIZER_KNOWLEDGE,
            GENERAL_AGRICULTURE,
            IRRIGATION_PRACTICES,
            PEST_KNOWLEDGE,
            REMOTE_SENSING_KNOWLEDGE,
            SOIL_KNOWLEDGE,
            WEATHER_KNOWLEDGE,
        )

        from .collections import SMART_AGRICULTURE_KNOWLEDGE

        domain_map = {
            KnowledgeDomain.CROPS: CROP_KNOWLEDGE,
            KnowledgeDomain.SOIL: SOIL_KNOWLEDGE,
            KnowledgeDomain.IRRIGATION: IRRIGATION_PRACTICES,
            KnowledgeDomain.FERTILIZER: FERTILIZER_KNOWLEDGE,
            KnowledgeDomain.PEST_DISEASE: PEST_KNOWLEDGE,
            KnowledgeDomain.WEATHER: WEATHER_KNOWLEDGE,
            KnowledgeDomain.REMOTE_SENSING: REMOTE_SENSING_KNOWLEDGE,
            KnowledgeDomain.SMART_AGRICULTURE: SMART_AGRICULTURE_KNOWLEDGE,
            KnowledgeDomain.PRECISION_FARMING: SMART_AGRICULTURE_KNOWLEDGE,
            KnowledgeDomain.DIGITAL_TWIN: SMART_AGRICULTURE_KNOWLEDGE,
            KnowledgeDomain.GENERAL: GENERAL_AGRICULTURE,
        }
        return domain_map.get(self.domain, GENERAL_AGRICULTURE)


class CropKnowledgeDocument(BaseKnowledgeDocument):
    """Crop-specific knowledge document.
    وثيقة معرفة خاصة بالمحاصيل"""

    domain: KnowledgeDomain = KnowledgeDomain.CROPS
    scientific_name: str = ""
    family: str = ""
    family_ar: str = ""
    varieties: list[str] = Field(default_factory=list)
    growth_stages: list[dict[str, Any]] = Field(default_factory=list)
    kc_values: dict[str, float] = Field(default_factory=dict)
    optimal_temperature_c: tuple[float, float] | None = None
    critical_temperature_c: tuple[float, float] | None = None
    water_requirement_mm_season: tuple[float, float] | None = None
    soil_requirements: dict[str, Any] = Field(default_factory=dict)
    planting_season: list[str] = Field(default_factory=list)
    harvest_days: int | None = None


class SoilTypeDocument(BaseKnowledgeDocument):
    """Soil type knowledge document.
    وثيقة معرفة أنواع التربة"""

    domain: KnowledgeDomain = KnowledgeDomain.SOIL
    soil_classification: str = ""
    texture: str = ""
    texture_ar: str = ""
    ph_range: tuple[float, float] | None = None
    ec_range_ds_m: tuple[float, float] | None = None
    organic_matter_percent: tuple[float, float] | None = None
    water_holding_capacity: str = ""
    drainage_class: str = ""
    cec_meq_100g: tuple[float, float] | None = None
    bulk_density_g_cm3: tuple[float, float] | None = None
    suitable_crops: list[str] = Field(default_factory=list)
    amendments: list[str] = Field(default_factory=list)


class IrrigationKnowledgeDocument(BaseKnowledgeDocument):
    """Irrigation knowledge document.
    وثيقة معرفة الري"""

    domain: KnowledgeDomain = KnowledgeDomain.IRRIGATION
    method: str = ""
    method_ar: str = ""
    efficiency_percent: tuple[float, float] | None = None
    suitable_crops: list[str] = Field(default_factory=list)
    suitable_soil_types: list[str] = Field(default_factory=list)
    operating_pressure_bar: tuple[float, float] | None = None
    flow_rate_l_h: tuple[float, float] | None = None
    advantages: list[str] = Field(default_factory=list)
    disadvantages: list[str] = Field(default_factory=list)


class FertilizerKnowledgeDocument(BaseKnowledgeDocument):
    """Fertilizer knowledge document.
    وثيقة معرفة التسميد"""

    domain: KnowledgeDomain = KnowledgeDomain.FERTILIZER
    fertilizer_type: str = ""
    fertilizer_type_ar: str = ""
    npk_ratio: str = ""
    nutrient_content_percent: dict[str, float] = Field(default_factory=dict)
    application_rate_kg_ha: dict[str, tuple[float, float]] = Field(default_factory=dict)
    application_method: str = ""
    timing: list[str] = Field(default_factory=list)
    crop_specific_rates: dict[str, dict[str, Any]] = Field(default_factory=dict)
    safety_notes: list[str] = Field(default_factory=list)


class WeatherPatternDocument(BaseKnowledgeDocument):
    """Weather and climate knowledge document.
    وثيقة معرفة الطقس والمناخ"""

    domain: KnowledgeDomain = KnowledgeDomain.WEATHER
    climate_zone: str = ""
    climate_zone_ar: str = ""
    temperature_range_c: dict[str, tuple[float, float]] = Field(default_factory=dict)
    annual_rainfall_mm: tuple[float, float] | None = None
    humidity_range_percent: tuple[float, float] | None = None
    growing_seasons: list[str] = Field(default_factory=list)
    weather_risks: list[str] = Field(default_factory=list)
    mitigation_strategies: list[str] = Field(default_factory=list)


class RemoteSensingGuideDocument(BaseKnowledgeDocument):
    """Remote sensing guide document.
    وثيقة دليل الاستشعار عن بعد"""

    domain: KnowledgeDomain = KnowledgeDomain.REMOTE_SENSING
    index_name: str = ""
    index_name_ar: str = ""
    formula: str = ""
    value_range: tuple[float, float] | None = None
    interpretation_guide: dict[str, str] = Field(default_factory=dict)
    interpretation_guide_ar: dict[str, str] = Field(default_factory=dict)
    data_source: str = ""
    spatial_resolution_m: float | None = None
    temporal_resolution_days: int | None = None
    use_cases: list[str] = Field(default_factory=list)


class SmartAgricultureDocument(BaseKnowledgeDocument):
    """Smart agriculture and precision farming knowledge.
    وثيقة الزراعة الذكية والزراعة الدقيقة

    Covers: IoT, drones, digital twins, AI/ML models, edge computing,
    blockchain traceability, and market intelligence.
    Based on: AGRARIAN (MDPI 2025), China Smart Agriculture Plan 2024-2028"""

    domain: KnowledgeDomain = KnowledgeDomain.SMART_AGRICULTURE
    technology_type: str = ""  # iot, drone, digital_twin, ai_model, blockchain, edge
    technology_type_ar: str = ""
    deployment_scale: str = ""  # field, farm, region, national
    connectivity_requirement: str = ""  # offline, low, moderate, high
    hardware_requirements: list[str] = Field(default_factory=list)
    integration_protocols: list[str] = Field(default_factory=list)  # MQTT, NATS, REST, etc.
    roi_metrics: dict[str, Any] = Field(default_factory=dict)
    case_studies: list[dict[str, str]] = Field(default_factory=list)


class PestVisionDocument(BaseKnowledgeDocument):
    """Computer vision pest/disease detection knowledge.
    وثيقة الرؤية الحاسوبية لكشف الآفات والأمراض

    Based on: RS-YOLO (96.6% mAP), RDW-YOLO, SerpensGate-YOLOv8,
    YOLO26 vision service detection classes."""

    domain: KnowledgeDomain = KnowledgeDomain.PEST_DISEASE
    detection_model: str = ""  # yolo26, rs-yolo, rdw-yolo
    target_classes: list[str] = Field(default_factory=list)
    target_classes_ar: list[str] = Field(default_factory=list)
    map_score: float | None = None  # mAP@0.5
    inference_device: str = ""  # gpu, cpu, edge
    image_size_px: int = 640
    min_confidence: float = 0.25
    treatment_recommendations: dict[str, str] = Field(default_factory=dict)
    treatment_recommendations_ar: dict[str, str] = Field(default_factory=dict)
    economic_impact: dict[str, Any] = Field(default_factory=dict)
