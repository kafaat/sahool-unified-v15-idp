"""
نماذج الري - SAHOOL Irrigation Models
======================================
نماذج البيانات لجدولة الري وإدارة المياه

Pydantic models for irrigation scheduling and water management
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ============== التعدادات - Enumerations ==============

class IrrigationType(str, Enum):
    """
    أنواع أنظمة الري
    Types of irrigation systems
    """
    DRIP = "drip"  # ري بالتنقيط
    SPRINKLER = "sprinkler"  # ري بالرش
    SURFACE = "surface"  # ري سطحي
    SUBSURFACE = "subsurface"  # ري تحت السطحي
    CENTER_PIVOT = "center_pivot"  # ري محوري


class SoilType(str, Enum):
    """
    أنواع التربة في اليمن
    Soil types in Yemen
    """
    SANDY = "sandy"  # رملية
    LOAMY = "loamy"  # طينية
    CLAY = "clay"  # طينية ثقيلة
    SILTY = "silty"  # غرينية
    ROCKY = "rocky"  # صخرية


class CropType(str, Enum):
    """
    أنواع المحاصيل الرئيسية في اليمن
    Main crop types in Yemen
    """
    # محاصيل حبوب - Cereals
    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    SORGHUM = "sorghum"  # ذرة رفيعة
    MILLET = "millet"  # دخن

    # محاصيل بقولية - Legumes
    LENTILS = "lentils"  # عدس
    BEANS = "beans"  # فول
    CHICKPEAS = "chickpeas"  # حمص

    # خضروات - Vegetables
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    ONION = "onion"  # بصل
    CUCUMBER = "cucumber"  # خيار
    EGGPLANT = "eggplant"  # باذنجان
    PEPPER = "pepper"  # فلفل

    # محاصيل نقدية - Cash crops
    COTTON = "cotton"  # قطن
    TOBACCO = "tobacco"  # تبغ
    SESAME = "sesame"  # سمسم

    # فواكه - Fruits
    MANGO = "mango"  # مانجو
    BANANA = "banana"  # موز
    GRAPES = "grapes"  # عنب
    DATES = "dates"  # نخيل

    # محاصيل عطرية - Aromatic crops
    COFFEE = "coffee"  # بن
    QAT = "qat"  # قات


class GrowthStage(str, Enum):
    """
    مراحل نمو المحصول
    Crop growth stages (based on FAO)
    """
    INITIAL = "initial"  # مرحلة البداية
    DEVELOPMENT = "development"  # مرحلة التطور
    MID_SEASON = "mid_season"  # منتصف الموسم
    LATE_SEASON = "late_season"  # نهاية الموسم


class IrrigationStatus(str, Enum):
    """
    حالة جدول الري
    Irrigation schedule status
    """
    SCHEDULED = "scheduled"  # مجدول
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    COMPLETED = "completed"  # مكتمل
    CANCELLED = "cancelled"  # ملغى
    SKIPPED = "skipped"  # متخطى (بسبب المطر)


# ============== النماذج الأساسية - Base Models ==============

class WeatherData(BaseModel):
    """
    بيانات الطقس للحسابات المائية
    Weather data for water requirement calculations
    """
    model_config = ConfigDict(populate_by_name=True)

    date: date = Field(..., description="التاريخ - Date")

    # درجة الحرارة - Temperature (°C)
    temp_max: float = Field(..., ge=-10, le=60, description="أقصى درجة حرارة - Max temperature")
    temp_min: float = Field(..., ge=-10, le=60, description="أدنى درجة حرارة - Min temperature")
    temp_mean: float | None = Field(None, description="متوسط درجة الحرارة - Mean temperature")

    # الرطوبة - Humidity (%)
    humidity_max: float | None = Field(None, ge=0, le=100, description="أقصى رطوبة - Max humidity")
    humidity_min: float | None = Field(None, ge=0, le=100, description="أدنى رطوبة - Min humidity")
    humidity_mean: float | None = Field(None, ge=0, le=100, description="متوسط الرطوبة - Mean humidity")

    # سرعة الرياح - Wind speed (m/s)
    wind_speed: float = Field(2.0, ge=0, le=50, description="سرعة الرياح - Wind speed at 2m height")

    # الإشعاع الشمسي - Solar radiation (MJ/m²/day)
    solar_radiation: float | None = Field(None, ge=0, le=50, description="الإشعاع الشمسي - Solar radiation")

    # ساعات السطوع - Sunshine hours
    sunshine_hours: float | None = Field(None, ge=0, le=24, description="ساعات السطوع - Sunshine hours")

    # الأمطار - Rainfall (mm)
    rainfall: float = Field(0.0, ge=0, description="كمية الأمطار - Rainfall amount")

    # الموقع - Location
    latitude: float = Field(..., ge=-90, le=90, description="خط العرض - Latitude")
    elevation: float = Field(0, ge=0, description="الارتفاع عن سطح البحر - Elevation (m)")

    @field_validator('temp_mean', mode='before')
    @classmethod
    def calculate_mean_temp(cls, v, info):
        """حساب متوسط الحرارة إذا لم يكن موجوداً"""
        if v is None and 'temp_max' in info.data and 'temp_min' in info.data:
            return (info.data['temp_max'] + info.data['temp_min']) / 2
        return v


class SoilProperties(BaseModel):
    """
    خصائص التربة
    Soil properties for water balance calculations
    """
    model_config = ConfigDict(populate_by_name=True)

    soil_type: SoilType = Field(..., description="نوع التربة - Soil type")

    # سعة احتفاظ المياه - Water holding capacity
    field_capacity: float = Field(..., ge=0, le=1, description="السعة الحقلية - Field capacity (m³/m³)")
    wilting_point: float = Field(..., ge=0, le=1, description="نقطة الذبول - Permanent wilting point (m³/m³)")

    # عمق الجذور - Root depth
    root_depth: float = Field(0.3, ge=0.1, le=3.0, description="عمق الجذور - Root depth (m)")

    # معدل التسرب - Infiltration rate
    infiltration_rate: float = Field(..., ge=0, description="معدل التسرب - Infiltration rate (mm/hr)")

    # الكثافة الظاهرية - Bulk density
    bulk_density: float = Field(1.3, ge=0.8, le=2.0, description="الكثافة الظاهرية - Bulk density (g/cm³)")

    @property
    def total_available_water(self) -> float:
        """
        إجمالي المياه المتاحة - Total Available Water (TAW) in mm
        TAW = (θFC - θWP) × root_depth × 1000
        """
        return (self.field_capacity - self.wilting_point) * self.root_depth * 1000

    @property
    def readily_available_water(self) -> float:
        """
        المياه المتاحة بسهولة - Readily Available Water (RAW) in mm
        Typically 50% of TAW for most crops
        """
        return self.total_available_water * 0.5


class CropCoefficient(BaseModel):
    """
    معامل المحصول (Kc) حسب مرحلة النمو
    Crop coefficient by growth stage (FAO-56)
    """
    model_config = ConfigDict(populate_by_name=True)

    crop_type: CropType = Field(..., description="نوع المحصول - Crop type")
    growth_stage: GrowthStage = Field(..., description="مرحلة النمو - Growth stage")

    # معامل المحصول - Crop coefficient
    kc_value: float = Field(..., ge=0.1, le=1.5, description="معامل المحصول - Kc value")

    # مدة المرحلة - Stage duration (days)
    stage_duration_days: int = Field(..., ge=1, description="مدة المرحلة بالأيام - Stage duration")

    # عامل الإجهاد المائي - Water stress factor
    p_value: float = Field(0.5, ge=0.1, le=1.0, description="عامل استنزاف المياه - Depletion factor")


# ============== نماذج توازن المياه - Water Balance Models ==============

class WaterBalance(BaseModel):
    """
    توازن المياه في التربة
    Soil water balance model
    """
    model_config = ConfigDict(populate_by_name=True)

    field_id: str = Field(..., description="معرّف الحقل - Field ID")
    date: date = Field(..., description="التاريخ - Date")

    # المدخلات - Inputs (mm)
    irrigation: float = Field(0.0, ge=0, description="كمية الري - Irrigation amount")
    rainfall: float = Field(0.0, ge=0, description="كمية الأمطار - Rainfall amount")
    effective_rainfall: float = Field(0.0, ge=0, description="الأمطار الفعالة - Effective rainfall")

    # المخرجات - Outputs (mm)
    et0: float = Field(..., ge=0, description="التبخر المرجعي - Reference evapotranspiration")
    etc: float = Field(..., ge=0, description="تبخر المحصول - Crop evapotranspiration")

    # الرصيد المائي - Water content
    soil_water_content: float = Field(..., ge=0, description="محتوى المياه - Soil water content (mm)")
    water_deficit: float = Field(0.0, description="عجز المياه - Water deficit (mm)")

    # كفاءة الري - Irrigation efficiency
    irrigation_efficiency: float = Field(0.85, ge=0.3, le=1.0, description="كفاءة الري - Irrigation efficiency")

    @property
    def water_balance(self) -> float:
        """
        المعادلة: توازن المياه = الري الفعال + الأمطار الفعالة - التبخر
        Water balance = Effective irrigation + Effective rainfall - ETc
        """
        effective_irrigation = self.irrigation * self.irrigation_efficiency
        return effective_irrigation + self.effective_rainfall - self.etc


# ============== نماذج جدولة الري - Irrigation Scheduling Models ==============

class IrrigationEvent(BaseModel):
    """
    حدث ري واحد
    Single irrigation event
    """
    model_config = ConfigDict(populate_by_name=True)

    event_id: str | None = Field(None, description="معرّف الحدث - Event ID")
    field_id: str = Field(..., description="معرّف الحقل - Field ID")

    # التوقيت - Timing
    scheduled_date: datetime = Field(..., description="موعد الري المجدول - Scheduled date/time")
    actual_date: datetime | None = Field(None, description="الموعد الفعلي - Actual date/time")
    duration_minutes: int = Field(..., ge=1, description="المدة بالدقائق - Duration in minutes")

    # كمية المياه - Water amount
    water_amount_mm: float = Field(..., ge=0, description="كمية المياه (مم) - Water amount (mm)")
    water_amount_m3: float | None = Field(None, ge=0, description="كمية المياه (م³) - Water amount (m³)")

    # التفاصيل - Details
    irrigation_type: IrrigationType = Field(..., description="نوع الري - Irrigation type")
    status: IrrigationStatus = Field(IrrigationStatus.SCHEDULED, description="الحالة - Status")

    # التحسين - Optimization factors
    is_night_irrigation: bool = Field(False, description="ري ليلي - Night irrigation (lower electricity cost)")
    priority: int = Field(1, ge=1, le=5, description="الأولوية - Priority (1=highest)")

    # البيانات الإضافية - Additional data
    notes: str | None = Field(None, description="ملاحظات - Notes")
    metadata: dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية - Metadata")

    @field_validator('water_amount_m3', mode='before')
    @classmethod
    def calculate_m3_from_mm(cls, v, info):
        """حساب كمية المياه بالمتر المكعب من الملليمتر"""
        if v is None and 'water_amount_mm' in info.data and 'metadata' in info.data:
            # إذا كانت مساحة الحقل متوفرة في البيانات الإضافية
            area_ha = info.data['metadata'].get('field_area_ha')
            if area_ha:
                # 1 mm على 1 ha = 10 m³
                return info.data['water_amount_mm'] * area_ha * 10
        return v


class IrrigationSchedule(BaseModel):
    """
    جدول الري الكامل للحقل
    Complete irrigation schedule for a field
    """
    model_config = ConfigDict(populate_by_name=True)

    schedule_id: str | None = Field(None, description="معرّف الجدول - Schedule ID")
    field_id: str = Field(..., description="معرّف الحقل - Field ID")
    tenant_id: str = Field(..., description="معرّف المستأجر - Tenant ID")

    # الفترة الزمنية - Time period
    start_date: date = Field(..., description="تاريخ البداية - Start date")
    end_date: date = Field(..., description="تاريخ النهاية - End date")

    # معلومات المحصول - Crop information
    crop_type: CropType = Field(..., description="نوع المحصول - Crop type")
    growth_stage: GrowthStage = Field(..., description="مرحلة النمو - Growth stage")
    planting_date: date | None = Field(None, description="تاريخ الزراعة - Planting date")

    # معلومات التربة - Soil information
    soil_type: SoilType = Field(..., description="نوع التربة - Soil type")

    # أحداث الري - Irrigation events
    events: list[IrrigationEvent] = Field(default_factory=list, description="أحداث الري - Irrigation events")

    # الإحصائيات - Statistics
    total_water_mm: float = Field(0.0, ge=0, description="إجمالي المياه (مم) - Total water (mm)")
    total_water_m3: float = Field(0.0, ge=0, description="إجمالي المياه (م³) - Total water (m³)")
    average_interval_days: float = Field(0.0, ge=0, description="متوسط الفترة بين الريات - Average interval")

    # تكاليف - Costs
    estimated_electricity_cost: float | None = Field(None, description="تكلفة الكهرباء المقدرة - Estimated electricity cost")
    estimated_water_cost: float | None = Field(None, description="تكلفة المياه المقدرة - Estimated water cost")

    # التحسين - Optimization
    optimization_score: float | None = Field(None, ge=0, le=100, description="نقاط التحسين - Optimization score")
    water_efficiency_score: float | None = Field(None, ge=0, le=100, description="نقاط كفاءة المياه - Water efficiency score")

    # البيانات الإضافية - Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="تاريخ الإنشاء - Created at")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="تاريخ التحديث - Updated at")
    metadata: dict[str, Any] = Field(default_factory=dict, description="بيانات إضافية - Additional metadata")

    def add_event(self, event: IrrigationEvent) -> None:
        """
        إضافة حدث ري للجدول
        Add irrigation event to schedule
        """
        self.events.append(event)
        self.total_water_mm += event.water_amount_mm
        if event.water_amount_m3:
            self.total_water_m3 += event.water_amount_m3
        self.updated_at = datetime.utcnow()

    def get_upcoming_events(self, days: int = 7) -> list[IrrigationEvent]:
        """
        الحصول على أحداث الري القادمة
        Get upcoming irrigation events
        """
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)
        return [
            event for event in self.events
            if event.status == IrrigationStatus.SCHEDULED
            and now <= event.scheduled_date <= future_date
        ]

    @property
    def completion_rate(self) -> float:
        """
        نسبة الإكمال
        Completion rate (%)
        """
        if not self.events:
            return 0.0
        completed = len([e for e in self.events if e.status == IrrigationStatus.COMPLETED])
        return (completed / len(self.events)) * 100


# ============== نماذج التوقعات - Forecast Models ==============

class IrrigationRecommendation(BaseModel):
    """
    توصية الري
    Irrigation recommendation
    """
    model_config = ConfigDict(populate_by_name=True)

    field_id: str = Field(..., description="معرّف الحقل - Field ID")
    recommendation_date: date = Field(default_factory=date.today, description="تاريخ التوصية - Recommendation date")

    # التوصية - Recommendation
    should_irrigate: bool = Field(..., description="هل يجب الري - Should irrigate")
    recommended_amount_mm: float = Field(0.0, ge=0, description="الكمية الموصى بها (مم) - Recommended amount")
    urgency: str = Field("low", description="الأهمية - Urgency: low/medium/high/critical")

    # الأسباب - Reasoning
    water_deficit_mm: float = Field(0.0, description="عجز المياه (مم) - Water deficit")
    days_since_last_irrigation: int = Field(0, ge=0, description="أيام منذ آخر ري - Days since last irrigation")
    rainfall_forecast_mm: float = Field(0.0, ge=0, description="توقعات الأمطار (مم) - Rainfall forecast")

    # التوقيت الأمثل - Optimal timing
    best_time_start: datetime | None = Field(None, description="أفضل وقت للبدء - Best start time")
    best_time_end: datetime | None = Field(None, description="أفضل وقت للانتهاء - Best end time")

    # الملاحظات - Notes
    notes: str | None = Field(None, description="ملاحظات - Notes")
    confidence_score: float = Field(1.0, ge=0, le=1, description="نسبة الثقة - Confidence score")


from datetime import timedelta

# لضمان استيراد timedelta
__all__ = [
    "IrrigationType",
    "SoilType",
    "CropType",
    "GrowthStage",
    "IrrigationStatus",
    "WeatherData",
    "SoilProperties",
    "CropCoefficient",
    "WaterBalance",
    "IrrigationEvent",
    "IrrigationSchedule",
    "IrrigationRecommendation",
]
