"""
Irrigation Advisor Service - Decision Service (Layer 3)
خدمة استشارة الري

Responsibilities:
1. Subscribe to weather and crop lifecycle events
2. Calculate irrigation requirements based on:
   - Current weather conditions
   - Crop growth stage
   - Soil type
   - Traditional Yemeni practices
3. Detect irrigation delays
4. Publish irrigation recommendations

Events Consumed:
- weather.daily.summary
- weather.anomaly.detected
- crop.stage.changed
- astro.star.rising

Events Produced:
- irrigation.schedule.proposed
- irrigation.delay.detected
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, Dict
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import nats

sys.path.insert(0, '/app')
from shared.events.base_event import create_event, EventTypes  # noqa: E402
from shared.utils.logging import configure_logging, get_logger, EventLogger  # noqa: E402
from shared.metrics import EVENTS_PUBLISHED, EVENTS_CONSUMED, init_service_info  # noqa: E402

configure_logging(service_name="irrigation-advisor-service")
logger = get_logger(__name__)
event_logger = EventLogger("irrigation-advisor-service")

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")
SERVICE_NAME = "irrigation-advisor-service"
SERVICE_LAYER = "decision"


# ============================================
# Irrigation Models
# ============================================

class IrrigationMethod(str, Enum):
    FLOOD = "flood"  # ري بالغمر
    DRIP = "drip"  # ري بالتنقيط
    SPRINKLER = "sprinkler"  # ري بالرش
    TRADITIONAL = "traditional"  # ري تقليدي يمني


class SoilType(str, Enum):
    SANDY = "sandy"  # رملية
    CLAY = "clay"  # طينية
    LOAMY = "loamy"  # طميية
    ROCKY = "rocky"  # صخرية


class CropGrowthStage(str, Enum):
    SEEDLING = "seedling"  # شتلة
    VEGETATIVE = "vegetative"  # نمو خضري
    FLOWERING = "flowering"  # إزهار
    FRUITING = "fruiting"  # إثمار
    MATURITY = "maturity"  # نضج


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class IrrigationRecommendation:
    """Irrigation recommendation"""
    field_id: str
    crop_type: str
    recommendation_type: str
    urgency: UrgencyLevel
    water_amount_liters: float
    duration_minutes: int
    best_time: str
    method: IrrigationMethod
    reason_ar: str
    reason_en: str
    traditional_wisdom: Optional[str]
    
    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "crop_type": self.crop_type,
            "recommendation_type": self.recommendation_type,
            "urgency": self.urgency.value,
            "water_amount_liters": self.water_amount_liters,
            "duration_minutes": self.duration_minutes,
            "best_time": self.best_time,
            "method": self.method.value,
            "reason": {"ar": self.reason_ar, "en": self.reason_en},
            "traditional_wisdom": self.traditional_wisdom
        }


# ============================================
# Crop Water Requirements (mm/day)
# ============================================

CROP_WATER_REQUIREMENTS = {
    "طماطم": {
        CropGrowthStage.SEEDLING: 2.5,
        CropGrowthStage.VEGETATIVE: 4.0,
        CropGrowthStage.FLOWERING: 5.5,
        CropGrowthStage.FRUITING: 6.0,
        CropGrowthStage.MATURITY: 3.5
    },
    "خيار": {
        CropGrowthStage.SEEDLING: 2.0,
        CropGrowthStage.VEGETATIVE: 3.5,
        CropGrowthStage.FLOWERING: 5.0,
        CropGrowthStage.FRUITING: 5.5,
        CropGrowthStage.MATURITY: 3.0
    },
    "قمح": {
        CropGrowthStage.SEEDLING: 1.5,
        CropGrowthStage.VEGETATIVE: 3.0,
        CropGrowthStage.FLOWERING: 4.5,
        CropGrowthStage.FRUITING: 5.0,
        CropGrowthStage.MATURITY: 2.0
    },
    "بن": {
        CropGrowthStage.SEEDLING: 2.0,
        CropGrowthStage.VEGETATIVE: 3.5,
        CropGrowthStage.FLOWERING: 4.5,
        CropGrowthStage.FRUITING: 5.0,
        CropGrowthStage.MATURITY: 3.0
    },
    "قات": {
        CropGrowthStage.SEEDLING: 2.5,
        CropGrowthStage.VEGETATIVE: 4.0,
        CropGrowthStage.FLOWERING: 4.5,
        CropGrowthStage.FRUITING: 4.0,
        CropGrowthStage.MATURITY: 3.5
    },
    "موز": {
        CropGrowthStage.SEEDLING: 3.0,
        CropGrowthStage.VEGETATIVE: 5.0,
        CropGrowthStage.FLOWERING: 6.0,
        CropGrowthStage.FRUITING: 7.0,
        CropGrowthStage.MATURITY: 5.0
    }
}

# Default for unknown crops
DEFAULT_WATER_REQ = {
    CropGrowthStage.SEEDLING: 2.0,
    CropGrowthStage.VEGETATIVE: 3.5,
    CropGrowthStage.FLOWERING: 4.5,
    CropGrowthStage.FRUITING: 5.0,
    CropGrowthStage.MATURITY: 3.0
}


# ============================================
# Traditional Yemeni Irrigation Wisdom
# ============================================

TRADITIONAL_WISDOM = {
    "العلب": "في العلب اسقِ على المغيب، الحرارة شديدة والماء يتبخر سريعاً",
    "القيظ": "في القيظ الري مرتين، صباحاً ومساءً، خاصة للخضروات",
    "الشبط": "في الشبط قلّل الري، النباتات في سكون والبرد يحفظ الرطوبة",
    "الحميم": "في الحميم زد الري للموز والبن، الحرارة والرطوبة عالية",
    "default": "اسقِ في الصباح الباكر أو المساء، تجنب الري في شدة الحر"
}


# ============================================
# Irrigation Calculator
# ============================================

class IrrigationCalculator:
    """Calculate irrigation requirements"""
    
    def __init__(self):
        self.field_states: Dict[str, Dict] = {}
        self.weather_data: Dict[str, Dict] = {}
        self.current_star: Optional[str] = None
    
    def update_weather(self, region: str, weather: Dict):
        """Update weather data for region"""
        self.weather_data[region] = weather
    
    def update_star(self, star_name: str):
        """Update current astronomical star"""
        self.current_star = star_name
    
    def update_field_state(self, field_id: str, state: Dict):
        """Update field state"""
        self.field_states[field_id] = {
            **state,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def calculate_requirement(
        self,
        field_id: str,
        crop_type: str,
        growth_stage: CropGrowthStage,
        field_area_sqm: float,
        soil_type: SoilType,
        region: str,
        last_irrigation: Optional[datetime] = None,
        irrigation_method: IrrigationMethod = IrrigationMethod.DRIP
    ) -> IrrigationRecommendation:
        """Calculate irrigation requirement for a field"""
        
        # Get base water requirement (mm/day)
        water_req = CROP_WATER_REQUIREMENTS.get(
            crop_type, DEFAULT_WATER_REQ
        ).get(growth_stage, 3.5)
        
        # Get weather data
        weather = self.weather_data.get(region, {})
        temp = weather.get("temperature_c", 25)
        humidity = weather.get("humidity_percent", 50)
        precipitation = weather.get("precipitation_mm", 0)
        wind = weather.get("wind_speed_kmh", 10)
        
        # Adjust for temperature
        if temp > 35:
            water_req *= 1.3
        elif temp > 30:
            water_req *= 1.15
        elif temp < 15:
            water_req *= 0.8
        
        # Adjust for humidity
        if humidity < 30:
            water_req *= 1.2
        elif humidity > 70:
            water_req *= 0.85
        
        # Adjust for wind
        if wind > 30:
            water_req *= 1.15
        
        # Subtract recent precipitation
        water_req = max(0, water_req - precipitation * 0.8)
        
        # Adjust for soil type
        soil_factor = {
            SoilType.SANDY: 1.2,  # Drains fast
            SoilType.CLAY: 0.8,  # Retains water
            SoilType.LOAMY: 1.0,
            SoilType.ROCKY: 1.3
        }
        water_req *= soil_factor.get(soil_type, 1.0)
        
        # Calculate total water (liters)
        water_liters = water_req * field_area_sqm  # mm * sqm = liters
        
        # Calculate duration based on method
        flow_rates = {
            IrrigationMethod.DRIP: 4,  # liters per emitter per hour
            IrrigationMethod.SPRINKLER: 15,  # mm per hour
            IrrigationMethod.FLOOD: 50,  # mm per hour
            IrrigationMethod.TRADITIONAL: 10
        }
        duration = int(water_liters / (flow_rates[irrigation_method] * (field_area_sqm / 100)))
        duration = max(15, min(duration, 180))  # 15 min to 3 hours
        
        # Determine urgency
        urgency = self._calculate_urgency(
            water_req, temp, humidity, last_irrigation
        )
        
        # Determine best time
        best_time = self._determine_best_time(temp, humidity)
        
        # Get traditional wisdom
        wisdom = TRADITIONAL_WISDOM.get(
            self.current_star, 
            TRADITIONAL_WISDOM["default"]
        )
        
        # Generate reason
        reason_ar, reason_en = self._generate_reason(
            crop_type, growth_stage, temp, humidity, precipitation
        )
        
        return IrrigationRecommendation(
            field_id=field_id,
            crop_type=crop_type,
            recommendation_type="scheduled" if urgency != UrgencyLevel.CRITICAL else "urgent",
            urgency=urgency,
            water_amount_liters=round(water_liters, 1),
            duration_minutes=duration,
            best_time=best_time,
            method=irrigation_method,
            reason_ar=reason_ar,
            reason_en=reason_en,
            traditional_wisdom=wisdom
        )
    
    def _calculate_urgency(
        self,
        water_req: float,
        temp: float,
        humidity: float,
        last_irrigation: Optional[datetime]
    ) -> UrgencyLevel:
        """Calculate urgency level"""
        if last_irrigation:
            days_since = (datetime.utcnow() - last_irrigation).days
            if days_since > 3 and water_req > 4:
                return UrgencyLevel.CRITICAL
            elif days_since > 2 and water_req > 3:
                return UrgencyLevel.HIGH
        
        if temp > 40 and humidity < 30:
            return UrgencyLevel.CRITICAL
        elif temp > 35 and humidity < 40:
            return UrgencyLevel.HIGH
        elif water_req > 5:
            return UrgencyLevel.MEDIUM
        
        return UrgencyLevel.LOW
    
    def _determine_best_time(self, temp: float, humidity: float) -> str:
        """Determine best irrigation time"""
        if temp > 35:
            return "05:00-07:00 أو 18:00-20:00"
        elif temp > 30:
            return "06:00-08:00 أو 17:00-19:00"
        elif humidity > 80:
            return "10:00-14:00"  # Midday to reduce disease
        else:
            return "06:00-09:00"
    
    def _generate_reason(
        self,
        crop_type: str,
        stage: CropGrowthStage,
        temp: float,
        humidity: float,
        precip: float
    ) -> tuple:
        """Generate reason in Arabic and English"""
        reasons_ar = []
        reasons_en = []
        
        stage_names = {
            CropGrowthStage.SEEDLING: ("مرحلة الشتلة", "seedling stage"),
            CropGrowthStage.VEGETATIVE: ("مرحلة النمو الخضري", "vegetative stage"),
            CropGrowthStage.FLOWERING: ("مرحلة الإزهار", "flowering stage"),
            CropGrowthStage.FRUITING: ("مرحلة الإثمار", "fruiting stage"),
            CropGrowthStage.MATURITY: ("مرحلة النضج", "maturity stage")
        }
        
        ar_stage, en_stage = stage_names.get(stage, ("", ""))
        reasons_ar.append(f"المحصول ({crop_type}) في {ar_stage}")
        reasons_en.append(f"Crop ({crop_type}) is in {en_stage}")
        
        if temp > 35:
            reasons_ar.append("درجة الحرارة مرتفعة")
            reasons_en.append("high temperature")
        
        if humidity < 40:
            reasons_ar.append("الرطوبة منخفضة")
            reasons_en.append("low humidity")
        
        if precip > 0:
            reasons_ar.append(f"هطول {precip}مم")
            reasons_en.append(f"{precip}mm precipitation")
        
        return " - ".join(reasons_ar), " - ".join(reasons_en)
    
    def check_irrigation_delay(
        self,
        field_id: str,
        last_irrigation: datetime,
        expected_frequency_days: int = 2
    ) -> Optional[Dict]:
        """Check if irrigation is delayed"""
        days_since = (datetime.utcnow() - last_irrigation).days
        
        if days_since > expected_frequency_days:
            return {
                "field_id": field_id,
                "days_overdue": days_since - expected_frequency_days,
                "last_irrigation": last_irrigation.isoformat(),
                "severity": "critical" if days_since > expected_frequency_days + 2 else "high"
            }
        
        return None


# ============================================
# Irrigation Advisor Service
# ============================================

class IrrigationAdvisorService:
    def __init__(self):
        self.nc = None
        self.js = None
        self.calculator = IrrigationCalculator()
    
    async def connect(self):
        self.nc = await nats.connect(NATS_URL)
        self.js = self.nc.jetstream()
        logger.info("irrigation_advisor_service_connected")
    
    async def start(self):
        """Start consuming events"""
        # Subscribe to weather events
        await self.js.subscribe(
            EventTypes.WEATHER_DAILY_SUMMARY,
            durable="irrigation-weather-daily",
            cb=self._handle_weather_summary
        )
        
        await self.js.subscribe(
            EventTypes.WEATHER_ANOMALY_DETECTED,
            durable="irrigation-weather-anomaly",
            cb=self._handle_weather_anomaly
        )
        
        # Subscribe to crop lifecycle events
        await self.js.subscribe(
            EventTypes.CROP_STAGE_CHANGED,
            durable="irrigation-crop-stage",
            cb=self._handle_crop_stage_change
        )
        
        # Subscribe to astronomical events
        await self.js.subscribe(
            EventTypes.ASTRO_STAR_RISING,
            durable="irrigation-astro",
            cb=self._handle_star_rising
        )
        
        logger.info("irrigation_advisor_service_started")
    
    async def _handle_weather_summary(self, msg):
        """Handle daily weather summary"""
        try:
            event = json.loads(msg.data.decode())
            payload = event.get("payload", {})
            
            weather = payload.get("summary", {}).get("current", {})
            location = payload.get("location", {})
            region = location.get("region", "المرتفعات")
            
            self.calculator.update_weather(region, weather)
            
            # Check if conditions warrant recommendations
            temp = weather.get("temperature_c", 25)
            precip = weather.get("precipitation_mm", 0)
            
            if temp > 30 and precip < 2:
                # Generate recommendations for tracked fields
                for field_id, state in self.calculator.field_states.items():
                    if state.get("region") == region:
                        await self._generate_and_publish_recommendation(
                            field_id, state, event.get("tenant_id", "default")
                        )
            
            await msg.ack()
            
        except Exception as e:
            logger.error("weather_summary_handling_failed", error=str(e))
            await msg.nak()
    
    async def _handle_weather_anomaly(self, msg):
        """Handle weather anomaly - may trigger urgent irrigation"""
        try:
            event = json.loads(msg.data.decode())
            payload = event.get("payload", {})
            
            anomaly = payload.get("anomaly", {})
            anomaly_type = anomaly.get("type")
            
            # Handle heat-related anomalies
            if anomaly_type in ["extreme_heat", "low_humidity"]:
                weather = payload.get("weather", {}).get("current", {})
                location = payload.get("location", {})
                region = location.get("region")
                
                self.calculator.update_weather(region, weather)
                
                # Urgent recommendations for all fields in region
                for field_id, state in self.calculator.field_states.items():
                    if state.get("region") == region:
                        await self._generate_and_publish_recommendation(
                            field_id, state, event.get("tenant_id", "default"),
                            urgent=True
                        )
            
            await msg.ack()
            
        except Exception as e:
            logger.error("weather_anomaly_handling_failed", error=str(e))
            await msg.nak()
    
    async def _handle_crop_stage_change(self, msg):
        """Handle crop stage change"""
        try:
            event = json.loads(msg.data.decode())
            payload = event.get("payload", {})
            
            field_id = payload.get("field_id")
            if not field_id:
                await msg.ack()
                return
            
            # Update field state
            self.calculator.update_field_state(field_id, {
                "crop_type": payload.get("crop_type"),
                "growth_stage": payload.get("current_stage"),
                "region": payload.get("region", "المرتفعات")
            })
            
            # Generate new recommendation based on new stage
            await self._generate_and_publish_recommendation(
                field_id,
                self.calculator.field_states[field_id],
                event.get("tenant_id", "default")
            )
            
            await msg.ack()
            
        except Exception as e:
            logger.error("crop_stage_handling_failed", error=str(e))
            await msg.nak()
    
    async def _handle_star_rising(self, msg):
        """Handle astronomical star rising"""
        try:
            event = json.loads(msg.data.decode())
            payload = event.get("payload", {})
            
            star = payload.get("star", {})
            star_name = star.get("name_ar", "")
            
            self.calculator.update_star(star_name)
            
            logger.info("star_updated", star=star_name)
            
            await msg.ack()
            
        except Exception as e:
            logger.error("star_rising_handling_failed", error=str(e))
            await msg.nak()
    
    async def _generate_and_publish_recommendation(
        self,
        field_id: str,
        state: Dict,
        tenant_id: str,
        urgent: bool = False
    ):
        """Generate and publish irrigation recommendation"""
        try:
            recommendation = self.calculator.calculate_requirement(
                field_id=field_id,
                crop_type=state.get("crop_type", "خضروات"),
                growth_stage=CropGrowthStage(state.get("growth_stage", "vegetative")),
                field_area_sqm=state.get("area_sqm", 1000),
                soil_type=SoilType(state.get("soil_type", "loamy")),
                region=state.get("region", "المرتفعات"),
                irrigation_method=IrrigationMethod(state.get("method", "drip"))
            )
            
            if urgent:
                recommendation.urgency = UrgencyLevel.CRITICAL
                recommendation.recommendation_type = "urgent"
            
            # Publish recommendation
            event = create_event(
                event_type=EventTypes.IRRIGATION_SCHEDULE_PROPOSED,
                payload={
                    "recommendation": recommendation.to_dict(),
                    "proposed_at": datetime.utcnow().isoformat() + "Z",
                    "valid_for_hours": 12
                },
                tenant_id=tenant_id
            )
            
            await self.js.publish(
                subject=EventTypes.IRRIGATION_SCHEDULE_PROPOSED,
                payload=json.dumps(event, ensure_ascii=False).encode()
            )
            
            event_logger.published(
                EventTypes.IRRIGATION_SCHEDULE_PROPOSED,
                field_id=field_id,
                urgency=recommendation.urgency.value
            )
            
            EVENTS_PUBLISHED.labels(
                service=SERVICE_NAME,
                event_type=EventTypes.IRRIGATION_SCHEDULE_PROPOSED,
                tenant_id=tenant_id
            ).inc()
            
        except Exception as e:
            logger.error("recommendation_generation_failed", field_id=field_id, error=str(e))
    
    async def stop(self):
        if self.nc:
            await self.nc.close()
        logger.info("irrigation_advisor_service_stopped")


# ============================================
# FastAPI Application
# ============================================

irrigation_service = IrrigationAdvisorService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_service_info(SERVICE_NAME, "1.0.0", SERVICE_LAYER)
    await irrigation_service.connect()
    await irrigation_service.start()
    yield
    await irrigation_service.stop()


app = FastAPI(
    title="Irrigation Advisor Service",
    description="SAHOOL - Irrigation Recommendations (Layer 3 - Decision)",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/healthz")
async def health():
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readyz")
async def ready():
    connected = irrigation_service.nc and irrigation_service.nc.is_connected
    return {"status": "ready" if connected else "not_ready"}


class CalculateRequest(BaseModel):
    field_id: str
    crop_type: str
    growth_stage: str
    field_area_sqm: float
    soil_type: str = "loamy"
    region: str = "المرتفعات"
    method: str = "drip"


@app.post("/api/irrigation/calculate")
async def calculate_irrigation(request: CalculateRequest):
    """Calculate irrigation requirement"""
    recommendation = irrigation_service.calculator.calculate_requirement(
        field_id=request.field_id,
        crop_type=request.crop_type,
        growth_stage=CropGrowthStage(request.growth_stage),
        field_area_sqm=request.field_area_sqm,
        soil_type=SoilType(request.soil_type),
        region=request.region,
        irrigation_method=IrrigationMethod(request.method)
    )
    return recommendation.to_dict()


@app.get("/api/irrigation/crops")
async def list_crops():
    """List supported crops and their water requirements"""
    return {
        "crops": list(CROP_WATER_REQUIREMENTS.keys()),
        "growth_stages": [s.value for s in CropGrowthStage],
        "soil_types": [s.value for s in SoilType],
        "methods": [m.value for m in IrrigationMethod]
    }


@app.get("/metrics")
async def metrics():
    from shared.metrics import get_metrics, get_metrics_content_type
    from fastapi.responses import Response
    return Response(content=get_metrics(), media_type=get_metrics_content_type())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8088")))
