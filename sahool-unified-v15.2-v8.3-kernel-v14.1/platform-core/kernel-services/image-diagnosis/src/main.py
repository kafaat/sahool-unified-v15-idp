"""
Image Diagnosis Service - Signal Producer (Layer 2)
خدمة تشخيص الصور - تحليل أمراض النباتات

Responsibilities:
1. Receive plant images from mobile app
2. Analyze images using ML models (local or API)
3. Detect diseases, pests, and nutrient deficiencies
4. Publish diagnosis events to NATS
5. NO public API (Layer 2 rule) - receives via internal queue

Events Produced:
- image.analyzed
- plant.disease.suspected
"""

import os
import sys
import json
import base64
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
import nats
from PIL import Image
import io

sys.path.insert(0, "/app")
from shared.events.base_event import create_event, EventTypes
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PUBLISHED, init_service_info

configure_logging(service_name="image-diagnosis-service")
logger = get_logger(__name__)
event_logger = EventLogger("image-diagnosis-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "image-diagnosis-service"
SERVICE_LAYER = "signal-producer"


# ============================================
# Diagnosis Categories
# ============================================


class DiagnosisCategory(str, Enum):
    DISEASE = "disease"
    PEST = "pest"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    WATER_STRESS = "water_stress"
    HEALTHY = "healthy"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DiagnosisResult:
    """Result of image analysis"""

    category: DiagnosisCategory
    condition_id: str
    condition_name_ar: str
    condition_name_en: str
    confidence: float  # 0.0 - 1.0
    severity: Severity
    affected_area_percent: float
    description_ar: str
    description_en: str
    symptoms: List[str]
    treatment_ar: str
    treatment_en: str
    prevention_ar: str
    prevention_en: str

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "condition_id": self.condition_id,
            "condition_name": {
                "ar": self.condition_name_ar,
                "en": self.condition_name_en,
            },
            "confidence": self.confidence,
            "severity": self.severity.value,
            "affected_area_percent": self.affected_area_percent,
            "description": {"ar": self.description_ar, "en": self.description_en},
            "symptoms": self.symptoms,
            "treatment": {"ar": self.treatment_ar, "en": self.treatment_en},
            "prevention": {"ar": self.prevention_ar, "en": self.prevention_en},
        }


# ============================================
# Yemen Crop Disease Database
# ============================================

DISEASE_DATABASE = {
    "tomato_late_blight": DiagnosisResult(
        category=DiagnosisCategory.DISEASE,
        condition_id="tomato_late_blight",
        condition_name_ar="اللفحة المتأخرة",
        condition_name_en="Late Blight",
        confidence=0.0,
        severity=Severity.HIGH,
        affected_area_percent=0.0,
        description_ar="مرض فطري خطير يصيب الطماطم والبطاطس، ينتشر بسرعة في الرطوبة العالية",
        description_en="Serious fungal disease affecting tomatoes and potatoes, spreads rapidly in high humidity",
        symptoms=[
            "بقع مائية على الأوراق",
            "بقع بنية داكنة",
            "عفن أبيض على السطح السفلي",
        ],
        treatment_ar="رش مبيد فطري نحاسي، إزالة الأجزاء المصابة، تحسين التهوية",
        treatment_en="Spray copper fungicide, remove infected parts, improve ventilation",
        prevention_ar="تجنب الري العلوي، توفير مسافات كافية بين النباتات، استخدام أصناف مقاومة",
        prevention_en="Avoid overhead irrigation, provide adequate plant spacing, use resistant varieties",
    ),
    "tomato_powdery_mildew": DiagnosisResult(
        category=DiagnosisCategory.DISEASE,
        condition_id="tomato_powdery_mildew",
        condition_name_ar="البياض الدقيقي",
        condition_name_en="Powdery Mildew",
        confidence=0.0,
        severity=Severity.MEDIUM,
        affected_area_percent=0.0,
        description_ar="مرض فطري يظهر كغبار أبيض على الأوراق",
        description_en="Fungal disease appearing as white powder on leaves",
        symptoms=["غبار أبيض على الأوراق", "اصفرار الأوراق", "تجعد الأوراق"],
        treatment_ar="رش الكبريت القابل للبلل، إزالة الأوراق المصابة",
        treatment_en="Spray wettable sulfur, remove infected leaves",
        prevention_ar="تحسين دوران الهواء، تجنب الرطوبة الزائدة",
        prevention_en="Improve air circulation, avoid excess humidity",
    ),
    "aphid_infestation": DiagnosisResult(
        category=DiagnosisCategory.PEST,
        condition_id="aphid_infestation",
        condition_name_ar="إصابة المن",
        condition_name_en="Aphid Infestation",
        confidence=0.0,
        severity=Severity.MEDIUM,
        affected_area_percent=0.0,
        description_ar="حشرات صغيرة تمتص عصارة النبات وتنقل الفيروسات",
        description_en="Small insects that suck plant sap and transmit viruses",
        symptoms=["حشرات صغيرة خضراء أو سوداء", "أوراق ملتفة", "إفرازات لزجة"],
        treatment_ar="رش بالصابون الحشري، استخدام المبيدات الطبيعية",
        treatment_en="Spray with insecticidal soap, use natural pesticides",
        prevention_ar="إطلاق الحشرات النافعة، زراعة نباتات طاردة",
        prevention_en="Release beneficial insects, plant repellent plants",
    ),
    "nitrogen_deficiency": DiagnosisResult(
        category=DiagnosisCategory.NUTRIENT_DEFICIENCY,
        condition_id="nitrogen_deficiency",
        condition_name_ar="نقص النيتروجين",
        condition_name_en="Nitrogen Deficiency",
        confidence=0.0,
        severity=Severity.MEDIUM,
        affected_area_percent=0.0,
        description_ar="نقص عنصر النيتروجين الضروري للنمو الخضري",
        description_en="Lack of nitrogen essential for vegetative growth",
        symptoms=["اصفرار الأوراق السفلية", "نمو بطيء", "أوراق صغيرة"],
        treatment_ar="إضافة سماد نيتروجيني، سماد عضوي متحلل",
        treatment_en="Add nitrogen fertilizer, composted organic matter",
        prevention_ar="التسميد المتوازن، تناوب المحاصيل مع البقوليات",
        prevention_en="Balanced fertilization, crop rotation with legumes",
    ),
    "water_stress_drought": DiagnosisResult(
        category=DiagnosisCategory.WATER_STRESS,
        condition_id="water_stress_drought",
        condition_name_ar="إجهاد مائي - جفاف",
        condition_name_en="Water Stress - Drought",
        confidence=0.0,
        severity=Severity.HIGH,
        affected_area_percent=0.0,
        description_ar="نقص المياه يؤدي لذبول النبات وتوقف النمو",
        description_en="Lack of water causes wilting and growth cessation",
        symptoms=["ذبول الأوراق", "احتراق حواف الأوراق", "سقوط الأزهار"],
        treatment_ar="ري عميق فوري، تغطية التربة بالملش",
        treatment_en="Immediate deep irrigation, mulch the soil",
        prevention_ar="نظام ري منتظم، استخدام الري بالتنقيط",
        prevention_en="Regular irrigation schedule, use drip irrigation",
    ),
    "healthy_plant": DiagnosisResult(
        category=DiagnosisCategory.HEALTHY,
        condition_id="healthy_plant",
        condition_name_ar="نبات سليم",
        condition_name_en="Healthy Plant",
        confidence=0.0,
        severity=Severity.NONE,
        affected_area_percent=0.0,
        description_ar="النبات يبدو بصحة جيدة",
        description_en="The plant appears healthy",
        symptoms=[],
        treatment_ar="الاستمرار في العناية الحالية",
        treatment_en="Continue current care",
        prevention_ar="مراقبة منتظمة للوقاية",
        prevention_en="Regular monitoring for prevention",
    ),
}


# ============================================
# Image Analyzer (Rule-based + Future ML)
# ============================================


class ImageAnalyzer:
    """
    Analyzes plant images for diseases and conditions.
    Currently uses rule-based analysis with image features.
    Designed for future ML model integration.
    """

    def __init__(self):
        self.supported_crops = [
            "tomato",
            "wheat",
            "coffee",
            "grape",
            "banana",
            "potato",
        ]

    async def analyze(
        self, image_data: bytes, crop_type: str, metadata: Optional[Dict] = None
    ) -> List[DiagnosisResult]:
        """
        Analyze image and return diagnosis results.

        In production, this would:
        1. Preprocess image
        2. Run through ML model
        3. Post-process results

        Currently: Returns rule-based analysis based on image features
        """
        try:
            # Load and analyze image
            image = Image.open(io.BytesIO(image_data))
            features = self._extract_features(image)

            # Analyze based on features
            results = self._rule_based_analysis(features, crop_type, metadata)

            return results

        except Exception as e:
            logger.error("image_analysis_failed", error=str(e))
            return []

    def _extract_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract visual features from image"""
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Resize for consistent analysis
        image = image.resize((224, 224))

        # Calculate color statistics
        pixels = list(image.getdata())
        r_vals = [p[0] for p in pixels]
        g_vals = [p[1] for p in pixels]
        b_vals = [p[2] for p in pixels]

        # Green ratio (indicator of plant health)
        total = sum(r_vals) + sum(g_vals) + sum(b_vals)
        green_ratio = sum(g_vals) / total if total > 0 else 0

        # Yellow/brown pixels (indicator of disease/stress)
        yellow_brown_count = sum(
            1 for r, g, b in pixels if r > 150 and g > 100 and b < 100
        )
        yellow_ratio = yellow_brown_count / len(pixels)

        # White/gray pixels (indicator of mildew)
        white_gray_count = sum(
            1 for r, g, b in pixels if r > 200 and g > 200 and b > 200
        )
        white_ratio = white_gray_count / len(pixels)

        # Dark spots (indicator of blight)
        dark_count = sum(1 for r, g, b in pixels if r < 50 and g < 50 and b < 50)
        dark_ratio = dark_count / len(pixels)

        return {
            "green_ratio": green_ratio,
            "yellow_ratio": yellow_ratio,
            "white_ratio": white_ratio,
            "dark_ratio": dark_ratio,
            "image_size": image.size,
            "brightness": sum(r_vals + g_vals + b_vals) / (3 * len(pixels)),
        }

    def _rule_based_analysis(
        self, features: Dict[str, Any], crop_type: str, metadata: Optional[Dict]
    ) -> List[DiagnosisResult]:
        """Rule-based analysis using extracted features"""
        results = []

        # Check for healthy plant first
        if (
            features["green_ratio"] > 0.4
            and features["yellow_ratio"] < 0.1
            and features["dark_ratio"] < 0.05
        ):

            healthy = DISEASE_DATABASE["healthy_plant"]
            healthy.confidence = 0.85 - features["yellow_ratio"] * 2
            results.append(healthy)
            return results

        # Check for late blight (dark spots + yellowing)
        if features["dark_ratio"] > 0.05 and features["yellow_ratio"] > 0.1:
            blight = DISEASE_DATABASE["tomato_late_blight"]
            blight.confidence = min(
                0.9, features["dark_ratio"] * 5 + features["yellow_ratio"] * 2
            )
            blight.affected_area_percent = features["dark_ratio"] * 100
            blight.severity = self._calculate_severity(blight.affected_area_percent)
            results.append(blight)

        # Check for powdery mildew (white patches)
        if features["white_ratio"] > 0.1:
            mildew = DISEASE_DATABASE["tomato_powdery_mildew"]
            mildew.confidence = min(0.85, features["white_ratio"] * 3)
            mildew.affected_area_percent = features["white_ratio"] * 100
            mildew.severity = self._calculate_severity(mildew.affected_area_percent)
            results.append(mildew)

        # Check for nutrient deficiency (low green, high yellow)
        if features["green_ratio"] < 0.3 and features["yellow_ratio"] > 0.2:
            deficiency = DISEASE_DATABASE["nitrogen_deficiency"]
            deficiency.confidence = min(0.75, features["yellow_ratio"] * 2)
            deficiency.affected_area_percent = features["yellow_ratio"] * 100
            deficiency.severity = self._calculate_severity(
                deficiency.affected_area_percent
            )
            results.append(deficiency)

        # Check for water stress (overall dull, low brightness)
        if features["brightness"] < 80 and features["green_ratio"] < 0.25:
            stress = DISEASE_DATABASE["water_stress_drought"]
            stress.confidence = 0.7
            stress.affected_area_percent = (1 - features["green_ratio"]) * 50
            stress.severity = self._calculate_severity(stress.affected_area_percent)
            results.append(stress)

        # If no specific condition detected, return unknown
        if not results:
            results.append(
                DiagnosisResult(
                    category=DiagnosisCategory.UNKNOWN,
                    condition_id="unknown",
                    condition_name_ar="غير محدد",
                    condition_name_en="Unknown",
                    confidence=0.5,
                    severity=Severity.LOW,
                    affected_area_percent=0,
                    description_ar="لم نتمكن من تحديد حالة محددة",
                    description_en="Could not identify a specific condition",
                    symptoms=[],
                    treatment_ar="استشر خبير زراعي",
                    treatment_en="Consult an agricultural expert",
                    prevention_ar="مراقبة مستمرة",
                    prevention_en="Continuous monitoring",
                )
            )

        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:3]  # Return top 3 diagnoses

    def _calculate_severity(self, affected_percent: float) -> Severity:
        """Calculate severity based on affected area"""
        if affected_percent < 5:
            return Severity.LOW
        elif affected_percent < 15:
            return Severity.MEDIUM
        elif affected_percent < 30:
            return Severity.HIGH
        else:
            return Severity.CRITICAL


# ============================================
# Image Diagnosis Service
# ============================================


class ImageDiagnosisService:
    def __init__(self):
        self.nc = None
        self.js = None
        self.analyzer = ImageAnalyzer()
        self.analysis_count = 0

    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("image_diagnosis_service_connected")

    async def start(self):
        """Start service and subscribe to image analysis requests"""
        # Subscribe to internal image analysis queue
        await self.js.subscribe(
            "internal.image.analyze",
            durable="image-diagnosis-consumer",
            cb=self._handle_analysis_request,
        )
        logger.info("image_diagnosis_service_started")

    async def _handle_analysis_request(self, msg):
        """Handle incoming analysis request from queue"""
        try:
            request = json.loads(msg.data.decode())
            image_b64 = request.get("image_base64")
            crop_type = request.get("crop_type", "unknown")
            field_id = request.get("field_id")
            tenant_id = request.get("tenant_id", "default")

            if not image_b64:
                await msg.ack()
                return

            image_data = base64.b64decode(image_b64)
            results = await self.analyze_and_publish(
                image_data, crop_type, field_id, tenant_id
            )

            await msg.ack()

        except Exception as e:
            logger.error("analysis_request_failed", error=str(e))
            await msg.nak()

    async def analyze_and_publish(
        self,
        image_data: bytes,
        crop_type: str,
        field_id: Optional[str] = None,
        tenant_id: str = "default",
        metadata: Optional[Dict] = None,
    ) -> List[DiagnosisResult]:
        """Analyze image and publish results"""
        self.analysis_count += 1
        analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{self.analysis_count}"

        logger.info("starting_analysis", analysis_id=analysis_id, crop_type=crop_type)

        # Perform analysis
        results = await self.analyzer.analyze(image_data, crop_type, metadata)

        if not results:
            return []

        # Publish image analyzed event
        event = create_event(
            event_type=EventTypes.IMAGE_ANALYZED,
            payload={
                "analysis_id": analysis_id,
                "crop_type": crop_type,
                "field_id": field_id,
                "diagnosis_count": len(results),
                "primary_diagnosis": results[0].to_dict() if results else None,
                "all_diagnoses": [r.to_dict() for r in results],
                "analyzed_at": datetime.utcnow().isoformat() + "Z",
            },
            tenant_id=tenant_id,
        )

        await self.js.publish(
            subject=EventTypes.IMAGE_ANALYZED,
            payload=json.dumps(event, ensure_ascii=False).encode(),
        )
        event_logger.published(EventTypes.IMAGE_ANALYZED, analysis_id=analysis_id)

        # If disease/pest detected, publish specific event
        for result in results:
            if result.category in [DiagnosisCategory.DISEASE, DiagnosisCategory.PEST]:
                if result.confidence > 0.6:  # Only high confidence
                    disease_event = create_event(
                        event_type=EventTypes.PLANT_DISEASE_SUSPECTED,
                        payload={
                            "analysis_id": analysis_id,
                            "diagnosis": result.to_dict(),
                            "crop_type": crop_type,
                            "field_id": field_id,
                            "requires_action": result.severity
                            in [Severity.HIGH, Severity.CRITICAL],
                        },
                        tenant_id=tenant_id,
                    )

                    await self.js.publish(
                        subject=EventTypes.PLANT_DISEASE_SUSPECTED,
                        payload=json.dumps(disease_event, ensure_ascii=False).encode(),
                    )
                    event_logger.published(
                        EventTypes.PLANT_DISEASE_SUSPECTED,
                        condition=result.condition_id,
                        confidence=result.confidence,
                    )

        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.IMAGE_ANALYZED,
            tenant_id=tenant_id,
        ).inc()

        return results

    async def stop(self):
        if self.nc:
            await self.nc.close()
        logger.info("image_diagnosis_service_stopped")


# ============================================
# FastAPI Application
# ============================================

image_service = ImageDiagnosisService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await image_service.connect()
    await image_service.start()
    yield
    await image_service.stop()


app = FastAPI(
    title="Image Diagnosis Service",
    description="SAHOOL - Plant Disease Image Analysis (Layer 2)",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = image_service.nc and image_service.nc.is_connected
    return {"status": "ready" if connected else "not_ready"}


@app.get("/internal/status")
async def internal_status():
    return {
        "service": SERVICE_NAME,
        "layer": SERVICE_LAYER,
        "analysis_count": image_service.analysis_count,
        "supported_crops": image_service.analyzer.supported_crops,
    }


@app.post("/internal/analyze")
async def internal_analyze(
    file: UploadFile = File(...),
    crop_type: str = "unknown",
    field_id: Optional[str] = None,
):
    """Internal endpoint for image analysis - not exposed via Kong"""
    contents = await file.read()
    results = await image_service.analyze_and_publish(
        contents, crop_type, field_id, "default"
    )
    return {"analysis_count": len(results), "results": [r.to_dict() for r in results]}


@app.get("/metrics")
async def metrics():
    from shared.metrics import get_metrics, get_metrics_content_type
    from fastapi.responses import Response

    return Response(content=get_metrics(), media_type=get_metrics_content_type())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8085")))
