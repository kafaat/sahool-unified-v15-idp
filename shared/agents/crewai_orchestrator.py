# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
CrewAI Multi-Agent Orchestrator
منسق الوكلاء المتعددين باستخدام CrewAI

Uses CrewAI (https://github.com/joaomdmoura/crewAI) for:
- Simple multi-agent orchestration
- Role-based agent definitions
- Task delegation and execution
- Sequential and parallel workflows

CrewAI provides a simpler alternative to complex FSM-based agents.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger()


class AgentRole(StrEnum):
    """Roles for agricultural AI agents."""

    CROP_ADVISOR = "crop_advisor"  # مستشار المحاصيل
    IRRIGATION_EXPERT = "irrigation_expert"  # خبير الري
    DISEASE_DIAGNOSTICIAN = "disease_diagnostician"  # مشخص الأمراض
    PEST_CONTROLLER = "pest_controller"  # مكافح الآفات
    SOIL_ANALYST = "soil_analyst"  # محلل التربة
    YIELD_PREDICTOR = "yield_predictor"  # متنبئ الإنتاجية
    MARKET_ANALYST = "market_analyst"  # محلل السوق
    COORDINATOR = "coordinator"  # منسق


@dataclass
class AgentConfig:
    """Configuration for an agricultural agent."""

    role: AgentRole
    goal: str
    goal_ar: str
    backstory: str
    backstory_ar: str
    tools: list[str] = field(default_factory=list)
    allow_delegation: bool = False
    verbose: bool = True


@dataclass
class TaskResult:
    """Result from an agent task."""

    agent_role: AgentRole
    task_description: str
    result: str
    result_ar: str
    confidence: float
    execution_time_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CrewResult:
    """Result from a crew execution."""

    query: str
    tasks_completed: list[TaskResult]
    final_answer: str
    final_answer_ar: str
    total_time_ms: float
    agents_used: list[AgentRole]


# Pre-defined agent configurations for agriculture
AGRICULTURAL_AGENTS = {
    AgentRole.CROP_ADVISOR: AgentConfig(
        role=AgentRole.CROP_ADVISOR,
        goal="Provide comprehensive crop management advice for Middle Eastern farmers",
        goal_ar="تقديم نصائح شاملة لإدارة المحاصيل للمزارعين في الشرق الأوسط",
        backstory="""You are an experienced agricultural advisor specializing in
        crops common to the Arabian Peninsula including wheat, barley, date palms,
        and vegetables. You understand the challenges of arid climate farming and
        water scarcity. You always provide bilingual advice (Arabic/English).""",
        backstory_ar="""أنت مستشار زراعي خبير متخصص في المحاصيل الشائعة في شبه الجزيرة
        العربية بما في ذلك القمح والشعير والنخيل والخضروات. تفهم تحديات الزراعة في المناخ
        الجاف وندرة المياه. تقدم دائماً نصائح ثنائية اللغة.""",
        tools=["weather_api", "crop_database", "ndvi_analyzer"],
        allow_delegation=True,
    ),
    AgentRole.IRRIGATION_EXPERT: AgentConfig(
        role=AgentRole.IRRIGATION_EXPERT,
        goal="Optimize irrigation schedules to maximize water efficiency",
        goal_ar="تحسين جداول الري لتعظيم كفاءة استخدام المياه",
        backstory="""You are an irrigation specialist with deep knowledge of
        drip irrigation, pivot systems, and traditional flood irrigation.
        You calculate evapotranspiration and soil moisture to recommend
        precise water amounts. Water conservation is your top priority.""",
        backstory_ar="""أنت متخصص في الري مع معرفة عميقة بالري بالتنقيط وأنظمة
        المحور والري بالغمر التقليدي. تحسب التبخر النتحي ورطوبة التربة لتوصية
        بكميات مياه دقيقة. توفير المياه هو أولويتك القصوى.""",
        tools=["soil_moisture_sensor", "weather_api", "et_calculator"],
    ),
    AgentRole.DISEASE_DIAGNOSTICIAN: AgentConfig(
        role=AgentRole.DISEASE_DIAGNOSTICIAN,
        goal="Accurately diagnose crop diseases and recommend treatments",
        goal_ar="تشخيص أمراض المحاصيل بدقة والتوصية بالعلاجات",
        backstory="""You are a plant pathologist specializing in diseases
        affecting crops in hot, arid climates. You can identify diseases
        from images and symptoms, and recommend both chemical and organic
        treatments. You always consider environmental impact.""",
        backstory_ar="""أنت أخصائي أمراض نباتية متخصص في الأمراض التي تصيب
        المحاصيل في المناخات الحارة والجافة. يمكنك تحديد الأمراض من الصور
        والأعراض، والتوصية بالعلاجات الكيميائية والعضوية.""",
        tools=["image_classifier", "disease_database", "treatment_guide"],
    ),
    AgentRole.PEST_CONTROLLER: AgentConfig(
        role=AgentRole.PEST_CONTROLLER,
        goal="Identify pests and recommend integrated pest management solutions",
        goal_ar="تحديد الآفات والتوصية بحلول الإدارة المتكاملة للآفات",
        backstory="""You are an entomologist and pest management expert.
        You identify pests like the Red Palm Weevil, locusts, and aphids.
        You prioritize biological control and IPM strategies over
        broad-spectrum pesticides.""",
        backstory_ar="""أنت عالم حشرات وخبير إدارة آفات. تحدد الآفات مثل سوسة
        النخيل الحمراء والجراد والمن. تعطي الأولوية للمكافحة الحيوية واستراتيجيات
        الإدارة المتكاملة للآفات على المبيدات واسعة النطاق.""",
        tools=["pest_identifier", "ipm_database", "pesticide_guide"],
    ),
    AgentRole.SOIL_ANALYST: AgentConfig(
        role=AgentRole.SOIL_ANALYST,
        goal="Analyze soil conditions and recommend amendments",
        goal_ar="تحليل ظروف التربة والتوصية بالتعديلات",
        backstory="""You are a soil scientist who understands the sandy,
        alkaline soils common in the Gulf region. You interpret soil tests
        and recommend fertilizers, pH adjustments, and organic matter
        additions to improve soil health.""",
        backstory_ar="""أنت عالم تربة تفهم التربة الرملية القلوية الشائعة في
        منطقة الخليج. تفسر اختبارات التربة وتوصي بالأسمدة وتعديلات الحموضة
        وإضافات المادة العضوية لتحسين صحة التربة.""",
        tools=["soil_database", "fertilizer_calculator", "ph_adjuster"],
    ),
    AgentRole.YIELD_PREDICTOR: AgentConfig(
        role=AgentRole.YIELD_PREDICTOR,
        goal="Predict crop yields using historical and current data",
        goal_ar="التنبؤ بإنتاجية المحاصيل باستخدام البيانات التاريخية والحالية",
        backstory="""You are a data scientist specializing in agricultural
        yield prediction. You use weather data, soil conditions, NDVI trends,
        and historical yields to provide accurate production estimates.""",
        backstory_ar="""أنت عالم بيانات متخصص في التنبؤ بالإنتاجية الزراعية.
        تستخدم بيانات الطقس وظروف التربة واتجاهات NDVI والإنتاجية التاريخية
        لتقديم تقديرات إنتاج دقيقة.""",
        tools=["ml_predictor", "historical_database", "ndvi_analyzer"],
    ),
    AgentRole.MARKET_ANALYST: AgentConfig(
        role=AgentRole.MARKET_ANALYST,
        goal="Provide market prices and optimal selling strategies",
        goal_ar="تقديم أسعار السوق واستراتيجيات البيع المثلى",
        backstory="""You track agricultural commodity prices in Saudi Arabia
        and the Gulf region. You advise farmers on the best time to sell
        their produce and which markets offer the best prices.""",
        backstory_ar="""تتابع أسعار السلع الزراعية في المملكة العربية السعودية
        ومنطقة الخليج. تنصح المزارعين بأفضل وقت لبيع منتجاتهم والأسواق التي
        تقدم أفضل الأسعار.""",
        tools=["price_database", "market_trends", "demand_forecast"],
    ),
    AgentRole.COORDINATOR: AgentConfig(
        role=AgentRole.COORDINATOR,
        goal="Coordinate multiple specialists to provide comprehensive advice",
        goal_ar="تنسيق المتخصصين المتعددين لتقديم نصيحة شاملة",
        backstory="""You are the lead agricultural consultant who coordinates
        between specialists. You understand which experts to consult for
        different problems and how to synthesize their advice into
        actionable recommendations.""",
        backstory_ar="""أنت المستشار الزراعي الرئيسي الذي ينسق بين المتخصصين.
        تفهم أي الخبراء يجب استشارتهم للمشاكل المختلفة وكيفية تجميع نصائحهم
        في توصيات قابلة للتنفيذ.""",
        tools=["all"],
        allow_delegation=True,
    ),
}


def _extract_arabic_or_fallback(english_answer: str) -> str:
    """
    Extract Arabic content from a bilingual response, or provide a fallback.

    If the response contains Arabic text (detected by presence of Arabic Unicode
    characters), attempt to extract the Arabic portion. Otherwise, provide a note
    in Arabic indicating the response is available in English only.
    """
    import re

    # Check if the response already contains Arabic text
    arabic_pattern = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")
    arabic_matches = arabic_pattern.findall(english_answer)

    if arabic_matches:
        # Extract lines that contain Arabic characters
        arabic_lines = []
        for line in english_answer.split("\n"):
            if arabic_pattern.search(line):
                arabic_lines.append(line.strip())
        if arabic_lines:
            return "\n".join(arabic_lines)

    # Fallback: provide a note in Arabic that the response is in English
    return f"الرد متاح باللغة الإنجليزية فقط:\n{english_answer}"


class AgriculturalCrew:
    """
    Agricultural AI Crew using CrewAI.
    طاقم الذكاء الاصطناعي الزراعي باستخدام CrewAI
    """

    def __init__(
        self,
        roles: list[AgentRole] | None = None,
        llm_provider: str = "ollama",
        model: str = "llama3.2",
    ):
        self.roles = roles or [
            AgentRole.CROP_ADVISOR,
            AgentRole.IRRIGATION_EXPERT,
            AgentRole.DISEASE_DIAGNOSTICIAN,
        ]
        self.llm_provider = llm_provider
        self.model = model

        self._crew = None
        self._agents = {}
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the CrewAI crew."""
        if self._initialized:
            return True

        try:
            from crewai import Agent

            # Create agents from configurations
            for role in self.roles:
                config = AGRICULTURAL_AGENTS.get(role)
                if config:
                    agent = Agent(
                        role=config.role.value,
                        goal=config.goal,
                        backstory=config.backstory,
                        allow_delegation=config.allow_delegation,
                        verbose=config.verbose,
                    )
                    self._agents[role] = agent

            self._initialized = True
            logger.info(
                "CrewAI crew initialized",
                agents=len(self._agents),
                roles=[r.value for r in self.roles],
            )
            return True

        except ImportError:
            logger.warning(
                "CrewAI not installed. Install with: pip install crewai",
                fallback="Using rule-based fallback",
            )
            return False

    async def execute(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> CrewResult:
        """
        Execute a query with the agricultural crew.
        تنفيذ استعلام مع الطاقم الزراعي
        """
        start_time = datetime.now(UTC)
        context = context or {}

        if not self._initialized:
            if not await self.initialize():
                # Fallback to rule-based response
                return self._fallback_execute(query, context, start_time)

        try:
            from crewai import Task

            # Determine which agents to use based on query
            selected_roles = self._select_agents(query)

            tasks = []
            task_results = []

            for role in selected_roles:
                agent = self._agents.get(role)
                if agent:
                    task = Task(
                        description=f"Answer this query: {query}",
                        agent=agent,
                        expected_output="Detailed agricultural advice in English and Arabic",
                    )
                    tasks.append(task)

            # Execute crew
            from crewai import Crew

            selected_agents = [self._agents[role] for role in selected_roles if role in self._agents]
            crew = Crew(
                agents=selected_agents,
                tasks=tasks,
                verbose=True,
            )

            result = crew.kickoff()

            end_time = datetime.now(UTC)
            total_time = (end_time - start_time).total_seconds() * 1000

            final_answer = str(result)

            # Extract Arabic content from the response if present,
            # otherwise provide a note indicating the response is in English
            final_answer_ar = _extract_arabic_or_fallback(final_answer)

            return CrewResult(
                query=query,
                tasks_completed=task_results,
                final_answer=final_answer,
                final_answer_ar=final_answer_ar,
                total_time_ms=total_time,
                agents_used=selected_roles,
            )

        except Exception as e:
            logger.error("CrewAI execution failed", error=str(e))
            return self._fallback_execute(query, context, start_time)

    def _select_agents(self, query: str) -> list[AgentRole]:
        """Select appropriate agents based on query content."""
        query_lower = query.lower()
        selected = []

        # Disease/pest related
        if any(kw in query_lower for kw in ["disease", "مرض", "بقع", "اصفرار", "ذبول", "rust", "blight"]):
            selected.append(AgentRole.DISEASE_DIAGNOSTICIAN)

        # Pest related
        if any(kw in query_lower for kw in ["pest", "آفة", "حشرة", "سوسة", "دودة", "weevil", "insect"]):
            selected.append(AgentRole.PEST_CONTROLLER)

        # Irrigation related
        if any(kw in query_lower for kw in ["water", "irrigation", "ري", "ماء", "سقي", "رطوبة"]):
            selected.append(AgentRole.IRRIGATION_EXPERT)

        # Soil related
        if any(kw in query_lower for kw in ["soil", "fertilizer", "تربة", "سماد", "nitrogen", "نيتروجين"]):
            selected.append(AgentRole.SOIL_ANALYST)

        # Yield/production related
        if any(kw in query_lower for kw in ["yield", "production", "إنتاج", "محصول", "harvest", "حصاد"]):
            selected.append(AgentRole.YIELD_PREDICTOR)

        # Market related
        if any(kw in query_lower for kw in ["price", "market", "سعر", "سوق", "sell", "بيع"]):
            selected.append(AgentRole.MARKET_ANALYST)

        # Default to crop advisor
        if not selected:
            selected.append(AgentRole.CROP_ADVISOR)

        return selected

    def _fallback_execute(
        self,
        query: str,
        context: dict[str, Any],
        start_time: datetime,
    ) -> CrewResult:
        """Fallback execution when CrewAI is not available."""
        selected_roles = self._select_agents(query)

        # Generate rule-based response
        responses = []
        for role in selected_roles:
            config = AGRICULTURAL_AGENTS.get(role)
            if config:
                responses.append(f"**{role.value}**: Based on your query about ")

        end_time = datetime.now(UTC)
        total_time = (end_time - start_time).total_seconds() * 1000

        # Simple response based on detected intent
        if AgentRole.IRRIGATION_EXPERT in selected_roles:
            answer = (
                "Based on typical conditions, I recommend checking soil moisture "
                "before irrigation. For wheat in the tillering stage, maintain "
                "soil moisture at 50-60% field capacity."
            )
            answer_ar = (
                "بناءً على الظروف النموذجية، أوصي بفحص رطوبة التربة قبل الري. "
                "للقمح في مرحلة التفريع، حافظ على رطوبة التربة عند 50-60% من السعة الحقلية."
            )
        elif AgentRole.DISEASE_DIAGNOSTICIAN in selected_roles:
            answer = (
                "Please provide an image of the affected plant for accurate diagnosis. "
                "Common symptoms like yellowing may indicate nutrient deficiency or disease."
            )
            answer_ar = (
                "يرجى تقديم صورة للنبات المصاب للتشخيص الدقيق. "
                "الأعراض الشائعة مثل الاصفرار قد تشير إلى نقص المغذيات أو المرض."
            )
        else:
            answer = (
                "I'd be happy to help with your agricultural query. "
                "Please provide more details about your crop and field conditions."
            )
            answer_ar = "يسعدني مساعدتك في استفسارك الزراعي. يرجى تقديم مزيد من التفاصيل حول محصولك وظروف الحقل."

        return CrewResult(
            query=query,
            tasks_completed=[
                TaskResult(
                    agent_role=selected_roles[0],
                    task_description=query,
                    result=answer,
                    result_ar=answer_ar,
                    confidence=0.7,
                    execution_time_ms=total_time,
                    metadata={"fallback": True},
                )
            ],
            final_answer=answer,
            final_answer_ar=answer_ar,
            total_time_ms=total_time,
            agents_used=selected_roles,
        )


class CrewAIOrchestrator:
    """
    Main orchestrator for agricultural AI agents.
    المنسق الرئيسي لوكلاء الذكاء الاصطناعي الزراعي
    """

    def __init__(self):
        self._crews: dict[str, AgriculturalCrew] = {}
        self._default_crew = None

    async def initialize(self) -> bool:
        """Initialize the orchestrator with default crews."""
        # Create default crew with common agents
        self._default_crew = AgriculturalCrew(
            roles=[
                AgentRole.COORDINATOR,
                AgentRole.CROP_ADVISOR,
                AgentRole.IRRIGATION_EXPERT,
                AgentRole.DISEASE_DIAGNOSTICIAN,
            ]
        )
        return await self._default_crew.initialize()

    def create_crew(
        self,
        name: str,
        roles: list[AgentRole],
        llm_provider: str = "ollama",
    ) -> AgriculturalCrew:
        """Create a specialized crew."""
        crew = AgriculturalCrew(roles=roles, llm_provider=llm_provider)
        self._crews[name] = crew
        return crew

    async def query(
        self,
        query: str,
        crew_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> CrewResult:
        """
        Execute a query with the specified or default crew.
        تنفيذ استعلام مع الطاقم المحدد أو الافتراضي
        """
        crew = self._crews.get(crew_name) if crew_name else self._default_crew

        if not crew:
            crew = self._default_crew or AgriculturalCrew()

        return await crew.execute(query, context)

    def get_available_agents(self) -> list[dict[str, str]]:
        """Get list of available agent roles."""
        return [
            {
                "role": role.value,
                "goal": config.goal,
                "goal_ar": config.goal_ar,
            }
            for role, config in AGRICULTURAL_AGENTS.items()
        ]
