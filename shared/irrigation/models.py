"""
Human-Machine Collaborative (HMC) Irrigation Decision Framework - Models
=========================================================================
نماذج إطار قرار الري التعاوني بين الإنسان والآلة

Pydantic models for the HMC irrigation decision framework, enabling structured
collaboration between farmers (domain experts) and AI systems for optimal
irrigation management.

Key concepts from the HMC framework:
1. Goal Anchoring (ترسيخ الأهداف) - Setting clear objectives and boundaries
2. Experience Injection (حقن الخبرة) - Incorporating local/tacit knowledge
3. Supervision Calibration (معايرة الإشراف) - Testing and validation cycles
4. Value Upgrade (ترقية القيمة) - Continuous learning and improvement

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

# =============================================================================
# Enums - تعدادات
# =============================================================================


class IrrigationGoalType(StrEnum):
    """
    Types of irrigation optimization goals.
    أنواع أهداف تحسين الري
    """

    WATER_SAVING = "water_saving"
    """Minimize water consumption | تقليل استهلاك المياه"""

    HIGH_YIELD = "high_yield"
    """Maximize crop yield | تعظيم إنتاجية المحصول"""

    WATER_FERTILIZER_SYNERGY = "water_fertilizer_synergy"
    """Optimize water-fertilizer coordination | تنسيق المياه والأسمدة"""

    BALANCED = "balanced"
    """Balance between water saving and yield | التوازن بين توفير المياه والإنتاج"""

    WATER_QUALITY = "water_quality"
    """Optimize for water quality management | إدارة جودة المياه"""

    ENERGY_EFFICIENT = "energy_efficient"
    """Minimize pumping energy | تقليل طاقة الضخ"""


class ExperienceSource(StrEnum):
    """
    Source of experience rules and knowledge.
    مصدر قواعد الخبرة والمعرفة
    """

    FARMER = "farmer"
    """Local farmer experience | خبرة المزارع المحلية"""

    RESEARCH = "research"
    """Agricultural research findings | نتائج البحث الزراعي"""

    AI_LEARNED = "ai_learned"
    """AI-derived patterns | أنماط مستخرجة من الذكاء الاصطناعي"""

    EXTENSION = "extension"
    """Extension service recommendations | توصيات الإرشاد الزراعي"""

    TRADITIONAL = "traditional"
    """Traditional farming wisdom | الحكمة الزراعية التقليدية"""


class DecisionType(StrEnum):
    """
    Types of human decisions in the collaborative process.
    أنواع القرارات البشرية في العملية التعاونية
    """

    APPROVE = "approve"
    """Approve AI recommendation | الموافقة على توصية الذكاء الاصطناعي"""

    REJECT = "reject"
    """Reject AI recommendation | رفض توصية الذكاء الاصطناعي"""

    MODIFY = "modify"
    """Modify AI recommendation | تعديل توصية الذكاء الاصطناعي"""

    DEFER = "defer"
    """Defer decision | تأجيل القرار"""

    OVERRIDE = "override"
    """Override with manual input | تجاوز بإدخال يدوي"""


class SoilType(StrEnum):
    """
    Soil types for zone configuration.
    أنواع التربة لتكوين المناطق
    """

    SANDY = "sandy"
    """Sandy soil | تربة رملية"""

    CLAY = "clay"
    """Clay soil | تربة طينية"""

    LOAMY = "loamy"
    """Loamy soil | تربة طفالية"""

    SANDY_LOAM = "sandy_loam"
    """Sandy loam | طفال رملي"""

    CLAY_LOAM = "clay_loam"
    """Clay loam | طفال طيني"""

    SILTY = "silty"
    """Silty soil | تربة غرينية"""


class ProductivityLevel(StrEnum):
    """
    Productivity levels for field zones.
    مستويات الإنتاجية لمناطق الحقل
    """

    LOW = "low"
    """Low productivity | إنتاجية منخفضة"""

    MEDIUM = "medium"
    """Medium productivity | إنتاجية متوسطة"""

    HIGH = "high"
    """High productivity | إنتاجية عالية"""


class ChecklistDimension(StrEnum):
    """
    HMC framework dimensions for checklist validation.
    أبعاد إطار HMC للتحقق من القائمة
    """

    GOAL_ANCHORING = "goal_anchoring"
    """Goal anchoring dimension | بُعد ترسيخ الأهداف"""

    EXPERIENCE_INJECTION = "experience_injection"
    """Experience injection dimension | بُعد حقن الخبرة"""

    SUPERVISION_CALIBRATION = "supervision_calibration"
    """Supervision calibration dimension | بُعد معايرة الإشراف"""

    VALUE_UPGRADE = "value_upgrade"
    """Value upgrade dimension | بُعد ترقية القيمة"""


class CalibrationMethod(StrEnum):
    """
    Methods for calibration/testing of irrigation programs.
    طرق معايرة/اختبار برامج الري
    """

    SIMULATION = "simulation"
    """Digital twin simulation | محاكاة التوأم الرقمي"""

    FIELD_TRIAL = "field_trial"
    """Small-scale field trial | تجربة حقلية صغيرة"""

    A_B_TEST = "a_b_test"
    """A/B testing comparison | مقارنة اختبار A/B"""

    EXPERT_REVIEW = "expert_review"
    """Expert agronomist review | مراجعة خبير زراعي"""


class SessionStatus(StrEnum):
    """
    Status of a collaborative decision session.
    حالة جلسة القرار التعاونية
    """

    INITIALIZED = "initialized"
    """Session started | بدأت الجلسة"""

    GOALS_SET = "goals_set"
    """Goals defined by human | حُددت الأهداف"""

    PROGRAM_GENERATED = "program_generated"
    """AI generated program | أنشأ الذكاء الاصطناعي البرنامج"""

    UNDER_REVIEW = "under_review"
    """Human reviewing program | الإنسان يراجع البرنامج"""

    EXPERIENCE_INJECTED = "experience_injected"
    """Local experience added | أُضيفت الخبرة المحلية"""

    CALIBRATING = "calibrating"
    """Running calibration tests | تشغيل اختبارات المعايرة"""

    APPROVED = "approved"
    """Human approved execution | وافق الإنسان على التنفيذ"""

    EXECUTING = "executing"
    """Program being executed | البرنامج قيد التنفيذ"""

    COMPLETED = "completed"
    """Session completed | اكتملت الجلسة"""

    CANCELLED = "cancelled"
    """Session cancelled | أُلغيت الجلسة"""


# =============================================================================
# Core Models - النماذج الأساسية
# =============================================================================


class BilingualLabel(BaseModel):
    """
    Bilingual label for names and descriptions.
    عنوان ثنائي اللغة للأسماء والأوصاف
    """

    en: str = Field(..., description="English text | النص بالإنجليزية")
    ar: str = Field(..., description="Arabic text | النص بالعربية")

    def __str__(self) -> str:
        return f"{self.en} | {self.ar}"


class IrrigationGoal(BaseModel):
    """
    An irrigation optimization goal with parameters.
    هدف تحسين الري مع المعلمات

    Example:
        goal = IrrigationGoal(
            goal_type=IrrigationGoalType.WATER_SAVING,
            target_reduction=0.3,  # 30% water reduction
            priority=1
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique goal ID | معرف الهدف الفريد")
    goal_type: IrrigationGoalType = Field(..., description="Type of irrigation goal | نوع هدف الري")
    name: str = Field(default="", description="Goal name (English) | اسم الهدف (إنجليزي)")
    name_ar: str = Field(default="", description="Goal name (Arabic) | اسم الهدف (عربي)")
    description: str = Field(default="", description="Goal description | وصف الهدف")
    description_ar: str = Field(default="", description="Goal description (Arabic) | وصف الهدف (عربي)")
    target_value: float | None = Field(None, description="Target metric value | القيمة المستهدفة للمقياس")
    target_reduction: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Target reduction percentage (0-1) | نسبة التخفيض المستهدفة",
    )
    priority: int = Field(default=1, ge=1, le=10, description="Priority level (1=highest) | مستوى الأولوية")
    is_primary: bool = Field(default=False, description="Is this the primary goal | هل هذا الهدف الرئيسي")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")

    model_config = {
        "json_schema_extra": {"example": {"goal_type": "water_saving", "target_reduction": 0.3, "priority": 1}}
    }


class EcologicalConstraint(BaseModel):
    """
    Ecological and resource constraints for irrigation.
    القيود البيئية والموارد للري

    These represent hard boundaries that the AI must respect,
    derived from environmental regulations, resource limitations,
    or sustainability requirements.

    Example:
        constraint = EcologicalConstraint(
            soil_salinity_limit=4.0,  # dS/m
            water_quota_reduction=0.3,
            carbon_emission_target=100.0  # kg CO2 per hectare
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique constraint ID | معرف القيد الفريد")
    name: str = Field(default="", description="Constraint name | اسم القيد")
    name_ar: str = Field(default="", description="Constraint name (Arabic) | اسم القيد (عربي)")
    description: str = Field(default="", description="Constraint description | وصف القيد")
    description_ar: str = Field(default="", description="Constraint description (Arabic) | وصف القيد (عربي)")

    # Water constraints
    water_quota_m3: float | None = Field(
        None, ge=0, description="Maximum water quota in m3/ha | الحصة المائية القصوى م3/هـ"
    )
    water_quota_reduction: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Required water reduction percentage (0-1) | نسبة تخفيض المياه المطلوبة",
    )
    min_irrigation_interval_hours: int | None = Field(
        None,
        ge=0,
        description="Minimum hours between irrigation events | الحد الأدنى للساعات بين أحداث الري",
    )

    # Soil constraints
    soil_salinity_limit: float | None = Field(
        None, ge=0, description="Maximum soil salinity (dS/m) | الحد الأقصى لملوحة التربة"
    )
    soil_moisture_min: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Minimum soil moisture percentage | الحد الأدنى لنسبة رطوبة التربة",
    )
    soil_moisture_max: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Maximum soil moisture percentage | الحد الأقصى لنسبة رطوبة التربة",
    )

    # Environmental constraints
    carbon_emission_target: float | None = Field(
        None, ge=0, description="Carbon emission limit (kg CO2/ha) | حد انبعاثات الكربون"
    )
    nitrogen_runoff_limit: float | None = Field(
        None, ge=0, description="Nitrogen runoff limit (kg N/ha) | حد جريان النيتروجين"
    )

    # Time constraints
    no_irrigation_hours: list[int] = Field(
        default_factory=list,
        description="Hours when irrigation is prohibited (0-23) | ساعات حظر الري",
    )
    seasonal_restrictions: dict[str, Any] = Field(
        default_factory=dict, description="Seasonal restrictions | قيود موسمية"
    )

    is_mandatory: bool = Field(default=True, description="Whether constraint is mandatory | هل القيد إلزامي")
    enforcement_level: str = Field(default="strict", description="Enforcement level: strict/warning | مستوى التنفيذ")

    @field_validator("soil_moisture_max")
    @classmethod
    def validate_moisture_range(cls, v: float | None, info) -> float | None:
        """Ensure max > min for soil moisture"""
        if v is not None and info.data.get("soil_moisture_min") is not None:
            if v < info.data["soil_moisture_min"]:
                raise ValueError(
                    "soil_moisture_max must be >= soil_moisture_min | "
                    "الحد الأقصى لرطوبة التربة يجب أن يكون >= الحد الأدنى"
                )
        return v


class ExperienceRule(BaseModel):
    """
    A rule derived from farming experience or research.
    قاعدة مستخرجة من الخبرة الزراعية أو البحث

    These rules encode tacit knowledge from farmers or validated
    research findings that should influence AI recommendations.

    Example:
        rule = ExperienceRule(
            condition="wheat_cold_wave",
            action="reduce_irrigation_20%",
            source=ExperienceSource.FARMER,
            rationale="Cold reduces evapotranspiration"
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique rule ID | معرف القاعدة الفريد")
    name: str = Field(default="", description="Rule name | اسم القاعدة")
    name_ar: str = Field(default="", description="Rule name (Arabic) | اسم القاعدة (عربي)")

    condition: str = Field(..., min_length=1, description="Condition that triggers the rule | الشرط الذي يفعّل القاعدة")
    condition_ar: str = Field(default="", description="Condition description (Arabic) | وصف الشرط (عربي)")

    action: str = Field(
        ...,
        min_length=1,
        description="Action to take when condition is met | الإجراء عند تحقق الشرط",
    )
    action_ar: str = Field(default="", description="Action description (Arabic) | وصف الإجراء (عربي)")

    source: ExperienceSource = Field(..., description="Source of the experience rule | مصدر قاعدة الخبرة")
    source_detail: str = Field(
        default="",
        description="Detailed source info (farmer name, study reference) | تفاصيل المصدر",
    )

    rationale: str = Field(default="", description="Explanation of why this rule works | شرح سبب نجاح هذه القاعدة")
    rationale_ar: str = Field(default="", description="Rationale in Arabic | المبرر بالعربية")

    # Applicability
    crop_types: list[str] = Field(default_factory=list, description="Applicable crop types | أنواع المحاصيل المطبقة")
    soil_types: list[SoilType] = Field(default_factory=list, description="Applicable soil types | أنواع التربة المطبقة")
    seasons: list[str] = Field(default_factory=list, description="Applicable seasons | المواسم المطبقة")
    growth_stages: list[str] = Field(default_factory=list, description="Applicable growth stages | مراحل النمو المطبقة")

    # Validation
    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence in the rule (0-1) | الثقة في القاعدة"
    )
    validation_count: int = Field(default=0, ge=0, description="Number of times validated | عدد مرات التحقق")
    success_rate: float | None = Field(
        None, ge=0.0, le=1.0, description="Historical success rate | معدل النجاح التاريخي"
    )

    is_active: bool = Field(default=True, description="Whether rule is active | هل القاعدة نشطة")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp | وقت الإنشاء"
    )
    created_by: str = Field(default="", description="Creator (user/system) | المُنشئ")

    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata | بيانات وصفية إضافية")


class HumanDecision(BaseModel):
    """
    A decision made by a human in the collaborative process.
    قرار اتخذه الإنسان في العملية التعاونية

    Records human judgment on AI-generated recommendations,
    enabling audit trails and learning from human feedback.

    Example:
        decision = HumanDecision(
            decision_type=DecisionType.MODIFY,
            rationale="Adjust timing for local conditions",
            override_ai=True,
            modifications={"start_time": "06:00", "duration": 45}
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique decision ID | معرف القرار الفريد")
    session_id: UUID | None = Field(None, description="Associated session ID | معرف الجلسة المرتبطة")
    recommendation_id: UUID | None = Field(
        None, description="AI recommendation being decided on | توصية الذكاء الاصطناعي المُقررة"
    )

    decision_type: DecisionType = Field(..., description="Type of decision made | نوع القرار المتخذ")

    rationale: str = Field(default="", description="Human's reasoning for the decision | مبرر الإنسان للقرار")
    rationale_ar: str = Field(default="", description="Rationale in Arabic | المبرر بالعربية")

    override_ai: bool = Field(
        default=False,
        description="Whether this overrides AI recommendation | هل يتجاوز توصية الذكاء الاصطناعي",
    )

    # Modifications (if decision_type is MODIFY)
    modifications: dict[str, Any] = Field(
        default_factory=dict,
        description="Specific modifications to the recommendation | التعديلات المحددة",
    )

    # Confidence and context
    confidence_level: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Human's confidence in this decision | ثقة الإنسان في القرار",
    )
    context_notes: str = Field(
        default="",
        description="Additional context for the decision | سياق إضافي للقرار",
    )

    # Who and when
    decided_by: str = Field(default="", description="User who made the decision | المستخدم المُقرر")
    decided_by_role: str = Field(default="farmer", description="Role of the decider | دور المُقرر")
    decided_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Decision timestamp | وقت القرار"
    )

    # For audit and learning
    tags: list[str] = Field(default_factory=list, description="Tags for categorization | علامات للتصنيف")
    feedback_collected: bool = Field(
        default=False, description="Whether feedback was collected | هل جُمعت التغذية الراجعة"
    )


class CalibrationResult(BaseModel):
    """
    Result of a calibration/testing cycle.
    نتيجة دورة المعايرة/الاختبار

    Records outcomes from simulation or field testing of
    irrigation programs before full deployment.

    Example:
        result = CalibrationResult(
            method=CalibrationMethod.SIMULATION,
            simulation_passed=True,
            predicted_water_saving=0.25,
            issues_found=["High pressure in zone 3"]
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique result ID | معرف النتيجة الفريد")
    session_id: UUID | None = Field(None, description="Associated session ID | معرف الجلسة المرتبطة")
    program_id: UUID | None = Field(None, description="Program being calibrated | البرنامج المُعاير")

    method: CalibrationMethod = Field(..., description="Calibration method used | طريقة المعايرة المستخدمة")

    # Test results
    simulation_passed: bool = Field(default=False, description="Simulation test passed | اجتاز اختبار المحاكاة")
    field_test_passed: bool = Field(default=False, description="Field test passed | اجتاز الاختبار الحقلي")

    # Predicted outcomes
    predicted_water_saving: float | None = Field(
        None, ge=0.0, le=1.0, description="Predicted water saving (0-1) | توفير المياه المتوقع"
    )
    predicted_yield_impact: float | None = Field(
        None, description="Predicted yield impact percentage | تأثير الإنتاجية المتوقع"
    )
    predicted_cost_saving: float | None = Field(None, description="Predicted cost saving | توفير التكلفة المتوقع")

    # Issues and recommendations
    issues_found: list[str] = Field(
        default_factory=list, description="Issues identified during calibration | المشاكل المكتشفة"
    )
    issues_found_ar: list[str] = Field(default_factory=list, description="Issues in Arabic | المشاكل بالعربية")

    recommendations: list[str] = Field(
        default_factory=list,
        description="Recommendations from calibration | توصيات من المعايرة",
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="Recommendations in Arabic | التوصيات بالعربية"
    )

    # Comparison with control (if A/B test)
    control_method: str | None = Field(None, description="Control method for comparison | طريقة المقارنة")
    improvement_over_control: float | None = Field(
        None, description="Percentage improvement over control | نسبة التحسن عن المقارنة"
    )

    # Metadata
    duration_hours: float | None = Field(None, ge=0, description="Duration of calibration test | مدة اختبار المعايرة")
    test_area_hectares: float | None = Field(
        None, ge=0, description="Area used for testing | المساحة المستخدمة للاختبار"
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Test start time | وقت بدء الاختبار"
    )
    completed_at: datetime | None = Field(None, description="Test completion time | وقت اكتمال الاختبار")

    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw test data | البيانات الخام للاختبار")

    @property
    def is_successful(self) -> bool:
        """Check if calibration was successful overall."""
        return self.simulation_passed or self.field_test_passed


class ZoneConfiguration(BaseModel):
    """
    Configuration for a specific irrigation zone.
    تكوين منطقة ري محددة

    Defines zone-specific parameters that may differ from
    field-level defaults based on soil, productivity, or
    farmer preferences.

    Example:
        zone = ZoneConfiguration(
            zone_id="zone_north",
            soil_type=SoilType.SANDY_LOAM,
            productivity_level=ProductivityLevel.HIGH,
            custom_params={"drip_rate": 2.0}
        )
    """

    zone_id: str = Field(..., min_length=1, description="Unique zone identifier | معرف المنطقة الفريد")
    name: str = Field(default="", description="Zone name | اسم المنطقة")
    name_ar: str = Field(default="", description="Zone name (Arabic) | اسم المنطقة (عربي)")
    description: str = Field(default="", description="Zone description | وصف المنطقة")

    # Physical characteristics
    soil_type: SoilType | None = Field(None, description="Soil type in zone | نوع التربة في المنطقة")
    productivity_level: ProductivityLevel = Field(
        default=ProductivityLevel.MEDIUM,
        description="Historical productivity level | مستوى الإنتاجية التاريخي",
    )
    area_hectares: float | None = Field(None, ge=0, description="Zone area in hectares | مساحة المنطقة بالهكتار")
    slope_percent: float | None = Field(None, ge=0, le=100, description="Terrain slope percentage | نسبة ميل التضاريس")

    # Irrigation infrastructure
    irrigation_type: str = Field(default="drip", description="Irrigation type: drip/sprinkler/flood | نوع الري")
    emitter_rate_lph: float | None = Field(
        None, ge=0, description="Emitter rate (liters/hour) | معدل المنقط (لتر/ساعة)"
    )
    emitter_spacing_m: float | None = Field(None, ge=0, description="Emitter spacing (meters) | المسافة بين المنقطات")

    # Custom parameters
    custom_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Zone-specific custom parameters | معلمات مخصصة للمنطقة",
    )

    # Override flags
    override_field_defaults: bool = Field(
        default=False,
        description="Override field-level defaults | تجاوز الإعدادات الافتراضية للحقل",
    )

    is_active: bool = Field(default=True, description="Whether zone is active | هل المنطقة نشطة")


class CollaborativeChecklistItem(BaseModel):
    """
    A single item in the HMC validation checklist.
    عنصر واحد في قائمة التحقق من HMC

    Tracks completion of specific validation steps in
    the human-machine collaborative process.

    Example:
        item = CollaborativeChecklistItem(
            dimension=ChecklistDimension.GOAL_ANCHORING,
            item="Define primary optimization goal",
            item_ar="تحديد هدف التحسين الرئيسي",
            checked=True
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique item ID | معرف العنصر الفريد")
    dimension: ChecklistDimension = Field(..., description="HMC framework dimension | بُعد إطار HMC")

    item: str = Field(..., min_length=1, description="Checklist item description | وصف عنصر القائمة")
    item_ar: str = Field(..., min_length=1, description="Item description (Arabic) | الوصف بالعربية")

    checked: bool = Field(default=False, description="Whether item is completed | هل اكتمل العنصر")
    checked_at: datetime | None = Field(None, description="When item was checked | وقت التحقق من العنصر")
    checked_by: str = Field(default="", description="Who checked the item | من حقق العنصر")

    notes: str = Field(default="", description="Additional notes for this item | ملاحظات إضافية")
    notes_ar: str = Field(default="", description="Notes in Arabic | الملاحظات بالعربية")

    is_mandatory: bool = Field(default=True, description="Whether item is mandatory | هل العنصر إلزامي")
    order: int = Field(default=0, description="Display order within dimension | ترتيب العرض")

    evidence: dict[str, Any] = Field(
        default_factory=dict, description="Evidence/artifacts for this item | الدليل/القطع الأثرية"
    )


class IrrigationSchedule(BaseModel):
    """
    A scheduled irrigation event.
    حدث ري مجدول

    Represents a single irrigation event within a program,
    with timing, duration, and zone targeting.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique schedule ID | معرف الجدول الفريد")
    zone_id: str = Field(..., description="Target zone | المنطقة المستهدفة")

    start_time: datetime = Field(..., description="Scheduled start time | وقت البدء المجدول")
    duration_minutes: int = Field(..., ge=1, description="Duration in minutes | المدة بالدقائق")
    volume_m3: float | None = Field(None, ge=0, description="Planned water volume (m3) | حجم المياه المخطط")

    # Conditions
    preconditions: dict[str, Any] = Field(
        default_factory=dict,
        description="Conditions that must be met before execution | الشروط المسبقة",
    )
    skip_if_rain_mm: float | None = Field(
        None, ge=0, description="Skip if rainfall exceeds (mm) | تجاوز إذا تجاوز المطر"
    )

    priority: int = Field(default=5, ge=1, le=10, description="Execution priority | أولوية التنفيذ")
    is_mandatory: bool = Field(default=False, description="Cannot be skipped | لا يمكن تجاوزه")


class IrrigationProgram(BaseModel):
    """
    A complete irrigation program generated by AI or modified by human.
    برنامج ري كامل أنشأه الذكاء الاصطناعي أو عدله الإنسان

    Contains the full schedule, parameters, and metadata for
    executing irrigation over a defined period.

    Example:
        program = IrrigationProgram(
            name="Winter Wheat - Week 12",
            field_id=field_uuid,
            schedules=[...],
            expected_water_usage_m3=1500.0
        )
    """

    id: UUID = Field(default_factory=uuid4, description="Unique program ID | معرف البرنامج الفريد")
    name: str = Field(..., min_length=1, description="Program name | اسم البرنامج")
    name_ar: str = Field(default="", description="Program name (Arabic) | اسم البرنامج (عربي)")
    description: str = Field(default="", description="Program description | وصف البرنامج")

    # Context
    field_id: UUID | None = Field(None, description="Target field ID | معرف الحقل المستهدف")
    farm_id: UUID | None = Field(None, description="Farm ID | معرف المزرعة")
    crop_type: str = Field(default="", description="Crop type | نوع المحصول")
    growth_stage: str = Field(default="", description="Current growth stage | مرحلة النمو الحالية")

    # Schedule
    schedules: list[IrrigationSchedule] = Field(default_factory=list, description="Irrigation events | أحداث الري")
    start_date: datetime | None = Field(None, description="Program start date | تاريخ بدء البرنامج")
    end_date: datetime | None = Field(None, description="Program end date | تاريخ انتهاء البرنامج")

    # Predictions
    expected_water_usage_m3: float | None = Field(
        None, ge=0, description="Expected total water usage (m3) | استخدام المياه المتوقع"
    )
    expected_yield_impact: float | None = Field(
        None, description="Expected yield impact percentage | تأثير الإنتاجية المتوقع"
    )
    expected_cost: float | None = Field(None, ge=0, description="Expected cost | التكلفة المتوقعة")

    # Generation info
    generated_by: str = Field(default="ai", description="Who generated: ai/human/hybrid | من أنشأ")
    generation_model: str = Field(default="", description="AI model used for generation | نموذج الذكاء الاصطناعي")
    confidence_score: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="AI confidence in the program | ثقة الذكاء الاصطناعي",
    )

    # Goals and constraints applied
    goals_applied: list[UUID] = Field(default_factory=list, description="Goal IDs applied | معرفات الأهداف المطبقة")
    constraints_applied: list[UUID] = Field(
        default_factory=list, description="Constraint IDs applied | معرفات القيود المطبقة"
    )
    rules_applied: list[UUID] = Field(
        default_factory=list,
        description="Experience rule IDs applied | معرفات قواعد الخبرة المطبقة",
    )

    # Status
    is_approved: bool = Field(default=False, description="Human approved | موافق عليه من الإنسان")
    approved_by: str = Field(default="", description="Who approved | من وافق")
    approved_at: datetime | None = Field(None, description="Approval time | وقت الموافقة")

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation time | وقت الإنشاء")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update time | وقت آخر تحديث"
    )
    version: int = Field(default=1, ge=1, description="Program version | إصدار البرنامج")

    parameters: dict[str, Any] = Field(default_factory=dict, description="Additional parameters | معلمات إضافية")


class ValidationReport(BaseModel):
    """
    Report from validating the collaborative checklist.
    تقرير من التحقق من قائمة التعاون

    Summarizes completion status across all HMC dimensions
    and identifies blocking issues.
    """

    id: UUID = Field(default_factory=uuid4, description="Report ID | معرف التقرير")
    session_id: UUID | None = Field(None, description="Associated session ID | معرف الجلسة المرتبطة")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Generation time | وقت الإنشاء"
    )

    is_complete: bool = Field(default=False, description="All mandatory items complete | اكتملت جميع العناصر الإلزامية")
    completion_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Overall completion percentage | نسبة الإكمال الإجمالية",
    )

    # Per-dimension status
    dimension_status: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Status per HMC dimension | الحالة لكل بُعد HMC",
    )

    # Issues
    blocking_issues: list[str] = Field(
        default_factory=list, description="Issues blocking approval | مشاكل تمنع الموافقة"
    )
    blocking_issues_ar: list[str] = Field(
        default_factory=list, description="Blocking issues in Arabic | المشاكل المانعة بالعربية"
    )

    warnings: list[str] = Field(default_factory=list, description="Non-blocking warnings | تحذيرات غير مانعة")
    warnings_ar: list[str] = Field(default_factory=list, description="Warnings in Arabic | التحذيرات بالعربية")

    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improvement | توصيات للتحسين"
    )

    # Ready for execution
    ready_for_execution: bool = Field(default=False, description="Ready for program execution | جاهز لتنفيذ البرنامج")


class SessionOutcome(BaseModel):
    """
    Outcome record for a completed decision session.
    سجل نتيجة لجلسة قرار مكتملة

    Captures the actual results after program execution
    for learning and improvement.
    """

    id: UUID = Field(default_factory=uuid4, description="Outcome ID | معرف النتيجة")
    session_id: UUID = Field(..., description="Session ID | معرف الجلسة")
    program_id: UUID = Field(..., description="Executed program ID | معرف البرنامج المنفذ")

    # Actual vs predicted
    actual_water_usage_m3: float | None = Field(
        None, ge=0, description="Actual water used (m3) | المياه المستخدمة فعلياً"
    )
    actual_yield: float | None = Field(None, ge=0, description="Actual yield achieved | الإنتاجية الفعلية")
    actual_cost: float | None = Field(None, ge=0, description="Actual cost | التكلفة الفعلية")

    # Performance metrics
    water_saving_achieved: float | None = Field(None, description="Water saving achieved (%) | توفير المياه المحقق")
    yield_vs_baseline: float | None = Field(None, description="Yield vs baseline (%) | الإنتاجية مقابل الأساس")
    cost_vs_baseline: float | None = Field(None, description="Cost vs baseline (%) | التكلفة مقابل الأساس")

    # Quality indicators
    overall_success: bool = Field(default=False, description="Overall success | النجاح الإجمالي")
    farmer_satisfaction: int | None = Field(None, ge=1, le=5, description="Farmer satisfaction (1-5) | رضا المزارع")

    # Lessons learned
    lessons_learned: list[str] = Field(
        default_factory=list, description="Lessons for future sessions | الدروس المستفادة"
    )
    lessons_learned_ar: list[str] = Field(default_factory=list, description="Lessons in Arabic | الدروس بالعربية")

    new_rules_extracted: list[UUID] = Field(
        default_factory=list,
        description="New experience rules extracted | قواعد خبرة جديدة مستخرجة",
    )

    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Recording time | وقت التسجيل")
    recorded_by: str = Field(default="", description="Who recorded | من سجل")

    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw outcome data | البيانات الخام للنتيجة")


class DecisionSession(BaseModel):
    """
    A complete human-machine collaborative decision session.
    جلسة قرار تعاونية كاملة بين الإنسان والآلة

    Tracks the full lifecycle of an irrigation decision from
    goal setting through execution and outcome recording.
    """

    id: UUID = Field(default_factory=uuid4, description="Session ID | معرف الجلسة")
    farm_id: UUID = Field(..., description="Farm ID | معرف المزرعة")
    field_id: UUID | None = Field(None, description="Field ID | معرف الحقل")
    farmer_id: str = Field(..., description="Farmer user ID | معرف المزارع")

    status: SessionStatus = Field(default=SessionStatus.INITIALIZED, description="Session status | حالة الجلسة")

    # Goals and constraints
    goals: list[IrrigationGoal] = Field(default_factory=list, description="Irrigation goals | أهداف الري")
    constraints: list[EcologicalConstraint] = Field(
        default_factory=list, description="Ecological constraints | القيود البيئية"
    )

    # Experience rules
    experience_rules: list[ExperienceRule] = Field(
        default_factory=list, description="Injected experience rules | قواعد الخبرة المحقونة"
    )

    # Zone configurations
    zone_configs: list[ZoneConfiguration] = Field(
        default_factory=list, description="Zone configurations | تكوينات المناطق"
    )

    # Generated program
    current_program: IrrigationProgram | None = Field(
        None, description="Current irrigation program | برنامج الري الحالي"
    )
    program_history: list[IrrigationProgram] = Field(
        default_factory=list, description="Previous program versions | إصدارات البرنامج السابقة"
    )

    # Human decisions
    decisions: list[HumanDecision] = Field(
        default_factory=list, description="Human decisions in session | قرارات الإنسان في الجلسة"
    )

    # Calibration
    calibration_results: list[CalibrationResult] = Field(
        default_factory=list, description="Calibration test results | نتائج اختبارات المعايرة"
    )

    # Checklist
    checklist_items: list[CollaborativeChecklistItem] = Field(
        default_factory=list, description="Checklist items | عناصر قائمة التحقق"
    )

    # Outcome
    outcome: SessionOutcome | None = Field(
        None, description="Session outcome after execution | نتيجة الجلسة بعد التنفيذ"
    )

    # Context
    context: dict[str, Any] = Field(default_factory=dict, description="Session context data | بيانات سياق الجلسة")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation time | وقت الإنشاء")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update time | وقت آخر تحديث"
    )
    completed_at: datetime | None = Field(None, description="Completion time | وقت الإكمال")

    # Iteration tracking
    iteration_count: int = Field(default=1, ge=1, description="Number of iteration cycles | عدد دورات التكرار")
    max_iterations: int = Field(default=10, ge=1, description="Maximum allowed iterations | الحد الأقصى للتكرارات")

    notes: str = Field(default="", description="Session notes | ملاحظات الجلسة")
    notes_ar: str = Field(default="", description="Notes in Arabic | الملاحظات بالعربية")


# =============================================================================
# Error Models - نماذج الأخطاء
# =============================================================================


class HMCError(BaseModel):
    """
    Error model for HMC framework operations.
    نموذج الخطأ لعمليات إطار HMC
    """

    code: str = Field(..., description="Error code | رمز الخطأ")
    message: str = Field(..., description="Error message (English) | رسالة الخطأ (إنجليزي)")
    message_ar: str = Field(..., description="Error message (Arabic) | رسالة الخطأ (عربي)")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error details | تفاصيل إضافية للخطأ")
    recoverable: bool = Field(default=True, description="Whether error is recoverable | هل الخطأ قابل للاسترداد")
    suggested_action: str = Field(default="", description="Suggested action to resolve | الإجراء المقترح للحل")
    suggested_action_ar: str = Field(default="", description="Suggested action (Arabic) | الإجراء المقترح (عربي)")


# =============================================================================
# Standard Error Instances - أمثلة الأخطاء القياسية
# =============================================================================


class HMCErrors:
    """Standard HMC error definitions | تعريفات أخطاء HMC القياسية"""

    SESSION_NOT_FOUND = HMCError(
        code="SESSION_NOT_FOUND",
        message="Decision session not found",
        message_ar="جلسة القرار غير موجودة",
        recoverable=False,
    )

    GOALS_NOT_SET = HMCError(
        code="GOALS_NOT_SET",
        message="Goals must be set before generating program",
        message_ar="يجب تحديد الأهداف قبل إنشاء البرنامج",
        suggested_action="Call human_sets_goals() first",
        suggested_action_ar="استدعِ human_sets_goals() أولاً",
    )

    PROGRAM_NOT_GENERATED = HMCError(
        code="PROGRAM_NOT_GENERATED",
        message="Irrigation program has not been generated",
        message_ar="لم يتم إنشاء برنامج الري",
        suggested_action="Call ai_generates_program() first",
        suggested_action_ar="استدعِ ai_generates_program() أولاً",
    )

    CALIBRATION_FAILED = HMCError(
        code="CALIBRATION_FAILED",
        message="Calibration tests failed",
        message_ar="فشلت اختبارات المعايرة",
        suggested_action="Review issues and modify program",
        suggested_action_ar="راجع المشاكل وعدّل البرنامج",
    )

    CHECKLIST_INCOMPLETE = HMCError(
        code="CHECKLIST_INCOMPLETE",
        message="Mandatory checklist items are incomplete",
        message_ar="عناصر قائمة التحقق الإلزامية غير مكتملة",
        suggested_action="Complete all mandatory items before approval",
        suggested_action_ar="أكمل جميع العناصر الإلزامية قبل الموافقة",
    )

    INVALID_CONSTRAINT = HMCError(
        code="INVALID_CONSTRAINT",
        message="Ecological constraint is invalid",
        message_ar="القيد البيئي غير صالح",
    )

    RULE_CONFLICT = HMCError(
        code="RULE_CONFLICT",
        message="Experience rules conflict with each other",
        message_ar="قواعد الخبرة متعارضة مع بعضها",
        suggested_action="Review and resolve conflicting rules",
        suggested_action_ar="راجع وحل القواعد المتعارضة",
    )

    MAX_ITERATIONS_REACHED = HMCError(
        code="MAX_ITERATIONS_REACHED",
        message="Maximum iteration limit reached",
        message_ar="تم الوصول إلى الحد الأقصى للتكرارات",
        suggested_action="Approve current program or reset session",
        suggested_action_ar="وافق على البرنامج الحالي أو أعد تعيين الجلسة",
    )
