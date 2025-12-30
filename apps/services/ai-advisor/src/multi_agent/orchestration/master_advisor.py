"""
Master Advisor - Central Orchestrator
المستشار الرئيسي - المنسق المركزي

Central orchestrator for SAHOOL multi-agent system. Analyzes queries, routes to appropriate
agents, executes in parallel or council mode, and aggregates responses.

منسق مركزي لنظام SAHOOL متعدد الوكلاء. يحلل الاستفسارات، يوجهها للوكلاء المناسبين،
ينفذها بشكل متوازي أو في وضع المجلس، ويجمع الاستجابات.
"""

import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

logger = structlog.get_logger()


# Query Types Enum | أنواع الاستفسارات
class QueryType(str, Enum):
    """
    Types of queries the system can handle
    أنواع الاستفسارات التي يمكن للنظام معالجتها
    """
    DIAGNOSIS = "diagnosis"                      # تشخيص الأمراض
    TREATMENT = "treatment"                      # العلاج
    IRRIGATION = "irrigation"                    # الري
    FERTILIZATION = "fertilization"              # التسميد
    PEST_MANAGEMENT = "pest_management"          # إدارة الآفات
    HARVEST_PLANNING = "harvest_planning"        # تخطيط الحصاد
    EMERGENCY = "emergency"                      # طوارئ
    ECOLOGICAL_TRANSITION = "ecological_transition"  # التحول البيئي
    MARKET_ANALYSIS = "market_analysis"          # تحليل السوق
    FIELD_ANALYSIS = "field_analysis"            # تحليل الحقل
    YIELD_PREDICTION = "yield_prediction"        # التنبؤ بالمحصول
    GENERAL_ADVISORY = "general_advisory"        # استشارة عامة


# Execution Mode | وضع التنفيذ
class ExecutionMode(str, Enum):
    """
    Execution modes for agent coordination
    أوضاع التنفيذ لتنسيق الوكلاء
    """
    PARALLEL = "parallel"          # تنفيذ متوازي
    SEQUENTIAL = "sequential"      # تنفيذ متتابع
    COUNCIL = "council"            # وضع المجلس (للقرارات الحرجة)
    SINGLE_AGENT = "single_agent"  # وكيل واحد


@dataclass
class FarmerQuery:
    """
    Farmer query with context and metadata
    استفسار المزارع مع السياق والبيانات الوصفية
    """
    query: str
    farmer_id: Optional[str] = None
    field_id: Optional[str] = None
    crop_type: Optional[str] = None
    language: str = "ar"  # Default to Arabic
    context: Dict[str, Any] = field(default_factory=dict)
    images: List[str] = field(default_factory=list)
    location: Optional[Dict[str, float]] = None  # {"lat": x, "lon": y}
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: str = "normal"  # normal, high, emergency


@dataclass
class QueryAnalysis:
    """
    Analysis of a farmer query
    تحليل استفسار المزارع
    """
    query_type: QueryType
    required_agents: List[str]
    execution_mode: ExecutionMode
    needs_consensus: bool
    confidence: float
    reasoning: str
    estimated_complexity: str  # low, medium, high
    context_requirements: List[str] = field(default_factory=list)


@dataclass
class AgentResponse:
    """
    Response from a single agent
    استجابة من وكيل واحد
    """
    agent_name: str
    agent_role: str
    response: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    sources: List[str] = field(default_factory=list)


@dataclass
class AdvisoryResponse:
    """
    Final aggregated advisory response
    الاستجابة الاستشارية النهائية المجمعة
    """
    query: str
    answer: str
    query_type: QueryType
    agents_consulted: List[str]
    execution_mode: ExecutionMode
    confidence: float
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    language: str = "ar"
    timestamp: datetime = field(default_factory=datetime.utcnow)


class AgentRegistry:
    """
    Registry of available agents and their capabilities
    سجل الوكلاء المتاحين وقدراتهم
    """

    def __init__(self):
        """Initialize agent registry | تهيئة سجل الوكلاء"""
        self._agents: Dict[str, Any] = {}
        self._capabilities: Dict[str, Set[QueryType]] = {}
        logger.info("agent_registry_initialized")

    def register_agent(
        self,
        name: str,
        agent: Any,
        capabilities: List[QueryType]
    ):
        """
        Register an agent with its capabilities
        تسجيل وكيل مع قدراته

        Args:
            name: Agent name | اسم الوكيل
            agent: Agent instance | مثيل الوكيل
            capabilities: List of query types the agent can handle
        """
        self._agents[name] = agent
        self._capabilities[name] = set(capabilities)
        logger.info(
            "agent_registered",
            agent_name=name,
            capabilities=[c.value for c in capabilities]
        )

    def get_agent(self, name: str) -> Optional[Any]:
        """Get agent by name | الحصول على الوكيل بالاسم"""
        return self._agents.get(name)

    def get_agents_for_query_type(self, query_type: QueryType) -> List[str]:
        """
        Get agents capable of handling a query type
        الحصول على الوكلاء القادرين على معالجة نوع استفسار
        """
        return [
            name for name, caps in self._capabilities.items()
            if query_type in caps
        ]

    def get_all_agents(self) -> Dict[str, Any]:
        """Get all registered agents | الحصول على جميع الوكلاء المسجلين"""
        return self._agents.copy()

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents with their capabilities
        سرد جميع الوكلاء مع قدراتهم
        """
        return [
            {
                "name": name,
                "capabilities": [c.value for c in caps],
                "role": getattr(agent, "role", "Unknown")
            }
            for name, (agent, caps) in zip(
                self._agents.keys(),
                zip(self._agents.values(), self._capabilities.values())
            )
        ]


class NATSBridge:
    """
    Bridge for NATS messaging (placeholder for future implementation)
    جسر لمراسلة NATS (نائب للتنفيذ المستقبلي)
    """

    def __init__(self, nats_url: str):
        """
        Initialize NATS bridge
        تهيئة جسر NATS

        Args:
            nats_url: NATS server URL | عنوان خادم NATS
        """
        self.nats_url = nats_url
        self.connected = False
        logger.info("nats_bridge_initialized", nats_url=nats_url)

    async def connect(self):
        """Connect to NATS server | الاتصال بخادم NATS"""
        # TODO: Implement actual NATS connection
        logger.info("nats_bridge_connect_placeholder")
        self.connected = True

    async def publish(self, subject: str, message: Dict[str, Any]):
        """Publish message to NATS | نشر رسالة إلى NATS"""
        # TODO: Implement actual NATS publishing
        logger.debug("nats_publish_placeholder", subject=subject)

    async def subscribe(self, subject: str, callback):
        """Subscribe to NATS subject | الاشتراك في موضوع NATS"""
        # TODO: Implement actual NATS subscription
        logger.debug("nats_subscribe_placeholder", subject=subject)


class ContextStore:
    """
    Store for conversation context and history
    مخزن لسياق المحادثة والتاريخ
    """

    def __init__(self):
        """Initialize context store | تهيئة مخزن السياق"""
        self._contexts: Dict[str, List[Dict[str, Any]]] = {}
        logger.info("context_store_initialized")

    def store_context(
        self,
        session_id: str,
        query: str,
        response: AdvisoryResponse
    ):
        """
        Store context for a session
        تخزين السياق لجلسة

        Args:
            session_id: Session identifier | معرف الجلسة
            query: Original query | الاستفسار الأصلي
            response: Advisory response | الاستجابة الاستشارية
        """
        if session_id not in self._contexts:
            self._contexts[session_id] = []

        self._contexts[session_id].append({
            "query": query,
            "response": response,
            "timestamp": datetime.utcnow()
        })

        # Keep only last 10 interactions
        # الاحتفاظ بآخر 10 تفاعلات فقط
        if len(self._contexts[session_id]) > 10:
            self._contexts[session_id] = self._contexts[session_id][-10:]

        logger.debug("context_stored", session_id=session_id)

    def get_context(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get context for a session
        الحصول على سياق لجلسة
        """
        return self._contexts.get(session_id, [])

    def clear_context(self, session_id: str):
        """Clear context for a session | مسح سياق لجلسة"""
        if session_id in self._contexts:
            del self._contexts[session_id]
            logger.debug("context_cleared", session_id=session_id)


class MasterAdvisor:
    """
    Master Advisor - Central Orchestrator for Multi-Agent System
    المستشار الرئيسي - المنسق المركزي لنظام متعدد الوكلاء

    The MasterAdvisor:
    - Analyzes farmer queries to determine intent and requirements
    - Routes queries to appropriate specialized agents
    - Executes agents in parallel, sequential, or council mode
    - Aggregates and synthesizes responses
    - Manages conversation context and history

    المستشار الرئيسي:
    - يحلل استفسارات المزارعين لتحديد النية والمتطلبات
    - يوجه الاستفسارات للوكلاء المتخصصين المناسبين
    - ينفذ الوكلاء بشكل متوازي، متتابع، أو في وضع المجلس
    - يجمع ويدمج الاستجابات
    - يدير سياق المحادثة والتاريخ
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        context_store: Optional[ContextStore] = None,
        nats_bridge: Optional[NATSBridge] = None,
        anthropic_api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        """
        Initialize Master Advisor
        تهيئة المستشار الرئيسي

        Args:
            agent_registry: Registry of available agents | سجل الوكلاء المتاحين
            context_store: Context storage | مخزن السياق
            nats_bridge: NATS messaging bridge | جسر رسائل NATS
            anthropic_api_key: Anthropic API key | مفتاح API
            model: Claude model to use | نموذج Claude المستخدم
        """
        self.agent_registry = agent_registry
        self.context_store = context_store or ContextStore()
        self.nats_bridge = nats_bridge

        # Initialize Claude for query analysis and synthesis
        # تهيئة Claude لتحليل الاستفسارات والتجميع
        self.llm = ChatAnthropic(
            anthropic_api_key=anthropic_api_key,
            model=model,
            max_tokens=4096,
            temperature=0.3
        ) if anthropic_api_key else None

        # Load available agents
        # تحميل الوكلاء المتاحين
        self.available_agents = agent_registry.get_all_agents()

        logger.info(
            "master_advisor_initialized",
            num_agents=len(self.available_agents),
            has_llm=self.llm is not None,
            has_nats=self.nats_bridge is not None
        )

    async def process_query(
        self,
        query: FarmerQuery,
        session_id: Optional[str] = None
    ) -> AdvisoryResponse:
        """
        Process a farmer query through the multi-agent system
        معالجة استفسار المزارع عبر نظام متعدد الوكلاء

        Args:
            query: Farmer query with context | استفسار المزارع مع السياق
            session_id: Session identifier for context | معرف الجلسة للسياق

        Returns:
            AdvisoryResponse: Aggregated response | الاستجابة المجمعة
        """
        start_time = datetime.utcnow()

        try:
            logger.info(
                "processing_query",
                query_length=len(query.query),
                language=query.language,
                priority=query.priority,
                has_images=len(query.images) > 0
            )

            # 1. Analyze query to determine strategy
            # تحليل الاستفسار لتحديد الاستراتيجية
            analysis = await self.analyze_query(query)

            logger.info(
                "query_analyzed",
                query_type=analysis.query_type.value,
                execution_mode=analysis.execution_mode.value,
                required_agents=analysis.required_agents,
                needs_consensus=analysis.needs_consensus
            )

            # 2. Get previous context if session exists
            # الحصول على السياق السابق إذا كانت الجلسة موجودة
            previous_context = []
            if session_id:
                previous_context = self.context_store.get_context(session_id)

            # 3. Execute agents based on mode
            # تنفيذ الوكلاء بناءً على الوضع
            agent_responses: List[AgentResponse] = []

            if analysis.execution_mode == ExecutionMode.PARALLEL:
                agent_responses = await self.execute_parallel(
                    analysis.required_agents,
                    query,
                    previous_context
                )
            elif analysis.execution_mode == ExecutionMode.SEQUENTIAL:
                agent_responses = await self.execute_sequential(
                    analysis.required_agents,
                    query,
                    previous_context
                )
            elif analysis.execution_mode == ExecutionMode.COUNCIL:
                agent_responses = await self.execute_council(
                    analysis.required_agents,
                    query,
                    previous_context
                )
            else:  # SINGLE_AGENT
                agent_responses = await self.execute_single(
                    analysis.required_agents[0] if analysis.required_agents else "general",
                    query,
                    previous_context
                )

            # 4. Aggregate responses
            # تجميع الاستجابات
            advisory_response = await self.aggregate_responses(
                query=query,
                analysis=analysis,
                agent_responses=agent_responses,
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )

            # 5. Store context
            # تخزين السياق
            if session_id:
                self.context_store.store_context(
                    session_id,
                    query.query,
                    advisory_response
                )

            # 6. Publish to NATS if available
            # النشر إلى NATS إذا كان متاحاً
            if self.nats_bridge and self.nats_bridge.connected:
                await self.nats_bridge.publish(
                    f"sahool.advisory.completed.{query.farmer_id or 'anonymous'}",
                    {
                        "query": query.query,
                        "response": advisory_response.answer,
                        "query_type": analysis.query_type.value
                    }
                )

            logger.info(
                "query_processed_successfully",
                query_type=analysis.query_type.value,
                agents_consulted=len(agent_responses),
                execution_time=advisory_response.metadata.get("execution_time", 0)
            )

            return advisory_response

        except Exception as e:
            logger.error(
                "query_processing_failed",
                error=str(e),
                query=query.query[:100]
            )

            # Return error response in appropriate language
            # إرجاع استجابة خطأ باللغة المناسبة
            error_message = (
                f"عذراً، حدث خطأ أثناء معالجة استفسارك: {str(e)}"
                if query.language == "ar"
                else f"Sorry, an error occurred while processing your query: {str(e)}"
            )

            return AdvisoryResponse(
                query=query.query,
                answer=error_message,
                query_type=QueryType.GENERAL_ADVISORY,
                agents_consulted=[],
                execution_mode=ExecutionMode.SINGLE_AGENT,
                confidence=0.0,
                warnings=[error_message],
                language=query.language,
                metadata={"error": str(e)}
            )

    async def analyze_query(self, query: FarmerQuery) -> QueryAnalysis:
        """
        Analyze query to determine type, required agents, and execution mode
        تحليل الاستفسار لتحديد النوع والوكلاء المطلوبين ووضع التنفيذ

        Args:
            query: Farmer query | استفسار المزارع

        Returns:
            QueryAnalysis: Analysis results | نتائج التحليل
        """
        if not self.llm:
            # Fallback: Simple keyword-based analysis
            # احتياطي: تحليل بسيط قائم على الكلمات المفتاحية
            return self._simple_query_analysis(query)

        try:
            analysis_prompt = f"""Analyze this agricultural query and determine:
1. Query type (diagnosis, irrigation, fertilization, pest_management, etc.)
2. Required specialized agents
3. Execution mode (parallel, sequential, council, single_agent)
4. Whether consensus is needed among agents
5. Complexity level (low, medium, high)

Query: {query.query}
Crop Type: {query.crop_type or 'Not specified'}
Context: {query.context}
Priority: {query.priority}

Available agents:
- field_analyst: Field and satellite analysis
- disease_expert: Disease diagnosis and treatment
- irrigation_advisor: Water management and irrigation
- yield_predictor: Yield prediction and harvest planning
- ecological_expert: Ecological transition and sustainable practices

Respond in JSON format:
{{
  "query_type": "diagnosis|irrigation|...",
  "required_agents": ["agent1", "agent2"],
  "execution_mode": "parallel|sequential|council|single_agent",
  "needs_consensus": true|false,
  "confidence": 0.0-1.0,
  "reasoning": "explanation",
  "complexity": "low|medium|high",
  "context_requirements": ["requirement1", "requirement2"]
}}

Use council mode only for critical decisions requiring consensus.
Use sequential mode when agents need to build on each other's results.
Use parallel mode when agents can work independently."""

            messages = [
                SystemMessage(content="You are an expert agricultural query analyzer."),
                HumanMessage(content=analysis_prompt)
            ]

            response = await self.llm.ainvoke(messages)

            # Parse JSON response
            # تحليل استجابة JSON
            import json
            analysis_data = json.loads(response.content)

            return QueryAnalysis(
                query_type=QueryType(analysis_data.get("query_type", "general_advisory")),
                required_agents=analysis_data.get("required_agents", []),
                execution_mode=ExecutionMode(analysis_data.get("execution_mode", "parallel")),
                needs_consensus=analysis_data.get("needs_consensus", False),
                confidence=analysis_data.get("confidence", 0.7),
                reasoning=analysis_data.get("reasoning", ""),
                estimated_complexity=analysis_data.get("complexity", "medium"),
                context_requirements=analysis_data.get("context_requirements", [])
            )

        except Exception as e:
            logger.error("query_analysis_failed", error=str(e))
            return self._simple_query_analysis(query)

    def _simple_query_analysis(self, query: FarmerQuery) -> QueryAnalysis:
        """
        Simple keyword-based query analysis (fallback)
        تحليل بسيط قائم على الكلمات المفتاحية (احتياطي)
        """
        query_lower = query.query.lower()

        # Keyword mapping for query types
        # تعيين الكلمات المفتاحية لأنواع الاستفسارات
        keyword_mapping = {
            QueryType.DIAGNOSIS: ["disease", "sick", "مرض", "مريض", "yellow", "spots", "بقع"],
            QueryType.IRRIGATION: ["water", "irrigation", "ري", "ماء", "رطوبة"],
            QueryType.FERTILIZATION: ["fertilizer", "nutrients", "سماد", "تسميد"],
            QueryType.PEST_MANAGEMENT: ["pest", "insect", "آفة", "حشرة"],
            QueryType.YIELD_PREDICTION: ["yield", "harvest", "محصول", "حصاد"],
            QueryType.FIELD_ANALYSIS: ["field", "satellite", "ndvi", "حقل", "صور"],
        }

        # Determine query type
        # تحديد نوع الاستفسار
        detected_type = QueryType.GENERAL_ADVISORY
        for qtype, keywords in keyword_mapping.items():
            if any(kw in query_lower for kw in keywords):
                detected_type = qtype
                break

        # Map query types to agents
        # تعيين أنواع الاستفسارات للوكلاء
        agent_mapping = {
            QueryType.DIAGNOSIS: ["disease_expert"],
            QueryType.TREATMENT: ["disease_expert"],
            QueryType.IRRIGATION: ["irrigation_advisor"],
            QueryType.FERTILIZATION: ["irrigation_advisor", "field_analyst"],
            QueryType.PEST_MANAGEMENT: ["disease_expert"],
            QueryType.YIELD_PREDICTION: ["yield_predictor"],
            QueryType.FIELD_ANALYSIS: ["field_analyst"],
            QueryType.ECOLOGICAL_TRANSITION: ["ecological_expert"],
            QueryType.GENERAL_ADVISORY: ["field_analyst", "disease_expert"],
        }

        required_agents = agent_mapping.get(detected_type, ["field_analyst"])

        # Determine execution mode
        # تحديد وضع التنفيذ
        execution_mode = (
            ExecutionMode.PARALLEL if len(required_agents) > 1
            else ExecutionMode.SINGLE_AGENT
        )

        # Emergency queries need council
        # الاستفسارات الطارئة تحتاج لمجلس
        if query.priority == "emergency":
            execution_mode = ExecutionMode.COUNCIL
            required_agents = ["disease_expert", "field_analyst", "irrigation_advisor"]

        return QueryAnalysis(
            query_type=detected_type,
            required_agents=required_agents,
            execution_mode=execution_mode,
            needs_consensus=(query.priority == "emergency"),
            confidence=0.6,  # Lower confidence for keyword-based analysis
            reasoning="Keyword-based analysis (fallback)",
            estimated_complexity="medium"
        )

    async def execute_parallel(
        self,
        agent_names: List[str],
        query: FarmerQuery,
        context: List[Dict[str, Any]]
    ) -> List[AgentResponse]:
        """
        Execute multiple agents in parallel
        تنفيذ وكلاء متعددين بشكل متوازي

        Args:
            agent_names: List of agent names | قائمة أسماء الوكلاء
            query: Farmer query | استفسار المزارع
            context: Previous context | السياق السابق

        Returns:
            List of agent responses | قائمة استجابات الوكلاء
        """
        logger.info("executing_parallel", agents=agent_names)

        # Create tasks for all agents
        # إنشاء مهام لجميع الوكلاء
        tasks = []
        for agent_name in agent_names:
            agent = self.agent_registry.get_agent(agent_name)
            if agent:
                tasks.append(self._execute_agent(agent, agent_name, query, context))

        # Execute in parallel using asyncio.gather
        # التنفيذ بشكل متوازي باستخدام asyncio.gather
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and collect valid responses
        # تصفية الاستثناءات وجمع الاستجابات الصحيحة
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(
                    "agent_execution_failed",
                    agent=agent_names[i] if i < len(agent_names) else "unknown",
                    error=str(response)
                )
            else:
                valid_responses.append(response)

        logger.info(
            "parallel_execution_complete",
            total_agents=len(agent_names),
            successful=len(valid_responses)
        )

        return valid_responses

    async def execute_sequential(
        self,
        agent_names: List[str],
        query: FarmerQuery,
        context: List[Dict[str, Any]]
    ) -> List[AgentResponse]:
        """
        Execute agents sequentially (when dependencies exist)
        تنفيذ الوكلاء بالتتابع (عند وجود تبعيات)

        Args:
            agent_names: List of agent names in order | قائمة أسماء الوكلاء بالترتيب
            query: Farmer query | استفسار المزارع
            context: Previous context | السياق السابق

        Returns:
            List of agent responses | قائمة استجابات الوكلاء
        """
        logger.info("executing_sequential", agents=agent_names)

        responses = []
        accumulated_context = context.copy()

        for agent_name in agent_names:
            agent = self.agent_registry.get_agent(agent_name)
            if not agent:
                logger.warning("agent_not_found", agent_name=agent_name)
                continue

            try:
                # Execute agent with accumulated context
                # تنفيذ الوكيل مع السياق المتراكم
                response = await self._execute_agent(
                    agent,
                    agent_name,
                    query,
                    accumulated_context
                )
                responses.append(response)

                # Add response to context for next agent
                # إضافة الاستجابة للسياق للوكيل التالي
                accumulated_context.append({
                    "agent": agent_name,
                    "response": response.response,
                    "confidence": response.confidence
                })

            except Exception as e:
                logger.error(
                    "sequential_agent_failed",
                    agent=agent_name,
                    error=str(e)
                )

        logger.info("sequential_execution_complete", agents_executed=len(responses))
        return responses

    async def execute_council(
        self,
        agent_names: List[str],
        query: FarmerQuery,
        context: List[Dict[str, Any]]
    ) -> List[AgentResponse]:
        """
        Execute agents in council mode for consensus on critical decisions
        تنفيذ الوكلاء في وضع المجلس للتوافق على القرارات الحرجة

        Council mode:
        1. All agents analyze independently (parallel)
        2. Responses are compared for consensus
        3. If disagreement exists, run deliberation round
        4. Final consensus is reached

        وضع المجلس:
        1. جميع الوكلاء يحللون بشكل مستقل (متوازي)
        2. مقارنة الاستجابات للتوافق
        3. في حالة الخلاف، تشغيل جولة مداولة
        4. الوصول إلى توافق نهائي
        """
        logger.info("executing_council", agents=agent_names)

        # Phase 1: Independent analysis (parallel)
        # المرحلة 1: تحليل مستقل (متوازي)
        initial_responses = await self.execute_parallel(agent_names, query, context)

        if not self.llm or len(initial_responses) < 2:
            # Can't form council without LLM or with single agent
            # لا يمكن تشكيل مجلس بدون LLM أو مع وكيل واحد
            return initial_responses

        # Phase 2: Check for consensus
        # المرحلة 2: التحقق من التوافق
        consensus_prompt = f"""Review these expert opinions on an agricultural query and determine if there's consensus.

Query: {query.query}

Expert Opinions:
{self._format_responses_for_council(initial_responses)}

Determine:
1. Is there consensus? (yes/no)
2. What are the main points of agreement?
3. What are the points of disagreement?
4. Confidence level in the collective recommendation (0-1)

Respond in JSON:
{{
  "consensus": true|false,
  "agreement_points": ["point1", "point2"],
  "disagreement_points": ["point1", "point2"],
  "confidence": 0.0-1.0,
  "reasoning": "explanation"
}}"""

        messages = [
            SystemMessage(content="You are analyzing expert consensus on agricultural advice."),
            HumanMessage(content=consensus_prompt)
        ]

        try:
            response = await self.llm.ainvoke(messages)
            import json
            consensus_data = json.loads(response.content)

            if consensus_data.get("consensus", False):
                logger.info("council_consensus_reached", confidence=consensus_data.get("confidence"))
                return initial_responses

            # Phase 3: Deliberation round (if no consensus)
            # المرحلة 3: جولة مداولة (إذا لم يكن هناك توافق)
            logger.info("council_deliberation_started", disagreements=consensus_data.get("disagreement_points"))

            # Create deliberation context
            # إنشاء سياق المداولة
            deliberation_context = context + [{
                "council_round": "deliberation",
                "initial_responses": initial_responses,
                "disagreement_points": consensus_data.get("disagreement_points", [])
            }]

            # Re-query agents with deliberation context
            # إعادة الاستعلام من الوكلاء مع سياق المداولة
            deliberation_responses = await self.execute_parallel(
                agent_names,
                query,
                deliberation_context
            )

            logger.info("council_deliberation_complete")
            return deliberation_responses

        except Exception as e:
            logger.error("council_consensus_check_failed", error=str(e))
            return initial_responses

    async def execute_single(
        self,
        agent_name: str,
        query: FarmerQuery,
        context: List[Dict[str, Any]]
    ) -> List[AgentResponse]:
        """
        Execute a single agent
        تنفيذ وكيل واحد
        """
        agent = self.agent_registry.get_agent(agent_name)
        if not agent:
            logger.warning("agent_not_found", agent_name=agent_name)
            return []

        try:
            response = await self._execute_agent(agent, agent_name, query, context)
            return [response]
        except Exception as e:
            logger.error("single_agent_execution_failed", agent=agent_name, error=str(e))
            return []

    async def _execute_agent(
        self,
        agent: Any,
        agent_name: str,
        query: FarmerQuery,
        context: List[Dict[str, Any]]
    ) -> AgentResponse:
        """
        Execute a single agent and return structured response
        تنفيذ وكيل واحد وإرجاع استجابة منظمة
        """
        start_time = datetime.utcnow()

        try:
            # Prepare context for agent
            # تحضير السياق للوكيل
            agent_context = {
                "crop_type": query.crop_type,
                "location": query.location,
                "field_id": query.field_id,
                "priority": query.priority,
                "previous_context": context[-3:] if context else []  # Last 3 interactions
            }

            # Call agent's think method
            # استدعاء طريقة التفكير للوكيل
            result = await agent.think(
                query=query.query,
                context=agent_context,
                use_rag=True
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return AgentResponse(
                agent_name=agent_name,
                agent_role=getattr(agent, "role", "Unknown"),
                response=result.get("response", ""),
                confidence=result.get("confidence", 0.7),
                metadata=result,
                execution_time=execution_time,
                sources=result.get("sources", [])
            )

        except Exception as e:
            logger.error("agent_execution_error", agent=agent_name, error=str(e))
            raise

    async def aggregate_responses(
        self,
        query: FarmerQuery,
        analysis: QueryAnalysis,
        agent_responses: List[AgentResponse],
        execution_time: float
    ) -> AdvisoryResponse:
        """
        Aggregate multiple agent responses into final advisory
        تجميع استجابات الوكلاء المتعددة في استشارة نهائية

        Args:
            query: Original query | الاستفسار الأصلي
            analysis: Query analysis | تحليل الاستفسار
            agent_responses: List of agent responses | قائمة استجابات الوكلاء
            execution_time: Total execution time | وقت التنفيذ الإجمالي

        Returns:
            AdvisoryResponse: Aggregated response | الاستجابة المجمعة
        """
        if not agent_responses:
            # No responses - return error
            # لا توجد استجابات - إرجاع خطأ
            error_msg = (
                "عذراً، لم نتمكن من الحصول على استجابة من الوكلاء"
                if query.language == "ar"
                else "Sorry, we couldn't get responses from agents"
            )
            return AdvisoryResponse(
                query=query.query,
                answer=error_msg,
                query_type=analysis.query_type,
                agents_consulted=[],
                execution_mode=analysis.execution_mode,
                confidence=0.0,
                language=query.language,
                metadata={"error": "no_agent_responses"}
            )

        if len(agent_responses) == 1:
            # Single agent - use response directly
            # وكيل واحد - استخدام الاستجابة مباشرة
            response = agent_responses[0]
            return AdvisoryResponse(
                query=query.query,
                answer=response.response,
                query_type=analysis.query_type,
                agents_consulted=[response.agent_name],
                execution_mode=analysis.execution_mode,
                confidence=response.confidence,
                language=query.language,
                metadata={
                    "execution_time": execution_time,
                    "agent_metadata": response.metadata
                }
            )

        # Multiple agents - synthesize responses
        # وكلاء متعددون - دمج الاستجابات
        if not self.llm:
            # Fallback: concatenate responses
            # احتياطي: دمج الاستجابات
            return self._simple_aggregation(
                query,
                analysis,
                agent_responses,
                execution_time
            )

        try:
            synthesis_prompt = f"""Synthesize these expert agricultural opinions into a comprehensive, actionable response.

Original Query: {query.query}
Language: {query.language}

Expert Responses:
{self._format_responses_for_synthesis(agent_responses)}

Create a comprehensive response that:
1. Answers the farmer's question directly
2. Combines insights from all experts
3. Resolves any minor conflicts
4. Provides actionable recommendations
5. Includes relevant warnings if any
6. Suggests next steps
7. Responds in {'Arabic' if query.language == 'ar' else 'English'}

Respond in JSON:
{{
  "answer": "comprehensive answer",
  "recommendations": ["rec1", "rec2"],
  "warnings": ["warning1", "warning2"],
  "next_steps": ["step1", "step2"],
  "confidence": 0.0-1.0
}}"""

            messages = [
                SystemMessage(content="You are synthesizing agricultural expert advice."),
                HumanMessage(content=synthesis_prompt)
            ]

            response = await self.llm.ainvoke(messages)

            import json
            synthesis_data = json.loads(response.content)

            return AdvisoryResponse(
                query=query.query,
                answer=synthesis_data.get("answer", ""),
                query_type=analysis.query_type,
                agents_consulted=[r.agent_name for r in agent_responses],
                execution_mode=analysis.execution_mode,
                confidence=synthesis_data.get("confidence", 0.7),
                recommendations=synthesis_data.get("recommendations", []),
                warnings=synthesis_data.get("warnings", []),
                next_steps=synthesis_data.get("next_steps", []),
                language=query.language,
                metadata={
                    "execution_time": execution_time,
                    "num_agents": len(agent_responses),
                    "agent_responses": [
                        {
                            "agent": r.agent_name,
                            "confidence": r.confidence,
                            "execution_time": r.execution_time
                        }
                        for r in agent_responses
                    ]
                }
            )

        except Exception as e:
            logger.error("response_synthesis_failed", error=str(e))
            return self._simple_aggregation(
                query,
                analysis,
                agent_responses,
                execution_time
            )

    def _simple_aggregation(
        self,
        query: FarmerQuery,
        analysis: QueryAnalysis,
        agent_responses: List[AgentResponse],
        execution_time: float
    ) -> AdvisoryResponse:
        """
        Simple aggregation without LLM (fallback)
        تجميع بسيط بدون LLM (احتياطي)
        """
        # Concatenate responses
        # دمج الاستجابات
        combined_answer = "\n\n".join([
            f"**{r.agent_role}**:\n{r.response}"
            for r in agent_responses
        ])

        # Average confidence
        # متوسط الثقة
        avg_confidence = sum(r.confidence for r in agent_responses) / len(agent_responses)

        return AdvisoryResponse(
            query=query.query,
            answer=combined_answer,
            query_type=analysis.query_type,
            agents_consulted=[r.agent_name for r in agent_responses],
            execution_mode=analysis.execution_mode,
            confidence=avg_confidence,
            language=query.language,
            metadata={
                "execution_time": execution_time,
                "aggregation_method": "simple_concatenation"
            }
        )

    def _format_responses_for_council(self, responses: List[AgentResponse]) -> str:
        """Format responses for council deliberation | تنسيق الاستجابات للمداولة"""
        formatted = []
        for r in responses:
            formatted.append(
                f"\n**{r.agent_role}** (Confidence: {r.confidence:.2f}):\n{r.response}"
            )
        return "\n".join(formatted)

    def _format_responses_for_synthesis(self, responses: List[AgentResponse]) -> str:
        """Format responses for synthesis | تنسيق الاستجابات للدمج"""
        formatted = []
        for r in responses:
            formatted.append(
                f"\n**{r.agent_name}** - {r.agent_role} (Confidence: {r.confidence:.2f}):\n{r.response}"
            )
        return "\n".join(formatted)
