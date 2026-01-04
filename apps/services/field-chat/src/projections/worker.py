"""
Chat Projection Worker
Subscribes to chat events and updates read models / broadcasts to WebSockets
"""

import asyncio
import contextlib
import json
import logging
import os
from collections.abc import Callable
from typing import Any

import nats
from nats.aio.client import Client as NATS

from ..events.types import (
    CHAT_MESSAGE_EDITED,
    CHAT_MESSAGE_SENT,
    CHAT_MESSAGES_READ,
    CHAT_PARTICIPANT_JOINED,
    CHAT_PARTICIPANT_LEFT,
    CHAT_THREAD_CREATED,
    SUBJECTS,
)

logger = logging.getLogger(__name__)

NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")


class ChatProjectionWorker:
    """
    Worker that subscribes to chat events and:
    1. Updates read models (denormalized tables)
    2. Broadcasts to WebSocket clients
    3. Triggers notifications
    """

    def __init__(self, broadcast_callback: Callable[[str, dict], Any] | None = None):
        self.nc: NATS | None = None
        self.js = None
        self.subscriptions = []
        self.running = False
        self.broadcast_callback = broadcast_callback

    async def connect(self):
        """Connect to NATS"""
        if self.nc is None or not self.nc.is_connected:
            self.nc = await nats.connect(NATS_URL)
            self.js = self.nc.jetstream()
            logger.info(f"Chat projection worker connected to NATS at {NATS_URL}")

    async def close(self):
        """Close NATS connection"""
        self.running = False
        for sub in self.subscriptions:
            with contextlib.suppress(Exception):
                await sub.unsubscribe()
        if self.nc and self.nc.is_connected:
            await self.nc.close()
            logger.info("Chat projection worker disconnected")

    async def start(self):
        """Start the projection worker"""
        await self.connect()
        self.running = True

        # Subscribe to all chat events
        event_handlers = {
            SUBJECTS[CHAT_THREAD_CREATED]: self._handle_thread_created,
            SUBJECTS[CHAT_MESSAGE_SENT]: self._handle_message_sent,
            SUBJECTS[CHAT_MESSAGE_EDITED]: self._handle_message_edited,
            SUBJECTS[CHAT_PARTICIPANT_JOINED]: self._handle_participant_joined,
            SUBJECTS[CHAT_PARTICIPANT_LEFT]: self._handle_participant_left,
            SUBJECTS[CHAT_MESSAGES_READ]: self._handle_messages_read,
        }

        for subject, handler in event_handlers.items():
            try:
                sub = await self.nc.subscribe(subject, cb=handler)
                self.subscriptions.append(sub)
                logger.info(f"Subscribed to {subject}")
            except Exception as e:
                logger.error(f"Failed to subscribe to {subject}: {e}")

        logger.info("Chat projection worker started")

        # Keep running
        while self.running:
            await asyncio.sleep(1)

    # ─────────────────────────────────────────────────────────────────────────
    # Event Handlers
    # ─────────────────────────────────────────────────────────────────────────

    async def _handle_thread_created(self, msg):
        """Handle chat_thread_created event"""
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            thread_id = payload.get("thread_id")

            logger.info(f"Thread created: {thread_id}")

            # Broadcast to subscribers
            await self._broadcast(
                thread_id,
                {
                    "type": "thread_created",
                    "thread_id": thread_id,
                    "scope_type": payload.get("scope_type"),
                    "scope_id": payload.get("scope_id"),
                    "created_by": payload.get("created_by"),
                    "timestamp": data.get("timestamp"),
                },
            )

        except Exception as e:
            logger.error(f"Error handling thread_created: {e}")

    async def _handle_message_sent(self, msg):
        """Handle chat_message_sent event"""
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            thread_id = payload.get("thread_id")
            message_id = payload.get("message_id")

            logger.info(f"Message sent: {message_id} in thread {thread_id}")

            # Broadcast to WebSocket clients
            await self._broadcast(
                thread_id,
                {
                    "type": "new_message",
                    "thread_id": thread_id,
                    "message_id": message_id,
                    "sender_id": payload.get("sender_id"),
                    "text": payload.get("text"),
                    "attachments": payload.get("attachments", []),
                    "reply_to_id": payload.get("reply_to_id"),
                    "timestamp": data.get("timestamp"),
                },
            )

            # Could trigger push notifications here
            await self._trigger_notifications(
                thread_id=thread_id,
                sender_id=payload.get("sender_id"),
                message_preview=self._truncate(payload.get("text", ""), 100),
            )

        except Exception as e:
            logger.error(f"Error handling message_sent: {e}")

    async def _handle_message_edited(self, msg):
        """Handle chat_message_edited event"""
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            thread_id = payload.get("thread_id")

            logger.info(
                f"Message edited: {payload.get('message_id')} in thread {thread_id}"
            )

            await self._broadcast(
                thread_id,
                {
                    "type": "message_edited",
                    "thread_id": thread_id,
                    "message_id": payload.get("message_id"),
                    "edited_by": payload.get("edited_by"),
                    "new_text": payload.get("new_text"),
                    "timestamp": data.get("timestamp"),
                },
            )

        except Exception as e:
            logger.error(f"Error handling message_edited: {e}")

    async def _handle_participant_joined(self, msg):
        """Handle chat_participant_joined event"""
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            thread_id = payload.get("thread_id")

            logger.info(
                f"Participant joined: {payload.get('user_id')} in thread {thread_id}"
            )

            await self._broadcast(
                thread_id,
                {
                    "type": "participant_joined",
                    "thread_id": thread_id,
                    "user_id": payload.get("user_id"),
                    "added_by": payload.get("added_by"),
                    "timestamp": data.get("timestamp"),
                },
            )

        except Exception as e:
            logger.error(f"Error handling participant_joined: {e}")

    async def _handle_participant_left(self, msg):
        """Handle chat_participant_left event"""
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            thread_id = payload.get("thread_id")

            logger.info(
                f"Participant left: {payload.get('user_id')} from thread {thread_id}"
            )

            await self._broadcast(
                thread_id,
                {
                    "type": "participant_left",
                    "thread_id": thread_id,
                    "user_id": payload.get("user_id"),
                    "timestamp": data.get("timestamp"),
                },
            )

        except Exception as e:
            logger.error(f"Error handling participant_left: {e}")

    async def _handle_messages_read(self, msg):
        """Handle chat_messages_read event"""
        try:
            data = json.loads(msg.data.decode())
            payload = data.get("payload", {})
            thread_id = payload.get("thread_id")

            logger.info(
                f"Messages read by: {payload.get('user_id')} in thread {thread_id}"
            )

            # Broadcast read receipt
            await self._broadcast(
                thread_id,
                {
                    "type": "read_receipt",
                    "thread_id": thread_id,
                    "user_id": payload.get("user_id"),
                    "last_read_message_id": payload.get("last_read_message_id"),
                    "timestamp": data.get("timestamp"),
                },
            )

        except Exception as e:
            logger.error(f"Error handling messages_read: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    async def _broadcast(self, thread_id: str, message: dict):
        """Broadcast message to WebSocket clients"""
        if self.broadcast_callback:
            try:
                await self.broadcast_callback(thread_id, message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

    async def _trigger_notifications(
        self,
        thread_id: str,
        sender_id: str,
        message_preview: str,
    ):
        """Trigger push notifications for new messages"""
        # Placeholder - integrate with notification service
        logger.debug(
            f"Would notify participants of thread {thread_id} about message from {sender_id}"
        )

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."


# ─────────────────────────────────────────────────────────────────────────────
# Standalone runner
# ─────────────────────────────────────────────────────────────────────────────


async def main():
    """Run the projection worker standalone"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = ChatProjectionWorker()

    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await worker.close()


if __name__ == "__main__":
    asyncio.run(main())
