"""
Chat Event Publisher
NATS JetStream publisher for chat events
"""

import os
import json
import logging
from uuid import uuid4
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

import nats
from nats.aio.client import Client as NATS

from .types import (
    SUBJECTS,
    CHAT_THREAD_CREATED,
    CHAT_MESSAGE_SENT,
    CHAT_MESSAGE_EDITED,
    CHAT_PARTICIPANT_JOINED,
    CHAT_PARTICIPANT_LEFT,
    CHAT_THREAD_ARCHIVED,
    CHAT_MESSAGES_READ,
)

logger = logging.getLogger(__name__)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


@dataclass
class EventEnvelope:
    """Standard event envelope"""

    event_id: str
    event_type: str
    version: int
    aggregate_id: str
    tenant_id: str
    correlation_id: str
    timestamp: str
    payload: dict

    @classmethod
    def create(
        cls,
        event_type: str,
        version: int,
        aggregate_id: str,
        tenant_id: str,
        correlation_id: str,
        payload: dict,
    ) -> "EventEnvelope":
        return cls(
            event_id=str(uuid4()),
            event_type=event_type,
            version=version,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            payload=payload,
        )


class ChatPublisher:
    """Publisher for chat events to NATS JetStream"""

    def __init__(self):
        self.nc: Optional[NATS] = None
        self.js = None

    async def connect(self):
        """Connect to NATS server"""
        if self.nc is None or not self.nc.is_connected:
            self.nc = await nats.connect(NATS_URL)
            self.js = self.nc.jetstream()
            logger.info(f"Connected to NATS at {NATS_URL}")

    async def close(self):
        """Close NATS connection"""
        if self.nc and self.nc.is_connected:
            await self.nc.close()
            logger.info("NATS connection closed")

    async def _publish(
        self,
        subject: str,
        event_type: str,
        tenant_id: str,
        aggregate_id: str,
        correlation_id: str,
        payload: dict,
    ):
        """Internal publish method"""
        await self.connect()

        envelope = EventEnvelope.create(
            event_type=event_type,
            version=1,
            aggregate_id=aggregate_id,
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            payload=payload,
        )

        data = json.dumps(asdict(envelope), default=str).encode()

        try:
            await self.nc.publish(subject, data)
            logger.info(f"Published {event_type} to {subject}")
        except Exception as e:
            logger.error(f"Failed to publish {event_type}: {e}")
            raise

    # ─────────────────────────────────────────────────────────────
    # Thread Events
    # ─────────────────────────────────────────────────────────────

    async def publish_thread_created(
        self,
        tenant_id: str,
        thread_id: str,
        scope_type: str,
        scope_id: str,
        created_by: str,
        title: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_thread_created event"""
        await self._publish(
            subject=SUBJECTS[CHAT_THREAD_CREATED],
            event_type=CHAT_THREAD_CREATED,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "scope_type": scope_type,
                "scope_id": scope_id,
                "created_by": created_by,
                "title": title,
            },
        )

    async def publish_thread_archived(
        self,
        tenant_id: str,
        thread_id: str,
        archived_by: str,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_thread_archived event"""
        await self._publish(
            subject=SUBJECTS[CHAT_THREAD_ARCHIVED],
            event_type=CHAT_THREAD_ARCHIVED,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "archived_by": archived_by,
            },
        )

    # ─────────────────────────────────────────────────────────────
    # Message Events
    # ─────────────────────────────────────────────────────────────

    async def publish_message_sent(
        self,
        tenant_id: str,
        thread_id: str,
        message_id: str,
        sender_id: str,
        text: Optional[str] = None,
        attachments: Optional[list[str]] = None,
        reply_to_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_message_sent event"""
        await self._publish(
            subject=SUBJECTS[CHAT_MESSAGE_SENT],
            event_type=CHAT_MESSAGE_SENT,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "message_id": message_id,
                "sender_id": sender_id,
                "text": text or "",
                "attachments": attachments or [],
                "reply_to_id": reply_to_id,
            },
        )

    async def publish_message_edited(
        self,
        tenant_id: str,
        thread_id: str,
        message_id: str,
        edited_by: str,
        new_text: str,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_message_edited event"""
        await self._publish(
            subject=SUBJECTS[CHAT_MESSAGE_EDITED],
            event_type=CHAT_MESSAGE_EDITED,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "message_id": message_id,
                "edited_by": edited_by,
                "new_text": new_text,
            },
        )

    # ─────────────────────────────────────────────────────────────
    # Participant Events
    # ─────────────────────────────────────────────────────────────

    async def publish_participant_joined(
        self,
        tenant_id: str,
        thread_id: str,
        user_id: str,
        added_by: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_participant_joined event"""
        await self._publish(
            subject=SUBJECTS[CHAT_PARTICIPANT_JOINED],
            event_type=CHAT_PARTICIPANT_JOINED,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "user_id": user_id,
                "added_by": added_by,
            },
        )

    async def publish_participant_left(
        self,
        tenant_id: str,
        thread_id: str,
        user_id: str,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_participant_left event"""
        await self._publish(
            subject=SUBJECTS[CHAT_PARTICIPANT_LEFT],
            event_type=CHAT_PARTICIPANT_LEFT,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "user_id": user_id,
            },
        )

    # ─────────────────────────────────────────────────────────────
    # Read Receipt Events
    # ─────────────────────────────────────────────────────────────

    async def publish_messages_read(
        self,
        tenant_id: str,
        thread_id: str,
        user_id: str,
        last_read_message_id: str,
        correlation_id: Optional[str] = None,
    ):
        """Publish chat_messages_read event"""
        await self._publish(
            subject=SUBJECTS[CHAT_MESSAGES_READ],
            event_type=CHAT_MESSAGES_READ,
            tenant_id=tenant_id,
            aggregate_id=thread_id,
            correlation_id=correlation_id or str(uuid4()),
            payload={
                "thread_id": thread_id,
                "user_id": user_id,
                "last_read_message_id": last_read_message_id,
            },
        )
