"""
Supervisor Agent
وكيل المشرف

Coordinates multiple specialized agents to answer complex queries.
ينسق بين وكلاء متخصصين متعددين للإجابة على استفسارات معقدة.
"""

from typing import Any

import structlog
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from ..agents import (
    BaseAgent,
)
from ..config import settings
from ..security import PromptGuard

logger = structlog.get_logger()


class Supervisor:
    """
    Supervisor coordinates multiple specialized agents
    المشرف ينسق بين وكلاء متخصصين متعددين

    The supervisor:
    - Analyzes user queries
    - Determines which agents to consult
    - Orchestrates agent interactions
    - Synthesizes responses into coherent answers

    المشرف:
    - يحلل استفسارات المستخدم
    - يحدد الوكلاء المطلوب استشارتهم
    - ينسق التفاعلات بين الوكلاء
    - يدمج الاستجابات في إجابات متماسكة
    """

    def __init__(self, agents: dict[str, BaseAgent]):
        """
        Initialize Supervisor
        تهيئة المشرف

        Args:
            agents: Dictionary of available agents | قاموس الوكلاء المتاحين
        """
        self.agents = agents

        # Initialize Claude for supervisor reasoning
        # تهيئة Claude لاستدلال المشرف
        self.llm = ChatAnthropic(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.claude_model,
            max_tokens=settings.max_tokens,
            temperature=0.3,  # Lower temperature for more focused routing
        )

        logger.info(
            "supervisor_initialized",
            num_agents=len(agents),
            agent_names=list(agents.keys()),
        )

    def _get_routing_prompt(self) -> str:
        """
        Get system prompt for agent routing
        الحصول على موجه النظام لتوجيه الوكلاء
        """
        agent_descriptions = []
        for name, agent in self.agents.items():
            agent_descriptions.append(f"- {name}: {agent.role}")

        agents_text = "\n".join(agent_descriptions)

        return f"""You are a Supervisor Agent coordinating a team of agricultural AI specialists.

Available agents:
{agents_text}

Your role is to:
1. Analyze user queries and determine which agents should be consulted
2. Break down complex queries into sub-tasks for specific agents
3. Coordinate agent interactions when multiple perspectives are needed
4. Synthesize agent responses into comprehensive, coherent answers

When routing queries:
- For NDVI, satellite imagery, and field health analysis -> field_analyst
- For crop diseases, pest identification, and treatment -> disease_expert
- For water management, irrigation scheduling -> irrigation_advisor
- For yield predictions, harvest timing, production forecasting -> yield_predictor

Respond with a JSON object containing:
{{
  "agents_needed": ["agent1", "agent2"],
  "reasoning": "why these agents",
  "query_breakdown": {{
    "agent1": "specific question for agent1",
    "agent2": "specific question for agent2"
  }}
}}

أنت وكيل مشرف ينسق فريقاً من متخصصي الذكاء الاصطناعي الزراعي.
حلل الاستفسارات وحدد الوكلاء المناسبين للإجابة عليها."""

    async def route_query(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Route query to appropriate agents
        توجيه الاستفسار إلى الوكلاء المناسبين

        Args:
            query: User query | استفسار المستخدم
            context: Additional context | سياق إضافي

        Returns:
            Routing decision | قرار التوجيه
        """
        try:
            # Guard against prompt injection
            # الحماية من حقن الأوامر
            sanitized_query, is_safe, warnings = PromptGuard.validate_and_sanitize(
                query, strict=False
            )

            if not is_safe:
                logger.warning(
                    "potential_injection_detected",
                    query_length=len(query),
                    warnings=warnings,
                )

            messages = [
                SystemMessage(content=self._get_routing_prompt()),
                HumanMessage(content=f"Query: {sanitized_query}\n\nContext: {context or {}}"),
            ]

            response = await self.llm.ainvoke(messages)

            # Parse routing decision (simplified - in production use JSON mode)
            # تحليل قرار التوجيه (مبسط - استخدم وضع JSON في الإنتاج)
            import json

            try:
                routing = json.loads(response.content)
            except (json.JSONDecodeError, TypeError, ValueError):
                # Fallback: route to all agents if parsing fails
                # احتياطي: التوجيه لجميع الوكلاء إذا فشل التحليل
                routing = {
                    "agents_needed": list(self.agents.keys()),
                    "reasoning": "Fallback routing due to parsing error",
                    "query_breakdown": dict.fromkeys(self.agents, query),
                }

            logger.info(
                "query_routed",
                agents_needed=routing.get("agents_needed", []),
                reasoning=routing.get("reasoning", ""),
            )

            return routing

        except Exception as e:
            logger.error("routing_failed", error=str(e))
            raise

    async def coordinate(
        self,
        query: str,
        context: dict[str, Any] | None = None,
        specific_agents: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Coordinate agents to answer a query
        تنسيق الوكلاء للإجابة على استفسار

        Args:
            query: User query | استفسار المستخدم
            context: Additional context | سياق إضافي
            specific_agents: List of specific agents to use (optional) | قائمة الوكلاء المحددين

        Returns:
            Coordinated response | استجابة منسقة
        """
        try:
            # Guard against prompt injection at coordination level
            # الحماية من حقن الأوامر على مستوى التنسيق
            sanitized_query, is_safe, warnings = PromptGuard.validate_and_sanitize(
                query, strict=False
            )

            if not is_safe:
                logger.warning(
                    "potential_injection_in_coordinate",
                    query_length=len(query),
                    warnings=warnings,
                )

            # Route query if specific agents not provided
            # توجيه الاستفسار إذا لم يتم توفير وكلاء محددين
            if not specific_agents:
                routing = await self.route_query(sanitized_query, context)
                agents_to_use = routing.get("agents_needed", [])
                query_breakdown = routing.get("query_breakdown", {})
            else:
                agents_to_use = specific_agents
                query_breakdown = dict.fromkeys(agents_to_use, sanitized_query)

            # Collect responses from agents
            # جمع الاستجابات من الوكلاء
            agent_responses = {}
            for agent_name in agents_to_use:
                if agent_name in self.agents:
                    agent = self.agents[agent_name]
                    agent_query = query_breakdown.get(agent_name, query)

                    response = await agent.think(query=agent_query, context=context, use_rag=True)
                    agent_responses[agent_name] = response

            # Synthesize responses
            # دمج الاستجابات
            synthesized = await self._synthesize_responses(
                query=query, agent_responses=agent_responses, context=context
            )

            logger.info(
                "coordination_complete",
                query_length=len(query),
                agents_consulted=len(agent_responses),
            )

            return {
                "query": sanitized_query,
                "original_query": query,
                "agents_consulted": list(agent_responses.keys()),
                "agent_responses": agent_responses,
                "synthesized_answer": synthesized,
                "status": "success",
                "security": {
                    "injection_detected": not is_safe,
                    "warnings": warnings if not is_safe else [],
                },
            }

        except Exception as e:
            logger.error("coordination_failed", error=str(e))
            return {"query": query, "error": str(e), "status": "failed"}

    async def _synthesize_responses(
        self,
        query: str,
        agent_responses: dict[str, dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Synthesize multiple agent responses into a coherent answer
        دمج استجابات الوكلاء المتعددة في إجابة متماسكة

        Args:
            query: Original user query | الاستفسار الأصلي
            agent_responses: Responses from agents | استجابات الوكلاء
            context: Additional context | سياق إضافي

        Returns:
            Synthesized answer | الإجابة المدمجة
        """
        synthesis_prompt = """You are synthesizing responses from multiple agricultural AI specialists.

Your task is to:
1. Combine insights from all agents
2. Resolve any contradictions
3. Create a comprehensive, coherent answer
4. Maintain technical accuracy
5. Communicate clearly in both Arabic and English when appropriate

Original query: {query}

Agent responses:
{responses}

Provide a well-structured, comprehensive answer that addresses the user's query.

أنت تدمج استجابات من عدة متخصصين في الذكاء الاصطناعي الزراعي.
قدم إجابة شاملة ومتماسكة تعالج استفسار المستخدم."""

        # Format agent responses
        # تنسيق استجابات الوكلاء
        responses_text = []
        for agent_name, response in agent_responses.items():
            responses_text.append(
                f"\n{agent_name} ({response.get('role', '')}):\n{response.get('response', '')}"
            )

        messages = [
            SystemMessage(content="You are an expert agricultural advisor synthesizing insights."),
            HumanMessage(
                content=synthesis_prompt.format(query=query, responses="\n".join(responses_text))
            ),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content

    def get_available_agents(self) -> list[dict[str, str]]:
        """
        Get list of available agents
        الحصول على قائمة الوكلاء المتاحين

        Returns:
            List of agent information | قائمة معلومات الوكلاء
        """
        return [
            {
                "name": name,
                "role": agent.role,
                "has_rag": agent.retriever is not None,
                "num_tools": len(agent.tools),
            }
            for name, agent in self.agents.items()
        ]
