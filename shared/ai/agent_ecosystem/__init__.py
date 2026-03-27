"""
AI Agent Ecosystem | نظام الوكلاء الذكيين

Defines 25+ specialized agricultural AI agents organized in 6 categories.
Implements agent activation, capability registry, and inter-agent communication.

Based on governance/agents.yaml definitions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class AgentCategory(StrEnum):
    """Agent categories | فئات الوكلاء"""

    PRODUCTION = "production"  # إنتاج
    MONITORING = "monitoring"  # مراقبة
    PLANNING = "planning"  # تخطيط
    MARKET = "market"  # سوق
    SUPPORT = "support"  # دعم
    ADVANCED = "advanced"  # متقدم


class AgentStatus(StrEnum):
    """Agent operational status | حالة تشغيل الوكيل"""

    ACTIVE = "active"  # نشط
    INACTIVE = "inactive"  # غير نشط
    WARMING_UP = "warming_up"  # قيد التحميل
    ERROR = "error"  # خطأ
    MAINTENANCE = "maintenance"  # صيانة


CATEGORY_AR = {
    AgentCategory.PRODUCTION: "إنتاج",
    AgentCategory.MONITORING: "مراقبة",
    AgentCategory.PLANNING: "تخطيط",
    AgentCategory.MARKET: "سوق",
    AgentCategory.SUPPORT: "دعم",
    AgentCategory.ADVANCED: "متقدم",
}

STATUS_AR = {
    AgentStatus.ACTIVE: "نشط",
    AgentStatus.INACTIVE: "غير نشط",
    AgentStatus.WARMING_UP: "قيد التحميل",
    AgentStatus.ERROR: "خطأ",
    AgentStatus.MAINTENANCE: "صيانة",
}


@dataclass
class AgentCapability:
    """A capability that an agent can perform | قدرة يمكن للوكيل تنفيذها"""

    name: str = ""
    name_ar: str = ""
    description: str = ""
    description_ar: str = ""
    input_types: list[str] = field(default_factory=list)
    output_type: str = ""


@dataclass
class AgentDefinition:
    """Definition of an AI agent | تعريف وكيل ذكي"""

    agent_id: str = ""
    name: str = ""
    name_ar: str = ""
    category: AgentCategory = AgentCategory.PRODUCTION
    category_ar: str = ""
    description: str = ""
    description_ar: str = ""
    capabilities: list[AgentCapability] = field(default_factory=list)
    required_services: list[str] = field(default_factory=list)
    model: str = "codellama:7b"
    status: AgentStatus = AgentStatus.INACTIVE
    status_ar: str = "غير نشط"
    priority: int = 5
    tags: list[str] = field(default_factory=list)


@dataclass
class AgentMessage:
    """Message between agents (A2A protocol) | رسالة بين الوكلاء"""

    message_id: str = ""
    from_agent: str = ""
    to_agent: str = ""
    message_type: str = "request"  # request, response, broadcast
    content: dict = field(default_factory=dict)
    timestamp: str = ""
    correlation_id: str = ""


@dataclass
class AgentEcosystemStatus:
    """Overall ecosystem status | حالة النظام البيئي"""

    total_agents: int = 0
    active_agents: int = 0
    inactive_agents: int = 0
    agents_by_category: dict[str, int] = field(default_factory=dict)
    message: str = ""
    message_ar: str = ""


# Agent definitions - 25 specialized agents
AGENT_DEFINITIONS: list[dict] = [
    # === PRODUCTION (5) | إنتاج ===
    {
        "agent_id": "crop_advisor",
        "name": "Crop Advisor",
        "name_ar": "مستشار المحاصيل",
        "category": AgentCategory.PRODUCTION,
        "description": "Provides crop management advice based on field conditions",
        "description_ar": "يقدم نصائح إدارة المحاصيل بناءً على ظروف الحقل",
        "capabilities": [
            {"name": "crop_recommendation", "name_ar": "توصية المحصول"},
            {"name": "growth_stage_assessment", "name_ar": "تقييم مرحلة النمو"},
            {"name": "variety_selection", "name_ar": "اختيار الصنف"},
        ],
        "required_services": ["advisory-service", "crop-intelligence-service"],
        "priority": 1,
        "tags": ["core", "advisory"],
    },
    {
        "agent_id": "irrigation_expert",
        "name": "Irrigation Expert",
        "name_ar": "خبير الري",
        "category": AgentCategory.PRODUCTION,
        "description": "Optimizes irrigation schedules and water usage",
        "description_ar": "يحسّن جداول الري واستخدام المياه",
        "capabilities": [
            {"name": "irrigation_scheduling", "name_ar": "جدولة الري"},
            {"name": "water_balance", "name_ar": "توازن المياه"},
            {"name": "efficiency_analysis", "name_ar": "تحليل الكفاءة"},
        ],
        "required_services": ["irrigation-smart", "weather-service", "iot-service"],
        "priority": 1,
        "tags": ["core", "irrigation"],
    },
    {
        "agent_id": "plant_doctor",
        "name": "Plant Doctor",
        "name_ar": "طبيب النبات",
        "category": AgentCategory.PRODUCTION,
        "description": "Diagnoses crop diseases and recommends treatments",
        "description_ar": "يشخص أمراض المحاصيل ويوصي بالعلاجات",
        "capabilities": [
            {"name": "disease_diagnosis", "name_ar": "تشخيص الأمراض"},
            {"name": "treatment_recommendation", "name_ar": "توصية العلاج"},
            {"name": "prevention_plan", "name_ar": "خطة الوقاية"},
        ],
        "required_services": ["crop-intelligence-service", "yolo26-vision-service"],
        "priority": 1,
        "tags": ["core", "health"],
    },
    {
        "agent_id": "fertilizer_specialist",
        "name": "Fertilizer Specialist",
        "name_ar": "أخصائي التسميد",
        "category": AgentCategory.PRODUCTION,
        "description": "Recommends optimal fertilizer types and rates",
        "description_ar": "يوصي بأنواع ومعدلات الأسمدة المثلى",
        "capabilities": [
            {"name": "nutrient_analysis", "name_ar": "تحليل المغذيات"},
            {"name": "fertilizer_prescription", "name_ar": "وصفة التسميد"},
            {"name": "soil_amendment", "name_ar": "تعديل التربة"},
        ],
        "required_services": ["advisory-service", "soil-analysis-service"],
        "priority": 2,
        "tags": ["core", "nutrition"],
    },
    {
        "agent_id": "yield_analyst",
        "name": "Yield Analyst",
        "name_ar": "محلل الإنتاجية",
        "category": AgentCategory.PRODUCTION,
        "description": "Predicts and analyzes crop yields",
        "description_ar": "يتنبأ بإنتاجية المحاصيل ويحللها",
        "capabilities": [
            {"name": "yield_prediction", "name_ar": "تنبؤ الإنتاجية"},
            {"name": "yield_gap_analysis", "name_ar": "تحليل فجوة الإنتاجية"},
            {"name": "harvest_timing", "name_ar": "توقيت الحصاد"},
        ],
        "required_services": ["yield-prediction-service", "crop-growth-model"],
        "priority": 2,
        "tags": ["core", "yield"],
    },
    # === MONITORING (5) | مراقبة ===
    {
        "agent_id": "satellite_analyst",
        "name": "Satellite Analyst",
        "name_ar": "محلل الأقمار الصناعية",
        "category": AgentCategory.MONITORING,
        "description": "Analyzes satellite imagery for vegetation health",
        "description_ar": "يحلل صور الأقمار الصناعية لصحة الغطاء النباتي",
        "capabilities": [
            {"name": "ndvi_analysis", "name_ar": "تحليل NDVI"},
            {"name": "change_detection", "name_ar": "كشف التغيرات"},
            {"name": "anomaly_detection", "name_ar": "كشف الشذوذ"},
        ],
        "required_services": ["vegetation-analysis-service"],
        "priority": 2,
        "tags": ["monitoring", "satellite"],
    },
    {
        "agent_id": "weather_monitor",
        "name": "Weather Monitor",
        "name_ar": "مراقب الطقس",
        "category": AgentCategory.MONITORING,
        "description": "Monitors weather conditions and issues alerts",
        "description_ar": "يراقب الأحوال الجوية ويصدر التنبيهات",
        "capabilities": [
            {"name": "forecast_analysis", "name_ar": "تحليل التوقعات"},
            {"name": "frost_alert", "name_ar": "تنبيه الصقيع"},
            {"name": "spray_window", "name_ar": "نافذة الرش"},
        ],
        "required_services": ["weather-service", "alert-service"],
        "priority": 1,
        "tags": ["monitoring", "weather"],
    },
    {
        "agent_id": "sensor_analyst",
        "name": "Sensor Analyst",
        "name_ar": "محلل المستشعرات",
        "category": AgentCategory.MONITORING,
        "description": "Processes and interprets IoT sensor data",
        "description_ar": "يعالج ويفسر بيانات مستشعرات إنترنت الأشياء",
        "capabilities": [
            {"name": "sensor_fusion", "name_ar": "دمج المستشعرات"},
            {"name": "threshold_alerts", "name_ar": "تنبيهات العتبات"},
            {"name": "trend_analysis", "name_ar": "تحليل الاتجاهات"},
        ],
        "required_services": ["iot-service", "iot-sensor-hub", "virtual-sensors"],
        "priority": 2,
        "tags": ["monitoring", "iot"],
    },
    {
        "agent_id": "pest_scout",
        "name": "Pest Scout",
        "name_ar": "كشاف الآفات",
        "category": AgentCategory.MONITORING,
        "description": "Scouts for pests and monitors population levels",
        "description_ar": "يكشف عن الآفات ويراقب مستويات الأعداد",
        "capabilities": [
            {"name": "pest_identification", "name_ar": "تحديد الآفات"},
            {"name": "population_monitoring", "name_ar": "مراقبة الأعداد"},
            {"name": "ipm_recommendation", "name_ar": "توصية الإدارة المتكاملة"},
        ],
        "required_services": ["pest-detection-service", "yolo26-vision-service"],
        "priority": 1,
        "tags": ["monitoring", "pest"],
    },
    {
        "agent_id": "soil_monitor",
        "name": "Soil Monitor",
        "name_ar": "مراقب التربة",
        "category": AgentCategory.MONITORING,
        "description": "Monitors soil health and conditions",
        "description_ar": "يراقب صحة التربة وظروفها",
        "capabilities": [
            {"name": "moisture_tracking", "name_ar": "تتبع الرطوبة"},
            {"name": "salinity_monitoring", "name_ar": "مراقبة الملوحة"},
            {"name": "nutrient_status", "name_ar": "حالة المغذيات"},
        ],
        "required_services": ["soil-analysis-service", "iot-sensor-hub"],
        "priority": 2,
        "tags": ["monitoring", "soil"],
    },
    # === PLANNING (4) | تخطيط ===
    {
        "agent_id": "season_planner",
        "name": "Season Planner",
        "name_ar": "مخطط الموسم",
        "category": AgentCategory.PLANNING,
        "description": "Plans seasonal agricultural activities",
        "description_ar": "يخطط الأنشطة الزراعية الموسمية",
        "capabilities": [
            {"name": "crop_calendar", "name_ar": "تقويم المحاصيل"},
            {"name": "rotation_planning", "name_ar": "تخطيط الدورة"},
            {"name": "resource_allocation", "name_ar": "تخصيص الموارد"},
        ],
        "required_services": ["advisory-service", "task-service"],
        "priority": 3,
        "tags": ["planning", "seasonal"],
    },
    {
        "agent_id": "inventory_manager",
        "name": "Inventory Manager",
        "name_ar": "مدير المخزون",
        "category": AgentCategory.PLANNING,
        "description": "Manages farm inventory and supplies",
        "description_ar": "يدير مخزون المزرعة والمستلزمات",
        "capabilities": [
            {"name": "stock_tracking", "name_ar": "تتبع المخزون"},
            {"name": "reorder_alerts", "name_ar": "تنبيهات إعادة الطلب"},
            {"name": "usage_forecast", "name_ar": "توقع الاستخدام"},
        ],
        "required_services": ["inventory-service"],
        "priority": 3,
        "tags": ["planning", "inventory"],
    },
    {
        "agent_id": "task_coordinator",
        "name": "Task Coordinator",
        "name_ar": "منسق المهام",
        "category": AgentCategory.PLANNING,
        "description": "Coordinates farm tasks and workforce",
        "description_ar": "ينسق مهام المزرعة والقوى العاملة",
        "capabilities": [
            {"name": "task_scheduling", "name_ar": "جدولة المهام"},
            {"name": "worker_assignment", "name_ar": "تعيين العمال"},
            {"name": "progress_tracking", "name_ar": "تتبع التقدم"},
        ],
        "required_services": ["task-service", "equipment-service"],
        "priority": 3,
        "tags": ["planning", "tasks"],
    },
    {
        "agent_id": "farm_accountant",
        "name": "Farm Accountant",
        "name_ar": "محاسب المزرعة",
        "category": AgentCategory.PLANNING,
        "description": "Tracks costs and generates financial reports",
        "description_ar": "يتتبع التكاليف ويولد التقارير المالية",
        "capabilities": [
            {"name": "cost_tracking", "name_ar": "تتبع التكاليف"},
            {"name": "roi_analysis", "name_ar": "تحليل العائد"},
            {"name": "budget_planning", "name_ar": "تخطيط الميزانية"},
        ],
        "required_services": ["billing-core"],
        "priority": 3,
        "tags": ["planning", "finance"],
    },
    # === MARKET (3) | سوق ===
    {
        "agent_id": "price_analyst",
        "name": "Price Analyst",
        "name_ar": "محلل الأسعار",
        "category": AgentCategory.MARKET,
        "description": "Analyzes market prices and trends",
        "description_ar": "يحلل أسعار السوق والاتجاهات",
        "capabilities": [
            {"name": "price_tracking", "name_ar": "تتبع الأسعار"},
            {"name": "trend_analysis", "name_ar": "تحليل الاتجاهات"},
            {"name": "price_forecast", "name_ar": "توقع الأسعار"},
        ],
        "required_services": ["marketplace-service"],
        "priority": 4,
        "tags": ["market", "prices"],
    },
    {
        "agent_id": "sales_broker",
        "name": "Sales Broker",
        "name_ar": "وسيط المبيعات",
        "category": AgentCategory.MARKET,
        "description": "Facilitates buying and selling transactions",
        "description_ar": "يسهل عمليات البيع والشراء",
        "capabilities": [
            {"name": "listing_optimization", "name_ar": "تحسين القوائم"},
            {"name": "buyer_matching", "name_ar": "مطابقة المشترين"},
            {"name": "negotiation_support", "name_ar": "دعم التفاوض"},
        ],
        "required_services": ["marketplace-service"],
        "priority": 4,
        "tags": ["market", "sales"],
    },
    {
        "agent_id": "procurement_advisor",
        "name": "Procurement Advisor",
        "name_ar": "مستشار المشتريات",
        "category": AgentCategory.MARKET,
        "description": "Advises on purchasing inputs and equipment",
        "description_ar": "ينصح بشراء المدخلات والمعدات",
        "capabilities": [
            {"name": "supplier_comparison", "name_ar": "مقارنة الموردين"},
            {"name": "cost_optimization", "name_ar": "تحسين التكاليف"},
            {"name": "quality_assessment", "name_ar": "تقييم الجودة"},
        ],
        "required_services": ["marketplace-service", "inventory-service"],
        "priority": 4,
        "tags": ["market", "procurement"],
    },
    # === SUPPORT (3) | دعم ===
    {
        "agent_id": "voice_assistant",
        "name": "Voice Assistant",
        "name_ar": "المساعد الصوتي",
        "category": AgentCategory.SUPPORT,
        "description": "Arabic voice interface for hands-free operation",
        "description_ar": "واجهة صوتية عربية للتشغيل بدون يدين",
        "capabilities": [
            {"name": "voice_recognition", "name_ar": "التعرف على الصوت"},
            {"name": "voice_command", "name_ar": "الأوامر الصوتية"},
            {"name": "text_to_speech", "name_ar": "تحويل النص لصوت"},
        ],
        "required_services": ["ai-chat-assistant"],
        "priority": 5,
        "tags": ["support", "voice"],
    },
    {
        "agent_id": "content_translator",
        "name": "Content Translator",
        "name_ar": "مترجم المحتوى",
        "category": AgentCategory.SUPPORT,
        "description": "Translates content between Arabic dialects and English",
        "description_ar": "يترجم المحتوى بين اللهجات العربية والإنجليزية",
        "capabilities": [
            {"name": "dialect_translation", "name_ar": "ترجمة اللهجات"},
            {"name": "technical_translation", "name_ar": "ترجمة تقنية"},
            {"name": "content_localization", "name_ar": "توطين المحتوى"},
        ],
        "required_services": ["ai-chat-assistant", "llm-orchestrator-service"],
        "priority": 5,
        "tags": ["support", "translation"],
    },
    {
        "agent_id": "report_generator",
        "name": "Report Generator",
        "name_ar": "مولد التقارير",
        "category": AgentCategory.SUPPORT,
        "description": "Generates comprehensive farm reports",
        "description_ar": "يولد تقارير شاملة للمزرعة",
        "capabilities": [
            {"name": "daily_report", "name_ar": "تقرير يومي"},
            {"name": "season_summary", "name_ar": "ملخص الموسم"},
            {"name": "compliance_report", "name_ar": "تقرير الامتثال"},
        ],
        "required_services": ["logistics-service", "billing-core"],
        "priority": 5,
        "tags": ["support", "reports"],
    },
    # === ADVANCED (5) | متقدم ===
    {
        "agent_id": "master_orchestrator",
        "name": "Master Orchestrator",
        "name_ar": "المنسق الرئيسي",
        "category": AgentCategory.ADVANCED,
        "description": "Coordinates multiple agents for complex tasks",
        "description_ar": "ينسق عدة وكلاء للمهام المعقدة",
        "capabilities": [
            {"name": "multi_agent_coordination", "name_ar": "تنسيق متعدد الوكلاء"},
            {"name": "consensus_building", "name_ar": "بناء التوافق"},
            {"name": "conflict_resolution", "name_ar": "حل النزاعات"},
        ],
        "required_services": ["agent-registry", "ai-agents-core"],
        "priority": 1,
        "tags": ["advanced", "orchestration"],
    },
    {
        "agent_id": "risk_analyst",
        "name": "Risk Analyst",
        "name_ar": "محلل المخاطر",
        "category": AgentCategory.ADVANCED,
        "description": "Assesses agricultural risks and mitigation strategies",
        "description_ar": "يقيم المخاطر الزراعية واستراتيجيات التخفيف",
        "capabilities": [
            {"name": "risk_assessment", "name_ar": "تقييم المخاطر"},
            {"name": "mitigation_planning", "name_ar": "تخطيط التخفيف"},
            {"name": "insurance_advisory", "name_ar": "استشارة التأمين"},
        ],
        "required_services": ["advisory-service", "weather-service"],
        "priority": 3,
        "tags": ["advanced", "risk"],
    },
    {
        "agent_id": "farmer_trainer",
        "name": "Farmer Trainer",
        "name_ar": "مدرب المزارعين",
        "category": AgentCategory.ADVANCED,
        "description": "Provides personalized training and education",
        "description_ar": "يقدم تدريباً وتعليماً مخصصاً",
        "capabilities": [
            {"name": "lesson_planning", "name_ar": "تخطيط الدروس"},
            {"name": "skill_assessment", "name_ar": "تقييم المهارات"},
            {"name": "progress_tracking", "name_ar": "تتبع التقدم"},
        ],
        "required_services": ["ai-chat-assistant"],
        "priority": 4,
        "tags": ["advanced", "education"],
    },
    {
        "agent_id": "compliance_agent",
        "name": "Compliance Agent",
        "name_ar": "وكيل الامتثال",
        "category": AgentCategory.ADVANCED,
        "description": "Ensures GlobalGAP and regulatory compliance",
        "description_ar": "يضمن الامتثال لـ GlobalGAP والتنظيمات",
        "capabilities": [
            {"name": "compliance_check", "name_ar": "فحص الامتثال"},
            {"name": "documentation", "name_ar": "التوثيق"},
            {"name": "audit_preparation", "name_ar": "تحضير التدقيق"},
        ],
        "required_services": ["globalgap-compliance", "audit-service"],
        "priority": 3,
        "tags": ["advanced", "compliance"],
    },
    {
        "agent_id": "sustainability_agent",
        "name": "Sustainability Agent",
        "name_ar": "وكيل الاستدامة",
        "category": AgentCategory.ADVANCED,
        "description": "Tracks and improves environmental sustainability",
        "description_ar": "يتتبع ويحسن الاستدامة البيئية",
        "capabilities": [
            {"name": "carbon_tracking", "name_ar": "تتبع الكربون"},
            {"name": "water_footprint", "name_ar": "البصمة المائية"},
            {"name": "biodiversity_monitoring", "name_ar": "مراقبة التنوع الحيوي"},
        ],
        "required_services": ["advisory-service"],
        "priority": 4,
        "tags": ["advanced", "sustainability"],
    },
]


class AgentEcosystem:
    """Manages the AI agent ecosystem.

    يدير نظام الوكلاء الذكيين البيئي.
    """

    def __init__(self):
        self._agents: dict[str, AgentDefinition] = {}
        self._load_agents()

    def _load_agents(self):
        """Load agent definitions."""
        for agent_dict in AGENT_DEFINITIONS:
            caps = []
            for cap in agent_dict.get("capabilities", []):
                caps.append(
                    AgentCapability(
                        name=cap.get("name", ""),
                        name_ar=cap.get("name_ar", ""),
                    )
                )

            agent = AgentDefinition(
                agent_id=agent_dict["agent_id"],
                name=agent_dict["name"],
                name_ar=agent_dict["name_ar"],
                category=agent_dict["category"],
                category_ar=CATEGORY_AR.get(agent_dict["category"], ""),
                description=agent_dict["description"],
                description_ar=agent_dict["description_ar"],
                capabilities=caps,
                required_services=agent_dict.get("required_services", []),
                status=AgentStatus.INACTIVE,
                status_ar=STATUS_AR[AgentStatus.INACTIVE],
                priority=agent_dict.get("priority", 5),
                tags=agent_dict.get("tags", []),
            )
            self._agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> AgentDefinition | None:
        """Get agent by ID."""
        return self._agents.get(agent_id)

    def list_agents(self, category: AgentCategory | None = None) -> list[AgentDefinition]:
        """List all agents, optionally filtered by category."""
        agents = list(self._agents.values())
        if category:
            agents = [a for a in agents if a.category == category]
        return sorted(agents, key=lambda a: a.priority)

    def activate_agent(self, agent_id: str) -> bool:
        """Activate an agent."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.status = AgentStatus.ACTIVE
            agent.status_ar = STATUS_AR[AgentStatus.ACTIVE]
            logger.info(f"Agent {agent_id} activated | تم تفعيل الوكيل {agent.name_ar}")
            return True
        return False

    def deactivate_agent(self, agent_id: str) -> bool:
        """Deactivate an agent."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.status = AgentStatus.INACTIVE
            agent.status_ar = STATUS_AR[AgentStatus.INACTIVE]
            return True
        return False

    def activate_category(self, category: AgentCategory) -> int:
        """Activate all agents in a category. Returns count activated."""
        count = 0
        for agent in self._agents.values():
            if agent.category == category:
                agent.status = AgentStatus.ACTIVE
                agent.status_ar = STATUS_AR[AgentStatus.ACTIVE]
                count += 1
        return count

    def activate_all(self) -> int:
        """Activate all agents. Returns count."""
        count = 0
        for agent in self._agents.values():
            agent.status = AgentStatus.ACTIVE
            agent.status_ar = STATUS_AR[AgentStatus.ACTIVE]
            count += 1
        return count

    def get_status(self) -> AgentEcosystemStatus:
        """Get ecosystem status summary."""
        agents = list(self._agents.values())
        active = sum(1 for a in agents if a.status == AgentStatus.ACTIVE)
        inactive = len(agents) - active

        by_category: dict[str, int] = {}
        for a in agents:
            cat = CATEGORY_AR.get(a.category, a.category.value)
            by_category[cat] = by_category.get(cat, 0) + 1

        return AgentEcosystemStatus(
            total_agents=len(agents),
            active_agents=active,
            inactive_agents=inactive,
            agents_by_category=by_category,
            message=f"Agent ecosystem: {active}/{len(agents)} active",
            message_ar=f"نظام الوكلاء: {active}/{len(agents)} نشط",
        )

    def find_agents_for_task(self, task_keywords: list[str]) -> list[AgentDefinition]:
        """Find agents whose capabilities match task keywords."""
        matches = []
        for agent in self._agents.values():
            for cap in agent.capabilities:
                for kw in task_keywords:
                    if kw.lower() in cap.name.lower() or kw.lower() in " ".join(agent.tags):
                        matches.append(agent)
                        break
                else:
                    continue
                break
        return matches
