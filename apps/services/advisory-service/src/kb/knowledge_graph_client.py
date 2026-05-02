"""
HTTP client for the SAHOOL ``knowledge-graph`` service.

Communicates with knowledge-graph at port 8140 over its REST API.
عميل HTTP للتواصل مع خدمة knowledge-graph.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 10.0


class KnowledgeGraphClient:
    """Async client over the knowledge-graph REST API.

    All methods are best-effort: network/parse errors are logged and
    return an empty value (``None`` / ``[]`` / ``{}``) rather than raising,
    so the caller can degrade gracefully.
    """

    def __init__(
        self,
        base_url: str = "http://knowledge-graph:8140/api/v1",
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self.client.aclose()

    # ---------- Entity reads -------------------------------------------------

    async def _get_entity(self, kind: str, entity_id: str) -> dict[str, Any] | None:
        try:
            resp = await self.client.get(f"{self.base_url}/entities/{kind}/{entity_id}")
            if resp.status_code == 200:
                return resp.json().get("data")
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("kg.get_entity_error", extra={"kind": kind, "id": entity_id, "error": str(exc)})
        return None

    async def get_crop(self, crop_id: str) -> dict[str, Any] | None:
        return await self._get_entity("crops", crop_id)

    async def get_disease(self, disease_id: str) -> dict[str, Any] | None:
        return await self._get_entity("diseases", disease_id)

    async def get_treatment(self, treatment_id: str) -> dict[str, Any] | None:
        return await self._get_entity("treatments", treatment_id)

    # ---------- Relationships ------------------------------------------------

    async def _get_relation(self, path: str) -> list[dict[str, Any]]:
        try:
            resp = await self.client.get(f"{self.base_url}/{path.lstrip('/')}")
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return data if isinstance(data, list) else []
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("kg.relation_error", extra={"path": path, "error": str(exc)})
        return []

    async def get_disease_treatments(self, disease_id: str) -> list[dict[str, Any]]:
        return await self._get_relation(f"relationships/disease-treatments/{disease_id}")

    async def get_affected_crops(self, disease_id: str) -> list[dict[str, Any]]:
        return await self._get_relation(f"relationships/affected-crops/{disease_id}")

    async def find_path(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
    ) -> dict[str, Any] | None:
        path = f"relationships/path/{source_type}/{source_id}/{target_type}/{target_id}"
        try:
            resp = await self.client.get(f"{self.base_url}/{path}")
            if resp.status_code == 200:
                return resp.json().get("data")
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("kg.find_path_error", extra={"path": path, "error": str(exc)})
        return None

    # ---------- Search & stats ----------------------------------------------

    async def search_entities(
        self,
        query: str,
        entity_type: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        try:
            params: dict[str, Any] = {"q": query, "limit": limit}
            if entity_type:
                params["entity_type"] = entity_type
            resp = await self.client.get(f"{self.base_url}/entities/search", params=params)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                return data if isinstance(data, list) else []
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("kg.search_error", extra={"query": query, "error": str(exc)})
        return []

    async def get_graph_stats(self) -> dict[str, Any]:
        try:
            resp = await self.client.get(f"{self.base_url}/graphs/stats")
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                return data if isinstance(data, dict) else {}
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("kg.stats_error", extra={"error": str(exc)})
        return {}
