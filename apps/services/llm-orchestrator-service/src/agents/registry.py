# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agent Registry for LLM Orchestrator Service.

This module maintains a registry of all SAHOOL AI agents and their
capabilities, endpoints, and metadata.

سجل الوكلاء لخدمة تنسيق نماذج اللغة الكبيرة.
تحتفظ هذه الوحدة بسجل لجميع وكلاء الذكاء الاصطناعي في سهول
وقدراتهم ونقاط نهايتهم وبياناتهم الوصفية.
"""

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from functools import lru_cache

from ..core.config import settings


class AgentCategory(StrEnum):
    """Categories of AI agents."""

    CROP_HEALTH = "crop_health"
    IRRIGATION = "irrigation"
    ADVISORY = "advisory"
    WEATHER = "weather"
    YIELD = "yield"
    VISION = "vision"
    TERRAIN = "terrain"
    ANALYTICS = "analytics"
    PEST = "pest"


class AgentCapability(StrEnum):
    """Capabilities that agents can have."""

    DISEASE_DETECTION = "disease_detection"
    NUTRIENT_ANALYSIS = "nutrient_analysis"
    IRRIGATION_PLANNING = "irrigation_planning"
    WEATHER_FORECAST = "weather_forecast"
    YIELD_PREDICTION = "yield_prediction"
    IMAGE_ANALYSIS = "image_analysis"
    PEST_DETECTION = "pest_detection"
    FERTILIZER_RECOMMENDATION = "fertilizer_recommendation"
    FIELD_ANALYSIS = "field_analysis"
    TERRAIN_ANALYSIS = "terrain_analysis"
    HYDROLOGY_ANALYSIS = "hydrology_analysis"
    LEVELING_OPTIMIZATION = "leveling_optimization"
    GENERAL_ADVISORY = "general_advisory"


@dataclass
class AgentInfo:
    """
    Information about a registered AI agent.
    معلومات عن وكيل ذكاء اصطناعي مسجل.
    """

    name: str
    name_ar: str
    base_url: str
    category: AgentCategory
    capabilities: list[AgentCapability]
    endpoints: dict[str, str]
    description_en: str
    description_ar: str
    priority: int = 0
    timeout: int = 30
    requires_image: bool = False
    requires_field_id: bool = False
    health_endpoint: str = "/healthz"
    active: bool = True
    tags: list[str] = field(default_factory=list)


class AgentRegistry:
    """
    Registry of all SAHOOL AI agents.
    سجل جميع وكلاء الذكاء الاصطناعي في سهول.
    """

    def __init__(self) -> None:
        """Initialize the agent registry with all known agents."""
        self._agents: dict[str, AgentInfo] = {}
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Register all known SAHOOL agents."""

        # Crop Intelligence Service
        self._agents["crop-intelligence"] = AgentInfo(
            name="crop-intelligence",
            name_ar="ذكاء المحاصيل",
            base_url=settings.crop_intelligence_url,
            category=AgentCategory.CROP_HEALTH,
            capabilities=[
                AgentCapability.DISEASE_DETECTION,
                AgentCapability.NUTRIENT_ANALYSIS,
                AgentCapability.FIELD_ANALYSIS,
            ],
            endpoints={
                "disease_detect": "/api/v1/disease/detect",
                "nutrient_detect": "/api/v1/nutrients/detect",
                "comprehensive": "/api/v1/comprehensive-analysis",
                "diagnosis": "/api/v1/fields/{field_id}/diagnosis",
            },
            description_en="Intelligent crop health diagnostics with disease and nutrient detection",
            description_ar="تشخيص صحة المحاصيل الذكي مع كشف الأمراض والعناصر الغذائية",
            priority=1,
            requires_field_id=True,
            tags=["crop", "health", "disease", "nutrient"],
        )

        # Advisory Service
        self._agents["advisory"] = AgentInfo(
            name="advisory",
            name_ar="الاستشارات",
            base_url=settings.advisory_url,
            category=AgentCategory.ADVISORY,
            capabilities=[
                AgentCapability.FERTILIZER_RECOMMENDATION,
                AgentCapability.GENERAL_ADVISORY,
                AgentCapability.DISEASE_DETECTION,
            ],
            endpoints={
                "disease_assess": "/disease/assess",
                "disease_symptoms": "/disease/symptoms",
                "fertilizer_plan": "/fertilizer/plan",
                "nutrient_ndvi": "/nutrient/ndvi",
                "crops": "/crops",
            },
            description_en="Agricultural advisory for disease diagnosis and fertilizer planning",
            description_ar="استشارات زراعية لتشخيص الأمراض وتخطيط الأسمدة",
            priority=2,
            tags=["advisory", "fertilizer", "disease"],
        )

        # Irrigation Smart Service
        self._agents["irrigation"] = AgentInfo(
            name="irrigation",
            name_ar="الري الذكي",
            base_url=settings.irrigation_url,
            category=AgentCategory.IRRIGATION,
            capabilities=[
                AgentCapability.IRRIGATION_PLANNING,
            ],
            endpoints={
                "schedule": "/api/v1/irrigation/schedule",
                "recommendation": "/api/v1/irrigation/recommend",
                "water_balance": "/api/v1/irrigation/water-balance",
            },
            description_en="Smart irrigation scheduling and water management",
            description_ar="جدولة الري الذكي وإدارة المياه",
            priority=1,
            requires_field_id=True,
            tags=["irrigation", "water", "scheduling"],
        )

        # Pest Detection Service
        self._agents["pest-detection"] = AgentInfo(
            name="pest-detection",
            name_ar="كشف الآفات",
            base_url=settings.pest_detection_url,
            category=AgentCategory.PEST,
            capabilities=[
                AgentCapability.PEST_DETECTION,
                AgentCapability.IMAGE_ANALYSIS,
            ],
            endpoints={
                "detect": "/api/v1/pest/detect",
                "analyze_image": "/api/v1/pest/analyze-image",
                "risk_assessment": "/api/v1/pest/risk",
            },
            description_en="Pest detection and risk assessment for crops",
            description_ar="كشف الآفات وتقييم المخاطر للمحاصيل",
            priority=2,
            requires_image=True,
            tags=["pest", "detection", "image"],
        )

        # Weather Service
        self._agents["weather"] = AgentInfo(
            name="weather",
            name_ar="الطقس",
            base_url=settings.weather_url,
            category=AgentCategory.WEATHER,
            capabilities=[
                AgentCapability.WEATHER_FORECAST,
            ],
            endpoints={
                "current": "/api/v1/weather/current",
                "forecast": "/api/v1/weather/forecast",
                "historical": "/api/v1/weather/historical",
                "alerts": "/api/v1/weather/alerts",
            },
            description_en="Weather data and forecasting for agricultural planning",
            description_ar="بيانات الطقس والتنبؤات للتخطيط الزراعي",
            priority=3,
            tags=["weather", "forecast", "climate"],
        )

        # Yield Prediction Service
        self._agents["yield-prediction-service"] = AgentInfo(
            name="yield-prediction-service",
            name_ar="محرك الإنتاجية",
            base_url=settings.yield_engine_url,
            category=AgentCategory.YIELD,
            capabilities=[
                AgentCapability.YIELD_PREDICTION,
            ],
            endpoints={
                "predict": "/api/v1/yield/predict",
                "estimate": "/api/v1/yield/estimate",
                "historical": "/api/v1/yield/historical",
            },
            description_en="Yield prediction and estimation for crops",
            description_ar="تنبؤ وتقدير الإنتاجية للمحاصيل",
            priority=2,
            requires_field_id=True,
            tags=["yield", "prediction", "harvest"],
        )

        # Field Intelligence
        self._agents["field-intelligence"] = AgentInfo(
            name="field-intelligence",
            name_ar="ذكاء الحقول",
            base_url=settings.field_intelligence_url,
            category=AgentCategory.ANALYTICS,
            capabilities=[
                AgentCapability.FIELD_ANALYSIS,
            ],
            endpoints={
                "analyze": "/api/v1/field/analyze",
                "zones": "/api/v1/field/zones",
                "status": "/api/v1/field/status",
            },
            description_en="Field-level analytics and zone management",
            description_ar="تحليلات على مستوى الحقل وإدارة المناطق",
            priority=2,
            requires_field_id=True,
            tags=["field", "analytics", "zones"],
        )

        # Indicators Service
        self._agents["indicators"] = AgentInfo(
            name="indicators",
            name_ar="المؤشرات",
            base_url=settings.indicators_url,
            category=AgentCategory.ANALYTICS,
            capabilities=[
                AgentCapability.FIELD_ANALYSIS,
            ],
            endpoints={
                "compute": "/api/v1/indicators/compute",
                "ndvi": "/api/v1/indicators/ndvi",
                "lai": "/api/v1/indicators/lai",
            },
            description_en="Vegetation indices computation (NDVI, LAI, etc.)",
            description_ar="حساب مؤشرات الغطاء النباتي (NDVI, LAI, إلخ)",
            priority=3,
            tags=["ndvi", "lai", "indices", "vegetation"],
        )

        # YOLO Vision Service
        self._agents["yolo-vision"] = AgentInfo(
            name="yolo-vision",
            name_ar="الرؤية بالذكاء الاصطناعي",
            base_url=settings.yolo_vision_url,
            category=AgentCategory.VISION,
            capabilities=[
                AgentCapability.IMAGE_ANALYSIS,
                AgentCapability.PEST_DETECTION,
                AgentCapability.DISEASE_DETECTION,
            ],
            endpoints={
                "detect": "/api/v1/vision/detect",
                "batch": "/api/v1/vision/batch",
                "models": "/api/v1/vision/models",
            },
            description_en="YOLO-based computer vision for pest, disease, and weed detection",
            description_ar="رؤية حاسوبية قائمة على YOLO لكشف الآفات والأمراض والأعشاب",
            priority=1,
            requires_image=True,
            timeout=60,
            tags=["vision", "yolo", "image", "detection"],
        )

        # Terrain Core Service
        self._agents["terrain"] = AgentInfo(
            name="terrain",
            name_ar="التضاريس",
            base_url=settings.terrain_url,
            category=AgentCategory.TERRAIN,
            capabilities=[
                AgentCapability.TERRAIN_ANALYSIS,
            ],
            endpoints={
                "analyze": "/api/v1/terrain/analyze",
                "dem": "/api/v1/terrain/dem",
                "slope": "/api/v1/terrain/slope",
                "aspect": "/api/v1/terrain/aspect",
            },
            description_en="Terrain analysis using DEM data",
            description_ar="تحليل التضاريس باستخدام بيانات نموذج الارتفاع الرقمي",
            priority=3,
            tags=["terrain", "dem", "slope", "elevation"],
        )

        # Hydrology Service
        self._agents["hydrology"] = AgentInfo(
            name="hydrology",
            name_ar="الهيدرولوجيا",
            base_url=settings.hydrology_url,
            category=AgentCategory.TERRAIN,
            capabilities=[
                AgentCapability.HYDROLOGY_ANALYSIS,
            ],
            endpoints={
                "drainage": "/api/v1/hydrology/drainage",
                "watershed": "/api/v1/hydrology/watershed",
                "flow": "/api/v1/hydrology/flow",
            },
            description_en="Hydrology and drainage analysis",
            description_ar="تحليل الهيدرولوجيا والصرف",
            priority=3,
            tags=["hydrology", "drainage", "watershed", "water"],
        )

        # Leveling Optimizer Service
        self._agents["leveling"] = AgentInfo(
            name="leveling",
            name_ar="تسوية الأراضي",
            base_url=settings.leveling_url,
            category=AgentCategory.TERRAIN,
            capabilities=[
                AgentCapability.LEVELING_OPTIMIZATION,
            ],
            endpoints={
                "optimize": "/api/v1/leveling/optimize",
                "cut_fill": "/api/v1/leveling/cut-fill",
                "cost": "/api/v1/leveling/cost",
            },
            description_en="Field leveling optimization and cut/fill calculations",
            description_ar="تحسين تسوية الحقول وحسابات القطع/الردم",
            priority=3,
            requires_field_id=True,
            tags=["leveling", "grading", "cut-fill"],
        )

    def get_agent(self, name: str) -> AgentInfo | None:
        """Get agent info by name."""
        return self._agents.get(name)

    def get_all_agents(self) -> list[AgentInfo]:
        """Get all registered agents."""
        return list(self._agents.values())

    def get_active_agents(self) -> list[AgentInfo]:
        """Get all active agents."""
        return [a for a in self._agents.values() if a.active]

    def get_agents_by_category(self, category: AgentCategory) -> list[AgentInfo]:
        """Get agents by category."""
        return [a for a in self._agents.values() if a.category == category and a.active]

    def get_agents_by_capability(self, capability: AgentCapability) -> list[AgentInfo]:
        """Get agents that have a specific capability."""
        return [a for a in self._agents.values() if capability in a.capabilities and a.active]

    def get_agents_for_intent(self, intent_type: str) -> list[AgentInfo]:
        """
        Get relevant agents for a given intent type.
        الحصول على الوكلاء المناسبين لنوع نية معين.
        """
        intent_to_capabilities: dict[str, list[AgentCapability]] = {
            "crop_disease": [AgentCapability.DISEASE_DETECTION],
            "irrigation_query": [AgentCapability.IRRIGATION_PLANNING],
            "fertilizer_advice": [AgentCapability.FERTILIZER_RECOMMENDATION],
            "pest_detection": [AgentCapability.PEST_DETECTION],
            "weather_query": [AgentCapability.WEATHER_FORECAST],
            "yield_prediction": [AgentCapability.YIELD_PREDICTION],
            "field_analysis": [AgentCapability.FIELD_ANALYSIS],
            "terrain_analysis": [AgentCapability.TERRAIN_ANALYSIS],
            "hydrology_query": [AgentCapability.HYDROLOGY_ANALYSIS],
            "leveling_query": [AgentCapability.LEVELING_OPTIMIZATION],
            "image_analysis": [AgentCapability.IMAGE_ANALYSIS],
            "general_advisory": [AgentCapability.GENERAL_ADVISORY],
        }

        capabilities = intent_to_capabilities.get(intent_type, [])
        agents: list[AgentInfo] = []

        for cap in capabilities:
            agents.extend(self.get_agents_by_capability(cap))

        # Remove duplicates while preserving order
        seen: set[str] = set()
        unique_agents: list[AgentInfo] = []
        for agent in agents:
            if agent.name not in seen:
                seen.add(agent.name)
                unique_agents.append(agent)

        # Sort by priority
        unique_agents.sort(key=lambda a: a.priority)

        return unique_agents

    def to_dict(self) -> dict:
        """Convert registry to dictionary for API response."""
        return {
            "agents": [
                {
                    "name": a.name,
                    "name_ar": a.name_ar,
                    "category": a.category.value,
                    "capabilities": [c.value for c in a.capabilities],
                    "description_en": a.description_en,
                    "description_ar": a.description_ar,
                    "active": a.active,
                    "tags": a.tags,
                }
                for a in self._agents.values()
            ],
            "total": len(self._agents),
            "active": sum(1 for a in self._agents.values() if a.active),
        }


@lru_cache
def get_agent_registry() -> AgentRegistry:
    """Get cached agent registry instance."""
    return AgentRegistry()
