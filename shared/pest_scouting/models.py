"""
Pest Scouting Data Models - نماذج بيانات مسح الآفات
====================================================

Data models for pest identification, scouting reports, outbreak tracking,
and treatment recommendations for Middle East agricultural pests.

Supported pests include:
- Red Palm Weevil (سوسة النخيل الحمراء)
- Dubas Bug (دوباس النخيل)
- Aphids (المن)
- Whiteflies (الذبابة البيضاء)
- Spider Mites (العنكبوت الأحمر)
- Locusts (الجراد)
- Date Moth (فراشة التمر)
- Tomato Leafminer (حافرة أنفاق الطماطم)

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any


class PestCategory(StrEnum):
    """Pest category classification | تصنيف فئة الآفة"""

    INSECT = "insect"  # حشرة
    MITE = "mite"  # عنكبوت/أكاروس
    NEMATODE = "nematode"  # نيماتودا
    FUNGAL = "fungal"  # فطري
    BACTERIAL = "bacterial"  # بكتيري
    VIRAL = "viral"  # فيروسي
    WEED = "weed"  # أعشاب ضارة
    VERTEBRATE = "vertebrate"  # فقاريات (طيور/قوارض)
    MOLLUSK = "mollusk"  # رخويات


class PestLifeStage(StrEnum):
    """Pest life stage | مرحلة حياة الآفة"""

    EGG = "egg"  # بيضة
    LARVA = "larva"  # يرقة
    NYMPH = "nymph"  # حورية
    PUPA = "pupa"  # عذراء
    ADULT = "adult"  # حشرة كاملة
    SPORE = "spore"  # بوغ (فطريات)
    MYCELIUM = "mycelium"  # غزل فطري
    ALL_STAGES = "all_stages"  # جميع المراحل


class InfestationLevel(StrEnum):
    """Infestation severity level | مستوى شدة الإصابة"""

    NONE = "none"  # لا إصابة
    TRACE = "trace"  # آثار بسيطة
    LOW = "low"  # منخفض
    MODERATE = "moderate"  # متوسط
    HIGH = "high"  # مرتفع
    SEVERE = "severe"  # شديد
    CRITICAL = "critical"  # حرج


class AlertPriority(StrEnum):
    """Alert priority levels | مستويات أولوية التنبيه"""

    CRITICAL = "critical"  # حرج - فوري <6 ساعات
    HIGH = "high"  # عالي - 24-48 ساعة
    MEDIUM = "medium"  # متوسط - أسبوع
    LOW = "low"  # منخفض - مراقبة
    INFORMATIONAL = "informational"  # معلوماتي


class ScoutingMethod(StrEnum):
    """Scouting methodology | طريقة المسح"""

    VISUAL_INSPECTION = "visual_inspection"  # فحص بصري
    TRAP_MONITORING = "trap_monitoring"  # مراقبة مصائد
    PHEROMONE_TRAP = "pheromone_trap"  # مصيدة فرمونية
    STICKY_TRAP = "sticky_trap"  # مصيدة لاصقة
    SWEEP_NET = "sweep_net"  # شبكة مسح
    BEAT_SHEET = "beat_sheet"  # ورقة الضرب
    SOIL_SAMPLING = "soil_sampling"  # أخذ عينات تربة
    LEAF_SAMPLING = "leaf_sampling"  # أخذ عينات أوراق
    ACOUSTIC_DETECTION = "acoustic_detection"  # كشف صوتي (سوسة النخيل)
    DRONE_IMAGERY = "drone_imagery"  # تصوير بطائرة مسيرة
    THERMAL_IMAGING = "thermal_imaging"  # تصوير حراري


class TreatmentType(StrEnum):
    """Treatment approach type | نوع أسلوب العلاج"""

    CHEMICAL = "chemical"  # كيميائي
    BIOLOGICAL = "biological"  # حيوي
    CULTURAL = "cultural"  # زراعي
    MECHANICAL = "mechanical"  # ميكانيكي
    PHEROMONE = "pheromone"  # فرموني
    INTEGRATED = "integrated"  # متكامل
    NO_ACTION = "no_action"  # لا إجراء


class TreatmentUrgency(StrEnum):
    """Treatment urgency level | مستوى استعجال العلاج"""

    IMMEDIATE = "immediate"  # فوري - خلال 24 ساعة
    URGENT = "urgent"  # عاجل - خلال 48 ساعة
    SOON = "soon"  # قريب - خلال أسبوع
    SCHEDULED = "scheduled"  # مجدول - حسب الجدول
    PREVENTIVE = "preventive"  # وقائي - قبل الإصابة
    MONITOR = "monitor"  # مراقبة فقط


class CropType(StrEnum):
    """Supported crop types | أنواع المحاصيل المدعومة"""

    DATE_PALM = "date_palm"  # نخيل التمر
    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    TOMATO = "tomato"  # طماطم
    CUCUMBER = "cucumber"  # خيار
    PEPPER = "pepper"  # فلفل
    EGGPLANT = "eggplant"  # باذنجان
    CITRUS = "citrus"  # حمضيات
    GRAPE = "grape"  # عنب
    OLIVE = "olive"  # زيتون
    ALFALFA = "alfalfa"  # برسيم
    ONION = "onion"  # بصل
    POTATO = "potato"  # بطاطس
    WATERMELON = "watermelon"  # بطيخ
    GENERAL = "general"  # عام


@dataclass
class PestIdentification:
    """
    Pest species identification information
    معلومات تعريف نوع الآفة
    """

    # Identification
    id: str
    scientific_name: str  # الاسم العلمي
    common_name: str  # الاسم الشائع (English)
    common_name_ar: str  # الاسم الشائع (العربية)
    local_names: list[str] = field(default_factory=list)  # أسماء محلية

    # Classification
    category: PestCategory = PestCategory.INSECT
    family: str = ""  # العائلة
    order: str = ""  # الرتبة

    # Description
    description: str = ""
    description_ar: str = ""

    # Identification features - English
    adult_description: str = ""
    larva_description: str = ""
    egg_description: str = ""
    damage_symptoms: list[str] = field(default_factory=list)

    # Identification features - Arabic
    adult_description_ar: str = ""
    larva_description_ar: str = ""
    egg_description_ar: str = ""
    damage_symptoms_ar: list[str] = field(default_factory=list)

    # Visual identification
    adult_size_mm: tuple[float, float] | None = None  # (min, max) size
    adult_color: str = ""
    adult_color_ar: str = ""
    distinguishing_features: list[str] = field(default_factory=list)
    distinguishing_features_ar: list[str] = field(default_factory=list)

    # Images for identification
    image_urls: list[str] = field(default_factory=list)

    # Host crops
    primary_hosts: list[CropType] = field(default_factory=list)
    secondary_hosts: list[CropType] = field(default_factory=list)

    # Biology
    life_cycle_days: tuple[int, int] | None = None  # (min, max) days
    generations_per_year: int | None = None
    overwintering_stage: PestLifeStage | None = None
    optimal_temperature_c: tuple[float, float] | None = None
    optimal_humidity_pct: tuple[float, float] | None = None

    # Economic importance
    is_quarantine_pest: bool = False  # آفة حجر زراعي
    economic_importance: str = ""  # low, moderate, high, very_high
    economic_importance_ar: str = ""
    potential_yield_loss_pct: tuple[float, float] | None = None

    # Geographic distribution
    distribution_regions: list[str] = field(default_factory=list)
    first_reported_saudi: str | None = None  # Year first reported in Saudi Arabia

    # Detection difficulty
    detection_difficulty: str = "moderate"  # easy, moderate, difficult
    detection_notes: str = ""
    detection_notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "scientific_name": self.scientific_name,
            "common_name": self.common_name,
            "common_name_ar": self.common_name_ar,
            "local_names": self.local_names,
            "category": self.category.value,
            "family": self.family,
            "order": self.order,
            "description": self.description,
            "description_ar": self.description_ar,
            "adult_description": self.adult_description,
            "larva_description": self.larva_description,
            "egg_description": self.egg_description,
            "damage_symptoms": self.damage_symptoms,
            "adult_description_ar": self.adult_description_ar,
            "larva_description_ar": self.larva_description_ar,
            "egg_description_ar": self.egg_description_ar,
            "damage_symptoms_ar": self.damage_symptoms_ar,
            "adult_size_mm": self.adult_size_mm,
            "adult_color": self.adult_color,
            "adult_color_ar": self.adult_color_ar,
            "distinguishing_features": self.distinguishing_features,
            "distinguishing_features_ar": self.distinguishing_features_ar,
            "image_urls": self.image_urls,
            "primary_hosts": [h.value for h in self.primary_hosts],
            "secondary_hosts": [h.value for h in self.secondary_hosts],
            "life_cycle_days": self.life_cycle_days,
            "generations_per_year": self.generations_per_year,
            "overwintering_stage": self.overwintering_stage.value if self.overwintering_stage else None,
            "optimal_temperature_c": self.optimal_temperature_c,
            "optimal_humidity_pct": self.optimal_humidity_pct,
            "is_quarantine_pest": self.is_quarantine_pest,
            "economic_importance": self.economic_importance,
            "economic_importance_ar": self.economic_importance_ar,
            "potential_yield_loss_pct": self.potential_yield_loss_pct,
            "distribution_regions": self.distribution_regions,
            "first_reported_saudi": self.first_reported_saudi,
            "detection_difficulty": self.detection_difficulty,
            "detection_notes": self.detection_notes,
            "detection_notes_ar": self.detection_notes_ar,
        }


@dataclass
class ScoutObservation:
    """
    Single pest observation during scouting
    ملاحظة آفة واحدة أثناء المسح
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pest_id: str = ""  # Reference to PestIdentification
    pest_name: str = ""
    pest_name_ar: str = ""

    # Observation details
    life_stage: PestLifeStage = PestLifeStage.ADULT
    count: int | None = None  # العدد (if countable)
    count_per_unit: float | None = None  # Count per plant/trap/sample
    unit_type: str = "per_plant"  # per_plant, per_trap, per_m2, percentage

    # Damage assessment
    damage_observed: bool = False
    damage_rating: int | None = None  # 0-10 scale
    affected_plant_parts: list[str] = field(default_factory=list)
    affected_plant_parts_ar: list[str] = field(default_factory=list)

    # Location within field
    sample_point_number: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    field_zone: str = ""  # edge, center, north, south, etc.

    # Conditions at observation
    temperature_c: float | None = None
    humidity_pct: float | None = None
    time_of_day: str = ""  # morning, midday, afternoon, evening

    # Evidence
    photo_urls: list[str] = field(default_factory=list)

    # Notes
    notes: str = ""
    notes_ar: str = ""

    # Confidence in identification
    identification_confidence: float = 0.8  # 0-1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "pest_id": self.pest_id,
            "pest_name": self.pest_name,
            "pest_name_ar": self.pest_name_ar,
            "life_stage": self.life_stage.value,
            "count": self.count,
            "count_per_unit": self.count_per_unit,
            "unit_type": self.unit_type,
            "damage_observed": self.damage_observed,
            "damage_rating": self.damage_rating,
            "affected_plant_parts": self.affected_plant_parts,
            "affected_plant_parts_ar": self.affected_plant_parts_ar,
            "sample_point_number": self.sample_point_number,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "field_zone": self.field_zone,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "time_of_day": self.time_of_day,
            "photo_urls": self.photo_urls,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
            "identification_confidence": self.identification_confidence,
        }


@dataclass
class ScoutReport:
    """
    Complete scouting report for a field
    تقرير مسح كامل للحقل
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    farm_id: str = ""
    field_id: str = ""

    # Crop information
    crop_type: CropType = CropType.GENERAL
    crop_variety: str = ""
    growth_stage: str = ""
    growth_stage_ar: str = ""
    planting_date: date | None = None

    # Scouting details
    scout_date: date = field(default_factory=date.today)
    scout_time: str = ""  # HH:MM
    scout_id: str = ""  # Scout/agronomist ID
    scout_name: str = ""
    scouting_method: ScoutingMethod = ScoutingMethod.VISUAL_INSPECTION

    # Sampling details
    field_area_ha: float = 0.0
    sample_points: int = 0  # Number of sample points
    plants_examined: int = 0
    traps_checked: int = 0

    # Observations
    observations: list[ScoutObservation] = field(default_factory=list)

    # Overall assessment
    overall_infestation: InfestationLevel = InfestationLevel.NONE
    primary_pest_id: str | None = None  # Most significant pest found
    primary_pest_name: str = ""
    primary_pest_name_ar: str = ""

    # Weather conditions
    temperature_c: float | None = None
    humidity_pct: float | None = None
    wind_speed_kmh: float | None = None
    recent_rainfall_mm: float | None = None

    # Recommendations summary
    action_required: bool = False
    recommended_action: str = ""
    recommended_action_ar: str = ""
    urgency: TreatmentUrgency = TreatmentUrgency.MONITOR

    # General field observations
    crop_health_rating: int | None = None  # 1-10
    weed_pressure: str = ""  # none, low, moderate, high
    irrigation_status: str = ""
    other_observations: str = ""
    other_observations_ar: str = ""

    # Report status
    status: str = "draft"  # draft, submitted, reviewed, archived
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "crop_type": self.crop_type.value,
            "crop_variety": self.crop_variety,
            "growth_stage": self.growth_stage,
            "growth_stage_ar": self.growth_stage_ar,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "scout_date": self.scout_date.isoformat(),
            "scout_time": self.scout_time,
            "scout_id": self.scout_id,
            "scout_name": self.scout_name,
            "scouting_method": self.scouting_method.value,
            "field_area_ha": self.field_area_ha,
            "sample_points": self.sample_points,
            "plants_examined": self.plants_examined,
            "traps_checked": self.traps_checked,
            "observations": [obs.to_dict() for obs in self.observations],
            "overall_infestation": self.overall_infestation.value,
            "primary_pest_id": self.primary_pest_id,
            "primary_pest_name": self.primary_pest_name,
            "primary_pest_name_ar": self.primary_pest_name_ar,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "wind_speed_kmh": self.wind_speed_kmh,
            "recent_rainfall_mm": self.recent_rainfall_mm,
            "action_required": self.action_required,
            "recommended_action": self.recommended_action,
            "recommended_action_ar": self.recommended_action_ar,
            "urgency": self.urgency.value,
            "crop_health_rating": self.crop_health_rating,
            "weed_pressure": self.weed_pressure,
            "irrigation_status": self.irrigation_status,
            "other_observations": self.other_observations,
            "other_observations_ar": self.other_observations_ar,
            "status": self.status,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def get_pest_summary(self) -> dict[str, Any]:
        """Get summary of pests found"""
        pest_counts: dict[str, int] = {}
        for obs in self.observations:
            key = obs.pest_id or obs.pest_name
            if key:
                pest_counts[key] = pest_counts.get(key, 0) + 1
        return {
            "total_observations": len(self.observations),
            "unique_pests": len(pest_counts),
            "pest_counts": pest_counts,
        }


@dataclass
class PestAlert:
    """
    Pest alert notification
    تنبيه آفة
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str = "threshold_exceeded"  # threshold_exceeded, new_detection, outbreak, quarantine

    # Priority
    priority: AlertPriority = AlertPriority.MEDIUM

    # Location
    tenant_id: str = ""
    farm_id: str = ""
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str = ""

    # Pest information
    pest_id: str = ""
    pest_name: str = ""
    pest_name_ar: str = ""
    pest_category: PestCategory = PestCategory.INSECT

    # Alert details - English
    title: str = ""
    description: str = ""
    impact: str = ""
    recommended_actions: list[str] = field(default_factory=list)

    # Alert details - Arabic
    title_ar: str = ""
    description_ar: str = ""
    impact_ar: str = ""
    recommended_actions_ar: list[str] = field(default_factory=list)

    # Threshold information
    current_value: float | None = None
    threshold_value: float | None = None
    threshold_unit: str = ""  # per_plant, per_trap, percentage

    # Economic impact
    potential_loss_min: float | None = None
    potential_loss_max: float | None = None
    currency: str = "SAR"

    # Crop information
    crop_type: CropType = CropType.GENERAL
    growth_stage: str = ""
    area_affected_ha: float | None = None

    # Time
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    response_deadline: datetime | None = None

    # Status
    is_active: bool = True
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution_notes: str = ""

    # Related
    scout_report_id: str | None = None
    treatment_recommendation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "alert_type": self.alert_type,
            "priority": self.priority.value,
            "tenant_id": self.tenant_id,
            "farm_id": self.farm_id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "pest_id": self.pest_id,
            "pest_name": self.pest_name,
            "pest_name_ar": self.pest_name_ar,
            "pest_category": self.pest_category.value,
            "title": self.title,
            "description": self.description,
            "impact": self.impact,
            "recommended_actions": self.recommended_actions,
            "title_ar": self.title_ar,
            "description_ar": self.description_ar,
            "impact_ar": self.impact_ar,
            "recommended_actions_ar": self.recommended_actions_ar,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "threshold_unit": self.threshold_unit,
            "potential_loss_min": self.potential_loss_min,
            "potential_loss_max": self.potential_loss_max,
            "currency": self.currency,
            "crop_type": self.crop_type.value,
            "growth_stage": self.growth_stage,
            "area_affected_ha": self.area_affected_ha,
            "detected_at": self.detected_at.isoformat(),
            "response_deadline": self.response_deadline.isoformat() if self.response_deadline else None,
            "is_active": self.is_active,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "scout_report_id": self.scout_report_id,
            "treatment_recommendation_id": self.treatment_recommendation_id,
        }

    def get_priority_icon(self) -> str:
        """Get priority icon for display"""
        icons = {
            AlertPriority.CRITICAL: "[!!!]",
            AlertPriority.HIGH: "[!!]",
            AlertPriority.MEDIUM: "[!]",
            AlertPriority.LOW: "[.]",
            AlertPriority.INFORMATIONAL: "[i]",
        }
        return icons.get(self.priority, "[.]")


@dataclass
class OutbreakRecord:
    """
    Historical outbreak record for tracking and analysis
    سجل تفشي تاريخي للتتبع والتحليل
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""

    # Pest information
    pest_id: str = ""
    pest_name: str = ""
    pest_name_ar: str = ""
    pest_category: PestCategory = PestCategory.INSECT

    # Location
    region: str = ""  # Geographic region
    region_ar: str = ""
    farm_ids: list[str] = field(default_factory=list)
    field_ids: list[str] = field(default_factory=list)

    # Crop
    affected_crops: list[CropType] = field(default_factory=list)
    primary_crop: CropType = CropType.GENERAL

    # Timeline
    first_detection_date: date | None = None
    peak_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = None

    # Severity
    peak_infestation_level: InfestationLevel = InfestationLevel.MODERATE
    total_area_affected_ha: float = 0.0
    peak_population_density: float | None = None
    population_unit: str = ""

    # Impact
    estimated_yield_loss_pct: float | None = None
    estimated_economic_loss: float | None = None
    currency: str = "SAR"
    quality_impact: str = ""  # none, minor, moderate, severe
    quality_impact_ar: str = ""

    # Response
    treatments_applied: list[str] = field(default_factory=list)
    treatments_applied_ar: list[str] = field(default_factory=list)
    treatment_effectiveness: str = ""  # poor, moderate, good, excellent
    treatment_effectiveness_ar: str = ""
    total_treatment_cost: float | None = None

    # Contributing factors
    weather_conditions: str = ""
    weather_conditions_ar: str = ""
    contributing_factors: list[str] = field(default_factory=list)
    contributing_factors_ar: list[str] = field(default_factory=list)

    # Lessons learned
    lessons_learned: list[str] = field(default_factory=list)
    lessons_learned_ar: list[str] = field(default_factory=list)
    recommendations_for_future: list[str] = field(default_factory=list)
    recommendations_for_future_ar: list[str] = field(default_factory=list)

    # Documentation
    report_urls: list[str] = field(default_factory=list)
    photo_urls: list[str] = field(default_factory=list)

    # Season pattern
    season: str = ""  # spring, summer, fall, winter
    year: int = 0
    is_recurring: bool = False
    previous_outbreak_ids: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    verified: bool = False
    verified_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "pest_id": self.pest_id,
            "pest_name": self.pest_name,
            "pest_name_ar": self.pest_name_ar,
            "pest_category": self.pest_category.value,
            "region": self.region,
            "region_ar": self.region_ar,
            "farm_ids": self.farm_ids,
            "field_ids": self.field_ids,
            "affected_crops": [c.value for c in self.affected_crops],
            "primary_crop": self.primary_crop.value,
            "first_detection_date": self.first_detection_date.isoformat() if self.first_detection_date else None,
            "peak_date": self.peak_date.isoformat() if self.peak_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_days": self.duration_days,
            "peak_infestation_level": self.peak_infestation_level.value,
            "total_area_affected_ha": self.total_area_affected_ha,
            "peak_population_density": self.peak_population_density,
            "population_unit": self.population_unit,
            "estimated_yield_loss_pct": self.estimated_yield_loss_pct,
            "estimated_economic_loss": self.estimated_economic_loss,
            "currency": self.currency,
            "quality_impact": self.quality_impact,
            "quality_impact_ar": self.quality_impact_ar,
            "treatments_applied": self.treatments_applied,
            "treatments_applied_ar": self.treatments_applied_ar,
            "treatment_effectiveness": self.treatment_effectiveness,
            "treatment_effectiveness_ar": self.treatment_effectiveness_ar,
            "total_treatment_cost": self.total_treatment_cost,
            "weather_conditions": self.weather_conditions,
            "weather_conditions_ar": self.weather_conditions_ar,
            "contributing_factors": self.contributing_factors,
            "contributing_factors_ar": self.contributing_factors_ar,
            "lessons_learned": self.lessons_learned,
            "lessons_learned_ar": self.lessons_learned_ar,
            "recommendations_for_future": self.recommendations_for_future,
            "recommendations_for_future_ar": self.recommendations_for_future_ar,
            "report_urls": self.report_urls,
            "photo_urls": self.photo_urls,
            "season": self.season,
            "year": self.year,
            "is_recurring": self.is_recurring,
            "previous_outbreak_ids": self.previous_outbreak_ids,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "verified": self.verified,
            "verified_by": self.verified_by,
        }


@dataclass
class TreatmentRecommendation:
    """
    Treatment recommendation for pest control
    توصية علاج لمكافحة الآفة
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = ""
    scout_report_id: str | None = None
    alert_id: str | None = None

    # Target
    pest_id: str = ""
    pest_name: str = ""
    pest_name_ar: str = ""
    target_life_stages: list[PestLifeStage] = field(default_factory=list)

    # Field information
    field_id: str = ""
    crop_type: CropType = CropType.GENERAL
    growth_stage: str = ""
    area_to_treat_ha: float = 0.0

    # Treatment type
    treatment_type: TreatmentType = TreatmentType.CHEMICAL
    urgency: TreatmentUrgency = TreatmentUrgency.SCHEDULED

    # Primary recommendation - English
    recommendation_title: str = ""
    recommendation_details: str = ""
    application_method: str = ""
    application_timing: str = ""
    precautions: list[str] = field(default_factory=list)

    # Primary recommendation - Arabic
    recommendation_title_ar: str = ""
    recommendation_details_ar: str = ""
    application_method_ar: str = ""
    application_timing_ar: str = ""
    precautions_ar: list[str] = field(default_factory=list)

    # Chemical options (if applicable)
    chemical_options: list[dict[str, Any]] = field(default_factory=list)
    # Each dict: {product_name, product_name_ar, active_ingredient, rate, rate_unit, phi_days, rei_hours}

    # Biological options
    biological_options: list[dict[str, Any]] = field(default_factory=list)
    # Each dict: {agent_name, agent_name_ar, type, application_rate, notes}

    # Cultural practices
    cultural_practices: list[str] = field(default_factory=list)
    cultural_practices_ar: list[str] = field(default_factory=list)

    # Economic analysis
    estimated_cost_per_ha: float | None = None
    estimated_total_cost: float | None = None
    expected_efficacy_pct: float | None = None
    expected_yield_saved_pct: float | None = None
    roi_estimate: float | None = None
    currency: str = "SAR"

    # Timing
    optimal_window_start: datetime | None = None
    optimal_window_end: datetime | None = None
    weather_requirements: str = ""
    weather_requirements_ar: str = ""

    # Follow-up
    follow_up_scouting_days: int | None = None
    retreatment_interval_days: int | None = None
    max_applications: int | None = None

    # Alternative actions
    if_threshold_not_met: str = ""
    if_threshold_not_met_ar: str = ""

    # Status
    status: str = "pending"  # pending, approved, rejected, implemented, completed
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    approved_by: str | None = None
    approved_at: datetime | None = None

    # Outcome (after implementation)
    outcome_efficacy: str | None = None  # poor, moderate, good, excellent
    outcome_notes: str = ""
    outcome_notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "scout_report_id": self.scout_report_id,
            "alert_id": self.alert_id,
            "pest_id": self.pest_id,
            "pest_name": self.pest_name,
            "pest_name_ar": self.pest_name_ar,
            "target_life_stages": [s.value for s in self.target_life_stages],
            "field_id": self.field_id,
            "crop_type": self.crop_type.value,
            "growth_stage": self.growth_stage,
            "area_to_treat_ha": self.area_to_treat_ha,
            "treatment_type": self.treatment_type.value,
            "urgency": self.urgency.value,
            "recommendation_title": self.recommendation_title,
            "recommendation_details": self.recommendation_details,
            "application_method": self.application_method,
            "application_timing": self.application_timing,
            "precautions": self.precautions,
            "recommendation_title_ar": self.recommendation_title_ar,
            "recommendation_details_ar": self.recommendation_details_ar,
            "application_method_ar": self.application_method_ar,
            "application_timing_ar": self.application_timing_ar,
            "precautions_ar": self.precautions_ar,
            "chemical_options": self.chemical_options,
            "biological_options": self.biological_options,
            "cultural_practices": self.cultural_practices,
            "cultural_practices_ar": self.cultural_practices_ar,
            "estimated_cost_per_ha": self.estimated_cost_per_ha,
            "estimated_total_cost": self.estimated_total_cost,
            "expected_efficacy_pct": self.expected_efficacy_pct,
            "expected_yield_saved_pct": self.expected_yield_saved_pct,
            "roi_estimate": self.roi_estimate,
            "currency": self.currency,
            "optimal_window_start": self.optimal_window_start.isoformat() if self.optimal_window_start else None,
            "optimal_window_end": self.optimal_window_end.isoformat() if self.optimal_window_end else None,
            "weather_requirements": self.weather_requirements,
            "weather_requirements_ar": self.weather_requirements_ar,
            "follow_up_scouting_days": self.follow_up_scouting_days,
            "retreatment_interval_days": self.retreatment_interval_days,
            "max_applications": self.max_applications,
            "if_threshold_not_met": self.if_threshold_not_met,
            "if_threshold_not_met_ar": self.if_threshold_not_met_ar,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "outcome_efficacy": self.outcome_efficacy,
            "outcome_notes": self.outcome_notes,
            "outcome_notes_ar": self.outcome_notes_ar,
        }


@dataclass
class EconomicThreshold:
    """
    Economic/action threshold for a pest
    العتبة الاقتصادية/عتبة التدخل للآفة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pest_id: str = ""
    pest_name: str = ""
    pest_name_ar: str = ""

    # Crop context
    crop_type: CropType = CropType.GENERAL
    growth_stages: list[str] = field(default_factory=list)  # Applicable growth stages

    # Threshold values
    action_threshold: float = 0.0  # When to take action
    economic_threshold: float = 0.0  # When economic damage begins
    threshold_unit: str = ""  # per_plant, per_trap, per_m2, percentage

    # Threshold description - English
    threshold_description: str = ""
    sampling_method: str = ""
    sampling_frequency: str = ""

    # Threshold description - Arabic
    threshold_description_ar: str = ""
    sampling_method_ar: str = ""
    sampling_frequency_ar: str = ""

    # Modifiers
    temperature_modifier: dict[str, float] = field(default_factory=dict)
    # e.g., {"hot": 0.8, "cool": 1.2} - lower threshold in hot weather

    growth_stage_modifier: dict[str, float] = field(default_factory=dict)
    # e.g., {"flowering": 0.7, "vegetative": 1.0} - more sensitive during flowering

    # Economic factors
    treatment_cost_per_ha: float = 0.0
    crop_value_per_ha: float = 0.0
    expected_loss_per_pest_unit: float = 0.0
    currency: str = "SAR"

    # Source
    source: str = ""  # Research institution, extension service
    source_ar: str = ""
    reference_year: int | None = None
    region_specific: str = ""  # If threshold is region-specific

    # Notes
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "pest_id": self.pest_id,
            "pest_name": self.pest_name,
            "pest_name_ar": self.pest_name_ar,
            "crop_type": self.crop_type.value,
            "growth_stages": self.growth_stages,
            "action_threshold": self.action_threshold,
            "economic_threshold": self.economic_threshold,
            "threshold_unit": self.threshold_unit,
            "threshold_description": self.threshold_description,
            "sampling_method": self.sampling_method,
            "sampling_frequency": self.sampling_frequency,
            "threshold_description_ar": self.threshold_description_ar,
            "sampling_method_ar": self.sampling_method_ar,
            "sampling_frequency_ar": self.sampling_frequency_ar,
            "temperature_modifier": self.temperature_modifier,
            "growth_stage_modifier": self.growth_stage_modifier,
            "treatment_cost_per_ha": self.treatment_cost_per_ha,
            "crop_value_per_ha": self.crop_value_per_ha,
            "expected_loss_per_pest_unit": self.expected_loss_per_pest_unit,
            "currency": self.currency,
            "source": self.source,
            "source_ar": self.source_ar,
            "reference_year": self.reference_year,
            "region_specific": self.region_specific,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }
