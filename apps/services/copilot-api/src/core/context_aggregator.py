"""
Agricultural Context Aggregator
مجمّع السياق الزراعي

Gathers: RAG knowledge + expert rules + field sensor data + weather
into a unified context for LLM generation.

Phase 4 of Component Unification Plan (PR #1344)
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()


@dataclass
class AggregatedContext:
    query: str
    field_id: str | None
    tenant_id: str
    rag_results: list[dict] = field(default_factory=list)
    weather_data: dict | None = None
    field_data: dict | None = None
    soil_data: dict | None = None
    advisory_rules: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        """Build context string for LLM prompt"""
        sections = []
        if self.field_data:
            sections.append(
                f"[Field Data] NDVI: {self.field_data.get('ndvi', 'N/A')}, "
                f"Crop: {self.field_data.get('crop_type', 'N/A')}, "
                f"Stage: {self.field_data.get('growth_stage', 'N/A')}, "
                f"Area: {self.field_data.get('area', 'N/A')} ha"
            )
        if self.weather_data:
            forecast = self.weather_data.get("forecast", [{}])
            if forecast:
                today = forecast[0] if isinstance(forecast, list) else forecast
                sections.append(
                    f"[Weather] Temp: {today.get('temp_max_c', 'N/A')}°C, "
                    f"Rain: {today.get('precipitation_mm', 0)}mm, "
                    f"Humidity: {today.get('humidity', 'N/A')}%"
                )
        if self.soil_data:
            sections.append(
                f"[Soil] pH: {self.soil_data.get('ph', 'N/A')}, "
                f"EC: {self.soil_data.get('ec', 'N/A')} dS/m, "
                f"N: {self.soil_data.get('nitrogen', 'N/A')} ppm"
            )
        if self.rag_results:
            top_results = self.rag_results[:3]
            for i, r in enumerate(top_results, 1):
                sections.append(f"[Knowledge {i}] {r.get('content', '')[:200]}")
        if self.advisory_rules:
            sections.append(f"[Rules] {'; '.join(self.advisory_rules[:5])}")
        return "\n".join(sections) if sections else "[No additional context available]"


class AgriContextAggregator:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def build_context(self, query: str, field_id: str | None, tenant_id: str) -> AggregatedContext:
        ctx = AggregatedContext(query=query, field_id=field_id, tenant_id=tenant_id)
        tasks = {}
        if field_id:
            tasks["field"] = self._get_field_data(field_id, tenant_id)
            tasks["weather"] = self._get_weather(field_id, tenant_id)
            tasks["soil"] = self._get_soil_data(field_id, tenant_id)
        tasks["rag"] = self._search_rag(query)

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for key, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                ctx.errors.append(f"{key}: {str(result)}")
                logger.warning("context_fetch_failed", source=key, error=str(result))
            elif key == "field":
                ctx.field_data = result
            elif key == "weather":
                ctx.weather_data = result
            elif key == "soil":
                ctx.soil_data = result
            elif key == "rag":
                ctx.rag_results = result if isinstance(result, list) else []
        return ctx

    async def _get_field_data(self, field_id: str, tenant_id: str) -> dict:
        resp = await self.client.get(
            f"http://field-management-service:3000/api/v1/fields/{field_id}", headers={"X-Tenant-Id": tenant_id}
        )
        resp.raise_for_status()
        return resp.json().get("data", resp.json())

    async def _get_weather(self, field_id: str, tenant_id: str, lat: float = 15.37, lon: float = 44.19) -> dict:
        resp = await self.client.post(
            "http://weather-service:8092/weather/forecast",
            json={"tenant_id": tenant_id, "field_id": field_id, "lat": lat, "lon": lon},
            params={"days": 3},
        )
        resp.raise_for_status()
        return resp.json()

    async def _get_soil_data(self, field_id: str, tenant_id: str) -> dict:
        resp = await self.client.get(
            f"http://soil-analysis-service:8134/tests/field/{field_id}", headers={"X-Tenant-Id": tenant_id}
        )
        resp.raise_for_status()
        data = resp.json()
        tests = data.get("tests", [])
        return tests[0] if tests else {}

    async def _search_rag(self, query: str) -> list[dict]:
        try:
            # TODO: real embeddings should come from the RAG pipeline
            resp = await self.client.post(
                "http://qdrant:6333/collections/sahool_knowledge/points/search",
                json={"vector": [0.0] * 384, "limit": 3, "with_payload": True},
            )
            resp.raise_for_status()
            return [{"content": r.get("payload", {}).get("content", "")} for r in resp.json().get("result", [])]
        except Exception:
            return []

    async def close(self):
        await self.client.aclose()
