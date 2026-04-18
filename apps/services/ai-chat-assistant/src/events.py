"""
NATS event handler for AI chat queries.
معالج أحداث NATS لاستفسارات الشات الذكية.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Optional

from nats.aio.client import Client as NATS

from src.cache import cache_manager
from src.config import settings
from src.llm_client import llm_client
from src.models import AIQuery, AIResponse, ResponseMetadata

logger = logging.getLogger(__name__)


class NATSEventHandler:
    """Handles NATS events for AI chat queries."""

    def __init__(self):
        self.nc: NATS | None = None
        self.subscription = None

    async def connect(self):
        """Connect to NATS server."""
        try:
            self.nc = NATS()
            await self.nc.connect(
                servers=[settings.NATS_URL],
                reconnect_time_wait=settings.NATS_RECONNECT_TIME_WAIT,
                max_reconnect_attempts=settings.NATS_MAX_RECONNECT_ATTEMPTS,
                name="ai-chat-assistant",
            )
            logger.info(f"Connected to NATS: {settings.NATS_URL}")

            # Subscribe to AI query events
            await self.subscribe()

        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise

    async def close(self):
        """Close NATS connection."""
        if self.subscription:
            await self.subscription.unsubscribe()

        if self.nc:
            await self.nc.drain()
            await self.nc.close()
            logger.info("NATS connection closed")

    async def subscribe(self):
        """Subscribe to AI chat query events."""
        if not self.nc:
            raise RuntimeError("NATS not connected")

        # Subscribe to ai_query subject
        self.subscription = await self.nc.subscribe(
            "sahool.chat.ai_query",
            cb=self._handle_ai_query,
        )
        logger.info("Subscribed to sahool.chat.ai_query")

    async def _handle_ai_query(self, msg):
        """
        Handle incoming AI query event from chat service.

        Args:
            msg: NATS message containing AI query
        """
        start_time = datetime.now(UTC)

        try:
            # Parse message data
            data = json.loads(msg.data.decode())

            # Extract tenant_id from NATS message subject or headers if not in payload
            if "tenant_id" not in data or not data.get("tenant_id"):
                # Try to extract from subject pattern: sahool.tenant.{tenant_id}.chat.ai_query
                subject = msg.subject
                parts = subject.split(".")
                if len(parts) >= 4 and parts[1] == "tenant":
                    data["tenant_id"] = parts[2]

            query = AIQuery(**data)

            # Validate tenant_id presence for multi-tenant isolation
            if not query.tenant_id:
                logger.warning(
                    f"Missing tenant_id in AI query from user {query.user_id}, "
                    f"conversation {query.conversation_id}. Rejecting for tenant isolation."
                )
                raise ValueError("tenant_id is required for tenant isolation")

            logger.info(
                f"Received AI query from user {query.user_id} "
                f"(tenant: {query.tenant_id}): {query.query[:50]}... (lang: {query.language})"
            )

            # Process query
            response = await self._process_query(query)

            # Publish response (tenant-scoped)
            await self._publish_response(response, tenant_id=query.tenant_id)

            # Log processing time
            total_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            logger.info(
                f"Processed query in {total_time_ms}ms "
                f"(cached: {response.metadata.cached}, "
                f"confidence: {response.metadata.confidence:.2f})"
            )

        except Exception as e:
            logger.error(f"Error handling AI query: {e}", exc_info=True)

            # Send error response back to chat so the user isn't left waiting
            try:
                conversation_id = "unknown"
                try:
                    data = json.loads(msg.data.decode())
                    conversation_id = data.get("conversation_id", "unknown")
                except Exception:
                    pass  # Best-effort extraction of conversation_id from malformed message

                total_time_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
                error_response = AIResponse(
                    conversation_id=conversation_id,
                    answer="عذراً، حدث خطأ أثناء معالجة استفسارك. يرجى المحاولة مرة أخرى.",
                    answer_en="Sorry, an error occurred while processing your query. Please try again.",
                    metadata=ResponseMetadata(
                        confidence=0.0,
                        agents_used=[],
                        processing_time_ms=total_time_ms,
                        cached=False,
                        should_escalate=True,
                        escalation_reason=f"Processing error: {type(e).__name__}",
                    ),
                )
                await self._publish_response(error_response, tenant_id=query.tenant_id)
            except Exception as publish_err:
                logger.error(f"Failed to publish error response: {publish_err}")

    async def _process_query(self, query: AIQuery) -> AIResponse:
        """
        Process AI query with caching and LLM orchestration.

        Args:
            query: Parsed AI query

        Returns:
            AI response with answer and metadata
        """
        # Step 1: Check cache (tenant-scoped)
        cached = await cache_manager.get(
            query=query.query,
            language=query.language,
            field_id=query.field_id,
            tenant_id=query.tenant_id,
        )

        if cached:
            # Cache hit - use cached response
            return AIResponse(
                conversation_id=query.conversation_id,
                answer=cached.answer,
                answer_en=cached.answer_en,
                metadata=cached.metadata,
            )

        # Step 2: Cache miss - call LLM orchestrator
        result = await llm_client.orchestrate(
            query=query.query,
            language=query.language,
            field_id=query.field_id,
            context=query.context,
        )

        # Step 3: Cache the response (tenant-scoped)
        await cache_manager.set(
            query=query.query,
            language=query.language,
            answer=result["answer"],
            answer_en=result.get("answer_en"),
            metadata=result["metadata"],
            field_id=query.field_id,
            tenant_id=query.tenant_id,
        )

        # Step 4: Return response
        return AIResponse(
            conversation_id=query.conversation_id,
            answer=result["answer"],
            answer_en=result.get("answer_en"),
            metadata=result["metadata"],
        )

    async def _publish_response(self, response: AIResponse, tenant_id: str | None = None):
        """
        Publish AI response back to chat service.

        Args:
            response: AI response to publish
            tenant_id: Tenant that owns the conversation. Required for tenant-
                scoped NATS subjects; falls back to "unknown" if missing so
                the publish doesn't silently leak across tenants.
        """
        if not self.nc:
            raise RuntimeError("NATS not connected")

        try:
            # Serialize response
            response_data = response.model_dump_json()

            try:
                from shared.events.subjects import get_tenant_subject

                _subject = get_tenant_subject(tenant_id or "unknown", "chat", "ai_response")
            except ImportError:
                _subject = f"sahool.tenant.{tenant_id or 'unknown'}.chat.ai_response"

            # Publish to response subject (tenant-scoped)
            await self.nc.publish(
                _subject,
                response_data.encode(),
            )

            logger.info(f"Published AI response for conversation {response.conversation_id}")

        except Exception as e:
            logger.error(f"Error publishing response: {e}")
            raise

    async def is_connected(self) -> bool:
        """Check if NATS is connected."""
        return self.nc is not None and self.nc.is_connected


# Global event handler instance
event_handler = NATSEventHandler()
