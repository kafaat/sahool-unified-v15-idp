"""
Message Bus
===========
ناقل الرسائل

NATS JetStream-backed message bus for OpenMultiAgent framework.
Provides publish/subscribe, request/reply, and team broadcast patterns.

Features:
- NATS JetStream integration for durable messaging
- Graceful fallback to in-memory pub/sub when NATS is unavailable
- Subject pattern: sahool.agent.{team_id}.{event}
- Team broadcast for multi-agent coordination
- Async-first API with structlog instrumentation

المميزات:
- تكامل مع NATS JetStream للرسائل المتينة
- تراجع سلس إلى ناقل رسائل داخلي عند عدم توفر NATS
- نمط الموضوع: sahool.agent.{team_id}.{event}
- بث للفريق لتنسيق الوكلاء المتعددين
- واجهة برمجة غير متزامنة مع أدوات structlog

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
import json
import os
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Constants & Events
# ─────────────────────────────────────────────────────────────────────────────

SUBJECT_PREFIX = "sahool.agent"


class AgentEvent(StrEnum):
    """
    Standard agent lifecycle events.
    أحداث دورة حياة الوكيل القياسية
    """

    TASK_ASSIGNED = "task_assigned"  # مهمة مُعيّنة
    TASK_COMPLETED = "task_completed"  # مهمة مكتملة
    TASK_FAILED = "task_failed"  # مهمة فاشلة
    AGENT_READY = "agent_ready"  # وكيل جاهز
    AGENT_BUSY = "agent_busy"  # وكيل مشغول


def build_subject(team_id: str, event: str) -> str:
    """
    Build a NATS subject for agent events.
    بناء موضوع NATS لأحداث الوكيل

    Pattern: sahool.agent.{team_id}.{event}

    Args:
        team_id: معرف الفريق - Team identifier
        event: الحدث - Event name

    Returns:
        str: Full NATS subject string
    """
    return f"{SUBJECT_PREFIX}.{team_id}.{event}"


# ─────────────────────────────────────────────────────────────────────────────
# In-Memory Fallback Bus
# ─────────────────────────────────────────────────────────────────────────────


class _InMemoryBus:
    """
    Simple in-memory pub/sub fallback when NATS is unavailable.
    ناقل رسائل داخلي بسيط عند عدم توفر NATS
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)
        self._pending_requests: dict[str, asyncio.Future] = {}

    async def publish(self, subject: str, data: bytes) -> None:
        """Publish to in-memory subscribers."""
        handlers = self._handlers.get(subject, [])
        # Also match wildcard subscribers
        parts = subject.rsplit(".", 1)
        if len(parts) == 2:
            wildcard = parts[0] + ".*"
            handlers = handlers + self._handlers.get(wildcard, [])

        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.warning("inmemory_handler_error", subject=subject, error=str(e))

        # Check for pending request/reply
        if subject in self._pending_requests:
            fut = self._pending_requests.pop(subject)
            if not fut.done():
                fut.set_result(data)

    def subscribe(self, subject: str, handler: Callable) -> None:
        """Subscribe to in-memory topic."""
        self._handlers[subject].append(handler)

    async def request(self, subject: str, data: bytes, timeout: float) -> bytes:
        """Request/reply over in-memory bus."""
        reply_subject = f"_reply.{uuid4().hex[:12]}"
        loop = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending_requests[reply_subject] = fut

        # Publish with reply subject embedded
        payload = json.loads(data)
        payload["_reply_to"] = reply_subject
        await self.publish(subject, json.dumps(payload).encode())

        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
            return result if isinstance(result, bytes) else result.encode()
        except asyncio.TimeoutError:
            self._pending_requests.pop(reply_subject, None)
            raise

    def clear(self) -> None:
        """Clear all subscriptions."""
        self._handlers.clear()
        self._pending_requests.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Message Bus
# ─────────────────────────────────────────────────────────────────────────────


class MessageBus:
    """
    NATS JetStream message bus for OpenMultiAgent.
    ناقل رسائل NATS JetStream لـ OpenMultiAgent

    Provides pub/sub, request/reply, and broadcast patterns for
    agent-to-agent communication. Falls back to an in-memory bus
    when NATS is unavailable.

    يوفر أنماط النشر/الاشتراك، الطلب/الرد، والبث لاتصال
    الوكيل بالوكيل. يتراجع إلى ناقل داخلي عند عدم توفر NATS.

    Example:
        >>> bus = MessageBus()
        >>> await bus.connect()
        >>> await bus.publish("sahool.agent.team1.task_assigned", {"task_id": "t1"})
        >>> await bus.broadcast("team1", {"type": "sync", "data": {}})
        >>> await bus.close()
    """

    def __init__(self) -> None:
        self.nc: Any = None  # nats.Client
        self.js: Any = None  # JetStream context
        self._connected = False
        self._subscriptions: list[Any] = []
        self._fallback = _InMemoryBus()

    # ─────────────────────────────────────────────────────────────────────────
    # Connection Lifecycle
    # ─────────────────────────────────────────────────────────────────────────

    async def connect(self, nats_url: str = "nats://nats:4222") -> None:
        """
        Connect to NATS server and initialize JetStream.
        الاتصال بخادم NATS وتهيئة JetStream

        Falls back to in-memory bus if connection fails.

        Args:
            nats_url: رابط NATS - NATS server URL (defaults to env NATS_URL)
        """
        url = os.getenv("NATS_URL", nats_url)

        try:
            import nats as nats_lib

            self.nc = await nats_lib.connect(
                url,
                max_reconnect_attempts=3,
                reconnect_time_wait=2,
            )
            self.js = self.nc.jetstream()

            # Ensure stream exists for agent events
            try:
                await self.js.find_stream_by_subject(f"{SUBJECT_PREFIX}.>")
            except Exception:
                await self.js.add_stream(
                    name="SAHOOL_AGENT",
                    subjects=[f"{SUBJECT_PREFIX}.>"],
                    retention="limits",
                    max_age=86400,  # 24 hours
                )

            self._connected = True
            logger.info("message_bus_connected", url=url)

        except Exception as e:
            self._connected = False
            self.nc = None
            self.js = None
            logger.warning(
                "message_bus_nats_fallback",
                error=str(e),
                mode="in_memory",
            )

    async def close(self) -> None:
        """
        Close NATS connection and clean up subscriptions.
        إغلاق اتصال NATS وتنظيف الاشتراكات
        """
        for sub in self._subscriptions:
            try:
                await sub.unsubscribe()
            except Exception:
                pass
        self._subscriptions.clear()

        if self.nc is not None:
            try:
                await self.nc.close()
            except Exception:
                pass
            self.nc = None
            self.js = None

        self._connected = False
        self._fallback.clear()
        logger.info("message_bus_closed")

    # ─────────────────────────────────────────────────────────────────────────
    # Publish / Subscribe
    # ─────────────────────────────────────────────────────────────────────────

    async def publish(self, subject: str, data: dict) -> None:
        """
        Publish a message to a subject.
        نشر رسالة إلى موضوع

        Args:
            subject: الموضوع - NATS subject (e.g. sahool.agent.team1.task_assigned)
            data: البيانات - Message payload (dict, will be JSON-encoded)
        """
        payload = self._encode(data)

        if self._connected and self.js is not None:
            try:
                await self.js.publish(subject, payload)
                logger.debug("message_bus_published", subject=subject)
                return
            except Exception as e:
                logger.warning("message_bus_publish_nats_failed", subject=subject, error=str(e))

        # Fallback to in-memory
        await self._fallback.publish(subject, payload)
        logger.debug("message_bus_published_inmemory", subject=subject)

    async def subscribe(self, subject: str, handler: Callable) -> None:
        """
        Subscribe to a subject with a message handler.
        الاشتراك في موضوع مع معالج رسائل

        The handler receives the decoded dict payload.

        Args:
            subject: الموضوع - NATS subject pattern (supports wildcards like *)
            handler: المعالج - Async callable(data: dict) -> None
        """

        async def _nats_wrapper(msg: Any) -> None:
            """Decode NATS message and call handler."""
            try:
                data = json.loads(msg.data.decode())
                await handler(data)
            except Exception as e:
                logger.warning("message_bus_handler_error", subject=subject, error=str(e))

        async def _inmemory_wrapper(raw: bytes) -> None:
            """Decode in-memory message and call handler."""
            try:
                data = json.loads(raw.decode() if isinstance(raw, bytes) else raw)
                await handler(data)
            except Exception as e:
                logger.warning("message_bus_handler_error", subject=subject, error=str(e))

        if self._connected and self.nc is not None:
            try:
                sub = await self.nc.subscribe(subject, cb=_nats_wrapper)
                self._subscriptions.append(sub)
                logger.debug("message_bus_subscribed", subject=subject)
                return
            except Exception as e:
                logger.warning("message_bus_subscribe_nats_failed", subject=subject, error=str(e))

        # Fallback to in-memory
        self._fallback.subscribe(subject, _inmemory_wrapper)
        logger.debug("message_bus_subscribed_inmemory", subject=subject)

    # ─────────────────────────────────────────────────────────────────────────
    # Request / Reply
    # ─────────────────────────────────────────────────────────────────────────

    async def request(
        self,
        subject: str,
        data: dict,
        timeout: float = 30.0,
    ) -> dict:
        """
        Send a request and wait for a reply.
        إرسال طلب وانتظار الرد

        Args:
            subject: الموضوع - NATS subject
            data: البيانات - Request payload
            timeout: المهلة - Timeout in seconds

        Returns:
            dict: Reply payload

        Raises:
            asyncio.TimeoutError: If no reply within timeout
        """
        payload = self._encode(data)

        if self._connected and self.nc is not None:
            try:
                response = await self.nc.request(subject, payload, timeout=timeout)
                return json.loads(response.data.decode())
            except Exception as e:
                if "timeout" in str(e).lower():
                    raise asyncio.TimeoutError(f"Request to {subject} timed out after {timeout}s") from e
                logger.warning("message_bus_request_nats_failed", subject=subject, error=str(e))

        # Fallback to in-memory
        result = await self._fallback.request(subject, payload, timeout)
        return json.loads(result.decode() if isinstance(result, bytes) else result)

    # ─────────────────────────────────────────────────────────────────────────
    # Team Broadcast
    # ─────────────────────────────────────────────────────────────────────────

    async def broadcast(self, team_id: str, message: dict) -> None:
        """
        Broadcast a message to all agents in a team.
        بث رسالة إلى جميع الوكلاء في فريق

        Publishes to: sahool.agent.{team_id}.broadcast

        Args:
            team_id: معرف الفريق - Team identifier
            message: الرسالة - Message payload
        """
        subject = build_subject(team_id, "broadcast")
        enriched = {
            **message,
            "_broadcast": True,
            "_team_id": team_id,
            "_timestamp": datetime.now(UTC).isoformat(),
        }
        await self.publish(subject, enriched)
        logger.debug("message_bus_broadcast", team_id=team_id)

    # ─────────────────────────────────────────────────────────────────────────
    # Utility
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        """Check if NATS is connected. | التحقق من اتصال NATS"""
        return self._connected

    def _encode(self, data: dict) -> bytes:
        """Encode dict to JSON bytes."""
        return json.dumps(data, default=str).encode()
