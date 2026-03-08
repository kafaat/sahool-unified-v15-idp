"""
Chat Endpoints for Copilot
نقاط نهاية المحادثة لـ Copilot

Main chat interface with RAG integration and agent routing.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timezone
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request

from ...core.agents import get_agent_router
from ...core.config import get_settings
from ...models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CopilotMode,
    MessageRole,
)
from ...db import save_message
from ...rag import get_rag_service
from ...security import MAX_PROMPT_CHARS
from ..deps import get_current_user
from ...events.publisher import publish_copilot_event
from ...security.prompt_guard import detect_prompt_injection

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request, user: dict = Depends(get_current_user)) -> ChatResponse:
    """
    Main chat endpoint with RAG and agent routing.
    نقطة نهاية المحادثة الرئيسية مع RAG وتوجيه الوكلاء

    Features:
    - Validates prompt size
    - Performs RAG search for context
    - Routes to appropriate agent
    - Generates response
    """
    start_time = time.time()
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

    # Perform RAG search
    rag_context = []
    rag_context_text = ""
    try:
        rag_service = get_rag_service()
        await rag_service.initialize()

        search_results = await rag_service.search(
            query=user_query,
            top_k=5,
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
            rag_context_text = rag_service.format_context_for_prompt(search_results)

    except Exception as e:
        logger.warning("RAG search failed", error=str(e))

    # Route to appropriate agent
    agent_router = get_agent_router()
    routing_result = agent_router.route(user_query)

    # Build system prompt with context
    system_prompt = _build_system_prompt(
        rag_context=rag_context_text,
        agent_type=routing_result.agent_type.value,
        language=_detect_language(user_query),
    )

    # Generate response
    response_content = await _generate_response(
        messages=request.messages,
        system_prompt=system_prompt,
        settings=settings,
    )

    elapsed_ms = (time.time() - start_time) * 1000

    logger.info(
        "Chat completed",
        session_id=request.session_id,
        agent=routing_result.agent_type.value,
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
        usage={"total_chars": total_chars, "response_chars": len(response_content)},
        timestamp=datetime.now(UTC),
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, req: Request, user: dict = Depends(get_current_user)):
    """
    Streaming chat endpoint.
    نقطة نهاية المحادثة المتدفقة

    Returns Server-Sent Events for streaming responses.
    """
    from fastapi.responses import StreamingResponse

    async def generate():
        """Generate streaming response"""
        # For now, return a simple streaming response
        # Full implementation would integrate with LLM streaming
        response = await chat(request, req, user)

        # Simulate streaming by chunking the response
        content = response.message.content
        chunk_size = 50

        for i in range(0, len(content), chunk_size):
            chunk = content[i : i + chunk_size]
            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
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
    # Simple detection based on Arabic character presence
    arabic_chars = sum(1 for c in text if "\u0600" <= c <= "\u06ff")
    if arabic_chars / max(len(text), 1) > 0.3:
        return "ar"
    return "en"


async def _generate_response(
    messages: list[ChatMessage],
    system_prompt: str,
    settings: Any,
) -> str:
    """
    Generate response using available LLM.
    توليد رد باستخدام نموذج اللغة المتاح

    Tries in order:
    1. Ollama (local)
    2. External LLM (if enabled)
    3. Fallback response
    """
    # Try Ollama first (offline-first)
    try:
        import httpx

        ollama_messages = [
            {"role": "system", "content": system_prompt},
        ]
        for msg in messages:
            ollama_messages.append(
                {
                    "role": msg.role.value,
                    "content": msg.content,
                }
            )

        async with httpx.AsyncClient(timeout=30.0) as client:
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
                return data.get("message", {}).get("content", "")

    except Exception as e:
        logger.debug("Ollama not available", error=str(e))

    # Try external LLM if enabled
    if settings.enable_external and settings.external_llm_api_key:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=30.0) as client:
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
                    return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.warning("External LLM failed", error=str(e))

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
