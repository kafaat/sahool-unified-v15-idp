# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Orchestrator API endpoints for LLM Orchestrator Service.

These endpoints handle the main orchestration logic, including
intent classification, agent execution, and response synthesis.

نقاط نهاية API للتنسيق لخدمة تنسيق نماذج اللغة الكبيرة.
تتعامل هذه النقاط مع منطق التنسيق الرئيسي، بما في ذلك
تصنيف النوايا، وتنفيذ الوكلاء، وتجميع الاستجابات.
"""

import time
import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ...agents.executor import AgentExecutor
from ...agents.quick_responses import QuickResponse
from ...agents.registry import AgentRegistry, get_agent_registry
from ...agents.router import SimpleAgentRouter, get_router
from ...agents.routing_rules import get_rules_for_display
from ...core.config import settings
from ...utils.intent_classifier import classify_intent
from ...utils.synthesizer import synthesize_response
from ..schemas import (
    AgentCall,
    ExecuteActionRequest,
    ExecuteActionResponse,
    ExecutionMode,
    ExecutionPlan,
    ExecutionPlanResponse,
    IntentType,
    OrchestratorResponse,
    UserIntent,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["orchestrator"])


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header - استخراج معرف المستأجر من الهيدر"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


def get_executor(request: Request) -> AgentExecutor:
    """Get agent executor from app state."""
    executor = getattr(request.app.state, "executor", None)
    if not executor:
        # Create executor without Redis for now
        executor = AgentExecutor()
        request.app.state.executor = executor
    return executor


@router.post(
    "/orchestrate",
    response_model=OrchestratorResponse,
    summary="Orchestrate AI Agents | تنسيق وكلاء الذكاء الاصطناعي",
    description="""
    Main orchestration endpoint that:
    1. Classifies user intent (Arabic/English)
    2. Determines relevant agents to call
    3. Executes agents in parallel
    4. Synthesizes a coherent response

    نقطة النهاية الرئيسية للتنسيق التي:
    1. تصنف نية المستخدم (عربي/إنجليزي)
    2. تحدد الوكلاء المناسبين للاستدعاء
    3. تنفذ الوكلاء بالتوازي
    4. تجمع استجابة متسقة
    """,
)
async def orchestrate(
    user_intent: UserIntent,
    request: Request,
    registry: AgentRegistry = Depends(get_agent_registry),
    executor: AgentExecutor = Depends(get_executor),
    tenant_id: str = Depends(get_tenant_id),
) -> OrchestratorResponse:
    """Main orchestration endpoint."""
    start_time = time.time()
    request_id = user_intent.correlation_id or str(uuid.uuid4())

    logger.info(
        "orchestration_started",
        request_id=request_id,
        text_length=len(user_intent.text),
        has_image=bool(user_intent.image_base64 or user_intent.image_url),
        field_id=user_intent.field_id,
    )

    try:
        # Step 1: Classify intent
        intent = await classify_intent(user_intent)

        logger.info(
            "intent_classified",
            request_id=request_id,
            intent=intent.intent_type.value,
            confidence=intent.confidence,
            language=intent.language_detected,
        )

        # Step 2: Get relevant agents
        agents = registry.get_agents_for_intent(intent.intent_type.value)

        if not agents:
            logger.warning(
                "no_agents_found",
                request_id=request_id,
                intent=intent.intent_type.value,
            )
            # Return a response with no agent results
            return OrchestratorResponse(
                request_id=request_id,
                success=True,
                summary_en="No specialized agents available for this query. Please provide more details.",
                summary_ar="لا توجد وكلاء متخصصون لهذا الاستفسار. يرجى تقديم المزيد من التفاصيل.",
                detailed_results=[],
                actions=[],
                recommendations_en=[
                    "Try rephrasing your question with more specific details",
                    "Include crop type or field information if available",
                ],
                recommendations_ar=[
                    "حاول إعادة صياغة سؤالك بمزيد من التفاصيل",
                    "قم بتضمين نوع المحصول أو معلومات الحقل إن توفرت",
                ],
                intent=intent,
                total_latency_ms=int((time.time() - start_time) * 1000),
                agents_called=0,
            )

        # Step 3: Create execution plan
        agent_calls = []
        for agent in agents[:5]:  # Limit to 5 agents
            # Determine the best endpoint for this intent
            endpoint_key = _get_endpoint_for_intent(intent.intent_type, agent.endpoints)
            endpoint = agent.endpoints.get(endpoint_key, list(agent.endpoints.values())[0])
            full_endpoint = f"{agent.base_url}{endpoint}"

            # Build parameters
            params = _build_agent_params(intent, user_intent, agent.name)

            agent_calls.append(
                AgentCall(
                    agent_name=agent.name,
                    endpoint=full_endpoint,
                    method="POST",
                    params=params,
                    priority=agent.priority,
                    timeout=agent.timeout,
                )
            )

        plan = ExecutionPlan(
            plan_id=f"plan_{request_id}",
            agents=agent_calls,
            execution_mode=ExecutionMode.PARALLEL,
            intent=intent,
        )

        logger.info(
            "execution_plan_created",
            request_id=request_id,
            agents=len(agent_calls),
            mode=plan.execution_mode.value,
        )

        # Step 4: Execute agents
        agent_results = await executor.execute_plan(plan)

        # Step 5: Synthesize response
        response = await synthesize_response(intent, agent_results, request_id)

        total_time = int((time.time() - start_time) * 1000)
        response.total_latency_ms = total_time

        logger.info(
            "orchestration_completed",
            request_id=request_id,
            success=response.success,
            agents_called=response.agents_called,
            total_latency_ms=total_time,
        )

        return response

    except Exception as e:
        logger.error(
            "orchestration_failed",
            request_id=request_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failed: {str(e)}",
        )


@router.post(
    "/orchestrate/image",
    response_model=OrchestratorResponse,
    summary="Orchestrate with Image | تنسيق مع صورة",
    description="""
    Orchestration endpoint optimized for image-based queries.
    Automatically routes to vision-capable agents.

    نقطة نهاية التنسيق المحسنة للاستفسارات القائمة على الصور.
    توجه تلقائياً إلى الوكلاء القادرين على معالجة الصور.
    """,
)
async def orchestrate_with_image(
    user_intent: UserIntent,
    request: Request,
    registry: AgentRegistry = Depends(get_agent_registry),
    executor: AgentExecutor = Depends(get_executor),
) -> OrchestratorResponse:
    """Orchestration endpoint for image-based queries."""
    # Validate image is provided
    if not user_intent.image_base64 and not user_intent.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image is required. Provide either image_base64 or image_url.",
        )

    # Force image analysis intent
    user_intent.context = user_intent.context or {}
    user_intent.context["force_image_analysis"] = True

    return await orchestrate(user_intent, request, registry, executor)


@router.get(
    "/orchestrate/plans",
    response_model=ExecutionPlanResponse,
    summary="Get Available Plans | الحصول على الخطط المتاحة",
    description="""
    Get information about available execution plans for different intents.

    الحصول على معلومات حول خطط التنفيذ المتاحة للنوايا المختلفة.
    """,
)
async def get_available_plans(
    registry: AgentRegistry = Depends(get_agent_registry),
) -> ExecutionPlanResponse:
    """Get available execution plans."""
    plans = []

    for intent_type in IntentType:
        if intent_type in (IntentType.UNKNOWN, IntentType.MULTI_INTENT):
            continue

        agents = registry.get_agents_for_intent(intent_type.value)

        plans.append(
            {
                "intent": intent_type.value,
                "agents": [
                    {
                        "name": a.name,
                        "name_ar": a.name_ar,
                        "capabilities": [c.value for c in a.capabilities],
                    }
                    for a in agents
                ],
                "agent_count": len(agents),
                "requires_image": any(a.requires_image for a in agents),
                "requires_field_id": any(a.requires_field_id for a in agents),
            }
        )

    return ExecutionPlanResponse(
        plans=plans,
        total=len(plans),
    )


@router.post(
    "/orchestrate/execute-action",
    response_model=ExecuteActionResponse,
    summary="Execute Action | تنفيذ إجراء",
    description="""
    Execute a recommended action from the orchestrator response.

    تنفيذ إجراء موصى به من استجابة المنسق.
    """,
)
async def execute_action(
    action_request: ExecuteActionRequest,
    request: Request,
    executor: AgentExecutor = Depends(get_executor),
    tenant_id: str = Depends(get_tenant_id),
) -> ExecuteActionResponse:
    """Execute a recommended action."""
    action = action_request.action

    # Check if confirmation is required
    if action.requires_confirmation and not action_request.confirmed:
        return ExecuteActionResponse(
            success=False,
            message_en="This action requires confirmation. Please confirm to proceed.",
            message_ar="هذا الإجراء يتطلب تأكيداً. يرجى التأكيد للمتابعة.",
        )

    # Execute the action based on type
    action_id = str(uuid.uuid4())

    logger.info(
        "action_execution_started",
        action_id=action_id,
        action_type=action.action_type.value,
        priority=action.priority,
    )

    try:
        # Map action types to service calls
        # In a real implementation, this would call the appropriate service
        result = await _execute_action_type(
            action,
            action_request.field_id,
            tenant_id,
            executor,
        )

        logger.info(
            "action_execution_completed",
            action_id=action_id,
            action_type=action.action_type.value,
            success=True,
        )

        return ExecuteActionResponse(
            success=True,
            action_id=action_id,
            message_en=f"Action '{action.action_type.value}' executed successfully.",
            message_ar=f"تم تنفيذ الإجراء '{action.action_type.value}' بنجاح.",
            result=result,
        )

    except Exception as e:
        logger.error(
            "action_execution_failed",
            action_id=action_id,
            action_type=action.action_type.value,
            error=str(e),
        )
        return ExecuteActionResponse(
            success=False,
            action_id=action_id,
            message_en=f"Action execution failed: {str(e)}",
            message_ar=f"فشل تنفيذ الإجراء: {str(e)}",
        )


@router.get(
    "/agents",
    summary="List Agents | قائمة الوكلاء",
    description="""
    Get information about all registered AI agents.

    الحصول على معلومات حول جميع وكلاء الذكاء الاصطناعي المسجلين.
    """,
)
async def list_agents(
    registry: AgentRegistry = Depends(get_agent_registry),
) -> dict[str, Any]:
    """List all registered agents."""
    return registry.to_dict()


@router.get(
    "/agents/health",
    summary="Agent Health Check | فحص صحة الوكلاء",
    description="""
    Check health status of all registered agents.

    فحص حالة صحة جميع الوكلاء المسجلين.
    """,
)
async def check_agents_health(
    registry: AgentRegistry = Depends(get_agent_registry),
    executor: AgentExecutor = Depends(get_executor),
) -> dict[str, Any]:
    """Check health of all agents."""
    agents = registry.get_active_agents()
    agent_urls = [(a.name, a.base_url) for a in agents]

    health_results = await executor.health_check_all(agent_urls)

    healthy_count = sum(1 for r in health_results if r.get("healthy", False))

    return {
        "total_agents": len(agents),
        "healthy_agents": healthy_count,
        "unhealthy_agents": len(agents) - healthy_count,
        "health_statuses": health_results,
    }


# Helper functions


def _get_endpoint_for_intent(intent_type: IntentType, endpoints: dict[str, str]) -> str:
    """Get the best endpoint for an intent type."""
    intent_to_endpoint: dict[IntentType, list[str]] = {
        IntentType.CROP_DISEASE: ["disease_detect", "detect", "comprehensive"],
        IntentType.IRRIGATION_QUERY: ["recommendation", "schedule", "water_balance"],
        IntentType.FERTILIZER_ADVICE: ["fertilizer_plan", "nutrient_detect"],
        IntentType.PEST_DETECTION: ["detect", "analyze_image", "risk_assessment"],
        IntentType.WEATHER_QUERY: ["current", "forecast"],
        IntentType.YIELD_PREDICTION: ["predict", "estimate"],
        IntentType.FIELD_ANALYSIS: ["analyze", "diagnosis", "status"],
        IntentType.TERRAIN_ANALYSIS: ["analyze", "dem", "slope"],
        IntentType.HYDROLOGY_QUERY: ["drainage", "watershed", "flow"],
        IntentType.LEVELING_QUERY: ["optimize", "cut_fill", "cost"],
        IntentType.IMAGE_ANALYSIS: ["detect", "analyze_image", "batch"],
        IntentType.GENERAL_ADVISORY: ["comprehensive", "analyze"],
    }

    preferred = intent_to_endpoint.get(intent_type, [])

    for key in preferred:
        if key in endpoints:
            return key

    # Return first available endpoint
    return list(endpoints.keys())[0] if endpoints else ""


def _build_agent_params(intent: Any, user_intent: UserIntent, agent_name: str) -> dict[str, Any]:
    """Build parameters for agent call."""
    params: dict[str, Any] = {}

    # Add entities from intent classification
    if hasattr(intent, "entities") and intent.entities:
        params.update(intent.entities)

    # Add field ID if available
    if user_intent.field_id:
        params["field_id"] = user_intent.field_id

    # Note: tenant_id is injected from X-Tenant-Id header at endpoint level, not from body

    # Add image data for vision agents
    if agent_name in ("yolo-vision", "pest-detection"):
        if user_intent.image_base64:
            params["image_base64"] = user_intent.image_base64
        if user_intent.image_url:
            params["image_url"] = user_intent.image_url

    # Add context
    if user_intent.context:
        params["context"] = user_intent.context

    return params


async def _execute_action_type(
    action: Any,
    field_id: str | None,
    tenant_id: str | None,
    executor: AgentExecutor,
) -> dict[str, Any]:
    """Execute a specific action type."""
    # This is a placeholder implementation
    # In production, this would call the appropriate service

    return {
        "status": "scheduled",
        "action_type": action.action_type.value,
        "field_id": field_id,
        "tenant_id": tenant_id,
        "scheduled_at": "2026-01-31T12:00:00Z",
    }


# =============================================================================
# Simple Agent Routing Endpoints
# نقاط نهاية التوجيه البسيط للوكلاء
# =============================================================================


@router.get(
    "/routing-rules",
    summary="Get Routing Rules | الحصول على قواعد التوجيه",
    description="""
    Get all available routing rules for agent selection.
    Shows intent-to-agent mappings, priorities, and requirements.

    الحصول على جميع قواعد التوجيه المتاحة لاختيار الوكلاء.
    يعرض ربط النوايا بالوكلاء والأولويات والمتطلبات.
    """,
)
async def get_routing_rules() -> dict[str, Any]:
    """Get all routing rules."""
    rules = get_rules_for_display()

    return {
        "rules": rules,
        "total": len(rules),
        "description_en": "Simple rule-based routing for fast agent selection",
        "description_ar": "توجيه قائم على القواعد لاختيار الوكلاء بسرعة",
    }


@router.post(
    "/route-preview",
    summary="Preview Routing | معاينة التوجيه",
    description="""
    Preview which agents would be selected for a given intent or text.
    Does not execute any agents - just shows the routing decision.

    معاينة الوكلاء الذين سيتم اختيارهم لنية أو نص معين.
    لا ينفذ أي وكلاء - يعرض قرار التوجيه فقط.
    """,
)
async def preview_routing(
    intent: str | None = None,
    text: str | None = None,
    has_image: bool = False,
    has_field_id: bool = False,
) -> dict[str, Any]:
    """Preview routing for an intent or text."""
    simple_router = get_router()

    # If text is provided, detect intent and route
    if text:
        result = simple_router.route(
            text=text,
            intent=intent,
            has_image=has_image,
            has_field_id=has_field_id,
        )

        # Handle quick response
        if result.is_quick_response and result.quick_response:
            return {
                "routing_type": "quick_response",
                "intent": "quick_response",
                "agents": [],
                "quick_response": {
                    "response_en": result.quick_response.response_en,
                    "response_ar": result.quick_response.response_ar,
                    "category": result.quick_response.category,
                },
                "description_en": "Query matched a pre-defined quick response",
                "description_ar": "الاستعلام يطابق رداً سريعاً محدداً مسبقاً",
            }

        return {
            "routing_type": "agent_routing",
            "intent": result.intent,
            "agents": result.agents,
            "priority": result.priority.value,
            "confidence": result.confidence,
            "requires_image": result.requires_image,
            "requires_field_id": result.requires_field_id,
            "matched_keywords": result.matched_keywords,
            "fallback_used": result.fallback_used,
            "input_text": text[:100] + "..." if len(text) > 100 else text,
        }

    # If only intent is provided, show preview
    if intent:
        preview = simple_router.preview_route(
            intent=intent,
            has_image=has_image,
            has_field_id=has_field_id,
        )
        return preview

    # Neither text nor intent provided
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Either 'intent' or 'text' must be provided",
    )


@router.get(
    "/quick-response",
    summary="Check Quick Response | التحقق من الرد السريع",
    description="""
    Check if a query matches a pre-defined quick response.
    Quick responses save API costs for common questions.

    التحقق مما إذا كان الاستعلام يطابق رداً سريعاً محدداً مسبقاً.
    الردود السريعة توفر تكاليف API للأسئلة الشائعة.
    """,
)
async def check_quick_response(
    text: str,
) -> dict[str, Any]:
    """Check if a query has a quick response."""
    simple_router = get_router()
    result = simple_router.route(text=text, has_image=False, has_field_id=False)

    if result.is_quick_response and result.quick_response:
        return {
            "has_quick_response": True,
            "response_en": result.quick_response.response_en,
            "response_ar": result.quick_response.response_ar,
            "category": result.quick_response.category,
            "confidence": result.confidence,
        }

    return {
        "has_quick_response": False,
        "detected_intent": result.intent,
        "agents": result.agents,
        "message_en": "No quick response available. Full orchestration recommended.",
        "message_ar": "لا يوجد رد سريع متاح. يُنصح بالتنسيق الكامل.",
    }


@router.post(
    "/orchestrate/simple",
    response_model=OrchestratorResponse,
    summary="Simple Orchestration | تنسيق بسيط",
    description="""
    Simplified orchestration using rule-based routing.
    Faster than full orchestration, returns quick responses when available.

    تنسيق مبسط باستخدام التوجيه القائم على القواعد.
    أسرع من التنسيق الكامل، يعيد الردود السريعة عند توفرها.
    """,
)
async def orchestrate_simple(
    user_intent: UserIntent,
    request: Request,
    registry: AgentRegistry = Depends(get_agent_registry),
    executor: AgentExecutor = Depends(get_executor),
    tenant_id: str = Depends(get_tenant_id),
) -> OrchestratorResponse:
    """Simplified orchestration with quick responses and rule-based routing."""
    start_time = time.time()
    request_id = user_intent.correlation_id or str(uuid.uuid4())

    logger.info(
        "simple_orchestration_started",
        request_id=request_id,
        text_length=len(user_intent.text),
    )

    # Step 1: Use simple router
    simple_router = get_router()
    has_image = bool(user_intent.image_base64 or user_intent.image_url)
    has_field_id = bool(user_intent.field_id)

    routing_result = simple_router.route(
        text=user_intent.text,
        has_image=has_image,
        has_field_id=has_field_id,
    )

    # Step 2: Check for quick response
    if routing_result.is_quick_response and routing_result.quick_response:
        total_time = int((time.time() - start_time) * 1000)

        logger.info(
            "quick_response_returned",
            request_id=request_id,
            category=routing_result.quick_response.category,
            latency_ms=total_time,
        )

        return OrchestratorResponse(
            request_id=request_id,
            success=True,
            summary_en=routing_result.quick_response.response_en,
            summary_ar=routing_result.quick_response.response_ar,
            detailed_results=[],
            actions=[],
            recommendations_en=[],
            recommendations_ar=[],
            intent=None,
            total_latency_ms=total_time,
            agents_called=0,
            metadata={
                "routing_type": "quick_response",
                "category": routing_result.quick_response.category,
            },
        )

    # Step 3: Get agents from routing result
    agents = []
    for agent_name in routing_result.agents:
        agent_info = registry.get_agent(agent_name)
        if agent_info and agent_info.active:
            agents.append(agent_info)

    if not agents:
        # Fallback to advisory
        advisory = registry.get_agent("advisory")
        if advisory:
            agents = [advisory]

    # Step 4: Create execution plan using routed agents
    agent_calls = []
    for agent in agents[:5]:
        # Use the first available endpoint
        endpoint_key = list(agent.endpoints.keys())[0] if agent.endpoints else ""
        endpoint = agent.endpoints.get(endpoint_key, "")
        full_endpoint = f"{agent.base_url}{endpoint}"

        params: dict[str, Any] = {}
        if user_intent.field_id:
            params["field_id"] = user_intent.field_id
        # tenant_id is injected from X-Tenant-Id header at endpoint level
        params["tenant_id"] = tenant_id
        if agent.requires_image and has_image:
            if user_intent.image_base64:
                params["image_base64"] = user_intent.image_base64
            if user_intent.image_url:
                params["image_url"] = user_intent.image_url
        if user_intent.context:
            params["context"] = user_intent.context

        agent_calls.append(
            AgentCall(
                agent_name=agent.name,
                endpoint=full_endpoint,
                method="POST",
                params=params,
                priority=agent.priority,
                timeout=agent.timeout,
            )
        )

    # Step 5: Execute agents
    plan = ExecutionPlan(
        plan_id=f"simple_{request_id}",
        agents=agent_calls,
        execution_mode=ExecutionMode.PARALLEL,
        intent=None,  # type: ignore
    )

    agent_results = await executor.execute_plan(plan)

    # Step 6: Create response
    successful_agents = sum(1 for r in agent_results if r.success)
    total_time = int((time.time() - start_time) * 1000)

    # Simple synthesis
    if successful_agents > 0:
        summary_en = f"Successfully received responses from {successful_agents} agent(s)."
        summary_ar = f"تم استلام استجابات من {successful_agents} وكيل(وكلاء) بنجاح."
    else:
        summary_en = "Unable to get responses from agents. Please try again."
        summary_ar = "تعذر الحصول على استجابات من الوكلاء. يرجى المحاولة مرة أخرى."

    logger.info(
        "simple_orchestration_completed",
        request_id=request_id,
        agents_called=len(agent_calls),
        successful=successful_agents,
        latency_ms=total_time,
    )

    return OrchestratorResponse(
        request_id=request_id,
        success=successful_agents > 0,
        summary_en=summary_en,
        summary_ar=summary_ar,
        detailed_results=agent_results,
        actions=[],
        recommendations_en=[],
        recommendations_ar=[],
        intent=None,
        total_latency_ms=total_time,
        agents_called=len(agent_calls),
        cached_responses=sum(1 for r in agent_results if r.cached),
        metadata={
            "routing_type": "simple",
            "routed_intent": routing_result.intent,
            "priority": routing_result.priority.value,
            "confidence": routing_result.confidence,
        },
    )
