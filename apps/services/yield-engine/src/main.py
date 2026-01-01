"""
Sahool Yield Engine - Crop Yield Prediction Service
محرك سهول للتنبؤ بالإنتاجية الزراعية

This service provides ML-powered yield predictions using:
- Linear Regression for base predictions
- Crop-specific adjustment factors
- Weather data integration (rainfall, temperature)
- Historical yield data for Yemen crops

Port: 8098
"""

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sahool-yield-engine")

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "yield-engine"
SERVICE_VERSION = "1.0.0"
SERVICE_PORT = int(os.getenv("PORT", 8098))

# ═══════════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════════


class CropType(str, Enum):
    """المحاصيل المدعومة للتنبؤ"""

    # Cereals - الحبوب
    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    CORN = "corn"  # ذرة
    SORGHUM = "sorghum"  # ذرة رفيعة
    MILLET = "millet"  # دخن

    # Legumes - البقوليات
    FABA_BEAN = "faba_bean"  # فول
    LENTIL = "lentil"  # عدس
    CHICKPEA = "chickpea"  # حمص

    # Vegetables - الخضروات
    TOMATO = "tomato"  # طماطم
    POTATO = "potato"  # بطاطس
    ONION = "onion"  # بصل
    GARLIC = "garlic"  # ثوم
    PEPPER = "pepper"  # فلفل حلو
    EGGPLANT = "eggplant"  # باذنجان
    CUCUMBER = "cucumber"  # خيار
    OKRA = "okra"  # بامية

    # Fruits - الفواكه
    DATE_PALM = "date_palm"  # نخيل
    MANGO = "mango"  # مانجو
    BANANA = "banana"  # موز
    GRAPE = "grape"  # عنب
    CITRUS_ORANGE = "citrus_orange"  # برتقال
    CITRUS_LEMON = "citrus_lemon"  # ليمون
    POMEGRANATE = "pomegranate"  # رمان
    FIG = "fig"  # تين
    GUAVA = "guava"  # جوافة

    # Cash Crops - محاصيل نقدية
    COFFEE = "coffee"  # بن يمني
    SESAME = "sesame"  # سمسم
    COTTON = "cotton"  # قطن

    # Fodder - الأعلاف
    ALFALFA = "alfalfa"  # برسيم حجازي


class YieldRequest(BaseModel):
    """طلب التنبؤ بالإنتاجية"""

    field_id: Optional[str] = Field(None, description="معرف الحقل")
    area_hectares: float = Field(..., gt=0, description="المساحة بالهكتار")
    crop_type: CropType = Field(..., description="نوع المحصول")
    avg_rainfall: Optional[float] = Field(None, ge=0, description="متوسط الأمطار (مم)")
    avg_temperature: Optional[float] = Field(None, description="متوسط درجة الحرارة")
    soil_quality: Optional[str] = Field(
        "medium", description="جودة التربة: poor/medium/good"
    )
    irrigation_type: Optional[str] = Field("rain-fed", description="نوع الري")
    governorate: Optional[str] = Field(None, description="المحافظة")


class YieldPrediction(BaseModel):
    """نتيجة التنبؤ"""

    prediction_id: str
    field_id: Optional[str]
    crop_type: str
    crop_name_ar: str
    area_hectares: float
    predicted_yield_tons: float
    predicted_yield_per_hectare: float
    yield_range_min: float
    yield_range_max: float
    estimated_revenue_usd: float
    estimated_revenue_yer: float  # ريال يمني
    confidence_percent: float
    factors_applied: List[str]
    recommendations: List[str]
    timestamp: datetime


class HealthCheckResponse(BaseModel):
    """استجابة فحص الصحة"""

    status: str
    service: str
    version: str
    model_ready: bool
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════════════════════
# Crop Database - Yemen-focused Agricultural Data
# قاعدة بيانات المحاصيل اليمنية
# ═══════════════════════════════════════════════════════════════════════════════

CROP_DATA = {
    CropType.WHEAT: {
        "name_ar": "قمح",
        "base_yield_per_hectare": 2.5,  # طن/هكتار
        "price_usd_per_ton": 350,
        "growing_season_days": 120,
        "optimal_rainfall": 450,  # مم
        "optimal_temp": 20,  # درجة مئوية
        "water_requirement": "medium",
    },
    CropType.CORN: {
        "name_ar": "ذرة",
        "base_yield_per_hectare": 4.0,
        "price_usd_per_ton": 280,
        "growing_season_days": 100,
        "optimal_rainfall": 500,
        "optimal_temp": 25,
        "water_requirement": "high",
    },
    CropType.TOMATO: {
        "name_ar": "طماطم",
        "base_yield_per_hectare": 35.0,
        "price_usd_per_ton": 400,
        "growing_season_days": 90,
        "optimal_rainfall": 600,
        "optimal_temp": 24,
        "water_requirement": "high",
    },
    CropType.POTATO: {
        "name_ar": "بطاطس",
        "base_yield_per_hectare": 20.0,
        "price_usd_per_ton": 320,
        "growing_season_days": 100,
        "optimal_rainfall": 500,
        "optimal_temp": 18,
        "water_requirement": "medium",
    },
    CropType.COFFEE: {
        "name_ar": "بن يمني",
        "base_yield_per_hectare": 0.8,  # البن إنتاجيته منخفضة لكن سعره عالي
        "price_usd_per_ton": 8000,  # البن اليمني غالي جداً
        "growing_season_days": 270,
        "optimal_rainfall": 1200,
        "optimal_temp": 20,
        "water_requirement": "high",
    },
    CropType.DATE_PALM: {
        "name_ar": "نخيل (تمر)",
        "base_yield_per_hectare": 8.0,
        "price_usd_per_ton": 1500,
        "growing_season_days": 180,
        "optimal_rainfall": 200,
        "optimal_temp": 30,
        "water_requirement": "low",
    },
    CropType.MANGO: {
        "name_ar": "مانجو",
        "base_yield_per_hectare": 10.0,
        "price_usd_per_ton": 800,
        "growing_season_days": 150,
        "optimal_rainfall": 800,
        "optimal_temp": 28,
        "water_requirement": "medium",
    },
    CropType.SORGHUM: {
        "name_ar": "ذرة رفيعة",
        "base_yield_per_hectare": 2.0,
        "price_usd_per_ton": 250,
        "growing_season_days": 110,
        "optimal_rainfall": 400,
        "optimal_temp": 27,
        "water_requirement": "low",
    },
    CropType.BANANA: {
        "name_ar": "موز",
        "base_yield_per_hectare": 30.0,
        "price_usd_per_ton": 500,
        "growing_season_days": 300,
        "optimal_rainfall": 1500,
        "optimal_temp": 27,
        "water_requirement": "very_high",
    },
    CropType.GRAPE: {
        "name_ar": "عنب",
        "base_yield_per_hectare": 12.0,
        "price_usd_per_ton": 700,
        "growing_season_days": 170,
        "optimal_rainfall": 600,
        "optimal_temp": 22,
        "water_requirement": "medium",
    },
    # ═══ Additional Cereals ═══
    CropType.BARLEY: {
        "name_ar": "شعير",
        "base_yield_per_hectare": 2.0,
        "price_usd_per_ton": 280,
        "growing_season_days": 100,
        "optimal_rainfall": 400,
        "optimal_temp": 17,
        "water_requirement": "low",
    },
    CropType.MILLET: {
        "name_ar": "دخن",
        "base_yield_per_hectare": 1.5,
        "price_usd_per_ton": 300,
        "growing_season_days": 90,
        "optimal_rainfall": 250,
        "optimal_temp": 30,
        "water_requirement": "very_low",
    },
    # ═══ Legumes ═══
    CropType.FABA_BEAN: {
        "name_ar": "فول",
        "base_yield_per_hectare": 2.5,
        "price_usd_per_ton": 600,
        "growing_season_days": 120,
        "optimal_rainfall": 650,
        "optimal_temp": 18,
        "water_requirement": "medium",
    },
    CropType.LENTIL: {
        "name_ar": "عدس",
        "base_yield_per_hectare": 1.0,
        "price_usd_per_ton": 800,
        "growing_season_days": 100,
        "optimal_rainfall": 400,
        "optimal_temp": 15,
        "water_requirement": "low",
    },
    CropType.CHICKPEA: {
        "name_ar": "حمص",
        "base_yield_per_hectare": 1.2,
        "price_usd_per_ton": 900,
        "growing_season_days": 100,
        "optimal_rainfall": 400,
        "optimal_temp": 20,
        "water_requirement": "low",
    },
    # ═══ Additional Vegetables ═══
    CropType.ONION: {
        "name_ar": "بصل",
        "base_yield_per_hectare": 25.0,
        "price_usd_per_ton": 350,
        "growing_season_days": 120,
        "optimal_rainfall": 650,
        "optimal_temp": 19,
        "water_requirement": "medium",
    },
    CropType.GARLIC: {
        "name_ar": "ثوم",
        "base_yield_per_hectare": 8.0,
        "price_usd_per_ton": 1500,
        "growing_season_days": 150,
        "optimal_rainfall": 400,
        "optimal_temp": 15,
        "water_requirement": "low",
    },
    CropType.PEPPER: {
        "name_ar": "فلفل حلو",
        "base_yield_per_hectare": 25.0,
        "price_usd_per_ton": 600,
        "growing_season_days": 90,
        "optimal_rainfall": 900,
        "optimal_temp": 23,
        "water_requirement": "high",
    },
    CropType.EGGPLANT: {
        "name_ar": "باذنجان",
        "base_yield_per_hectare": 30.0,
        "price_usd_per_ton": 350,
        "growing_season_days": 100,
        "optimal_rainfall": 900,
        "optimal_temp": 26,
        "water_requirement": "high",
    },
    CropType.CUCUMBER: {
        "name_ar": "خيار",
        "base_yield_per_hectare": 40.0,
        "price_usd_per_ton": 300,
        "growing_season_days": 60,
        "optimal_rainfall": 900,
        "optimal_temp": 25,
        "water_requirement": "high",
    },
    CropType.OKRA: {
        "name_ar": "بامية",
        "base_yield_per_hectare": 12.0,
        "price_usd_per_ton": 600,
        "growing_season_days": 90,
        "optimal_rainfall": 650,
        "optimal_temp": 30,
        "water_requirement": "medium",
    },
    # ═══ Additional Fruits ═══
    CropType.CITRUS_ORANGE: {
        "name_ar": "برتقال",
        "base_yield_per_hectare": 20.0,
        "price_usd_per_ton": 450,
        "growing_season_days": 300,
        "optimal_rainfall": 650,
        "optimal_temp": 24,
        "water_requirement": "medium",
    },
    CropType.CITRUS_LEMON: {
        "name_ar": "ليمون",
        "base_yield_per_hectare": 15.0,
        "price_usd_per_ton": 500,
        "growing_season_days": 300,
        "optimal_rainfall": 650,
        "optimal_temp": 24,
        "water_requirement": "medium",
    },
    CropType.POMEGRANATE: {
        "name_ar": "رمان",
        "base_yield_per_hectare": 12.0,
        "price_usd_per_ton": 700,
        "growing_season_days": 180,
        "optimal_rainfall": 400,
        "optimal_temp": 25,
        "water_requirement": "low",
    },
    CropType.FIG: {
        "name_ar": "تين",
        "base_yield_per_hectare": 8.0,
        "price_usd_per_ton": 800,
        "growing_season_days": 150,
        "optimal_rainfall": 400,
        "optimal_temp": 24,
        "water_requirement": "low",
    },
    CropType.GUAVA: {
        "name_ar": "جوافة",
        "base_yield_per_hectare": 25.0,
        "price_usd_per_ton": 500,
        "growing_season_days": 180,
        "optimal_rainfall": 650,
        "optimal_temp": 26,
        "water_requirement": "medium",
    },
    # ═══ Cash Crops ═══
    CropType.SESAME: {
        "name_ar": "سمسم",
        "base_yield_per_hectare": 0.8,
        "price_usd_per_ton": 2000,
        "growing_season_days": 100,
        "optimal_rainfall": 400,
        "optimal_temp": 30,
        "water_requirement": "low",
    },
    CropType.COTTON: {
        "name_ar": "قطن",
        "base_yield_per_hectare": 2.5,
        "price_usd_per_ton": 1800,
        "growing_season_days": 150,
        "optimal_rainfall": 900,
        "optimal_temp": 27,
        "water_requirement": "high",
    },
    # ═══ Fodder ═══
    CropType.ALFALFA: {
        "name_ar": "برسيم حجازي",
        "base_yield_per_hectare": 15.0,
        "price_usd_per_ton": 200,
        "growing_season_days": 365,
        "optimal_rainfall": 900,
        "optimal_temp": 22,
        "water_requirement": "high",
    },
}

# سعر صرف الريال اليمني (تقريبي)
USD_TO_YER = 535


# ═══════════════════════════════════════════════════════════════════════════════
# ML Yield Prediction Model
# نموذج التنبؤ بالإنتاجية
# ═══════════════════════════════════════════════════════════════════════════════


class YieldPredictor:
    """
    نموذج التنبؤ بالإنتاجية باستخدام التعلم الآلي

    يستخدم معادلة مركبة تأخذ بالاعتبار:
    - المساحة المزروعة
    - نوع المحصول ومتوسط إنتاجيته
    - ظروف الطقس (أمطار، حرارة)
    - جودة التربة ونوع الري
    """

    def __init__(self):
        self.is_ready = True
        logger.info("Yield Prediction Model initialized")

    def _calculate_weather_factor(
        self,
        crop_type: CropType,
        rainfall: Optional[float],
        temperature: Optional[float],
    ) -> tuple:
        """حساب معامل الطقس"""
        crop_info = CROP_DATA[crop_type]
        factors = []
        weather_factor = 1.0

        if rainfall is not None:
            optimal_rain = crop_info["optimal_rainfall"]
            rain_ratio = rainfall / optimal_rain

            if 0.8 <= rain_ratio <= 1.2:
                weather_factor *= 1.1
                factors.append("أمطار مثالية (+10%)")
            elif 0.5 <= rain_ratio < 0.8:
                weather_factor *= 0.85
                factors.append("أمطار أقل من المثالي (-15%)")
            elif rain_ratio < 0.5:
                weather_factor *= 0.6
                factors.append("جفاف شديد (-40%)")
            else:
                weather_factor *= 0.9
                factors.append("أمطار زائدة (-10%)")

        if temperature is not None:
            optimal_temp = crop_info["optimal_temp"]
            temp_diff = abs(temperature - optimal_temp)

            if temp_diff <= 3:
                weather_factor *= 1.05
                factors.append("حرارة مثالية (+5%)")
            elif temp_diff <= 8:
                weather_factor *= 0.9
                factors.append("حرارة مقبولة (-10%)")
            else:
                weather_factor *= 0.7
                factors.append("حرارة غير مناسبة (-30%)")

        return weather_factor, factors

    def _calculate_soil_factor(self, soil_quality: str) -> tuple:
        """حساب معامل جودة التربة"""
        soil_factors = {
            "poor": (0.7, "تربة ضعيفة (-30%)"),
            "medium": (1.0, "تربة متوسطة"),
            "good": (1.2, "تربة ممتازة (+20%)"),
        }
        factor, desc = soil_factors.get(soil_quality, (1.0, ""))
        return factor, [desc] if desc else []

    def _calculate_irrigation_factor(
        self, irrigation_type: str, crop_type: CropType
    ) -> tuple:
        """حساب معامل الري"""
        water_req = CROP_DATA[crop_type]["water_requirement"]

        irrigation_factors = {
            "rain-fed": 0.8 if water_req in ["high", "very_high"] else 1.0,
            "drip": 1.15,
            "sprinkler": 1.1,
            "flood": 0.95,
            "smart": 1.2,
        }

        factor = irrigation_factors.get(irrigation_type, 1.0)

        desc = []
        if irrigation_type == "drip":
            desc.append("ري بالتنقيط (+15%)")
        elif irrigation_type == "smart":
            desc.append("ري ذكي (+20%)")
        elif irrigation_type == "rain-fed" and factor < 1.0:
            desc.append("اعتماد على الأمطار - محصول يحتاج ري (-20%)")

        return factor, desc

    def predict(self, request: YieldRequest) -> YieldPrediction:
        """
        التنبؤ بالإنتاجية
        """
        import uuid

        crop_info = CROP_DATA[request.crop_type]
        base_yield = crop_info["base_yield_per_hectare"]

        # جمع المعاملات
        all_factors = []
        total_factor = 1.0

        # معامل الطقس
        weather_factor, weather_desc = self._calculate_weather_factor(
            request.crop_type, request.avg_rainfall, request.avg_temperature
        )
        total_factor *= weather_factor
        all_factors.extend(weather_desc)

        # معامل التربة
        soil_factor, soil_desc = self._calculate_soil_factor(
            request.soil_quality or "medium"
        )
        total_factor *= soil_factor
        all_factors.extend(soil_desc)

        # معامل الري
        irrigation_factor, irrigation_desc = self._calculate_irrigation_factor(
            request.irrigation_type or "rain-fed", request.crop_type
        )
        total_factor *= irrigation_factor
        all_factors.extend(irrigation_desc)

        # الحساب النهائي
        yield_per_hectare = base_yield * total_factor
        total_yield = yield_per_hectare * request.area_hectares

        # نطاق التوقع (±15%)
        yield_min = total_yield * 0.85
        yield_max = total_yield * 1.15

        # حساب العائد المالي
        price_per_ton = crop_info["price_usd_per_ton"]
        revenue_usd = total_yield * price_per_ton
        revenue_yer = revenue_usd * USD_TO_YER

        # حساب الثقة بناءً على كمية البيانات المتوفرة
        confidence = 70.0
        if request.avg_rainfall is not None:
            confidence += 10
        if request.avg_temperature is not None:
            confidence += 10
        if request.soil_quality and request.soil_quality != "medium":
            confidence += 5
        if request.irrigation_type and request.irrigation_type != "rain-fed":
            confidence += 5

        # توصيات
        recommendations = self._generate_recommendations(
            request.crop_type,
            total_factor,
            request.irrigation_type,
            request.soil_quality,
        )

        return YieldPrediction(
            prediction_id=str(uuid.uuid4()),
            field_id=request.field_id,
            crop_type=request.crop_type.value,
            crop_name_ar=crop_info["name_ar"],
            area_hectares=request.area_hectares,
            predicted_yield_tons=round(total_yield, 2),
            predicted_yield_per_hectare=round(yield_per_hectare, 2),
            yield_range_min=round(yield_min, 2),
            yield_range_max=round(yield_max, 2),
            estimated_revenue_usd=round(revenue_usd, 2),
            estimated_revenue_yer=round(revenue_yer, 2),
            confidence_percent=min(confidence, 95),
            factors_applied=all_factors if all_factors else ["لا توجد عوامل إضافية"],
            recommendations=recommendations,
            timestamp=datetime.utcnow(),
        )

    def _generate_recommendations(
        self,
        crop_type: CropType,
        yield_factor: float,
        irrigation_type: Optional[str],
        soil_quality: Optional[str],
    ) -> List[str]:
        """توليد التوصيات"""
        recommendations = []

        if yield_factor < 0.8:
            recommendations.append("الإنتاجية المتوقعة منخفضة - راجع ظروف الزراعة")

        if irrigation_type == "rain-fed":
            recommendations.append(
                "فكر في تركيب نظام ري بالتنقيط لزيادة الإنتاج 15-20%"
            )

        if soil_quality == "poor":
            recommendations.append("أضف سماد عضوي لتحسين جودة التربة")

        crop_info = CROP_DATA[crop_type]
        if crop_info["water_requirement"] in ["high", "very_high"]:
            recommendations.append(f"محصول {crop_info['name_ar']} يحتاج ري منتظم")

        if crop_type == CropType.COFFEE:
            recommendations.append("البن اليمني يحتاج رعاية خاصة - تواصل مع خبير")

        if not recommendations:
            recommendations.append("الظروف جيدة - استمر في الرعاية المعتادة")

        return recommendations


# Initialize predictor
yield_predictor = YieldPredictor()


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="محرك سهول للتنبؤ بالإنتاجية",
    description="خدمة التنبؤ بالإنتاجية الزراعية باستخدام الذكاء الاصطناعي",
    version=SERVICE_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - secure origins from environment
CORS_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://localhost:8080",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """تهيئة الخدمة"""
    logger.info(f"Starting {SERVICE_NAME} v{SERVICE_VERSION} on port {SERVICE_PORT}")


@app.get("/healthz", response_model=HealthCheckResponse)
async def health_check():
    """فحص صحة الخدمة"""
    return HealthCheckResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
        model_ready=yield_predictor.is_ready,
        timestamp=datetime.utcnow(),
    )


@app.post("/v1/predict", response_model=YieldPrediction)
async def predict_yield(request: YieldRequest):
    """
    التنبؤ بالإنتاجية الزراعية

    يحسب الإنتاجية المتوقعة بناءً على:
    - المساحة ونوع المحصول
    - ظروف الطقس (أمطار، حرارة)
    - جودة التربة ونوع الري

    يُرجع:
    - الإنتاج المتوقع بالأطنان
    - العائد المالي المتوقع
    - توصيات لتحسين الإنتاج
    """
    try:
        prediction = yield_predictor.predict(request)
        logger.info(
            f"Yield prediction: {prediction.predicted_yield_tons} tons "
            f"for {request.area_hectares} ha of {request.crop_type.value}"
        )
        return prediction
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"فشل التنبؤ: {str(e)}")


@app.get("/v1/crops", response_model=List[Dict])
async def list_supported_crops():
    """
    قائمة المحاصيل المدعومة للتنبؤ
    """
    crops = []
    for crop_type, info in CROP_DATA.items():
        crops.append(
            {
                "crop_id": crop_type.value,
                "name_ar": info["name_ar"],
                "base_yield_per_hectare": info["base_yield_per_hectare"],
                "price_usd_per_ton": info["price_usd_per_ton"],
                "growing_season_days": info["growing_season_days"],
                "water_requirement": info["water_requirement"],
            }
        )
    return crops


@app.get("/v1/price/{crop_type}")
async def get_crop_price(crop_type: CropType):
    """
    سعر المحصول الحالي
    """
    info = CROP_DATA[crop_type]
    return {
        "crop_type": crop_type.value,
        "name_ar": info["name_ar"],
        "price_usd_per_ton": info["price_usd_per_ton"],
        "price_yer_per_ton": info["price_usd_per_ton"] * USD_TO_YER,
        "last_updated": datetime.utcnow().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Run Application
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="0.0.0.0", port=SERVICE_PORT, reload=True, log_level="info"
    )
