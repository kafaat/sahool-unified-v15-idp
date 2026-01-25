"""
SAHOOL Field Health API
واجهة برمجة تطبيقات صحة الحقل

POST /api/v1/field-health - تحليل صحة الحقل الزراعي
Field health analysis endpoint with AI-powered insights
"""

from datetime import timezone, datetime, UTC
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ============== Request/Response Models ==============
# نماذج الطلب والاستجابة


class SensorData(BaseModel):
    """بيانات أجهزة الاستشعار - Sensor data from IoT devices"""

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=100,
        description="رطوبة التربة بالنسبة المئوية - Soil moisture percentage (0-100%)",
    )
    temperature: float = Field(
        ..., ge=-50, le=60, description="درجة الحرارة بالدرجات المئوية - Temperature in Celsius"
    )
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="الرطوبة النسبية بالنسبة المئوية - Relative humidity percentage",
    )


class NDVIData(BaseModel):
    """بيانات مؤشر الغطاء النباتي - NDVI vegetation index data"""

    ndvi_value: float = Field(..., ge=-1, le=1, description="قيمة مؤشر NDVI - NDVI value (-1 to 1)")
    image_date: str | None = Field(
        None, description="تاريخ التقاط صورة القمر الصناعي - Satellite image capture date"
    )
    cloud_coverage: float | None = Field(
        None, ge=0, le=100, description="نسبة تغطية السحب - Cloud coverage percentage"
    )


class WeatherData(BaseModel):
    """بيانات الطقس - Weather data"""

    precipitation: float = Field(
        ..., ge=0, description="هطول الأمطار بالملليمتر - Precipitation in mm"
    )
    wind_speed: float | None = Field(
        None, ge=0, description="سرعة الرياح بالكيلومتر/ساعة - Wind speed in km/h"
    )
    forecast_days: int | None = Field(
        7, ge=1, le=14, description="أيام التنبؤ - Forecast days ahead"
    )


class FieldHealthRequest(BaseModel):
    """طلب تحليل صحة الحقل - Field health analysis request"""

    field_id: str = Field(..., description="معرف الحقل - Field identifier")
    crop_type: str = Field(..., description="نوع المحصول - Crop type")
    sensor_data: SensorData = Field(..., description="بيانات أجهزة الاستشعار - Sensor readings")
    ndvi_data: NDVIData = Field(..., description="بيانات الغطاء النباتي - NDVI data")
    weather_data: WeatherData = Field(..., description="بيانات الطقس - Weather information")


class RiskFactor(BaseModel):
    """عامل خطر - Risk factor identified"""

    type: str = Field(..., description="نوع الخطر - Risk type")
    severity: str = Field(..., description="شدة الخطر - Severity: low, medium, high, critical")
    description_ar: str = Field(..., description="وصف الخطر بالعربية - Description in Arabic")
    description_en: str = Field(..., description="وصف الخطر بالإنجليزية - Description in English")
    impact_score: float = Field(..., ge=0, le=100, description="تأثير الخطر - Impact score")


class FieldHealthResponse(BaseModel):
    """استجابة تحليل صحة الحقل - Field health analysis response"""

    field_id: str = Field(..., description="معرف الحقل - Field ID")
    crop_type: str = Field(..., description="نوع المحصول - Crop type")
    overall_health_score: float = Field(
        ..., ge=0, le=100, description="درجة الصحة الإجمالية - Overall health score (0-100)"
    )
    health_status: str = Field(
        ..., description="حالة الصحة - Health status: excellent, good, fair, poor, critical"
    )
    health_status_ar: str = Field(..., description="حالة الصحة بالعربية - Health status in Arabic")

    # Component scores - درجات المكونات
    ndvi_score: float = Field(..., ge=0, le=100, description="درجة الغطاء النباتي - NDVI score")
    soil_moisture_score: float = Field(
        ..., ge=0, le=100, description="درجة رطوبة التربة - Soil moisture score"
    )
    weather_score: float = Field(..., ge=0, le=100, description="درجة الطقس - Weather score")
    sensor_anomaly_score: float = Field(
        ..., ge=0, le=100, description="درجة شذوذ الأجهزة - Sensor anomaly score"
    )

    risk_factors: list[RiskFactor] = Field(
        default_factory=list, description="عوامل الخطر المحددة - Identified risk factors"
    )
    recommendations_ar: list[str] = Field(
        default_factory=list, description="التوصيات بالعربية - Recommendations in Arabic"
    )
    recommendations_en: list[str] = Field(
        default_factory=list, description="التوصيات بالإنجليزية - Recommendations in English"
    )

    analysis_timestamp: str = Field(..., description="وقت التحليل - Analysis timestamp")
    metadata: dict[str, Any] | None = Field(None, description="بيانات إضافية - Additional metadata")


# ============== Router Setup ==============
# إعداد الموجه

router = APIRouter(prefix="/api/v1", tags=["field-health"])


# ============== Helper Functions ==============
# الدوال المساعدة


def calculate_ndvi_score(ndvi_data: NDVIData, crop_type: str) -> float:
    """
    حساب درجة صحة النبات من مؤشر NDVI
    Calculate plant health score from NDVI index

    Args:
        ndvi_data: بيانات مؤشر NDVI - NDVI data
        crop_type: نوع المحصول - Crop type

    Returns:
        درجة من 0-100 - Score from 0-100
    """
    ndvi = ndvi_data.ndvi_value

    # تصنيف قيم NDVI - NDVI value classification
    # -1 to 0: ماء أو سطح غير نباتي - Water or non-vegetation
    # 0 to 0.2: تربة عارية أو نباتات ضعيفة - Bare soil or sparse vegetation
    # 0.2 to 0.4: نباتات متوسطة - Moderate vegetation
    # 0.4 to 0.6: نباتات صحية - Healthy vegetation
    # 0.6 to 1.0: نباتات كثيفة جداً - Very dense vegetation

    if ndvi < 0:
        score = 0
    elif ndvi < 0.2:
        score = ndvi / 0.2 * 30  # 0-30 range
    elif ndvi < 0.4:
        score = 30 + ((ndvi - 0.2) / 0.2) * 30  # 30-60 range
    elif ndvi < 0.6:
        score = 60 + ((ndvi - 0.4) / 0.2) * 25  # 60-85 range
    else:
        score = 85 + ((ndvi - 0.6) / 0.4) * 15  # 85-100 range

    # تعديل بناءً على تغطية السحب - Adjust for cloud coverage
    if ndvi_data.cloud_coverage and ndvi_data.cloud_coverage > 30:
        # تقليل الثقة في القراءة عند وجود سحب كثيفة
        # Reduce confidence when heavy cloud coverage
        score = score * (1 - (ndvi_data.cloud_coverage - 30) / 100)

    return min(100, max(0, score))


def calculate_soil_moisture_score(sensor_data: SensorData, crop_type: str) -> float:
    """
    حساب درجة رطوبة التربة المثلى
    Calculate optimal soil moisture score

    Args:
        sensor_data: بيانات الأجهزة - Sensor data
        crop_type: نوع المحصول - Crop type

    Returns:
        درجة من 0-100 - Score from 0-100
    """
    moisture = sensor_data.soil_moisture

    # نطاقات الرطوبة المثلى حسب نوع المحصول
    # Optimal moisture ranges by crop type
    optimal_ranges = {
        "wheat": (25, 35),  # قمح - Wheat
        "corn": (30, 40),  # ذرة - Corn
        "rice": (60, 80),  # أرز - Rice
        "tomato": (25, 35),  # طماطم - Tomato
        "potato": (30, 40),  # بطاطس - Potato
        "cotton": (20, 30),  # قطن - Cotton
        "default": (25, 40),  # افتراضي - Default
    }

    # الحصول على النطاق المثلى - Get optimal range
    optimal_min, optimal_max = optimal_ranges.get(crop_type.lower(), optimal_ranges["default"])

    if optimal_min <= moisture <= optimal_max:
        # رطوبة مثالية - Optimal moisture
        score = 100
    elif moisture < optimal_min:
        # جفاف - Too dry
        if moisture < optimal_min * 0.5:
            score = 20  # جفاف شديد - Severe drought
        else:
            score = 50 + (moisture - optimal_min * 0.5) / (optimal_min * 0.5) * 50
    else:
        # رطوبة زائدة - Too wet
        if moisture > optimal_max * 1.5:
            score = 20  # غمر شديد - Severe waterlogging
        else:
            score = 100 - (moisture - optimal_max) / (optimal_max * 0.5) * 50

    return min(100, max(0, score))


def calculate_weather_score(weather_data: WeatherData, crop_type: str) -> float:
    """
    حساب درجة ملاءمة الطقس
    Calculate weather suitability score

    Args:
        weather_data: بيانات الطقس - Weather data
        crop_type: نوع المحصول - Crop type

    Returns:
        درجة من 0-100 - Score from 0-100
    """
    score = 100

    # تقييم هطول الأمطار - Evaluate precipitation
    precipitation = weather_data.precipitation

    if precipitation == 0:
        # لا أمطار - No rain
        score -= 15
    elif precipitation > 50:
        # أمطار غزيرة جداً - Very heavy rain
        score -= 25
    elif precipitation > 30:
        # أمطار غزيرة - Heavy rain
        score -= 10

    # تقييم سرعة الرياح - Evaluate wind speed
    if weather_data.wind_speed:
        if weather_data.wind_speed > 50:
            # رياح عاصفة - Storm winds
            score -= 30
        elif weather_data.wind_speed > 30:
            # رياح قوية - Strong winds
            score -= 15

    return min(100, max(0, score))


def calculate_sensor_anomaly_score(sensor_data: SensorData) -> float:
    """
    كشف الشذوذ في قراءات الأجهزة
    Detect anomalies in sensor readings

    Args:
        sensor_data: بيانات الأجهزة - Sensor data

    Returns:
        درجة من 0-100 (100 = لا شذوذ) - Score from 0-100 (100 = no anomaly)
    """
    score = 100
    anomalies = 0

    # فحص نطاقات القراءات غير الطبيعية
    # Check for abnormal reading ranges

    # درجة حرارة خارج النطاق المعقول - Temperature out of reasonable range
    if sensor_data.temperature < -10 or sensor_data.temperature > 50:
        score -= 30
        anomalies += 1
    elif sensor_data.temperature < 0 or sensor_data.temperature > 45:
        score -= 15
        anomalies += 1

    # رطوبة غير متناسقة - Inconsistent humidity
    if sensor_data.humidity < 10 or sensor_data.humidity > 95:
        score -= 20
        anomalies += 1

    # تحقق من التناسق بين الرطوبة ورطوبة التربة
    # Check consistency between humidity and soil moisture
    if sensor_data.humidity > 80 and sensor_data.soil_moisture < 20:
        # رطوبة جوية عالية لكن تربة جافة - High air humidity but dry soil
        score -= 15
        anomalies += 1

    return min(100, max(0, score))


def identify_risk_factors(
    request: FieldHealthRequest,
    ndvi_score: float,
    soil_score: float,
    weather_score: float,
    sensor_score: float,
) -> list[RiskFactor]:
    """
    تحديد عوامل الخطر
    Identify risk factors based on analysis

    Returns:
        قائمة عوامل الخطر - List of risk factors
    """
    risks = []

    # خطر ضعف النمو النباتي - Poor vegetation growth risk
    if ndvi_score < 40:
        risks.append(
            RiskFactor(
                type="vegetation_stress",
                severity="critical" if ndvi_score < 20 else "high",
                description_ar="ضعف شديد في النمو النباتي يتطلب تدخل فوري",
                description_en="Severe vegetation stress requiring immediate intervention",
                impact_score=100 - ndvi_score,
            )
        )
    elif ndvi_score < 60:
        risks.append(
            RiskFactor(
                type="vegetation_stress",
                severity="medium",
                description_ar="إجهاد نباتي متوسط قد يؤثر على الإنتاجية",
                description_en="Moderate vegetation stress may affect productivity",
                impact_score=60 - ndvi_score,
            )
        )

    # خطر الجفاف أو الغمر - Drought or waterlogging risk
    if soil_score < 40:
        moisture = request.sensor_data.soil_moisture
        if moisture < 20:
            risks.append(
                RiskFactor(
                    type="drought",
                    severity="high",
                    description_ar="جفاف شديد في التربة يتطلب ري فوري",
                    description_en="Severe soil drought requiring immediate irrigation",
                    impact_score=80,
                )
            )
        else:
            risks.append(
                RiskFactor(
                    type="waterlogging",
                    severity="high",
                    description_ar="رطوبة زائدة في التربة قد تسبب تعفن الجذور",
                    description_en="Excessive soil moisture may cause root rot",
                    impact_score=70,
                )
            )

    # خطر الطقس السيء - Adverse weather risk
    if weather_score < 60:
        if request.weather_data.precipitation > 50:
            risks.append(
                RiskFactor(
                    type="heavy_rain",
                    severity="medium",
                    description_ar="أمطار غزيرة قد تؤثر على العمليات الزراعية",
                    description_en="Heavy rainfall may affect agricultural operations",
                    impact_score=50,
                )
            )

        if request.weather_data.wind_speed and request.weather_data.wind_speed > 40:
            risks.append(
                RiskFactor(
                    type="strong_winds",
                    severity="high",
                    description_ar="رياح قوية قد تضر بالمحاصيل",
                    description_en="Strong winds may damage crops",
                    impact_score=60,
                )
            )

    # خطر أعطال الأجهزة - Sensor malfunction risk
    if sensor_score < 70:
        risks.append(
            RiskFactor(
                type="sensor_anomaly",
                severity="low",
                description_ar="قراءات شاذة من الأجهزة تحتاج للمراجعة",
                description_en="Anomalous sensor readings need review",
                impact_score=30,
            )
        )

    return risks


def generate_recommendations(
    request: FieldHealthRequest,
    overall_score: float,
    risk_factors: list[RiskFactor],
    soil_score: float,
    ndvi_score: float,
) -> tuple[list[str], list[str]]:
    """
    توليد التوصيات الزراعية
    Generate agricultural recommendations

    Returns:
        (توصيات بالعربية, توصيات بالإنجليزية) - (Arabic recommendations, English recommendations)
    """
    recommendations_ar = []
    recommendations_en = []

    # توصيات بناءً على درجة الصحة الإجمالية
    # Recommendations based on overall health
    if overall_score < 50:
        recommendations_ar.append("⚠️ الحقل يحتاج لتدخل فوري لتحسين الصحة العامة")
        recommendations_en.append(
            "⚠️ Field requires immediate intervention to improve overall health"
        )

    # توصيات رطوبة التربة - Soil moisture recommendations
    moisture = request.sensor_data.soil_moisture
    if moisture < 20:
        recommendations_ar.append("💧 تنفيذ خطة ري عاجلة لمعالجة الجفاف الشديد")
        recommendations_en.append(
            "💧 Implement emergency irrigation plan to address severe drought"
        )
    elif moisture < 30:
        recommendations_ar.append("💧 زيادة معدل الري للوصول للرطوبة المثلى")
        recommendations_en.append("💧 Increase irrigation rate to reach optimal moisture")
    elif moisture > 60:
        recommendations_ar.append("💧 تقليل الري وتحسين الصرف لمنع تعفن الجذور")
        recommendations_en.append("💧 Reduce irrigation and improve drainage to prevent root rot")

    # توصيات النمو النباتي - Vegetation growth recommendations
    if ndvi_score < 40:
        recommendations_ar.append("🌱 فحص نظام التسميد وإجراء تحليل للتربة")
        recommendations_en.append("🌱 Check fertilization system and conduct soil analysis")
        recommendations_ar.append("🔍 فحص المحاصيل للكشف عن الآفات والأمراض")
        recommendations_en.append("🔍 Inspect crops for pests and diseases")

    # توصيات الطقس - Weather recommendations
    if request.weather_data.precipitation > 40:
        recommendations_ar.append("☔ تأجيل عمليات الرش والتسميد حتى تحسن الطقس")
        recommendations_en.append("☔ Postpone spraying and fertilization until weather improves")

    if request.weather_data.wind_speed and request.weather_data.wind_speed > 40:
        recommendations_ar.append("💨 تركيب مصدات رياح لحماية المحاصيل")
        recommendations_en.append("💨 Install windbreaks to protect crops")

    # توصيات الصيانة - Maintenance recommendations
    if any(r.type == "sensor_anomaly" for r in risk_factors):
        recommendations_ar.append("🔧 فحص وصيانة أجهزة الاستشعار للتأكد من دقة القراءات")
        recommendations_en.append("🔧 Check and maintain sensors to ensure accurate readings")

    # توصيات عامة للتحسين - General improvement recommendations
    if overall_score < 70:
        recommendations_ar.append("📊 زيادة تكرار المراقبة لتتبع تحسن الصحة")
        recommendations_en.append("📊 Increase monitoring frequency to track health improvement")

    return recommendations_ar, recommendations_en


def get_health_status(score: float) -> tuple[str, str]:
    """
    تحديد حالة الصحة من الدرجة
    Determine health status from score

    Returns:
        (status_en, status_ar) - Health status in English and Arabic
    """
    if score >= 85:
        return "excellent", "ممتاز"
    elif score >= 70:
        return "good", "جيد"
    elif score >= 50:
        return "fair", "مقبول"
    elif score >= 30:
        return "poor", "ضعيف"
    else:
        return "critical", "حرج"


# ============== API Endpoint ==============
# نقطة النهاية للواجهة البرمجية


@router.post("/field-health", response_model=FieldHealthResponse)
async def analyze_field_health(request: FieldHealthRequest) -> FieldHealthResponse:
    """
    تحليل صحة الحقل الزراعي
    Analyze agricultural field health

    يقوم هذا النقطة بتحليل شامل لصحة الحقل بناءً على:
    This endpoint performs comprehensive field health analysis based on:

    - مؤشر NDVI للغطاء النباتي (40%) - NDVI vegetation index (40%)
    - رطوبة التربة من أجهزة الاستشعار (25%) - Soil moisture from sensors (25%)
    - بيانات الطقس والتنبؤات (20%) - Weather data and forecasts (20%)
    - كشف الشذوذ في قراءات الأجهزة (15%) - Sensor anomaly detection (15%)

    Args:
        request: طلب تحليل صحة الحقل - Field health analysis request

    Returns:
        تحليل شامل مع درجة الصحة والمخاطر والتوصيات
        Comprehensive analysis with health score, risks, and recommendations

    Raises:
        HTTPException: في حالة وجود خطأ في البيانات المدخلة
    """
    try:
        # حساب درجات المكونات المختلفة
        # Calculate component scores

        # 1. درجة مؤشر NDVI - NDVI score (40% weight)
        ndvi_score = calculate_ndvi_score(request.ndvi_data, request.crop_type)

        # 2. درجة رطوبة التربة - Soil moisture score (25% weight)
        soil_moisture_score = calculate_soil_moisture_score(request.sensor_data, request.crop_type)

        # 3. درجة الطقس - Weather score (20% weight)
        weather_score = calculate_weather_score(request.weather_data, request.crop_type)

        # 4. درجة شذوذ الأجهزة - Sensor anomaly score (15% weight)
        sensor_anomaly_score = calculate_sensor_anomaly_score(request.sensor_data)

        # حساب الدرجة الإجمالية بالأوزان المحددة
        # Calculate weighted overall score
        overall_health_score = (
            ndvi_score * 0.40
            + soil_moisture_score * 0.25
            + weather_score * 0.20
            + sensor_anomaly_score * 0.15
        )

        # تحديد حالة الصحة - Determine health status
        health_status, health_status_ar = get_health_status(overall_health_score)

        # تحديد عوامل الخطر - Identify risk factors
        risk_factors = identify_risk_factors(
            request, ndvi_score, soil_moisture_score, weather_score, sensor_anomaly_score
        )

        # توليد التوصيات - Generate recommendations
        recommendations_ar, recommendations_en = generate_recommendations(
            request, overall_health_score, risk_factors, soil_moisture_score, ndvi_score
        )

        # بناء الاستجابة - Build response
        response = FieldHealthResponse(
            field_id=request.field_id,
            crop_type=request.crop_type,
            overall_health_score=round(overall_health_score, 2),
            health_status=health_status,
            health_status_ar=health_status_ar,
            ndvi_score=round(ndvi_score, 2),
            soil_moisture_score=round(soil_moisture_score, 2),
            weather_score=round(weather_score, 2),
            sensor_anomaly_score=round(sensor_anomaly_score, 2),
            risk_factors=risk_factors,
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
            analysis_timestamp=datetime.now(UTC).isoformat(),
            metadata={
                "ndvi_weight": 0.40,
                "soil_moisture_weight": 0.25,
                "weather_weight": 0.20,
                "sensor_anomaly_weight": 0.15,
                "total_risk_factors": len(risk_factors),
                "critical_risks": len([r for r in risk_factors if r.severity == "critical"]),
                "high_risks": len([r for r in risk_factors if r.severity == "high"]),
            },
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error during health analysis: {str(e)}"
        )
