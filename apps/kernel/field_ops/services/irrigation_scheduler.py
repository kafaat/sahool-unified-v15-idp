"""
خدمة جدولة الري - SAHOOL Irrigation Scheduler
==============================================
نظام متقدم لجدولة الري وتحسين استخدام المياه

Advanced irrigation scheduling and water optimization system
Based on FAO-56 methodology (Penman-Monteith)
"""

import math
from datetime import date, datetime, timedelta

from ..models.irrigation import (
    CropType,
    GrowthStage,
    IrrigationEvent,
    IrrigationRecommendation,
    IrrigationSchedule,
    IrrigationType,
    SoilProperties,
    SoilType,
    WaterBalance,
    WeatherData,
)

# ============== جداول معاملات المحاصيل اليمنية - Yemen Crop Coefficient Tables ==============

# معاملات المحاصيل (Kc) حسب مراحل النمو لمحاصيل اليمن
# Crop coefficients by growth stage for Yemen crops (FAO-56 + local adaptations)
YEMEN_CROP_KC_TABLE: dict[CropType, dict[GrowthStage, dict[str, float]]] = {
    # محاصيل الحبوب - Cereals
    CropType.WHEAT: {
        GrowthStage.INITIAL: {"kc": 0.3, "duration_days": 15, "p": 0.55},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 30, "p": 0.55},
        GrowthStage.MID_SEASON: {"kc": 1.15, "duration_days": 50, "p": 0.55},
        GrowthStage.LATE_SEASON: {"kc": 0.4, "duration_days": 30, "p": 0.55},
    },
    CropType.BARLEY: {
        GrowthStage.INITIAL: {"kc": 0.3, "duration_days": 15, "p": 0.55},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 25, "p": 0.55},
        GrowthStage.MID_SEASON: {"kc": 1.15, "duration_days": 50, "p": 0.55},
        GrowthStage.LATE_SEASON: {"kc": 0.25, "duration_days": 25, "p": 0.55},
    },
    CropType.SORGHUM: {
        GrowthStage.INITIAL: {"kc": 0.3, "duration_days": 20, "p": 0.55},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 35, "p": 0.55},
        GrowthStage.MID_SEASON: {"kc": 1.1, "duration_days": 40, "p": 0.55},
        GrowthStage.LATE_SEASON: {"kc": 0.55, "duration_days": 30, "p": 0.55},
    },
    CropType.MILLET: {
        GrowthStage.INITIAL: {"kc": 0.3, "duration_days": 15, "p": 0.55},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 25, "p": 0.55},
        GrowthStage.MID_SEASON: {"kc": 1.0, "duration_days": 40, "p": 0.55},
        GrowthStage.LATE_SEASON: {"kc": 0.3, "duration_days": 25, "p": 0.55},
    },
    # البقوليات - Legumes
    CropType.LENTILS: {
        GrowthStage.INITIAL: {"kc": 0.4, "duration_days": 15, "p": 0.45},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 30, "p": 0.45},
        GrowthStage.MID_SEASON: {"kc": 1.1, "duration_days": 50, "p": 0.45},
        GrowthStage.LATE_SEASON: {"kc": 0.3, "duration_days": 20, "p": 0.45},
    },
    CropType.BEANS: {
        GrowthStage.INITIAL: {"kc": 0.4, "duration_days": 20, "p": 0.45},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 30, "p": 0.45},
        GrowthStage.MID_SEASON: {"kc": 1.15, "duration_days": 40, "p": 0.45},
        GrowthStage.LATE_SEASON: {"kc": 0.35, "duration_days": 20, "p": 0.45},
    },
    CropType.CHICKPEAS: {
        GrowthStage.INITIAL: {"kc": 0.4, "duration_days": 15, "p": 0.50},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 30, "p": 0.50},
        GrowthStage.MID_SEASON: {"kc": 1.1, "duration_days": 50, "p": 0.50},
        GrowthStage.LATE_SEASON: {"kc": 0.3, "duration_days": 25, "p": 0.50},
    },
    # الخضروات - Vegetables
    CropType.TOMATO: {
        GrowthStage.INITIAL: {"kc": 0.6, "duration_days": 30, "p": 0.40},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 40, "p": 0.40},
        GrowthStage.MID_SEASON: {"kc": 1.15, "duration_days": 45, "p": 0.40},
        GrowthStage.LATE_SEASON: {"kc": 0.8, "duration_days": 30, "p": 0.40},
    },
    CropType.POTATO: {
        GrowthStage.INITIAL: {"kc": 0.5, "duration_days": 25, "p": 0.35},
        GrowthStage.DEVELOPMENT: {"kc": 0.75, "duration_days": 30, "p": 0.35},
        GrowthStage.MID_SEASON: {"kc": 1.15, "duration_days": 45, "p": 0.35},
        GrowthStage.LATE_SEASON: {"kc": 0.75, "duration_days": 25, "p": 0.35},
    },
    CropType.ONION: {
        GrowthStage.INITIAL: {"kc": 0.5, "duration_days": 15, "p": 0.30},
        GrowthStage.DEVELOPMENT: {"kc": 0.75, "duration_days": 30, "p": 0.30},
        GrowthStage.MID_SEASON: {"kc": 1.05, "duration_days": 70, "p": 0.30},
        GrowthStage.LATE_SEASON: {"kc": 0.85, "duration_days": 40, "p": 0.30},
    },
    CropType.CUCUMBER: {
        GrowthStage.INITIAL: {"kc": 0.6, "duration_days": 20, "p": 0.50},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 30, "p": 0.50},
        GrowthStage.MID_SEASON: {"kc": 1.0, "duration_days": 40, "p": 0.50},
        GrowthStage.LATE_SEASON: {"kc": 0.75, "duration_days": 20, "p": 0.50},
    },
    CropType.EGGPLANT: {
        GrowthStage.INITIAL: {"kc": 0.6, "duration_days": 30, "p": 0.45},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 40, "p": 0.45},
        GrowthStage.MID_SEASON: {"kc": 1.05, "duration_days": 40, "p": 0.45},
        GrowthStage.LATE_SEASON: {"kc": 0.9, "duration_days": 25, "p": 0.45},
    },
    CropType.PEPPER: {
        GrowthStage.INITIAL: {"kc": 0.6, "duration_days": 30, "p": 0.30},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 35, "p": 0.30},
        GrowthStage.MID_SEASON: {"kc": 1.05, "duration_days": 40, "p": 0.30},
        GrowthStage.LATE_SEASON: {"kc": 0.9, "duration_days": 25, "p": 0.30},
    },
    # المحاصيل النقدية - Cash crops
    CropType.COTTON: {
        GrowthStage.INITIAL: {"kc": 0.35, "duration_days": 30, "p": 0.65},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 50, "p": 0.65},
        GrowthStage.MID_SEASON: {"kc": 1.15, "duration_days": 55, "p": 0.65},
        GrowthStage.LATE_SEASON: {"kc": 0.7, "duration_days": 45, "p": 0.65},
    },
    CropType.TOBACCO: {
        GrowthStage.INITIAL: {"kc": 0.35, "duration_days": 20, "p": 0.40},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 35, "p": 0.40},
        GrowthStage.MID_SEASON: {"kc": 1.1, "duration_days": 40, "p": 0.40},
        GrowthStage.LATE_SEASON: {"kc": 0.9, "duration_days": 15, "p": 0.40},
    },
    CropType.SESAME: {
        GrowthStage.INITIAL: {"kc": 0.35, "duration_days": 20, "p": 0.60},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 30, "p": 0.60},
        GrowthStage.MID_SEASON: {"kc": 1.1, "duration_days": 40, "p": 0.60},
        GrowthStage.LATE_SEASON: {"kc": 0.25, "duration_days": 20, "p": 0.60},
    },
    # الفواكه - Fruits
    CropType.MANGO: {
        GrowthStage.INITIAL: {"kc": 0.6, "duration_days": 60, "p": 0.50},
        GrowthStage.DEVELOPMENT: {"kc": 0.8, "duration_days": 90, "p": 0.50},
        GrowthStage.MID_SEASON: {"kc": 0.95, "duration_days": 120, "p": 0.50},
        GrowthStage.LATE_SEASON: {"kc": 0.9, "duration_days": 95, "p": 0.50},
    },
    CropType.BANANA: {
        GrowthStage.INITIAL: {"kc": 0.5, "duration_days": 90, "p": 0.35},
        GrowthStage.DEVELOPMENT: {"kc": 0.7, "duration_days": 90, "p": 0.35},
        GrowthStage.MID_SEASON: {"kc": 1.1, "duration_days": 120, "p": 0.35},
        GrowthStage.LATE_SEASON: {"kc": 1.0, "duration_days": 60, "p": 0.35},
    },
    CropType.GRAPES: {
        GrowthStage.INITIAL: {"kc": 0.3, "duration_days": 20, "p": 0.45},
        GrowthStage.DEVELOPMENT: {"kc": 0.5, "duration_days": 50, "p": 0.45},
        GrowthStage.MID_SEASON: {"kc": 0.85, "duration_days": 90, "p": 0.45},
        GrowthStage.LATE_SEASON: {"kc": 0.45, "duration_days": 60, "p": 0.45},
    },
    CropType.DATES: {
        GrowthStage.INITIAL: {"kc": 0.9, "duration_days": 60, "p": 0.50},
        GrowthStage.DEVELOPMENT: {"kc": 0.95, "duration_days": 110, "p": 0.50},
        GrowthStage.MID_SEASON: {"kc": 0.95, "duration_days": 120, "p": 0.50},
        GrowthStage.LATE_SEASON: {"kc": 0.95, "duration_days": 75, "p": 0.50},
    },
    # المحاصيل العطرية - Aromatic crops
    CropType.COFFEE: {
        GrowthStage.INITIAL: {"kc": 0.9, "duration_days": 60, "p": 0.40},
        GrowthStage.DEVELOPMENT: {"kc": 0.95, "duration_days": 90, "p": 0.40},
        GrowthStage.MID_SEASON: {"kc": 1.05, "duration_days": 120, "p": 0.40},
        GrowthStage.LATE_SEASON: {"kc": 1.05, "duration_days": 95, "p": 0.40},
    },
    CropType.QAT: {
        GrowthStage.INITIAL: {"kc": 0.8, "duration_days": 30, "p": 0.40},
        GrowthStage.DEVELOPMENT: {"kc": 0.9, "duration_days": 60, "p": 0.40},
        GrowthStage.MID_SEASON: {"kc": 1.0, "duration_days": 150, "p": 0.40},
        GrowthStage.LATE_SEASON: {"kc": 0.95, "duration_days": 125, "p": 0.40},
    },
}


# جداول خصائص التربة - Soil properties table
SOIL_PROPERTIES_TABLE: dict[SoilType, dict[str, float]] = {
    SoilType.SANDY: {
        "field_capacity": 0.10,  # 10% محتوى مائي
        "wilting_point": 0.04,  # 4%
        "infiltration_rate": 50.0,  # mm/hr - سريع
        "bulk_density": 1.6,  # g/cm³
    },
    SoilType.LOAMY: {
        "field_capacity": 0.25,  # 25%
        "wilting_point": 0.13,  # 13%
        "infiltration_rate": 25.0,  # mm/hr - متوسط
        "bulk_density": 1.4,
    },
    SoilType.CLAY: {
        "field_capacity": 0.35,  # 35%
        "wilting_point": 0.20,  # 20%
        "infiltration_rate": 5.0,  # mm/hr - بطيء
        "bulk_density": 1.2,
    },
    SoilType.SILTY: {
        "field_capacity": 0.30,  # 30%
        "wilting_point": 0.15,  # 15%
        "infiltration_rate": 15.0,  # mm/hr
        "bulk_density": 1.3,
    },
    SoilType.ROCKY: {
        "field_capacity": 0.08,  # 8%
        "wilting_point": 0.03,  # 3%
        "infiltration_rate": 100.0,  # mm/hr - سريع جداً
        "bulk_density": 1.8,
    },
}


# كفاءة أنظمة الري - Irrigation system efficiency
IRRIGATION_EFFICIENCY: dict[IrrigationType, float] = {
    IrrigationType.DRIP: 0.90,  # 90% كفاءة عالية
    IrrigationType.SPRINKLER: 0.75,  # 75%
    IrrigationType.SURFACE: 0.60,  # 60% كفاءة منخفضة
    IrrigationType.SUBSURFACE: 0.95,  # 95% كفاءة عالية جداً
    IrrigationType.CENTER_PIVOT: 0.85,  # 85%
}


# ============== فئة جدولة الري - Irrigation Scheduler Class ==============


class IrrigationScheduler:
    """
    محدد جدول الري المتقدم
    Advanced irrigation scheduler using FAO-56 Penman-Monteith method

    الميزات الرئيسية:
    - حساب التبخر المرجعي (ET0) بطريقة Penman-Monteith
    - حساب احتياجات المياه للمحاصيل
    - تحسين جدول الري لتقليل الهدر
    - مراعاة توقعات الطقس وتكاليف الكهرباء

    Main features:
    - ET0 calculation using Penman-Monteith
    - Crop water requirements calculation
    - Schedule optimization to minimize waste
    - Weather forecast and electricity cost consideration
    """

    def __init__(self):
        """تهيئة محدد جدول الري - Initialize irrigation scheduler"""
        self.crop_kc_table = YEMEN_CROP_KC_TABLE
        self.soil_properties_table = SOIL_PROPERTIES_TABLE
        self.irrigation_efficiency = IRRIGATION_EFFICIENCY

    # ============== حساب احتياجات المياه - Water Requirements ==============

    def calculate_water_requirement(
        self,
        field_id: str,
        crop_type: CropType,
        growth_stage: GrowthStage,
        et0: float,
        effective_rainfall: float = 0.0,
        soil_type: SoilType = SoilType.LOAMY,
        irrigation_type: IrrigationType = IrrigationType.DRIP,
    ) -> float:
        """
        حساب احتياجات المياه للمحصول
        Calculate crop water requirements

        Args:
            field_id: معرّف الحقل - Field ID
            crop_type: نوع المحصول - Crop type
            growth_stage: مرحلة النمو - Growth stage
            et0: التبخر المرجعي - Reference evapotranspiration (mm/day)
            effective_rainfall: الأمطار الفعالة - Effective rainfall (mm/day)
            soil_type: نوع التربة - Soil type
            irrigation_type: نوع نظام الري - Irrigation system type

        Returns:
            float: كمية المياه المطلوبة (مم/يوم) - Required water amount (mm/day)
        """
        # الحصول على معامل المحصول - Get crop coefficient
        kc = self._get_crop_coefficient(crop_type, growth_stage)

        # حساب تبخر المحصول - Calculate crop evapotranspiration
        etc = et0 * kc

        # طرح الأمطار الفعالة - Subtract effective rainfall
        net_irrigation = max(0, etc - effective_rainfall)

        # تعديل حسب نوع التربة - Adjust for soil type
        adjusted_requirement = self.adjust_for_soil_type(net_irrigation, soil_type)

        # تعديل حسب كفاءة نظام الري - Adjust for irrigation efficiency
        efficiency = self.irrigation_efficiency.get(irrigation_type, 0.75)
        gross_irrigation = adjusted_requirement / efficiency

        return gross_irrigation

    def adjust_for_soil_type(self, base_requirement: float, soil_type: SoilType) -> float:
        """
        تعديل احتياجات المياه حسب نوع التربة
        Adjust water requirements based on soil type

        Args:
            base_requirement: الاحتياج الأساسي - Base requirement (mm)
            soil_type: نوع التربة - Soil type

        Returns:
            float: الاحتياج المعدل - Adjusted requirement (mm)
        """
        # عوامل التعديل حسب نوع التربة
        # Adjustment factors by soil type
        adjustment_factors = {
            SoilType.SANDY: 1.15,  # تحتاج المزيد من المياه - Needs more water
            SoilType.LOAMY: 1.0,  # مثالية - Ideal
            SoilType.CLAY: 0.95,  # تحتفظ بالمياه - Retains water
            SoilType.SILTY: 1.05,  # متوسط
            SoilType.ROCKY: 1.20,  # تحتاج المزيد - Needs more
        }

        factor = adjustment_factors.get(soil_type, 1.0)
        return base_requirement * factor

    # ============== حساب التبخر - ET0 Calculation ==============

    def calculate_et0_penman_monteith(self, weather_data: WeatherData) -> float:
        """
        حساب التبخر المرجعي بطريقة Penman-Monteith (FAO-56)
        Calculate reference evapotranspiration using Penman-Monteith method

        المعادلة الكاملة من FAO-56:
        ET0 = (0.408 * Δ * (Rn - G) + γ * (900/(T+273)) * u2 * (es - ea)) /
              (Δ + γ * (1 + 0.34 * u2))

        Args:
            weather_data: بيانات الطقس - Weather data

        Returns:
            float: التبخر المرجعي (مم/يوم) - Reference ET0 (mm/day)
        """
        # معاملات الحساب - Calculation parameters
        T = weather_data.temp_mean or (weather_data.temp_max + weather_data.temp_min) / 2
        T_max = weather_data.temp_max
        T_min = weather_data.temp_min
        u2 = weather_data.wind_speed
        lat = weather_data.latitude
        elev = weather_data.elevation

        # الضغط الجوي - Atmospheric pressure (kPa)
        P = 101.3 * ((293 - 0.0065 * elev) / 293) ** 5.26

        # ثابت البسيكرومتر - Psychrometric constant (kPa/°C)
        gamma = 0.000665 * P

        # ميل منحنى ضغط البخار - Slope of saturation vapour pressure curve (kPa/°C)
        delta = 4098 * (0.6108 * math.exp((17.27 * T) / (T + 237.3))) / ((T + 237.3) ** 2)

        # ضغط البخار المشبع - Saturation vapour pressure (kPa)
        e_T_max = 0.6108 * math.exp((17.27 * T_max) / (T_max + 237.3))
        e_T_min = 0.6108 * math.exp((17.27 * T_min) / (T_min + 237.3))
        es = (e_T_max + e_T_min) / 2

        # ضغط البخار الفعلي - Actual vapour pressure (kPa)
        if weather_data.humidity_mean:
            RH_mean = weather_data.humidity_mean
            ea = es * (RH_mean / 100)
        elif weather_data.humidity_max and weather_data.humidity_min:
            ea = (
                e_T_min * (weather_data.humidity_max / 100)
                + e_T_max * (weather_data.humidity_min / 100)
            ) / 2
        else:
            ea = es * 0.7  # افتراض 70% رطوبة - Assume 70% humidity

        # الإشعاع الصافي - Net radiation (MJ/m²/day)
        if weather_data.solar_radiation:
            Rs = weather_data.solar_radiation
        else:
            # تقدير الإشعاع الشمسي من ساعات السطوع
            # Estimate solar radiation from sunshine hours
            Rs = self._estimate_solar_radiation(
                lat, weather_data.date, weather_data.sunshine_hours or 8
            )

        # الإشعاع خارج الغلاف الجوي - Extraterrestrial radiation
        Ra = self._calculate_extraterrestrial_radiation(lat, weather_data.date)

        # الإشعاع الصافي - Net radiation
        albedo = 0.23  # معامل الانعكاس للمراعي - Albedo for grass reference
        Rns = (1 - albedo) * Rs  # الإشعاع الشمسي الصافي قصير الموجة

        # الإشعاع طويل الموجة الصافي - Net longwave radiation
        stefan_boltzmann = 4.903e-9  # MJ/K⁴/m²/day
        Rnl = (
            stefan_boltzmann
            * (((T_max + 273.16) ** 4 + (T_min + 273.16) ** 4) / 2)
            * (0.34 - 0.14 * math.sqrt(ea))
            * (1.35 * (Rs / Ra) - 0.35)
        )

        Rn = Rns - Rnl

        # تدفق الحرارة في التربة - Soil heat flux (MJ/m²/day)
        # للحسابات اليومية يُفترض أنه صفر - For daily calculations, assumed zero
        G = 0

        # معادلة Penman-Monteith الكاملة - Full Penman-Monteith equation
        numerator = 0.408 * delta * (Rn - G) + gamma * (900 / (T + 273)) * u2 * (es - ea)
        denominator = delta + gamma * (1 + 0.34 * u2)

        et0 = numerator / denominator

        # التأكد من أن القيمة موجبة ومنطقية - Ensure positive and reasonable value
        et0 = max(0, min(et0, 15))  # الحد الأقصى 15 مم/يوم

        return et0

    def _estimate_solar_radiation(
        self, latitude: float, date_val: date, sunshine_hours: float
    ) -> float:
        """
        تقدير الإشعاع الشمسي من ساعات السطوع
        Estimate solar radiation from sunshine hours
        """
        # الإشعاع خارج الغلاف الجوي
        Ra = self._calculate_extraterrestrial_radiation(latitude, date_val)

        # أقصى ساعات نهار محتملة
        N = self._calculate_daylight_hours(latitude, date_val)

        # معادلة Angström - Angström formula
        # Rs = (as + bs * (n/N)) * Ra
        # as = 0.25, bs = 0.50 (قيم افتراضية)
        as_coeff = 0.25
        bs_coeff = 0.50

        Rs = (as_coeff + bs_coeff * (sunshine_hours / N)) * Ra

        return Rs

    def _calculate_extraterrestrial_radiation(self, latitude: float, date_val: date) -> float:
        """
        حساب الإشعاع خارج الغلاف الجوي
        Calculate extraterrestrial radiation (Ra)
        """
        # تحويل خط العرض إلى راديان
        lat_rad = latitude * math.pi / 180

        # رقم اليوم في السنة - Day of year
        J = date_val.timetuple().tm_yday

        # الميل الشمسي - Solar declination (rad)
        delta = 0.409 * math.sin((2 * math.pi / 365) * J - 1.39)

        # المسافة العكسية النسبية للأرض-الشمس
        dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * J)

        # زاوية شروق الشمس - Sunset hour angle (rad)
        ws = math.acos(-math.tan(lat_rad) * math.tan(delta))

        # ثابت الإشعاع الشمسي - Solar constant
        Gsc = 0.0820  # MJ/m²/min

        # الإشعاع خارج الغلاف الجوي
        Ra = (
            (24 * 60 / math.pi)
            * Gsc
            * dr
            * (
                ws * math.sin(lat_rad) * math.sin(delta)
                + math.cos(lat_rad) * math.cos(delta) * math.sin(ws)
            )
        )

        return Ra

    def _calculate_daylight_hours(self, latitude: float, date_val: date) -> float:
        """
        حساب أقصى ساعات النهار
        Calculate maximum daylight hours
        """
        lat_rad = latitude * math.pi / 180
        J = date_val.timetuple().tm_yday
        delta = 0.409 * math.sin((2 * math.pi / 365) * J - 1.39)
        ws = math.acos(-math.tan(lat_rad) * math.tan(delta))

        N = (24 / math.pi) * ws

        return N

    # ============== حساب الأمطار الفعالة - Effective Rainfall ==============

    def calculate_effective_rainfall(self, total_rainfall: float, soil_type: SoilType) -> float:
        """
        حساب الأمطار الفعالة (الجزء الذي يستفيد منه المحصول)
        Calculate effective rainfall using USDA method

        Args:
            total_rainfall: إجمالي الأمطار (مم) - Total rainfall (mm)
            soil_type: نوع التربة - Soil type

        Returns:
            float: الأمطار الفعالة (مم) - Effective rainfall (mm)
        """
        # طريقة USDA SCS - USDA SCS method
        if total_rainfall < 250:
            Pe = (total_rainfall * (125 - 0.2 * total_rainfall)) / 125
        else:
            Pe = 125 + 0.1 * total_rainfall

        # تعديل حسب نوع التربة - Adjust for soil type
        soil_efficiency = {
            SoilType.SANDY: 0.7,  # تسرب عالي - High percolation
            SoilType.LOAMY: 0.9,  # مثالي
            SoilType.CLAY: 0.95,  # احتفاظ عالي - High retention
            SoilType.SILTY: 0.85,
            SoilType.ROCKY: 0.5,  # جريان سطحي عالي - High runoff
        }

        efficiency = soil_efficiency.get(soil_type, 0.8)
        Pe = Pe * efficiency

        return min(Pe, total_rainfall)

    # ============== توازن المياه - Water Balance ==============

    def calculate_water_balance(
        self,
        field_id: str,
        date_val: date,
        weather_data: WeatherData,
        crop_type: CropType,
        growth_stage: GrowthStage,
        soil_properties: SoilProperties,
        irrigation_amount: float = 0.0,
        previous_balance: WaterBalance | None = None,
    ) -> WaterBalance:
        """
        حساب توازن المياه في التربة
        Calculate soil water balance

        Args:
            field_id: معرّف الحقل
            date_val: التاريخ
            weather_data: بيانات الطقس
            crop_type: نوع المحصول
            growth_stage: مرحلة النمو
            soil_properties: خصائص التربة
            irrigation_amount: كمية الري (مم)
            previous_balance: التوازن السابق

        Returns:
            WaterBalance: توازن المياه
        """
        # حساب ET0 - Calculate ET0
        et0 = self.calculate_et0_penman_monteith(weather_data)

        # حساب ETc - Calculate ETc
        kc = self._get_crop_coefficient(crop_type, growth_stage)
        etc = et0 * kc

        # حساب الأمطار الفعالة - Calculate effective rainfall
        effective_rain = self.calculate_effective_rainfall(
            weather_data.rainfall, soil_properties.soil_type
        )

        # المحتوى المائي السابق - Previous water content
        previous_content = (
            previous_balance.soil_water_content
            if previous_balance
            else soil_properties.total_available_water * 0.5  # ابدأ بـ 50%
        )

        # حساب المحتوى المائي الجديد - Calculate new water content
        # المحتوى الجديد = السابق + الري + الأمطار الفعالة - التبخر
        new_content = previous_content + irrigation_amount + effective_rain - etc

        # الحد الأقصى للمحتوى المائي - Maximum water content
        max_content = soil_properties.total_available_water

        # إذا تجاوز الحد الأقصى، هناك تصريف - If exceeds max, drainage occurs
        if new_content > max_content:
            new_content - max_content
            new_content = max_content
        else:
            pass

        # حساب عجز المياه - Calculate water deficit
        deficit = max(0, soil_properties.readily_available_water - new_content)

        return WaterBalance(
            field_id=field_id,
            date=date_val,
            irrigation=irrigation_amount,
            rainfall=weather_data.rainfall,
            effective_rainfall=effective_rain,
            et0=et0,
            etc=etc,
            soil_water_content=new_content,
            water_deficit=deficit,
        )

    # ============== جدولة الري - Irrigation Scheduling ==============

    def get_optimal_schedule(
        self,
        field_id: str,
        tenant_id: str,
        crop_type: CropType,
        growth_stage: GrowthStage,
        soil_type: SoilType,
        irrigation_type: IrrigationType,
        weather_forecast: list[WeatherData],
        field_area_ha: float,
        start_date: date | None = None,
        optimize_for_cost: bool = True,
        electricity_night_discount: float = 0.3,
    ) -> IrrigationSchedule:
        """
        إنشاء جدول ري محسّن
        Generate optimized irrigation schedule

        Args:
            field_id: معرّف الحقل
            tenant_id: معرّف المستأجر
            crop_type: نوع المحصول
            growth_stage: مرحلة النمو
            soil_type: نوع التربة
            irrigation_type: نوع نظام الري
            weather_forecast: توقعات الطقس (7-14 يوم)
            field_area_ha: مساحة الحقل (هكتار)
            start_date: تاريخ البداية
            optimize_for_cost: تحسين التكلفة (ري ليلي)
            electricity_night_discount: خصم الكهرباء الليلي

        Returns:
            IrrigationSchedule: جدول الري المحسّن
        """
        if not start_date:
            start_date = date.today()

        # الحصول على خصائص التربة - Get soil properties
        soil_props_data = self.soil_properties_table[soil_type]
        soil_properties = SoilProperties(
            soil_type=soil_type,
            field_capacity=soil_props_data["field_capacity"],
            wilting_point=soil_props_data["wilting_point"],
            infiltration_rate=soil_props_data["infiltration_rate"],
            bulk_density=soil_props_data["bulk_density"],
        )

        # إنشاء جدول الري - Create irrigation schedule
        schedule = IrrigationSchedule(
            field_id=field_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=start_date + timedelta(days=len(weather_forecast) - 1),
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_type=soil_type,
            metadata={"field_area_ha": field_area_ha},
        )

        # تتبع توازن المياه - Track water balance
        current_balance = None

        for i, weather in enumerate(weather_forecast):
            current_date = start_date + timedelta(days=i)

            # حساب توازن المياه بدون ري - Calculate water balance without irrigation
            temp_balance = self.calculate_water_balance(
                field_id=field_id,
                date_val=current_date,
                weather_data=weather,
                crop_type=crop_type,
                growth_stage=growth_stage,
                soil_properties=soil_properties,
                irrigation_amount=0,
                previous_balance=current_balance,
            )

            # تحديد ما إذا كان الري مطلوباً - Determine if irrigation is needed
            irrigation_needed = self._is_irrigation_needed(
                temp_balance, soil_properties, crop_type, growth_stage
            )

            if irrigation_needed:
                # حساب كمية الري المطلوبة - Calculate required irrigation
                irrigation_amount = self._calculate_irrigation_amount(
                    temp_balance, soil_properties, irrigation_type
                )

                # إعادة حساب التوازن مع الري - Recalculate with irrigation
                current_balance = self.calculate_water_balance(
                    field_id=field_id,
                    date_val=current_date,
                    weather_data=weather,
                    crop_type=crop_type,
                    growth_stage=growth_stage,
                    soil_properties=soil_properties,
                    irrigation_amount=irrigation_amount,
                    previous_balance=current_balance,
                )

                # تحديد أفضل وقت للري - Determine best irrigation time
                if optimize_for_cost:
                    # الري الليلي (23:00 - 05:00) لتوفير الكهرباء
                    # Night irrigation (23:00 - 05:00) to save electricity
                    scheduled_time = datetime.combine(
                        current_date, datetime.min.time()
                    ) + timedelta(hours=23)
                    is_night = True
                else:
                    # الري الصباحي (06:00) لتقليل التبخر
                    # Morning irrigation (06:00) to reduce evaporation
                    scheduled_time = datetime.combine(
                        current_date, datetime.min.time()
                    ) + timedelta(hours=6)
                    is_night = False

                # حساب مدة الري - Calculate irrigation duration
                flow_rate = self._estimate_flow_rate(irrigation_type, field_area_ha)
                duration_min = int((irrigation_amount * field_area_ha * 10) / flow_rate)

                # إنشاء حدث الري - Create irrigation event
                event = IrrigationEvent(
                    field_id=field_id,
                    scheduled_date=scheduled_time,
                    duration_minutes=duration_min,
                    water_amount_mm=irrigation_amount,
                    water_amount_m3=irrigation_amount * field_area_ha * 10,
                    irrigation_type=irrigation_type,
                    is_night_irrigation=is_night,
                    priority=self._calculate_priority(current_balance, soil_properties),
                    metadata={
                        "field_area_ha": field_area_ha,
                        "deficit": temp_balance.water_deficit,
                    },
                )

                schedule.add_event(event)
            else:
                # لا حاجة للري - No irrigation needed
                current_balance = temp_balance

        # حساب الإحصائيات - Calculate statistics
        schedule = self._calculate_schedule_statistics(schedule, electricity_night_discount)

        return schedule

    def _is_irrigation_needed(
        self,
        water_balance: WaterBalance,
        soil_properties: SoilProperties,
        crop_type: CropType,
        growth_stage: GrowthStage,
    ) -> bool:
        """
        تحديد ما إذا كان الري مطلوباً
        Determine if irrigation is needed
        """
        # الحصول على عامل الاستنزاف - Get depletion factor (p)
        crop_data = self.crop_kc_table.get(crop_type, {}).get(growth_stage, {})
        p_value = crop_data.get("p", 0.5)

        # حد الري = p * TAW
        # Irrigation threshold = p * TAW
        threshold = p_value * soil_properties.total_available_water

        # الري مطلوب إذا كان المحتوى المائي أقل من الحد
        # Irrigation needed if water content below threshold
        return water_balance.soil_water_content < threshold

    def _calculate_irrigation_amount(
        self,
        water_balance: WaterBalance,
        soil_properties: SoilProperties,
        irrigation_type: IrrigationType,
    ) -> float:
        """
        حساب كمية الري المطلوبة
        Calculate required irrigation amount
        """
        # ملء التربة إلى السعة الحقلية - Fill soil to field capacity
        target_content = soil_properties.total_available_water
        deficit = target_content - water_balance.soil_water_content

        # تعديل حسب كفاءة النظام - Adjust for system efficiency
        efficiency = self.irrigation_efficiency.get(irrigation_type, 0.75)
        gross_irrigation = deficit / efficiency

        return max(0, gross_irrigation)

    def _calculate_priority(
        self,
        water_balance: WaterBalance,
        soil_properties: SoilProperties,
    ) -> int:
        """
        حساب أولوية الري (1 = أعلى، 5 = أدنى)
        Calculate irrigation priority (1 = highest, 5 = lowest)
        """
        # النسبة المئوية للمحتوى المائي - Water content percentage
        water_percent = water_balance.soil_water_content / soil_properties.total_available_water

        if water_percent < 0.3:
            return 1  # حرج - Critical
        elif water_percent < 0.5:
            return 2  # مرتفع - High
        elif water_percent < 0.7:
            return 3  # متوسط - Medium
        else:
            return 4  # منخفض - Low

    def _estimate_flow_rate(self, irrigation_type: IrrigationType, area_ha: float) -> float:
        """
        تقدير معدل التدفق (م³/ساعة)
        Estimate flow rate (m³/hour)
        """
        # معدلات تدفق تقريبية - Approximate flow rates
        base_rates = {
            IrrigationType.DRIP: 2.0,  # م³/ساعة/هكتار
            IrrigationType.SPRINKLER: 15.0,
            IrrigationType.SURFACE: 30.0,
            IrrigationType.SUBSURFACE: 2.5,
            IrrigationType.CENTER_PIVOT: 20.0,
        }

        base_rate = base_rates.get(irrigation_type, 10.0)
        return base_rate * area_ha

    def _calculate_schedule_statistics(
        self,
        schedule: IrrigationSchedule,
        electricity_discount: float = 0.3,
    ) -> IrrigationSchedule:
        """
        حساب إحصائيات الجدول
        Calculate schedule statistics
        """
        if not schedule.events:
            return schedule

        # متوسط الفترة بين الريات - Average interval
        dates = sorted([e.scheduled_date.date() for e in schedule.events])
        if len(dates) > 1:
            intervals = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            schedule.average_interval_days = sum(intervals) / len(intervals)

        # تكاليف الكهرباء - Electricity costs
        # افتراض: 0.5 ريال/كيلو واط ساعة، 1 كيلو واط/م³
        # Assumption: 0.5 YER/kWh, 1 kW/m³
        total_cost = 0
        night_events = 0

        for event in schedule.events:
            cost_per_m3 = 0.5  # ريال/م³
            if event.is_night_irrigation:
                cost_per_m3 *= 1 - electricity_discount
                night_events += 1

            if event.water_amount_m3:
                total_cost += event.water_amount_m3 * cost_per_m3

        schedule.estimated_electricity_cost = total_cost

        # نقاط التحسين - Optimization score
        # أعلى نقاط للري الليلي وكفاءة المياه
        # Higher score for night irrigation and water efficiency
        night_ratio = night_events / len(schedule.events) if schedule.events else 0
        schedule.optimization_score = min(100, 70 + night_ratio * 30)

        # كفاءة المياه - Water efficiency
        # بناءً على تقليل الهدر وتوقيت الري
        schedule.water_efficiency_score = min(
            100,
            60 + night_ratio * 20 + (1 if schedule.average_interval_days > 3 else 0) * 20,
        )

        return schedule

    # ============== دوال مساعدة - Helper Functions ==============

    def _get_crop_coefficient(self, crop_type: CropType, growth_stage: GrowthStage) -> float:
        """
        الحصول على معامل المحصول
        Get crop coefficient (Kc)
        """
        crop_data = self.crop_kc_table.get(crop_type, {})
        stage_data = crop_data.get(growth_stage, {})

        return stage_data.get("kc", 1.0)

    def get_irrigation_recommendation(
        self,
        field_id: str,
        water_balance: WaterBalance,
        soil_properties: SoilProperties,
        crop_type: CropType,
        growth_stage: GrowthStage,
        weather_forecast: list[WeatherData],
    ) -> IrrigationRecommendation:
        """
        الحصول على توصية ري
        Get irrigation recommendation
        """
        # تحديد ما إذا كان الري مطلوباً
        should_irrigate = self._is_irrigation_needed(
            water_balance, soil_properties, crop_type, growth_stage
        )

        # حساب الكمية الموصى بها
        recommended_amount = 0.0
        urgency = "low"

        if should_irrigate:
            recommended_amount = self._calculate_irrigation_amount(
                water_balance, soil_properties, IrrigationType.DRIP
            )

            # تحديد الأهمية
            water_percent = water_balance.soil_water_content / soil_properties.total_available_water

            if water_percent < 0.3:
                urgency = "critical"
            elif water_percent < 0.5:
                urgency = "high"
            elif water_percent < 0.7:
                urgency = "medium"

        # التحقق من توقعات الأمطار
        rainfall_forecast = sum(w.rainfall for w in weather_forecast[:3])

        # أفضل وقت للري
        best_time = None
        if should_irrigate:
            # الليل للتوفير في الكهرباء
            tomorrow = date.today() + timedelta(days=1)
            best_time = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=23)

        return IrrigationRecommendation(
            field_id=field_id,
            should_irrigate=should_irrigate,
            recommended_amount_mm=recommended_amount,
            urgency=urgency,
            water_deficit_mm=water_balance.water_deficit,
            rainfall_forecast_mm=rainfall_forecast,
            best_time_start=best_time,
            notes="ري ليلي موصى به لتوفير الكهرباء" if should_irrigate else None,
        )


# ============== مصدّر الوحدة - Module Exports ==============

__all__ = [
    "IrrigationScheduler",
    "YEMEN_CROP_KC_TABLE",
    "SOIL_PROPERTIES_TABLE",
    "IRRIGATION_EFFICIENCY",
]
