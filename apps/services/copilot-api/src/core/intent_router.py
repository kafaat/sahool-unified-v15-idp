"""
Intent Router - Routes agricultural queries to expert microservices
موجّه النوايا - يوجه الاستعلامات الزراعية للخدمات المتخصصة

Phase 1 of Component Unification Plan (PR #1344)
"""

import httpx
import structlog
from dataclasses import dataclass

from shared.ai.intent_classifier import AgriIntent, IntentResult, INTENT_SERVICE_MAP

logger = structlog.get_logger()


@dataclass
class RouterResult:
    intent: AgriIntent
    response: dict
    service_used: str
    service_port: int
    confidence: float
    language: str


class IntentRouter:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def route(self, intent_result: IntentResult, query: str, context: dict | None = None) -> RouterResult:
        service_info = INTENT_SERVICE_MAP.get(intent_result.intent)
        if not service_info:
            return await self._fallback_to_rag(query, intent_result)

        service_name = service_info["service"]
        port = service_info["port"]

        try:
            response = await self._call_service(service_name, port, query, intent_result, context)
            return RouterResult(
                intent=intent_result.intent,
                response=response,
                service_used=service_name,
                service_port=port,
                confidence=intent_result.confidence,
                language=intent_result.language,
            )
        except Exception as e:
            logger.warning("service_call_failed", service=service_name, error=str(e))
            if "fallback" in service_info:
                return await self._try_fallback(service_info, query, intent_result, context)
            return await self._fallback_to_rag(query, intent_result)

    async def _call_service(
        self, service: str, port: int, query: str, intent: IntentResult, context: dict | None
    ) -> dict:
        # Route to appropriate endpoint based on intent
        url, payload = self._build_request(service, port, query, intent, context)
        resp = await self.client.post(url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _build_request(
        self, service: str, port: int, query: str, intent: IntentResult, context: dict | None
    ) -> tuple[str, dict]:
        base = f"http://{service}:{port}"
        field_id = (context or {}).get("field_id", "")
        tenant_id = (context or {}).get("tenant_id", "")

        routes = {
            AgriIntent.CROP_DISEASE: (
                f"{base}/api/v1/disease/detect",
                {
                    "crop_type": context.get("crop_type", "wheat") if context else "wheat",
                    "description": query,
                },
            ),
            AgriIntent.IRRIGATION: (
                f"{base}/v1/calculate",
                {"field_id": field_id, "query": query},
            ),
            AgriIntent.FERTILIZER: (
                f"{base}/api/v1/advisory/fertilizer",
                {"query": query, "field_id": field_id},
            ),
            AgriIntent.PEST_DETECTION: (
                f"{base}/api/v1/pests/identify/symptoms",
                {
                    "crop": context.get("crop_type", "wheat") if context else "wheat",
                    "symptoms": [query],
                },
            ),
            AgriIntent.WEATHER: (
                f"{base}/weather/forecast",
                {
                    "tenant_id": tenant_id,
                    "field_id": field_id,
                    "lat": 15.37,
                    "lon": 44.19,
                },
            ),
            AgriIntent.MARKET_PRICE: (
                f"{base}/api/v1/marketplace/prices",
                {"query": query},
            ),
            AgriIntent.NDVI_ANALYSIS: (
                f"{base}/v1/indices/{field_id}",
                {},
            ),
        }
        return routes.get(intent.intent, (f"{base}/healthz", {}))

    async def _try_fallback(
        self, service_info: dict, query: str, intent: IntentResult, context: dict | None
    ) -> RouterResult:
        fb_service = service_info["fallback"]
        fb_port = service_info["fallback_port"]
        try:
            response = await self._call_service(fb_service, fb_port, query, intent, context)
            return RouterResult(
                intent=intent.intent,
                response=response,
                service_used=fb_service,
                service_port=fb_port,
                confidence=intent.confidence * 0.8,
                language=intent.language,
            )
        except Exception:
            return await self._fallback_to_rag(query, intent)

    async def _fallback_to_rag(self, query: str, intent: IntentResult) -> RouterResult:
        return RouterResult(
            intent=intent.intent,
            response={"answer": query, "source": "rag_fallback"},
            service_used="copilot-api",
            service_port=8088,
            confidence=0.3,
            language=intent.language,
        )

    async def close(self):
        await self.client.aclose()
