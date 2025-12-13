"""
Disease Risk Service - Decision Service (Layer 3)
خدمة مخاطر الأمراض - خدمة القرار

Responsibilities:
1. Subscribe to weather and image diagnosis events
2. Calculate disease risk based on environmental conditions
3. Predict disease outbreaks
4. Publish risk assessments and warnings

Events Consumed:
- weather.anomaly.detected
- weather.daily.summary
- plant.disease.suspected
- ndvi.anomaly.detected

Events Produced:
- disease.risk.calculated
- disease.outbreak.predicted
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import create_event, EventTypes, Event
from shared.utils.logging import configure_logging, get_logger, EventLogger
from shared.metrics import EVENTS_PUBLISHED, EVENTS_CONSUMED, init_service_info

configure_logging(service_name="disease-risk-service")
logger = get_logger(__name__)
event_logger = EventLogger("disease-risk-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sahool:sahool@localhost:5432/disease_risk")
SERVICE_NAME = "disease-risk-service"
SERVICE_LAYER = "decision"


# ============================================
# Risk Models
# ============================================

class RiskLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DiseaseType(str, Enum):
    FUNGAL = "fungal"
    BACTERIAL = "bacterial"
    VIRAL = "viral"
    PEST = "pest"


@dataclass
class DiseaseRiskFactor:
    """Individual risk factor"""
    factor_name: str
    factor_name_ar: str
    current_value: float
    optimal_range: tuple
    risk_contribution: float  # 0.0 - 1.0
    
    def to_dict(self) -> dict:
        return {
            "factor_name": self.factor_name,
            "factor_name_ar": self.factor_name_ar,
            "current_value": self.current_value,
            "optimal_range": {"min": self.optimal_range[0], "max": self.optimal_range[1]},
            "risk_contribution": self.risk_contribution
        }


@dataclass
class DiseaseRiskAssessment:
    """Complete risk assessment for a disease"""
    disease_id: str
    disease_name_ar: str
    disease_name_en: str
    disease_type: DiseaseType
    risk_level: RiskLevel
    risk_score: float  # 0.0 - 1.0
    risk_factors: List[DiseaseRiskFactor]
    affected_crops: List[str]
    prediction_confidence: float
    prevention_actions: List[str]
    treatment_actions: List[str]
    outbreak_probability: float
    days_to_potential_outbreak: Optional[int]
    
    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "disease_name": {"ar": self.disease_name_ar, "en": self.disease_name_en},
            "disease_type": self.disease_type.value,
            "risk_level": self.risk_level.value,
            "risk_score": round(self.risk_score, 2),
            "risk_factors": [f.to_dict() for f in self.risk_factors],
            "affected_crops": self.affected_crops,
            "prediction_confidence": round(self.prediction_confidence, 2),
            "prevention_actions": self.prevention_actions,
            "treatment_actions": self.treatment_actions,
            "outbreak_probability": round(self.outbreak_probability, 2),
            "days_to_potential_outbreak": self.days_to_potential_outbreak
        }


# ============================================
# Disease Risk Models (Yemen-specific)
# ============================================

DISEASE_RISK_MODELS = {
    "late_blight": {
        "disease_id": "late_blight",
        "disease_name_ar": "اللفحة المتأخرة",
        "disease_name_en": "Late Blight",
        "disease_type": DiseaseType.FUNGAL,
        "affected_crops": ["طماطم", "بطاطس", "فلفل"],
        "optimal_conditions": {
            "temperature": (15, 22),
            "humidity": (85, 100),
            "precipitation": (5, 50)
        },
        "prevention_actions": [
            "رش مبيد فطري وقائي",
            "تحسين التهوية بين النباتات",
            "تجنب الري العلوي في المساء"
        ],
        "treatment_actions": [
            "رش مبيد نحاسي فوري",
            "إزالة وحرق الأجزاء المصابة",
            "زيادة فترات التهوية"
        ]
    },
    "powdery_mildew": {
        "disease_id": "powdery_mildew",
        "disease_name_ar": "البياض الدقيقي",
        "disease_name_en": "Powdery Mildew",
        "disease_type": DiseaseType.FUNGAL,
        "affected_crops": ["عنب", "خيار", "كوسة", "قرع"],
        "optimal_conditions": {
            "temperature": (20, 30),
            "humidity": (40, 70),
            "precipitation": (0, 2)
        },
        "prevention_actions": [
            "رش كبريت وقائي",
            "زراعة أصناف مقاومة",
            "تقليم لتحسين التهوية"
        ],
        "treatment_actions": [
            "رش بيكربونات الصوديوم",
            "رش مبيد فطري جهازي",
            "إزالة الأوراق المصابة"
        ]
    },
    "rust": {
        "disease_id": "rust",
        "disease_name_ar": "الصدأ",
        "disease_name_en": "Rust",
        "disease_type": DiseaseType.FUNGAL,
        "affected_crops": ["قمح", "شعير", "بن"],
        "optimal_conditions": {
            "temperature": (15, 25),
            "humidity": (80, 100),
            "precipitation": (2, 20)
        },
        "prevention_actions": [
            "استخدام بذور معالجة",
            "زراعة أصناف مقاومة",
            "التسميد المتوازن"
        ],
        "treatment_actions": [
            "رش مبيد فطري ثلاثي الأزول",
            "إزالة بقايا المحصول السابق"
        ]
    },
    "bacterial_wilt": {
        "disease_id": "bacterial_wilt",
        "disease_name_ar": "الذبول البكتيري",
        "disease_name_en": "Bacterial Wilt",
        "disease_type": DiseaseType.BACTERIAL,
        "affected_crops": ["طماطم", "باذنجان", "فلفل", "موز"],
        "optimal_conditions": {
            "temperature": (25, 35),
            "humidity": (70, 90),
            "precipitation": (10, 40)
        },
        "prevention_actions": [
            "تعقيم التربة",
            "تناوب المحاصيل",
            "استخدام شتلات سليمة"
        ],
        "treatment_actions": [
            "إزالة النباتات المصابة",
            "تعقيم الأدوات",
            "تجنب الري الزائد"
        ]
    },
    "aphid_virus_transmission": {
        "disease_id": "aphid_virus_transmission",
        "disease_name_ar": "فيروسات المن",
        "disease_name_en": "Aphid-transmitted Viruses",
        "disease_type": DiseaseType.VIRAL,
        "affected_crops": ["خيار", "كوسة", "فلفل", "طماطم"],
        "optimal_conditions": {
            "temperature": (20, 30),
            "humidity": (50, 80),
            "precipitation": (0, 5)
        },
        "prevention_actions": [
            "مكافحة المن مبكراً",
            "استخدام مصائد صفراء",
            "زراعة حواجز نباتية"
        ],
        "treatment_actions": [
            "رش مبيد حشري جهازي",
            "إزالة النباتات المصابة",
            "زيادة الحشرات المفترسة"
        ]
    }
}


# ============================================
# Risk Calculator
# ============================================

class DiseaseRiskCalculator:
    """Calculate disease risk based on environmental conditions"""
    
    def __init__(self):
        self.weather_history: Dict[str, List[Dict]] = defaultdict(list)
        self.disease_detections: Dict[str, List[Dict]] = defaultdict(list)
    
    def record_weather(self, region: str, weather_data: Dict):
        """Record weather data for risk calculation"""
        self.weather_history[region].append({
            "timestamp": datetime.utcnow().isoformat(),
            "data": weather_data
        })
        # Keep only last 7 days
        if len(self.weather_history[region]) > 168:  # 7 days * 24 hours
            self.weather_history[region] = self.weather_history[region][-168:]
    
    def record_disease_detection(self, region: str, disease_data: Dict):
        """Record disease detection for outbreak prediction"""
        self.disease_detections[region].append({
            "timestamp": datetime.utcnow().isoformat(),
            "data": disease_data
        })
        # Keep only last 30 days
        if len(self.disease_detections[region]) > 720:
            self.disease_detections[region] = self.disease_detections[region][-720:]
    
    def calculate_risk(
        self, 
        region: str,
        current_weather: Dict,
        crop_type: Optional[str] = None
    ) -> List[DiseaseRiskAssessment]:
        """Calculate risk for all relevant diseases"""
        assessments = []
        
        for disease_id, model in DISEASE_RISK_MODELS.items():
            # Skip if crop not affected
            if crop_type and crop_type not in model["affected_crops"]:
                continue
            
            assessment = self._calculate_single_disease_risk(
                disease_id, model, current_weather, region
            )
            if assessment.risk_score > 0.2:  # Only include meaningful risks
                assessments.append(assessment)
        
        # Sort by risk score
        assessments.sort(key=lambda x: x.risk_score, reverse=True)
        return assessments
    
    def _calculate_single_disease_risk(
        self,
        disease_id: str,
        model: Dict,
        weather: Dict,
        region: str
    ) -> DiseaseRiskAssessment:
        """Calculate risk for a single disease"""
        optimal = model["optimal_conditions"]
        risk_factors = []
        total_risk = 0.0
        factor_count = 0
        
        # Temperature factor
        current_temp = weather.get("temperature_c", 25)
        temp_opt = optimal["temperature"]
        temp_risk = self._calculate_factor_risk(current_temp, temp_opt)
        risk_factors.append(DiseaseRiskFactor(
            factor_name="temperature",
            factor_name_ar="درجة الحرارة",
            current_value=current_temp,
            optimal_range=temp_opt,
            risk_contribution=temp_risk
        ))
        total_risk += temp_risk
        factor_count += 1
        
        # Humidity factor
        current_humidity = weather.get("humidity_percent", 50)
        humidity_opt = optimal["humidity"]
        humidity_risk = self._calculate_factor_risk(current_humidity, humidity_opt)
        risk_factors.append(DiseaseRiskFactor(
            factor_name="humidity",
            factor_name_ar="الرطوبة",
            current_value=current_humidity,
            optimal_range=humidity_opt,
            risk_contribution=humidity_risk
        ))
        total_risk += humidity_risk * 1.2  # Humidity is weighted more
        factor_count += 1.2
        
        # Precipitation factor
        current_precip = weather.get("precipitation_mm", 0)
        precip_opt = optimal["precipitation"]
        precip_risk = self._calculate_factor_risk(current_precip, precip_opt)
        risk_factors.append(DiseaseRiskFactor(
            factor_name="precipitation",
            factor_name_ar="الهطول",
            current_value=current_precip,
            optimal_range=precip_opt,
            risk_contribution=precip_risk
        ))
        total_risk += precip_risk
        factor_count += 1
        
        # Calculate average risk
        avg_risk = total_risk / factor_count if factor_count > 0 else 0
        
        # Adjust based on recent disease detections in region
        detection_factor = self._get_detection_factor(region, disease_id)
        final_risk = min(1.0, avg_risk * (1 + detection_factor))
        
        # Determine risk level
        risk_level = self._risk_score_to_level(final_risk)
        
        # Calculate outbreak probability
        outbreak_prob = self._calculate_outbreak_probability(
            final_risk, detection_factor, region
        )
        
        # Estimate days to outbreak
        days_to_outbreak = None
        if outbreak_prob > 0.5:
            days_to_outbreak = max(1, int((1 - outbreak_prob) * 14))
        
        return DiseaseRiskAssessment(
            disease_id=disease_id,
            disease_name_ar=model["disease_name_ar"],
            disease_name_en=model["disease_name_en"],
            disease_type=model["disease_type"],
            risk_level=risk_level,
            risk_score=final_risk,
            risk_factors=risk_factors,
            affected_crops=model["affected_crops"],
            prediction_confidence=0.7 + (len(self.weather_history.get(region, [])) / 168) * 0.2,
            prevention_actions=model["prevention_actions"],
            treatment_actions=model["treatment_actions"],
            outbreak_probability=outbreak_prob,
            days_to_potential_outbreak=days_to_outbreak
        )
    
    def _calculate_factor_risk(self, current: float, optimal: tuple) -> float:
        """Calculate how close current value is to optimal disease conditions"""
        opt_min, opt_max = optimal
        opt_mid = (opt_min + opt_max) / 2
        opt_range = opt_max - opt_min
        
        if opt_min <= current <= opt_max:
            # Within optimal range - high risk
            distance_from_mid = abs(current - opt_mid)
            return 1.0 - (distance_from_mid / (opt_range / 2)) * 0.3
        else:
            # Outside optimal range
            if current < opt_min:
                distance = opt_min - current
            else:
                distance = current - opt_max
            
            # Risk decreases with distance from optimal
            return max(0, 1.0 - (distance / opt_range))
    
    def _get_detection_factor(self, region: str, disease_id: str) -> float:
        """Get boost factor based on recent detections"""
        detections = self.disease_detections.get(region, [])
        relevant = [d for d in detections if d["data"].get("disease_id") == disease_id]
        
        if not relevant:
            return 0.0
        
        # More recent detections = higher factor
        recent_count = len([d for d in relevant 
                          if datetime.fromisoformat(d["timestamp"]) > 
                             datetime.utcnow() - timedelta(days=7)])
        
        return min(0.5, recent_count * 0.1)
    
    def _calculate_outbreak_probability(
        self, 
        risk_score: float,
        detection_factor: float,
        region: str
    ) -> float:
        """Calculate probability of outbreak"""
        base_prob = risk_score * 0.7
        detection_boost = detection_factor * 0.5
        
        # Historical weather trend
        history = self.weather_history.get(region, [])
        if len(history) > 24:
            # Check if conditions have been favorable for multiple days
            favorable_hours = sum(
                1 for h in history[-48:] 
                if h["data"].get("humidity_percent", 0) > 70
            )
            trend_factor = favorable_hours / 48 * 0.3
        else:
            trend_factor = 0
        
        return min(1.0, base_prob + detection_boost + trend_factor)
    
    def _risk_score_to_level(self, score: float) -> RiskLevel:
        """Convert risk score to level"""
        if score < 0.2:
            return RiskLevel.NONE
        elif score < 0.4:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MODERATE
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL


# ============================================
# Disease Risk Service
# ============================================

class DiseaseRiskService:
    def __init__(self):
        self.nc = None
        self.js = None
        self.calculator = DiseaseRiskCalculator()
        self.running = False
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("disease_risk_service_connected")
    
    async def start(self):
        """Start consuming events"""
        self.running = True
        
        # Subscribe to weather events
        await self.js.subscribe(
            EventTypes.WEATHER_ANOMALY_DETECTED,
            durable="disease-risk-weather-anomaly",
            cb=self._handle_weather_anomaly
        )
        
        await self.js.subscribe(
            EventTypes.WEATHER_DAILY_SUMMARY,
            durable="disease-risk-weather-daily",
            cb=self._handle_weather_summary
        )
        
        # Subscribe to disease detection events
        await self.js.subscribe(
            EventTypes.PLANT_DISEASE_SUSPECTED,
            durable="disease-risk-detection",
            cb=self._handle_disease_detection
        )
        
        logger.info("disease_risk_service_started")
    
    async def _handle_weather_anomaly(self, msg):
        """Handle weather anomaly event"""
        try:
            event = json.loads(msg.data.decode())
            EVENTS_CONSUMED.labels(
                service=SERVICE_NAME,
                event_type=EventTypes.WEATHER_ANOMALY_DETECTED,
                tenant_id=event.get("tenant_id", "default")
            ).inc()
            
            payload = event.get("payload", {})
            weather = payload.get("weather", {}).get("current", {})
            location = payload.get("location", {})
            region = location.get("region", "المرتفعات")
            
            # Record weather
            self.calculator.record_weather(region, weather)
            
            # Calculate risks
            assessments = self.calculator.calculate_risk(region, weather)
            
            # Publish high-risk assessments
            for assessment in assessments:
                if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    await self._publish_risk_assessment(assessment, location, event.get("tenant_id", "default"))
            
            await msg.ack()
            
        except Exception as e:
            logger.error("weather_anomaly_handling_failed", error=str(e))
            await msg.nak()
    
    async def _handle_weather_summary(self, msg):
        """Handle daily weather summary"""
        try:
            event = json.loads(msg.data.decode())
            EVENTS_CONSUMED.labels(
                service=SERVICE_NAME,
                event_type=EventTypes.WEATHER_DAILY_SUMMARY,
                tenant_id=event.get("tenant_id", "default")
            ).inc()
            
            payload = event.get("payload", {})
            weather = payload.get("summary", {}).get("current", {})
            location = payload.get("location", {})
            region = location.get("region", "المرتفعات")
            
            self.calculator.record_weather(region, weather)
            
            # Daily comprehensive risk assessment
            assessments = self.calculator.calculate_risk(region, weather)
            
            for assessment in assessments:
                if assessment.risk_level != RiskLevel.NONE:
                    await self._publish_risk_assessment(
                        assessment, location, event.get("tenant_id", "default")
                    )
                    
                    # Check for outbreak prediction
                    if assessment.outbreak_probability > 0.6:
                        await self._publish_outbreak_prediction(
                            assessment, location, event.get("tenant_id", "default")
                        )
            
            await msg.ack()
            
        except Exception as e:
            logger.error("weather_summary_handling_failed", error=str(e))
            await msg.nak()
    
    async def _handle_disease_detection(self, msg):
        """Handle plant disease detection event"""
        try:
            event = json.loads(msg.data.decode())
            EVENTS_CONSUMED.labels(
                service=SERVICE_NAME,
                event_type=EventTypes.PLANT_DISEASE_SUSPECTED,
                tenant_id=event.get("tenant_id", "default")
            ).inc()
            
            payload = event.get("payload", {})
            diagnosis = payload.get("diagnosis", {})
            
            # Record detection for outbreak tracking
            # Note: In production, would get region from field_id lookup
            self.calculator.record_disease_detection("المرتفعات", diagnosis)
            
            await msg.ack()
            
        except Exception as e:
            logger.error("disease_detection_handling_failed", error=str(e))
            await msg.nak()
    
    async def _publish_risk_assessment(
        self, 
        assessment: DiseaseRiskAssessment,
        location: Dict,
        tenant_id: str
    ):
        """Publish disease risk assessment event"""
        event = create_event(
            event_type=EventTypes.DISEASE_RISK_CALCULATED,
            payload={
                "assessment": assessment.to_dict(),
                "location": location,
                "calculated_at": datetime.utcnow().isoformat() + "Z"
            },
            tenant_id=tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.DISEASE_RISK_CALCULATED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        event_logger.published(
            EventTypes.DISEASE_RISK_CALCULATED,
            disease=assessment.disease_id,
            risk_level=assessment.risk_level.value
        )
        
        EVENTS_PUBLISHED.labels(
            service=SERVICE_NAME,
            event_type=EventTypes.DISEASE_RISK_CALCULATED,
            tenant_id=tenant_id
        ).inc()
    
    async def _publish_outbreak_prediction(
        self,
        assessment: DiseaseRiskAssessment,
        location: Dict,
        tenant_id: str
    ):
        """Publish disease outbreak prediction"""
        event = create_event(
            event_type=EventTypes.DISEASE_OUTBREAK_PREDICTED,
            payload={
                "disease": {
                    "id": assessment.disease_id,
                    "name": {"ar": assessment.disease_name_ar, "en": assessment.disease_name_en},
                    "type": assessment.disease_type.value
                },
                "outbreak_probability": assessment.outbreak_probability,
                "days_to_potential_outbreak": assessment.days_to_potential_outbreak,
                "affected_crops": assessment.affected_crops,
                "location": location,
                "immediate_actions": assessment.prevention_actions[:2],
                "predicted_at": datetime.utcnow().isoformat() + "Z"
            },
            tenant_id=tenant_id
        )
        
        await self.js.publish(
            subject=EventTypes.DISEASE_OUTBREAK_PREDICTED,
            payload=json.dumps(event, ensure_ascii=False).encode()
        )
        
        event_logger.published(
            EventTypes.DISEASE_OUTBREAK_PREDICTED,
            disease=assessment.disease_id,
            probability=assessment.outbreak_probability
        )
    
    async def stop(self):
        self.running = False
        if self.nc:
            await self.nc.close()
        logger.info("disease_risk_service_stopped")


# ============================================
# FastAPI Application
# ============================================

disease_service = DiseaseRiskService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await disease_service.connect()
    await disease_service.start()
    yield
    await disease_service.stop()


app = FastAPI(
    title="Disease Risk Service",
    description="SAHOOL - Disease Risk Assessment (Layer 3 - Decision)",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = disease_service.nc and disease_service.nc.is_connected
    return {"status": "ready" if connected else "not_ready"}


class RiskQueryRequest(BaseModel):
    region: str
    temperature_c: float
    humidity_percent: float
    precipitation_mm: float = 0
    crop_type: Optional[str] = None


@app.post("/api/risk/calculate")
async def calculate_risk(request: RiskQueryRequest):
    """Calculate disease risk for given conditions"""
    weather = {
        "temperature_c": request.temperature_c,
        "humidity_percent": request.humidity_percent,
        "precipitation_mm": request.precipitation_mm
    }
    
    assessments = disease_service.calculator.calculate_risk(
        request.region,
        weather,
        request.crop_type
    )
    
    return {
        "region": request.region,
        "crop_type": request.crop_type,
        "risk_count": len(assessments),
        "assessments": [a.to_dict() for a in assessments]
    }


@app.get("/api/risk/diseases")
async def list_diseases():
    """List all monitored diseases"""
    return {
        "diseases": [
            {
                "id": k,
                "name_ar": v["disease_name_ar"],
                "name_en": v["disease_name_en"],
                "type": v["disease_type"].value,
                "affected_crops": v["affected_crops"]
            }
            for k, v in DISEASE_RISK_MODELS.items()
        ]
    }


@app.get("/metrics")
async def metrics():
    from shared.metrics import get_metrics, get_metrics_content_type
    from fastapi.responses import Response
    return Response(content=get_metrics(), media_type=get_metrics_content_type())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8087")))
