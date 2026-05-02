"""
CRAG-style (Corrective Retrieval-Augmented Generation) knowledge base
backed by Qdrant.

The blocking ``qdrant_client.QdrantClient`` calls are wrapped with
``asyncio.to_thread`` so they don't stall the event loop.

قاعدة معرفة مع تطبيق CRAG (تصحيحي) باستخدام Qdrant للاسترجاع المتجهي.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)

# CRAG decision thresholds — module-level so tests can patch them.
# Heuristics inspired by Yan et al., "Corrective Retrieval Augmented Generation"
# (arXiv:2401.15884): high (>= .70) → trust top hits, mid (>= .40) → widen
# search to recover relevant context, low → fall back to a general collection.
CRAG_CORRECT_THRESHOLD = 0.7
CRAG_AMBIGUOUS_THRESHOLD = 0.4

DEFAULT_COLLECTION = "general_agriculture"

# Pre-provisioned collections (created out-of-band; we only check presence).
KNOWN_COLLECTIONS: list[str] = [
    "crop_knowledge",
    "pest_knowledge",
    "crop_water_requirements",
    "irrigation_practices",
    "soil_knowledge",
    "fertilizer_knowledge",
    "weather_knowledge",
    "remote_sensing_knowledge",
    "smart_agriculture_knowledge",
    "research_references",
    "precision_farming_knowledge",
    "digital_twin_knowledge",
    "general_agriculture",
]


class CragKnowledgeBase:
    """CRAG retriever over Qdrant.

    Strategy in :meth:`retrieve_with_crag`:

    * average top-k score >= 0.7 → CORRECT, return as-is.
    * 0.4 <= average < 0.7    → AMBIGUOUS, widen the search (no filters).
    * average < 0.4           → INCORRECT, fall back to ``general_agriculture``.
    """

    def __init__(
        self,
        qdrant_host: str = "qdrant",
        qdrant_port: int = 6333,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        # Imported lazily so unit tests don't require qdrant-client installed.
        from qdrant_client import QdrantClient  # noqa: PLC0415

        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.default_collection = collection
        self.collections = list(KNOWN_COLLECTIONS)
        self._ensure_collections()

    def _ensure_collections(self) -> None:
        """Warn (don't fail) if any expected collection is missing."""
        try:
            existing = {c.name for c in self.client.get_collections().collections}
            missing = [c for c in self.collections if c not in existing]
            if missing:
                logger.warning(
                    "crag.missing_collections",
                    extra={"missing": missing, "fallback": self.default_collection},
                )
        except Exception as exc:  # noqa: BLE001 — fail open
            logger.error("crag.collections_check_failed", extra={"error": str(exc)})

    async def search(
        self,
        query_embedding: list[float],
        collection: str | None = None,
        limit: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Vector search with optional payload filters.

        The blocking Qdrant call is offloaded via :func:`asyncio.to_thread`.
        """
        from qdrant_client.http.models import (  # noqa: PLC0415
            FieldCondition,
            Filter,
            MatchValue,
        )

        collection_name = collection or self.default_collection
        qdrant_filter = None
        if filters:
            conditions = [FieldCondition(key=key, match=MatchValue(value=value)) for key, value in filters.items()]
            qdrant_filter = Filter(must=conditions)

        try:
            results = await asyncio.to_thread(
                self.client.search,
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=qdrant_filter,
                with_payload=True,
            )
        except Exception as exc:  # noqa: BLE001 — fail open
            logger.error("crag.search_failed", extra={"collection": collection_name, "error": str(exc)})
            return []

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "text": (hit.payload or {}).get("text", ""),
            }
            for hit in results
        ]

    async def retrieve_with_crag(
        self,
        query_text: str,
        embedding_func: Callable[[str], Awaitable[list[float]]],
        collection: str | None = None,
        region: str | None = None,
        crop_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """CRAG-style corrective retrieval.

        Args:
            query_text: free-form natural language query.
            embedding_func: async function ``str -> list[float]``.
            collection: Qdrant collection (defaults to ``self.default_collection``).
            region / crop_type: optional payload filters.
        """
        query_emb = await embedding_func(query_text)
        filters: dict[str, Any] = {}
        if region:
            filters["region"] = region
        if crop_type:
            filters["crop_type"] = crop_type

        initial = await self.search(query_emb, collection=collection, limit=5, filters=filters or None)
        if not initial:
            return []

        avg_score = sum(r["score"] for r in initial) / len(initial)

        if avg_score >= CRAG_CORRECT_THRESHOLD:
            return initial[:3]

        if avg_score >= CRAG_AMBIGUOUS_THRESHOLD:
            expanded = await self.search(query_emb, collection=collection, limit=15)
            expanded.sort(key=lambda x: x["score"], reverse=True)
            return expanded[:5]

        return await self.search(query_emb, collection=DEFAULT_COLLECTION, limit=5)
