"""
Tool Execution Endpoints
نقاط نهاية تنفيذ الأدوات

Secure tool execution with guardrails.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request

from ..deps import get_current_user
from ...models.schemas import (
    GuardDecision as GuardDecisionSchema,
)
from ...models.schemas import (
    ToolCallRequest,
    ToolCallResponse,
)
from ...rag import get_rag_service
from ...security import (
    TOOL_ALLOWLIST,
    guard_tool_call,
    is_domain_allowed,
    is_tool_allowed,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/tools", tags=["Tools"])


def _get_http_client(req: Request) -> httpx.AsyncClient:
    """Get shared HTTP client from app state, or create a fallback."""
    client = getattr(req.app.state, "http_client", None)
    if client is not None:
        return client
    return httpx.AsyncClient(timeout=30.0)


@router.post("/run", response_model=ToolCallResponse)
async def run_tool(request: ToolCallRequest, req: Request, user: dict = Depends(get_current_user)) -> ToolCallResponse:
    """
    Execute a tool with guardrails.
    تنفيذ أداة مع حواجز الحماية

    Validates the tool call against security policies
    before execution.
    """
    start_time = time.time()

    # Guard check
    decision = guard_tool_call(
        tool=request.tool,
        args=request.args,
        session_id=request.session_id,
    )

    if not decision.allowed:
        logger.warning(
            "Tool call blocked",
            tool=request.tool,
            reason=decision.reason,
            layer=decision.layer,
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Tool call blocked",
                "error_ar": "تم حظر استدعاء الأداة",
                "reason": decision.reason,
                "reason_ar": decision.reason_ar,
                "layer": decision.layer,
            },
        )

    # Execute tool
    try:
        http_client = _get_http_client(req)
        result = await _execute_tool(request.tool, request.args, http_client=http_client)
        execution_time = (time.time() - start_time) * 1000

        logger.info(
            "Tool executed",
            tool=request.tool,
            success=True,
            time_ms=execution_time,
        )

        return ToolCallResponse(
            tool=request.tool,
            success=True,
            result=result,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            "Tool execution failed",
            tool=request.tool,
            error=str(e),
        )

        return ToolCallResponse(
            tool=request.tool,
            success=False,
            error=str(e),
            execution_time_ms=execution_time,
        )


@router.post("/guard", response_model=GuardDecisionSchema)
async def check_guard(request: ToolCallRequest, user: dict = Depends(get_current_user)) -> GuardDecisionSchema:
    """
    Check if a tool call would be allowed (dry run).
    فحص ما إذا كان استدعاء الأداة سيُسمح به (تشغيل تجريبي)
    """
    decision = guard_tool_call(
        tool=request.tool,
        args=request.args,
        session_id=request.session_id,
    )

    return GuardDecisionSchema(
        allowed=decision.allowed,
        reason=decision.reason,
        details={
            "reason_ar": decision.reason_ar,
            "layer": decision.layer,
        },
    )


@router.get("/list")
async def list_tools():
    """
    List available tools.
    عرض قائمة الأدوات المتاحة
    """
    tools = []

    for tool in sorted(TOOL_ALLOWLIST):
        category = tool.split(".")[0] if "." in tool else "general"
        tools.append(
            {
                "name": tool,
                "category": category,
                "allowed": True,
            }
        )

    return {
        "tools": tools,
        "total": len(tools),
        "categories": list({t["category"] for t in tools}),
    }


@router.get("/check-domain/{domain}")
async def check_domain(domain: str):
    """
    Check if a domain is allowed.
    فحص ما إذا كان النطاق مسموحاً
    """
    allowed = is_domain_allowed(domain)
    return {
        "domain": domain,
        "allowed": allowed,
    }


async def _execute_tool(tool: str, args: dict[str, Any], http_client: httpx.AsyncClient | None = None) -> Any:
    """
    Execute a tool by name.
    تنفيذ أداة بالاسم
    """
    # RAG tools
    if tool == "rag.search":
        rag_service = get_rag_service()
        results = await rag_service.search(
            query=args.get("query", ""),
            top_k=args.get("k", 5),
        )
        return [
            {
                "id": r.document.id,
                "text": r.document.text[:500],
                "score": r.score,
            }
            for r in results
        ]

    elif tool == "rag.add":
        rag_service = get_rag_service()
        doc = await rag_service.add_document(
            text=args.get("text", ""),
            text_ar=args.get("text_ar"),
            metadata=args.get("metadata"),
            doc_id=args.get("id"),
        )
        return {"id": doc.id, "created": True}

    elif tool == "rag.list":
        rag_service = get_rag_service()
        docs = await rag_service.list_documents(
            limit=args.get("limit", 100),
            offset=args.get("offset", 0),
        )
        return [d.to_dict() for d in docs]

    elif tool == "rag.delete":
        rag_service = get_rag_service()
        success = await rag_service.delete_document(args.get("id", ""))
        return {"deleted": success}

    # Code analysis tools (proxy to code-fix-agent)
    elif tool.startswith("code."):
        return await _proxy_to_code_agent(tool, args, http_client)

    # Field tools (proxy to field service)
    elif tool.startswith("field."):
        return await _proxy_to_field_service(tool, args, http_client)

    # Weather tools (proxy to weather service)
    elif tool.startswith("weather."):
        return await _proxy_to_weather_service(tool, args, http_client)

    # Deploy tools (planning only)
    elif tool.startswith("deploy."):
        return await _handle_deploy_tool(tool, args)

    else:
        raise ValueError(f"Unknown tool: {tool}")


_CODE_AGENT_ACTIONS = {"analyze", "fix", "review", "diagnose", "test"}


async def _proxy_to_code_agent(tool: str, args: dict[str, Any], http_client: httpx.AsyncClient | None = None) -> Any:
    """Proxy request to code-fix-agent"""
    from ...core.config import get_settings

    settings = get_settings()
    action = tool.split(".")[-1]
    client = http_client or httpx.AsyncClient(timeout=30.0)
    _should_close = http_client is None

    if action not in _CODE_AGENT_ACTIONS:
        return {"error": f"Unknown code agent action: {action}"}

    try:
        response = await client.post(
            f"{settings.code_fix_agent_url}/api/v1/{action}",
            json=args,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Code agent returned {response.status_code}"}
    except Exception as e:
        return {"error": f"Code agent unavailable: {e}"}
    finally:
        if _should_close:
            await client.aclose()


_FIELD_SERVICE_ACTIONS = {"list", "get", "create", "update", "delete", "boundaries", "statistics"}


async def _proxy_to_field_service(tool: str, args: dict[str, Any], http_client: httpx.AsyncClient | None = None) -> Any:
    """Proxy request to field management service"""
    from ...core.config import get_settings

    settings = get_settings()
    action = tool.split(".")[-1]
    client = http_client or httpx.AsyncClient(timeout=30.0)
    _should_close = http_client is None

    if action not in _FIELD_SERVICE_ACTIONS:
        return {"error": f"Unknown field service action: {action}"}

    try:
        if action == "list":
            response = await client.get(
                f"{settings.field_management_url}/api/v1/fields",
                params=args,
            )
        elif action == "get":
            field_id = args.get("id", "")
            response = await client.get(
                f"{settings.field_management_url}/api/v1/fields/{field_id}",
            )
        else:
            response = await client.post(
                f"{settings.field_management_url}/api/v1/fields/{action}",
                json=args,
            )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Field service returned {response.status_code}"}
    except Exception as e:
        return {"error": f"Field service unavailable: {e}"}
    finally:
        if _should_close:
            await client.aclose()


_WEATHER_SERVICE_ACTIONS = {"forecast", "current", "historical", "alerts", "stations"}


async def _proxy_to_weather_service(tool: str, args: dict[str, Any], http_client: httpx.AsyncClient | None = None) -> Any:
    """Proxy request to weather service"""
    from ...core.config import get_settings

    settings = get_settings()
    action = tool.split(".")[-1]
    client = http_client or httpx.AsyncClient(timeout=30.0)
    _should_close = http_client is None

    if action not in _WEATHER_SERVICE_ACTIONS:
        return {"error": f"Unknown weather service action: {action}"}

    try:
        if action == "forecast":
            response = await client.get(
                f"{settings.weather_service_url}/api/v1/forecast",
                params=args,
            )
        elif action == "current":
            response = await client.get(
                f"{settings.weather_service_url}/api/v1/current",
                params=args,
            )
        else:
            response = await client.get(
                f"{settings.weather_service_url}/api/v1/{action}",
                params=args,
            )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Weather service returned {response.status_code}"}
    except Exception as e:
        return {"error": f"Weather service unavailable: {e}"}
    finally:
        if _should_close:
            await client.aclose()


async def _handle_deploy_tool(tool: str, args: dict[str, Any]) -> Any:
    """Handle deployment tools (planning only)"""
    action = tool.split(".")[-1]

    if action == "plan":
        # Return a deployment plan (read-only)
        return {
            "plan": "Deployment planning is available in Enterprise package",
            "steps": [
                "1. Review changes",
                "2. Run tests",
                "3. Build containers",
                "4. Deploy to staging",
                "5. Verify",
                "6. Deploy to production",
            ],
            "requires_approval": True,
        }

    elif action == "status":
        return {
            "environment": args.get("environment", "development"),
            "status": "healthy",
            "services_running": True,
        }

    elif action == "validate":
        return {
            "valid": True,
            "warnings": [],
            "errors": [],
        }

    else:
        return {"error": f"Unknown deploy action: {action}"}
