"""
LLM Orchestrator client for routing queries to AI agents.
عميل تنسيق LLM لتوجيه الاستفسارات إلى وكلاء الذكاء الاصطناعي.
"""

import logging
from typing import Optional, List, Dict, Any
import httpx
from datetime import UTC, datetime

from src.config import settings
from src.models import ResponseMetadata

logger = logging.getLogger(__name__)


class LLMOrchestratorClient:
    """Client for LLM Orchestrator service."""

    def __init__(self):
        self.base_url = settings.LLM_ORCHESTRATOR_URL
        self.timeout = settings.LLM_ORCHESTRATOR_TIMEOUT
        self.client: httpx.AsyncClient | None = None

    async def connect(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
        )
        logger.info(f"LLM Orchestrator client initialized: {self.base_url}")

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            logger.info("LLM Orchestrator client closed")

    async def orchestrate(
        self,
        query: str,
        language: str = "ar",
        field_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send query to LLM orchestrator for processing.

        Args:
            query: User question
            language: Query language (ar/en)
            field_id: Optional field ID for context
            context: Additional context dictionary

        Returns:
            Dict with answer and metadata
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call connect() first.")

        start_time = datetime.now(UTC)

        try:
            # Prepare request payload
            payload = {
                "text": query,
                "language": language,
            }

            if field_id:
                payload["field_id"] = field_id

            if context:
                payload["context"] = context

            # Make request to orchestrator
            response = await self.client.post(
                "/api/v1/orchestrate",
                json=payload,
            )
            response.raise_for_status()

            # Parse response
            data = response.json()

            # Calculate processing time
            processing_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

            # Extract metadata
            metadata = self._extract_metadata(data, processing_time_ms)

            logger.info(
                f"Orchestrated query (intent: {metadata.intent}, "
                f"confidence: {metadata.confidence:.2f}, "
                f"time: {processing_time_ms}ms)"
            )

            return {
                "answer": data.get("answer", ""),
                "answer_en": data.get("answer_en"),
                "metadata": metadata,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from orchestrator: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error to orchestrator: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling orchestrator: {e}")
            raise

    def _extract_metadata(self, data: dict[str, Any], processing_time_ms: int) -> ResponseMetadata:
        """Extract response metadata from orchestrator response."""

        # Get confidence score
        confidence = data.get("confidence", 0.0)
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except ValueError:
                confidence = 0.0

        # Normalize to 0-1 range
        if confidence > 1.0:
            confidence = confidence / 100.0

        # Get agents used
        agents_used = data.get("agents_used", [])
        if not isinstance(agents_used, list):
            agents_used = []

        # Get intent
        intent = data.get("intent", "unknown")

        # Determine if should escalate
        should_escalate = confidence < settings.MIN_CONFIDENCE_THRESHOLD
        escalation_reason = None

        if should_escalate:
            escalation_reason = f"Low confidence score: {confidence:.2f} < {settings.MIN_CONFIDENCE_THRESHOLD}"

        # Check for critical topics
        critical_keywords = ["pesticide", "مبيد", "herbicide", "insecticide", "سم"]
        query_lower = data.get("query", "").lower()

        if any(keyword in query_lower for keyword in critical_keywords):
            should_escalate = True
            if not escalation_reason:
                escalation_reason = "Critical topic detected (pesticides/chemicals)"

        return ResponseMetadata(
            confidence=confidence,
            agents_used=agents_used,
            processing_time_ms=processing_time_ms,
            cached=False,
            intent=intent,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
        )

    async def health_check(self) -> bool:
        """Check if orchestrator service is healthy."""
        try:
            if not self.client:
                return False

            response = await self.client.get("/healthz", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global client instance
llm_client = LLMOrchestratorClient()
