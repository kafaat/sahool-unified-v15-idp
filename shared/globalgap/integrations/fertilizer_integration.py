"""
GlobalGAP Fertilizer Integration
تكامل الأسمدة مع GlobalGAP

Integrates fertilizer-advisor service with GlobalGAP nutrient management requirements.
Tracks fertilizer applications, generates nutrient management plans, and monitors MRL compliance.

يربط خدمة مستشار الأسمدة مع متطلبات إدارة العناصر الغذائية في GlobalGAP.
يتتبع تطبيقات الأسمدة، ويولد خطط إدارة العناصر الغذائية، ويراقب الامتثال لـ MRL.

Usage:
    from shared.globalgap.integrations.fertilizer_integration import (
        FertilizerIntegration,
        NutrientManagementPlan,
        FertilizerApplicationRecord
    )

    integration = FertilizerIntegration()
    await integration.connect()

    # Record fertilizer application
    await integration.record_fertilizer_application(
        farm_id=uuid4(),
        field_id=uuid4(),
        fertilizer_name="NPK 20-20-20",
        quantity_kg=100.0,
        based_on_soil_test=True
    )

    # Generate nutrient management plan
    plan = await integration.generate_nutrient_management_plan(
        farm_id=uuid4(),
        field_id=uuid4(),
        crop_type="tomato",
        target_yield_kg_per_ha=50000
    )
"""

from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from shared.events.publisher import EventPublisher

from .events import (
    FertilizerApplicationRecordedEvent,
    GlobalGAPSubjects,
)

# ─────────────────────────────────────────────────────────────────────────────
# Enums and Constants
# ─────────────────────────────────────────────────────────────────────────────


class FertilizerType(str, Enum):
    """
    Fertilizer types
    أنواع الأسمدة
    """

    ORGANIC = "ORGANIC"  # عضوي
    INORGANIC = "INORGANIC"  # غير عضوي
    ORGANIC_MINERAL = "ORGANIC_MINERAL"  # عضوي معدني
    FOLIAR = "FOLIAR"  # ورقي
    LIQUID = "LIQUID"  # سائل
    GRANULAR = "GRANULAR"  # حبيبي
    SLOW_RELEASE = "SLOW_RELEASE"  # بطيء الإطلاق
    CONTROLLED_RELEASE = "CONTROLLED_RELEASE"  # متحكم الإطلاق


class ApplicationMethod(str, Enum):
    """
    Application methods
    طرق التطبيق
    """

    BROADCAST = "BROADCAST"  # نثر
    BANDING = "BANDING"  # شريطي
    SIDE_DRESSING = "SIDE_DRESSING"  # جانبي
    TOP_DRESSING = "TOP_DRESSING"  # سطحي
    FOLIAR_SPRAY = "FOLIAR_SPRAY"  # رش ورقي
    FERTIGATION = "FERTIGATION"  # سماد مع الري
    INJECTION = "INJECTION"  # حقن
    INCORPORATION = "INCORPORATION"  # خلط مع التربة


class NutrientType(str, Enum):
    """
    Nutrient types
    أنواع العناصر الغذائية
    """

    NITROGEN = "N"  # نيتروجين
    PHOSPHORUS = "P"  # فوسفور
    POTASSIUM = "K"  # بوتاسيوم
    CALCIUM = "Ca"  # كالسيوم
    MAGNESIUM = "Mg"  # مغنيسيوم
    SULFUR = "S"  # كبريت
    IRON = "Fe"  # حديد
    MANGANESE = "Mn"  # منجنيز
    ZINC = "Zn"  # زنك
    COPPER = "Cu"  # نحاس
    BORON = "B"  # بورون
    MOLYBDENUM = "Mo"  # موليبدينوم


# ─────────────────────────────────────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────────────────────────────────────


class FertilizerApplicationRecord(BaseModel):
    """
    Fertilizer application record for GlobalGAP compliance
    سجل تطبيق الأسمدة للامتثال لـ GlobalGAP
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Record ID")
    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Application details
    application_date: date = Field(..., description="Application date")

    # Fertilizer information
    fertilizer_name: str = Field(..., description="Fertilizer product name")
    fertilizer_type: FertilizerType = Field(..., description="Fertilizer type")
    manufacturer: str | None = Field(None, description="Manufacturer name")

    # NPK and composition
    npk_ratio: str | None = Field(None, description="NPK ratio (e.g., 20-20-20)")
    nitrogen_percentage: float | None = Field(None, ge=0, le=100, description="N %")
    phosphorus_percentage: float | None = Field(
        None, ge=0, le=100, description="P %"
    )
    potassium_percentage: float | None = Field(None, ge=0, le=100, description="K %")

    # Other nutrients
    secondary_nutrients: dict[str, float] | None = Field(
        None, description="Secondary nutrients (e.g., {'Ca': 5.0, 'Mg': 2.0})"
    )
    micronutrients: dict[str, float] | None = Field(
        None, description="Micronutrients (e.g., {'Fe': 0.5, 'Zn': 0.2})"
    )

    # Quantities
    quantity_applied_kg: float = Field(
        ..., ge=0, description="Total quantity applied in kg"
    )
    application_rate_kg_per_ha: float | None = Field(
        None, ge=0, description="Application rate per hectare"
    )
    area_applied_ha: float | None = Field(
        None, ge=0, description="Area applied in hectares"
    )

    # Nutrient quantities (calculated)
    nitrogen_applied_kg: float | None = Field(
        None, ge=0, description="Total N applied in kg"
    )
    phosphorus_applied_kg: float | None = Field(
        None, ge=0, description="Total P applied in kg"
    )
    potassium_applied_kg: float | None = Field(
        None, ge=0, description="Total K applied in kg"
    )

    # Application method
    application_method: ApplicationMethod = Field(..., description="Application method")
    application_equipment: str | None = Field(None, description="Equipment used")

    # Compliance requirements
    based_on_soil_test: bool = Field(..., description="Based on soil test results")
    soil_test_date: date | None = Field(None, description="Soil test date")
    soil_test_report_url: str | None = Field(
        None, description="Soil test report URL"
    )

    based_on_plant_tissue_analysis: bool = Field(
        default=False, description="Based on plant tissue analysis"
    )
    tissue_analysis_date: date | None = Field(
        None, description="Tissue analysis date"
    )

    nutrient_plan_followed: bool = Field(
        ..., description="Follows nutrient management plan"
    )
    nutrient_plan_id: str | None = Field(
        None, description="Nutrient management plan ID"
    )

    # MRL compliance
    mrl_compliant: bool = Field(default=True, description="MRL compliant")
    heavy_metals_tested: bool = Field(default=False, description="Heavy metals tested")
    organic_certified: bool = Field(
        default=False, description="Organic certified (if organic type)"
    )

    # Justification
    application_reason_en: str = Field(..., description="Application reason (English)")
    application_reason_ar: str | None = Field(
        None, description="Application reason (Arabic)"
    )

    crop_stage: str | None = Field(
        None, description="Crop growth stage at application"
    )
    target_nutrient_deficiency: str | None = Field(
        None, description="Target nutrient deficiency"
    )

    # Weather and conditions
    weather_conditions: str | None = Field(
        None, description="Weather conditions during application"
    )
    soil_moisture: str | None = Field(None, description="Soil moisture conditions")

    # Operator
    operator_name: str | None = Field(None, description="Operator name")
    operator_trained: bool = Field(
        default=False, description="Operator trained in fertilizer application"
    )

    # Evidence
    application_record_url: str | None = Field(
        None, description="Application record document URL"
    )
    product_label_url: str | None = Field(None, description="Product label/MSDS URL")
    receipt_url: str | None = Field(None, description="Purchase receipt URL")

    # Metadata
    recorded_by: UUID | None = Field(None, description="User who recorded")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class NutrientRequirement(BaseModel):
    """
    Nutrient requirement for a crop
    متطلبات العناصر الغذائية للمحصول
    """

    nutrient: str = Field(..., description="Nutrient symbol (N, P, K, etc.)")
    nutrient_name_en: str = Field(..., description="Nutrient name (English)")
    nutrient_name_ar: str = Field(..., description="Nutrient name (Arabic)")

    required_kg_per_ha: float = Field(
        ..., ge=0, description="Required amount in kg per hectare"
    )
    current_soil_level_ppm: float | None = Field(
        None, ge=0, description="Current soil level in ppm"
    )
    optimal_soil_level_ppm: float | None = Field(
        None, ge=0, description="Optimal soil level in ppm"
    )

    deficit_kg_per_ha: float | None = Field(
        None, description="Deficit amount in kg per hectare"
    )
    is_deficient: bool = Field(default=False, description="Is deficient")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class NutrientManagementPlan(BaseModel):
    """
    Nutrient management plan for GlobalGAP compliance
    خطة إدارة العناصر الغذائية للامتثال لـ GlobalGAP
    """

    plan_id: str = Field(default_factory=lambda: str(uuid4()), description="Plan ID")
    farm_id: UUID = Field(..., description="Farm ID")
    field_id: UUID | None = Field(None, description="Field ID")
    tenant_id: UUID = Field(..., description="Tenant ID")

    # Crop and season
    crop_type: str = Field(..., description="Crop type")
    crop_variety: str | None = Field(None, description="Crop variety")
    growing_season: str = Field(..., description="Growing season (e.g., 2024-Spring)")

    planting_date: date | None = Field(None, description="Planting date")
    expected_harvest_date: date | None = Field(
        None, description="Expected harvest date"
    )

    # Yield targets
    target_yield_kg_per_ha: float = Field(
        ..., ge=0, description="Target yield in kg per hectare"
    )
    previous_yield_kg_per_ha: float | None = Field(
        None, ge=0, description="Previous season yield"
    )

    # Soil analysis
    soil_test_date: date = Field(..., description="Soil test date")
    soil_test_report_url: str | None = Field(
        None, description="Soil test report URL"
    )

    soil_ph: float | None = Field(None, ge=0, le=14, description="Soil pH")
    soil_organic_matter_percentage: float | None = Field(
        None, ge=0, le=100, description="Organic matter %"
    )
    soil_texture: str | None = Field(
        None, description="Soil texture (sandy, loamy, clay)"
    )

    # Nutrient requirements
    nutrient_requirements: list[NutrientRequirement] = Field(
        default_factory=list, description="List of nutrient requirements"
    )

    # Total nutrient needs (kg/ha)
    total_nitrogen_needed_kg_per_ha: float = Field(
        ..., ge=0, description="Total N needed in kg/ha"
    )
    total_phosphorus_needed_kg_per_ha: float = Field(
        ..., ge=0, description="Total P needed in kg/ha"
    )
    total_potassium_needed_kg_per_ha: float = Field(
        ..., ge=0, description="Total K needed in kg/ha"
    )

    # Planned applications
    number_of_applications: int = Field(
        ..., ge=1, description="Number of planned applications"
    )
    application_schedule: list[dict[str, Any]] = Field(
        default_factory=list, description="Application schedule with dates and amounts"
    )

    # Organic vs. inorganic strategy
    organic_fertilizer_percentage: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Target % of nutrients from organic sources",
    )

    # Environmental considerations
    nitrogen_leaching_risk: str = Field(
        default="LOW",
        pattern="^(LOW|MEDIUM|HIGH)$",
        description="Nitrogen leaching risk assessment",
    )
    phosphorus_runoff_risk: str = Field(
        default="LOW",
        pattern="^(LOW|MEDIUM|HIGH)$",
        description="Phosphorus runoff risk assessment",
    )

    # Compliance
    complies_with_globalgap: bool = Field(
        ..., description="Complies with GlobalGAP requirements"
    )
    complies_with_local_regulations: bool = Field(
        default=True, description="Complies with local regulations"
    )

    # Recommendations
    recommendations_en: list[str] = Field(
        default_factory=list, description="Recommendations (English)"
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="Recommendations (Arabic)"
    )

    # Plan metadata
    prepared_by: UUID | None = Field(None, description="User who prepared the plan")
    approved_by: UUID | None = Field(
        None, description="Agronomist/manager who approved"
    )
    approved_date: date | None = Field(None, description="Approval date")

    plan_status: str = Field(
        default="DRAFT",
        pattern="^(DRAFT|APPROVED|ACTIVE|COMPLETED|ARCHIVED)$",
        description="Plan status",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class MRLComplianceCheck(BaseModel):
    """
    MRL (Maximum Residue Level) compliance check for fertilizers
    فحص الامتثال لحدود البقايا القصوى للأسمدة
    """

    check_id: str = Field(default_factory=lambda: str(uuid4()), description="Check ID")
    farm_id: UUID = Field(..., description="Farm ID")
    fertilizer_name: str = Field(..., description="Fertilizer name")

    # Heavy metals check
    heavy_metals_tested: bool = Field(..., description="Heavy metals tested")
    cadmium_ppm: float | None = Field(
        None, ge=0, description="Cadmium content in ppm"
    )
    lead_ppm: float | None = Field(None, ge=0, description="Lead content in ppm")
    mercury_ppm: float | None = Field(
        None, ge=0, description="Mercury content in ppm"
    )
    arsenic_ppm: float | None = Field(
        None, ge=0, description="Arsenic content in ppm"
    )

    # MRL limits (example values - actual limits vary by jurisdiction)
    cadmium_limit_ppm: float = Field(
        default=1.5, ge=0, description="Cadmium MRL limit in ppm"
    )
    lead_limit_ppm: float = Field(
        default=120.0, ge=0, description="Lead MRL limit in ppm"
    )
    mercury_limit_ppm: float = Field(
        default=1.0, ge=0, description="Mercury MRL limit in ppm"
    )
    arsenic_limit_ppm: float = Field(
        default=40.0, ge=0, description="Arsenic MRL limit in ppm"
    )

    # Compliance status
    is_cadmium_compliant: bool = Field(..., description="Cadmium compliant")
    is_lead_compliant: bool = Field(..., description="Lead compliant")
    is_mercury_compliant: bool = Field(..., description="Mercury compliant")
    is_arsenic_compliant: bool = Field(..., description="Arsenic compliant")

    overall_mrl_compliant: bool = Field(..., description="Overall MRL compliance")

    # Test information
    test_date: date = Field(..., description="Test date")
    test_laboratory: str | None = Field(None, description="Testing laboratory")
    test_report_url: str | None = Field(None, description="Test report URL")

    # Non-compliance details
    non_compliance_issues_en: list[str] = Field(
        default_factory=list, description="Non-compliance issues (English)"
    )
    non_compliance_issues_ar: list[str] = Field(
        default_factory=list, description="Non-compliance issues (Arabic)"
    )

    checked_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Integration Class
# ─────────────────────────────────────────────────────────────────────────────


class FertilizerIntegration:
    """
    Integration between fertilizer-advisor service and GlobalGAP nutrient management compliance
    التكامل بين خدمة مستشار الأسمدة والامتثال لإدارة العناصر الغذائية في GlobalGAP

    Responsibilities:
    - Track fertilizer applications
    - Generate nutrient management plans
    - Monitor MRL compliance
    - Ensure soil test-based fertilization
    - Emit NATS events for fertilizer tracking
    """

    def __init__(self, publisher: EventPublisher | None = None):
        """
        Initialize fertilizer integration

        Args:
            publisher: Event publisher instance (will create if not provided)
        """
        self.publisher = publisher
        self._connected = False

    async def connect(self) -> bool:
        """
        Connect to NATS for event publishing
        الاتصال بـ NATS لنشر الأحداث

        Returns:
            True if connected successfully
        """
        if self.publisher is None:
            self.publisher = EventPublisher(
                service_name="globalgap-fertilizer-integration"
            )

        if not self.publisher.is_connected:
            self._connected = await self.publisher.connect()
        else:
            self._connected = True

        return self._connected

    async def close(self):
        """Close NATS connection"""
        if self.publisher:
            await self.publisher.close()
        self._connected = False

    # ─────────────────────────────────────────────────────────────────────────
    # Record Fertilizer Application
    # ─────────────────────────────────────────────────────────────────────────

    async def record_fertilizer_application(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        fertilizer_name: str,
        fertilizer_type: FertilizerType,
        quantity_applied_kg: float,
        application_method: ApplicationMethod,
        application_reason_en: str,
        based_on_soil_test: bool,
        nutrient_plan_followed: bool,
        field_id: UUID | None = None,
        application_date: date | None = None,
        npk_ratio: str | None = None,
        area_applied_ha: float | None = None,
        soil_test_date: date | None = None,
        application_reason_ar: str | None = None,
        mrl_compliant: bool = True,
        recorded_by: UUID | None = None,
    ) -> FertilizerApplicationRecord:
        """
        Record fertilizer application for GlobalGAP compliance
        تسجيل تطبيق الأسمدة للامتثال لـ GlobalGAP

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            fertilizer_name: Fertilizer product name
            fertilizer_type: Fertilizer type
            quantity_applied_kg: Quantity applied in kg
            application_method: Application method
            application_reason_en: Application reason (English)
            based_on_soil_test: Based on soil test
            nutrient_plan_followed: Follows nutrient management plan
            field_id: Field ID (optional)
            application_date: Application date (defaults to today)
            npk_ratio: NPK ratio
            area_applied_ha: Area applied in hectares
            soil_test_date: Soil test date
            application_reason_ar: Application reason (Arabic)
            mrl_compliant: MRL compliant
            recorded_by: User ID who recorded

        Returns:
            FertilizerApplicationRecord instance
        """
        app_date = application_date or date.today()

        # Calculate application rate
        application_rate_kg_per_ha = None
        if area_applied_ha and area_applied_ha > 0:
            application_rate_kg_per_ha = quantity_applied_kg / area_applied_ha

        record = FertilizerApplicationRecord(
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            application_date=app_date,
            fertilizer_name=fertilizer_name,
            fertilizer_type=fertilizer_type,
            npk_ratio=npk_ratio,
            quantity_applied_kg=quantity_applied_kg,
            application_rate_kg_per_ha=application_rate_kg_per_ha,
            area_applied_ha=area_applied_ha,
            application_method=application_method,
            based_on_soil_test=based_on_soil_test,
            soil_test_date=soil_test_date,
            nutrient_plan_followed=nutrient_plan_followed,
            mrl_compliant=mrl_compliant,
            application_reason_en=application_reason_en,
            application_reason_ar=application_reason_ar,
            recorded_by=recorded_by,
        )

        # Emit NATS event
        if self._connected:
            event = FertilizerApplicationRecordedEvent(
                farm_id=farm_id,
                tenant_id=tenant_id,
                field_id=field_id,
                application_date=app_date,
                fertilizer_name=fertilizer_name,
                fertilizer_type=fertilizer_type.value,
                npk_ratio=npk_ratio,
                quantity_applied_kg=quantity_applied_kg,
                application_rate_kg_per_ha=application_rate_kg_per_ha,
                area_applied_ha=area_applied_ha,
                application_method=application_method.value,
                based_on_soil_test=based_on_soil_test,
                soil_test_date=soil_test_date,
                nutrient_plan_followed=nutrient_plan_followed,
                mrl_compliant=mrl_compliant,
                application_reason_en=application_reason_en,
                application_reason_ar=application_reason_ar,
                recorded_by=recorded_by,
            )

            await self.publisher.publish_event(
                GlobalGAPSubjects.FERTILIZER_APPLICATION_RECORDED, event
            )

        return record

    # ─────────────────────────────────────────────────────────────────────────
    # Generate Nutrient Management Plan
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_nutrient_management_plan(
        self,
        farm_id: UUID,
        tenant_id: UUID,
        crop_type: str,
        target_yield_kg_per_ha: float,
        soil_test_date: date,
        growing_season: str,
        field_id: UUID | None = None,
        crop_variety: str | None = None,
        soil_ph: float | None = None,
        soil_organic_matter_percentage: float | None = None,
        previous_yield_kg_per_ha: float | None = None,
        planting_date: date | None = None,
        expected_harvest_date: date | None = None,
        prepared_by: UUID | None = None,
    ) -> NutrientManagementPlan:
        """
        Generate nutrient management plan based on crop requirements and soil test
        إنشاء خطة إدارة العناصر الغذائية بناءً على متطلبات المحصول واختبار التربة

        Args:
            farm_id: Farm ID
            tenant_id: Tenant ID
            crop_type: Crop type
            target_yield_kg_per_ha: Target yield in kg/ha
            soil_test_date: Soil test date
            growing_season: Growing season
            field_id: Field ID (optional)
            crop_variety: Crop variety
            soil_ph: Soil pH
            soil_organic_matter_percentage: Organic matter %
            previous_yield_kg_per_ha: Previous yield
            planting_date: Planting date
            expected_harvest_date: Expected harvest date
            prepared_by: User who prepared the plan

        Returns:
            NutrientManagementPlan instance
        """
        # Simplified nutrient calculations (in practice, these would be more complex)
        # Based on target yield and crop type

        # Example: Tomato nutrient requirements (kg/ha for target yield)
        # These are simplified examples - actual calculations would be crop-specific
        n_requirement = target_yield_kg_per_ha * 0.003  # 3 kg N per 1000 kg yield
        p_requirement = target_yield_kg_per_ha * 0.001  # 1 kg P per 1000 kg yield
        k_requirement = target_yield_kg_per_ha * 0.004  # 4 kg K per 1000 kg yield

        # Create nutrient requirements
        nutrient_requirements = [
            NutrientRequirement(
                nutrient="N",
                nutrient_name_en="Nitrogen",
                nutrient_name_ar="نيتروجين",
                required_kg_per_ha=n_requirement,
                is_deficient=True,
            ),
            NutrientRequirement(
                nutrient="P",
                nutrient_name_en="Phosphorus",
                nutrient_name_ar="فوسفور",
                required_kg_per_ha=p_requirement,
                is_deficient=True,
            ),
            NutrientRequirement(
                nutrient="K",
                nutrient_name_en="Potassium",
                nutrient_name_ar="بوتاسيوم",
                required_kg_per_ha=k_requirement,
                is_deficient=True,
            ),
        ]

        # Create application schedule (split applications)
        number_of_applications = 4  # Typical for most crops
        application_schedule = []

        if planting_date:
            # Base application at planting
            application_schedule.append(
                {
                    "application_number": 1,
                    "timing": "At planting",
                    "timing_ar": "عند الزراعة",
                    "days_after_planting": 0,
                    "scheduled_date": planting_date.isoformat(),
                    "n_kg_per_ha": n_requirement * 0.3,
                    "p_kg_per_ha": p_requirement * 0.5,
                    "k_kg_per_ha": k_requirement * 0.3,
                }
            )

            # Subsequent applications
            for i in range(2, number_of_applications + 1):
                days_after = 30 * (i - 1)
                app_date = planting_date + timedelta(days=days_after)
                application_schedule.append(
                    {
                        "application_number": i,
                        "timing": f"{days_after} days after planting",
                        "timing_ar": f"{days_after} يوم بعد الزراعة",
                        "days_after_planting": days_after,
                        "scheduled_date": app_date.isoformat(),
                        "n_kg_per_ha": n_requirement * 0.233,  # Remaining split
                        "p_kg_per_ha": p_requirement * 0.167,
                        "k_kg_per_ha": k_requirement * 0.233,
                    }
                )

        # Recommendations
        recommendations_en = [
            "Apply nitrogen in split doses to reduce leaching risk",
            "Base fertilizer rates on soil test results",
            "Monitor crop response and adjust applications as needed",
            "Keep records of all fertilizer applications for GlobalGAP compliance",
        ]

        recommendations_ar = [
            "تطبيق النيتروجين على دفعات لتقليل مخاطر الترشيح",
            "معدلات الأسمدة الأساسية على نتائج اختبار التربة",
            "مراقبة استجابة المحصول وتعديل التطبيقات حسب الحاجة",
            "الاحتفاظ بسجلات جميع تطبيقات الأسمدة للامتثال لـ GlobalGAP",
        ]

        # Assess leaching/runoff risks based on soil texture and organic matter
        nitrogen_leaching_risk = (
            "MEDIUM"  # Would be calculated based on soil properties
        )
        phosphorus_runoff_risk = "LOW"

        plan = NutrientManagementPlan(
            farm_id=farm_id,
            tenant_id=tenant_id,
            field_id=field_id,
            crop_type=crop_type,
            crop_variety=crop_variety,
            growing_season=growing_season,
            planting_date=planting_date,
            expected_harvest_date=expected_harvest_date,
            target_yield_kg_per_ha=target_yield_kg_per_ha,
            previous_yield_kg_per_ha=previous_yield_kg_per_ha,
            soil_test_date=soil_test_date,
            soil_ph=soil_ph,
            soil_organic_matter_percentage=soil_organic_matter_percentage,
            nutrient_requirements=nutrient_requirements,
            total_nitrogen_needed_kg_per_ha=n_requirement,
            total_phosphorus_needed_kg_per_ha=p_requirement,
            total_potassium_needed_kg_per_ha=k_requirement,
            number_of_applications=number_of_applications,
            application_schedule=application_schedule,
            nitrogen_leaching_risk=nitrogen_leaching_risk,
            phosphorus_runoff_risk=phosphorus_runoff_risk,
            complies_with_globalgap=True,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
            prepared_by=prepared_by,
            plan_status="DRAFT",
        )

        return plan

    # ─────────────────────────────────────────────────────────────────────────
    # MRL Compliance Check
    # ─────────────────────────────────────────────────────────────────────────

    async def check_mrl_compliance(
        self,
        farm_id: UUID,
        fertilizer_name: str,
        test_date: date,
        cadmium_ppm: float | None = None,
        lead_ppm: float | None = None,
        mercury_ppm: float | None = None,
        arsenic_ppm: float | None = None,
        test_laboratory: str | None = None,
        test_report_url: str | None = None,
    ) -> MRLComplianceCheck:
        """
        Check MRL compliance for fertilizer heavy metals
        فحص الامتثال لحدود البقايا القصوى للمعادن الثقيلة في الأسمدة

        Args:
            farm_id: Farm ID
            fertilizer_name: Fertilizer name
            test_date: Test date
            cadmium_ppm: Cadmium content in ppm
            lead_ppm: Lead content in ppm
            mercury_ppm: Mercury content in ppm
            arsenic_ppm: Arsenic content in ppm
            test_laboratory: Testing laboratory
            test_report_url: Test report URL

        Returns:
            MRLComplianceCheck instance
        """
        # Default MRL limits (based on EU regulations - adjust per local requirements)
        cadmium_limit = 1.5  # ppm
        lead_limit = 120.0  # ppm
        mercury_limit = 1.0  # ppm
        arsenic_limit = 40.0  # ppm

        heavy_metals_tested = any([cadmium_ppm, lead_ppm, mercury_ppm, arsenic_ppm])

        # Check compliance for each metal
        is_cadmium_compliant = cadmium_ppm is None or cadmium_ppm <= cadmium_limit
        is_lead_compliant = lead_ppm is None or lead_ppm <= lead_limit
        is_mercury_compliant = mercury_ppm is None or mercury_ppm <= mercury_limit
        is_arsenic_compliant = arsenic_ppm is None or arsenic_ppm <= arsenic_limit

        overall_mrl_compliant = (
            is_cadmium_compliant
            and is_lead_compliant
            and is_mercury_compliant
            and is_arsenic_compliant
        )

        # Build non-compliance issues
        issues_en = []
        issues_ar = []

        if not is_cadmium_compliant:
            issues_en.append(
                f"Cadmium exceeds limit: {cadmium_ppm:.2f} ppm > {cadmium_limit} ppm"
            )
            issues_ar.append(
                f"الكادميوم يتجاوز الحد: {cadmium_ppm:.2f} ppm > {cadmium_limit} ppm"
            )

        if not is_lead_compliant:
            issues_en.append(
                f"Lead exceeds limit: {lead_ppm:.2f} ppm > {lead_limit} ppm"
            )
            issues_ar.append(
                f"الرصاص يتجاوز الحد: {lead_ppm:.2f} ppm > {lead_limit} ppm"
            )

        if not is_mercury_compliant:
            issues_en.append(
                f"Mercury exceeds limit: {mercury_ppm:.2f} ppm > {mercury_limit} ppm"
            )
            issues_ar.append(
                f"الزئبق يتجاوز الحد: {mercury_ppm:.2f} ppm > {mercury_limit} ppm"
            )

        if not is_arsenic_compliant:
            issues_en.append(
                f"Arsenic exceeds limit: {arsenic_ppm:.2f} ppm > {arsenic_limit} ppm"
            )
            issues_ar.append(
                f"الزرنيخ يتجاوز الحد: {arsenic_ppm:.2f} ppm > {arsenic_limit} ppm"
            )

        check = MRLComplianceCheck(
            farm_id=farm_id,
            fertilizer_name=fertilizer_name,
            heavy_metals_tested=heavy_metals_tested,
            cadmium_ppm=cadmium_ppm,
            lead_ppm=lead_ppm,
            mercury_ppm=mercury_ppm,
            arsenic_ppm=arsenic_ppm,
            cadmium_limit_ppm=cadmium_limit,
            lead_limit_ppm=lead_limit,
            mercury_limit_ppm=mercury_limit,
            arsenic_limit_ppm=arsenic_limit,
            is_cadmium_compliant=is_cadmium_compliant,
            is_lead_compliant=is_lead_compliant,
            is_mercury_compliant=is_mercury_compliant,
            is_arsenic_compliant=is_arsenic_compliant,
            overall_mrl_compliant=overall_mrl_compliant,
            test_date=test_date,
            test_laboratory=test_laboratory,
            test_report_url=test_report_url,
            non_compliance_issues_en=issues_en,
            non_compliance_issues_ar=issues_ar,
        )

        return check

    # ─────────────────────────────────────────────────────────────────────────
    # Context Manager Support
    # ─────────────────────────────────────────────────────────────────────────

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Enums
    "FertilizerType",
    "ApplicationMethod",
    "NutrientType",
    # Models
    "FertilizerApplicationRecord",
    "NutrientRequirement",
    "NutrientManagementPlan",
    "MRLComplianceCheck",
    # Integration
    "FertilizerIntegration",
]
