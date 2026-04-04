"""
Chat Endpoints for Copilot
نقاط نهاية المحادثة لـ Copilot

Main chat interface with RAG integration and agent routing.

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import json

# Import guardrails for input/output validation (C-09)
# SECURITY: Guardrails are MANDATORY in production. If the import fails in
# production (partial deploy, broken dependency), the service must refuse to
# start — otherwise prompt injection filtering is silently disabled.
import os as _os
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from shared.ai.intent_classifier import AgriIntent, AgriIntentClassifier

from ...core.agents import get_agent_router
from ...core.config import get_settings
from ...core.intent_router import IntentRouter
from ...db import save_message
from ...events.publisher import publish_copilot_event
from ...models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CopilotMode,
    MessageRole,
)
from ...rag import get_rag_service
from ...security import MAX_PROMPT_CHARS
from ...security.prompt_guard import detect_prompt_injection, sanitize_input
from ..deps import get_current_user

try:
    from shared.guardrails import TrustLevel, input_filter

    HAS_GUARDRAILS = True
except ImportError:
    HAS_GUARDRAILS = False
    if _os.getenv("ENVIRONMENT") == "production":
        raise RuntimeError(
            "shared.guardrails is required in production but could not be imported. "
            "Refusing to start — prompt injection filtering would be disabled."
        )

logger = structlog.get_logger(__name__)

if not HAS_GUARDRAILS:
    logger.warning(
        "guardrails_unavailable",
        environment=_os.getenv("ENVIRONMENT", "development"),
        message="shared.guardrails not available — prompt injection filtering is DISABLED.",
    )
router = APIRouter(tags=["Chat"])

# Intent classification and routing (module-level singletons)
_intent_classifier = AgriIntentClassifier()
_intent_router: IntentRouter | None = None

# In-memory rate limiter - حد الطلبات في الذاكرة
_rate_limits: dict[str, list[float]] = defaultdict(list)
_RATE_WINDOW = 60  # seconds
_RATE_MAX = 30  # max requests per window


def _check_rate_limit(user_id: str) -> None:
    """Check per-user rate limit. Raises 429 if exceeded."""
    now = time.time()
    _rate_limits[user_id] = [t for t in _rate_limits[user_id] if now - t < _RATE_WINDOW]
    if len(_rate_limits[user_id]) >= _RATE_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded | تم تجاوز حد الطلبات")
    _rate_limits[user_id].append(now)


def _get_intent_router() -> IntentRouter:
    global _intent_router
    if _intent_router is None:
        _intent_router = IntentRouter()
    return _intent_router


def _get_http_client(req: Request) -> httpx.AsyncClient:
    """Get shared HTTP client from app state.

    Raises RuntimeError if not initialized (lifespan must run first).
    """
    client = getattr(req.app.state, "http_client", None)
    if client is None:
        raise RuntimeError(
            "http_client not initialized in app.state. Ensure the lifespan context manager ran correctly."
        )
    return client


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request, user: dict = Depends(get_current_user)) -> ChatResponse:
    """
    Main chat endpoint with RAG and agent routing.
    نقطة نهاية المحادثة الرئيسية مع RAG وتوجيه الوكلاء
    """
    start_time = time.time()

    # Rate limit check - فحص حد الطلبات
    _check_rate_limit(user.get("user_id", ""))

    settings = get_settings()

    # Validate total prompt size
    total_chars = sum(len(m.content) for m in request.messages)
    if total_chars > MAX_PROMPT_CHARS:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "Prompt too large",
                "error_ar": "الطلب كبير جداً",
                "max_chars": MAX_PROMPT_CHARS,
                "actual_chars": total_chars,
            },
        )

    # Get the last user message for context
    last_message = request.messages[-1]
    user_query = last_message.content

    # Prompt injection detection
    is_injection, pattern_name = detect_prompt_injection(user_query)
    if is_injection:
        nc = getattr(req.app.state, "nc", None)
        await publish_copilot_event(
            nc,
            "prompt_injection_detected",
            {
                "user_id": user.get("user_id"),
                "tenant_id": user.get("tenant_id"),
                "session_id": request.session_id,
                "pattern": pattern_name,
            },
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Prompt injection detected",
                "error_ar": "تم اكتشاف محاولة حقن أوامر",
                "pattern": pattern_name,
            },
        )

    # Sanitize user input before further processing
    user_query = sanitize_input(user_query)

    # Guardrails input validation
    if HAS_GUARDRAILS:
        try:
            guard_result = input_filter.filter_input(
                text=user_query,
                trust_level=TrustLevel.BASIC,
                mask_pii=True,
            )
            if not guard_result.is_safe:
                logger.warning(
                    "Guardrails blocked input",
                    session_id=request.session_id,
                    violations=[str(v) for v in guard_result.violations],
                )
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Input blocked by safety guardrails",
                        "error_ar": "تم حظر الإدخال بواسطة حواجز الأمان",
                        "violations": [str(v) for v in guard_result.violations],
                    },
                )
            # Use the filtered (PII-masked) text for downstream processing
            user_query = guard_result.filtered_text
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Guardrails input validation error, proceeding with caution", error=str(e))

    # Publish chat_started event
    nc = getattr(req.app.state, "nc", None)
    await publish_copilot_event(
        nc,
        "chat_started",
        {
            "user_id": user.get("user_id"),
            "tenant_id": user.get("tenant_id"),
            "session_id": request.session_id,
        },
    )

    # Intent classification — run before RAG/LLM to enable service routing
    # تصنيف النية — يتم قبل RAG/LLM لتمكين توجيه الخدمة
    intent_result = None
    intent_router_result = None
    intent_context_text = ""
    try:
        intent_result = await _intent_classifier.classify(user_query)
        if intent_result.confidence >= 0.7 and intent_result.intent != AgriIntent.GENERAL_ADVISORY:
            field_id = getattr(request, "field_id", None)
            if field_id is None:
                request_context = getattr(request, "context", None)
                if isinstance(request_context, dict):
                    field_id = request_context.get("field_id")
            intent_router_result = await _get_intent_router().route(
                intent_result,
                user_query,
                {
                    "field_id": field_id,
                    "tenant_id": user.get("tenant_id"),
                },
            )
            if intent_router_result and intent_router_result.response:
                intent_context_text = json.dumps(intent_router_result.response, ensure_ascii=False)
    except Exception as e:
        logger.warning("Intent classification/routing failed, proceeding without", error=str(e))

    # Perform RAG search (service already initialized in lifespan)
    rag_context = []
    rag_context_text = ""
    try:
        rag_service = get_rag_service()
        search_results = await rag_service.search(
            query=user_query,
            top_k=5,
            tenant_id=user.get("tenant_id", ""),
        )

        if search_results:
            rag_context = [
                {
                    "id": r.document.id,
                    "text": r.document.text[:500],
                    "score": r.score,
                }
                for r in search_results
            ]
            rag_context_text = rag_service.format_context_for_prompt(
                search_results,
                language=_detect_language(user_query),
            )

    except Exception as e:
        logger.warning("RAG search failed", error=str(e))

    # Prepend intent-routed service context to RAG context if available
    if intent_context_text:
        rag_context_text = (
            f"[Service context for {intent_result.intent.value}]:\n{intent_context_text}\n\n{rag_context_text}"
        )

    # Route to appropriate agent
    agent_router = get_agent_router()
    routing_result = agent_router.route(user_query)

    # Build system prompt with context
    system_prompt = _build_system_prompt(
        rag_context=rag_context_text,
        agent_type=routing_result.agent_type.value,
        language=_detect_language(user_query),
    )

    # Generate response using shared HTTP client
    http_client = _get_http_client(req)
    response_content = await _generate_response(
        messages=request.messages,
        system_prompt=system_prompt,
        settings=settings,
        http_client=http_client,
    )

    elapsed_ms = (time.time() - start_time) * 1000

    logger.info(
        "Chat completed",
        session_id=request.session_id,
        agent=routing_result.agent_type.value,
        intent=intent_result.intent.value if intent_result else None,
        intent_confidence=intent_result.confidence if intent_result else None,
        service_used=intent_router_result.service_used if intent_router_result else None,
        rag_hits=len(rag_context),
        elapsed_ms=elapsed_ms,
    )

    # Publish chat_completed event
    await publish_copilot_event(
        nc,
        "chat_completed",
        {
            "user_id": user.get("user_id"),
            "tenant_id": user.get("tenant_id"),
            "session_id": request.session_id,
            "agent": routing_result.agent_type.value,
            "rag_hits": len(rag_context),
            "elapsed_ms": elapsed_ms,
        },
    )

    # Persist chat messages to database (non-blocking)
    # حفظ رسائل المحادثة في قاعدة البيانات (بدون حجب)
    try:
        user_id = user.get("user_id", "")
        tenant_id = user.get("tenant_id", "")

        # Save the user message
        await save_message(
            session_id=request.session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            role=last_message.role.value,
            content=user_query,
            rag_context=None,
            agent_type=None,
        )

        # Save the assistant response with RAG context and agent info
        await save_message(
            session_id=request.session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            role=MessageRole.ASSISTANT.value,
            content=response_content,
            rag_context=rag_context if rag_context else None,
            agent_type=routing_result.agent_type.value,
        )
    except Exception as e:
        logger.warning(
            "Failed to persist chat messages",
            error=str(e),
            session_id=request.session_id,
            error_ar="فشل في حفظ رسائل المحادثة",
        )

    return ChatResponse(
        session_id=request.session_id,
        mode=CopilotMode.OFFLINE if settings.is_offline_mode else CopilotMode.HYBRID,
        message=ChatMessage(
            role=MessageRole.ASSISTANT,
            content=response_content,
        ),
        rag_context=rag_context if rag_context else None,
        intent=intent_result.intent.value if intent_result else None,
        services_used=[intent_router_result.service_used] if intent_router_result else [],
        confidence=intent_result.confidence if intent_result else None,
        usage={"total_chars": total_chars, "response_chars": len(response_content)},
        timestamp=datetime.now(UTC),
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, req: Request, user: dict = Depends(get_current_user)):
    """
    Streaming chat endpoint using Ollama's native streaming.
    نقطة نهاية المحادثة المتدفقة باستخدام التدفق الأصلي من Ollama

    Returns Server-Sent Events for real-time streaming responses.
    Falls back to non-streaming if Ollama streaming is unavailable.
    """
    settings = get_settings()

    # Validate prompt
    total_chars = sum(len(m.content) for m in request.messages)
    if total_chars > MAX_PROMPT_CHARS:
        raise HTTPException(status_code=413, detail={"error": "Prompt too large", "error_ar": "الطلب كبير جداً"})

    last_message = request.messages[-1]
    user_query = last_message.content

    # Prompt injection detection
    is_injection, pattern_name = detect_prompt_injection(user_query)
    if is_injection:
        raise HTTPException(
            status_code=400, detail={"error": "Prompt injection detected", "error_ar": "تم اكتشاف محاولة حقن أوامر"}
        )

    # Sanitize user input before further processing
    user_query = sanitize_input(user_query)

    # Build system prompt
    rag_context_text = ""
    try:
        rag_service = get_rag_service()
        results = await rag_service.search(query=user_query, top_k=5, tenant_id=user.get("tenant_id", ""))
        if results:
            rag_context_text = rag_service.format_context_for_prompt(results, language=_detect_language(user_query))
    except Exception:
        logger.warning("RAG context retrieval failed, proceeding without context", exc_info=True)

    agent_router = get_agent_router()
    routing_result = agent_router.route(user_query)
    system_prompt = _build_system_prompt(
        rag_context=rag_context_text,
        agent_type=routing_result.agent_type.value,
        language=_detect_language(user_query),
    )

    ollama_messages = [
        {"role": "system", "content": system_prompt},
        *[{"role": m.role.value, "content": m.content} for m in request.messages],
    ]

    async def generate_stream():
        """Stream response chunks from Ollama."""
        try:
            http_client = _get_http_client(req)
            async with http_client.stream(
                "POST",
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": ollama_messages,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': 'LLM unavailable'})}\n\n"
                    yield "data: [DONE]\n\n"
                    return

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield f"data: {json.dumps({'content': content})}\n\n"
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.warning("Streaming failed, falling back", error=str(e))
            # Fallback: generate full response and send at once
            http_client = _get_http_client(req)
            response_content = await _generate_response(
                messages=request.messages,
                system_prompt=system_prompt,
                settings=settings,
                http_client=http_client,
            )
            yield f"data: {json.dumps({'content': response_content})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _build_system_prompt(
    rag_context: str,
    agent_type: str,
    language: str,
) -> str:
    """Build system prompt with context and agent instructions"""
    base_prompt = """أنت مساعد SAHOOL الذكي - منصة الزراعة الذكية الوطنية.
You are SAHOOL's intelligent assistant - the National Agricultural Intelligence Platform.

You help with:
- Code analysis and fixing (تحليل وإصلاح الكود)
- Field and crop management (إدارة الحقول والمحاصيل)
- Weather and irrigation advice (نصائح الطقس والري)
- Agricultural recommendations (التوصيات الزراعية)

Be concise, helpful, and bilingual (Arabic/English) when appropriate.
"""

    agent_instructions = {
        "code_fix": """
Focus on code analysis and fixing. When reviewing code:
- Identify bugs and security issues
- Suggest fixes with explanations
- Follow best practices
""",
        "code_review": """
Focus on code review and quality. When reviewing:
- Check for code quality issues
- Evaluate test coverage
- Suggest improvements
""",
        "field_advisor": """
Focus on field and crop advice. Consider:
- NDVI and vegetation health
- Growth stages
- Regional conditions
""",
        "weather_advisor": """
Focus on weather and climate advice. Include:
- Forecast information
- Agricultural impact
- Timing recommendations
""",
        "irrigation_advisor": """
Focus on irrigation planning. Consider:
- Soil moisture levels
- Crop water requirements
- Weather forecast
- Efficiency optimization
""",
        "general": """
Provide general assistance. Be helpful and informative.
""",
    }

    # Build full prompt
    prompt_parts = [base_prompt]

    # Add agent-specific instructions
    agent_inst = agent_instructions.get(agent_type, agent_instructions["general"])
    prompt_parts.append(agent_inst)

    # Add RAG context if available
    if rag_context:
        prompt_parts.append(f"""
Use the following SAHOOL knowledge base context when relevant:

{rag_context}

If the context doesn't answer the question, say so and provide general guidance.
""")

    return "\n".join(prompt_parts)


def _detect_language(text: str) -> str:
    """Detect language (Arabic or English)"""
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    if arabic_chars / max(len(text), 1) > 0.3:
        return "ar"
    return "en"


async def _generate_response(
    messages: list[ChatMessage],
    system_prompt: str,
    settings: Any,
    http_client: httpx.AsyncClient | None = None,
) -> str:
    """
    Generate response using available LLM.
    توليد رد باستخدام نموذج اللغة المتاح

    Tries in order:
    1. Ollama (local)
    2. External LLM (if enabled)
    3. Fallback response
    """
    # Use shared client or create a temporary one
    client = http_client or httpx.AsyncClient(timeout=30.0)
    _should_close = http_client is None

    try:
        # Try Ollama first (offline-first)
        try:
            ollama_messages = [
                {"role": "system", "content": system_prompt},
                *[{"role": msg.role.value, "content": msg.content} for msg in messages],
            ]

            response = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": ollama_messages,
                    "stream": False,
                },
            )
            if response.status_code == 200:
                data = response.json()
                response_content = data.get("message", {}).get("content", "")
                if len(response_content) > 50000:
                    response_content = response_content[:50000] + "\n\n[Response truncated]"
                return response_content

        except Exception as e:
            logger.debug("Ollama not available", error=str(e))

        # Try external LLM if enabled
        if settings.enable_external and settings.external_llm_api_key:
            try:
                response = await client.post(
                    f"{settings.external_llm_base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.external_llm_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.external_llm_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            *[{"role": m.role.value, "content": m.content} for m in messages],
                        ],
                        "temperature": settings.external_llm_temperature,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    response_content = data["choices"][0]["message"]["content"]
                    if len(response_content) > 50000:
                        response_content = response_content[:50000] + "\n\n[Response truncated]"
                    return response_content

            except Exception as e:
                logger.warning("External LLM failed", error=str(e))

    finally:
        if _should_close:
            await client.aclose()

    # Fallback response
    last_message = messages[-1].content
    if _detect_language(last_message) == "ar":
        return """أنا مساعد SAHOOL. للأسف، لا يمكنني الاتصال بنموذج اللغة حالياً.

يرجى:
1. التحقق من تشغيل Ollama محلياً
2. أو تفعيل الوصول الخارجي في الإعدادات

يمكنني مساعدتك في:
- تحليل الكود وإصلاح الأخطاء
- استشارات الحقول والمحاصيل
- نصائح الري والطقس"""
    else:
        return """I'm SAHOOL's assistant. Unfortunately, I cannot connect to the language model right now.

Please:
1. Check if Ollama is running locally
2. Or enable external access in settings

I can help you with:
- Code analysis and bug fixing
- Field and crop advisory
- Irrigation and weather advice"""
