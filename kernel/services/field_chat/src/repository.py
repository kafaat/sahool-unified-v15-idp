"""
Field Chat Repository
Data access layer for chat operations
"""

from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

from .models import ChatThread, ChatMessage, ChatParticipant


class ChatRepository:
    """Repository for chat data operations"""

    # ─────────────────────────────────────────────────────────────
    # Thread Operations
    # ─────────────────────────────────────────────────────────────

    async def get_or_create_thread(
        self,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
        created_by: str,
        title: Optional[str] = None,
    ) -> tuple[ChatThread, bool]:
        """
        Get existing thread or create new one (idempotent)
        Returns (thread, created) tuple
        """
        thread = await ChatThread.get_or_none(
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
        )

        if thread:
            return thread, False

        thread = await ChatThread.create(
            id=uuid4(),
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
            created_by=created_by,
            title=title or self._generate_title(scope_type, scope_id),
        )

        # Add creator as participant
        await self.add_participant(tenant_id, thread.id, created_by)

        return thread, True

    async def get_thread(
        self,
        thread_id: UUID,
        tenant_id: str,
    ) -> Optional[ChatThread]:
        """Get thread by ID"""
        return await ChatThread.get_or_none(
            id=thread_id,
            tenant_id=tenant_id,
        )

    async def get_thread_by_scope(
        self,
        tenant_id: str,
        scope_type: str,
        scope_id: str,
    ) -> Optional[ChatThread]:
        """Get thread by scope"""
        return await ChatThread.get_or_none(
            tenant_id=tenant_id,
            scope_type=scope_type,
            scope_id=scope_id,
        )

    async def list_threads(
        self,
        tenant_id: str,
        user_id: Optional[str] = None,
        scope_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ChatThread]:
        """List threads with optional filters"""
        query = ChatThread.filter(tenant_id=tenant_id, is_archived=False)

        if scope_type:
            query = query.filter(scope_type=scope_type)

        if user_id:
            # Only threads user participates in
            participant_threads = await ChatParticipant.filter(
                tenant_id=tenant_id,
                user_id=user_id,
            ).values_list("thread_id", flat=True)
            query = query.filter(id__in=participant_threads)

        return await query.order_by("-last_message_at").offset(offset).limit(limit)

    async def archive_thread(
        self,
        thread_id: UUID,
        tenant_id: str,
    ) -> bool:
        """Archive a thread"""
        updated = await ChatThread.filter(
            id=thread_id,
            tenant_id=tenant_id,
        ).update(is_archived=True)
        return updated > 0

    # ─────────────────────────────────────────────────────────────
    # Message Operations
    # ─────────────────────────────────────────────────────────────

    async def create_message(
        self,
        tenant_id: str,
        thread_id: UUID,
        sender_id: str,
        text: Optional[str] = None,
        attachments: Optional[list[str]] = None,
        reply_to_id: Optional[UUID] = None,
        message_type: str = "text",
    ) -> ChatMessage:
        """Create a new message"""
        message = await ChatMessage.create(
            id=uuid4(),
            tenant_id=tenant_id,
            thread_id=thread_id,
            sender_id=sender_id,
            text=text,
            attachments=attachments,
            reply_to_id=reply_to_id,
            message_type=message_type,
        )

        # Update thread stats
        await ChatThread.filter(id=thread_id).update(
            last_message_at=datetime.utcnow(),
            message_count=await ChatMessage.filter(thread_id=thread_id).count(),
        )

        # Increment unread for other participants
        await ChatParticipant.filter(
            thread_id=thread_id,
        ).exclude(user_id=sender_id).update(
            unread_count=ChatParticipant.unread_count + 1,
        )

        return message

    async def get_message(
        self,
        message_id: UUID,
        tenant_id: str,
    ) -> Optional[ChatMessage]:
        """Get message by ID"""
        return await ChatMessage.get_or_none(
            id=message_id,
            tenant_id=tenant_id,
        )

    async def list_messages(
        self,
        thread_id: UUID,
        tenant_id: str,
        limit: int = 50,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
    ) -> list[ChatMessage]:
        """List messages in a thread with pagination"""
        query = ChatMessage.filter(
            thread_id=thread_id,
            tenant_id=tenant_id,
        )

        if before:
            query = query.filter(created_at__lt=before)
        if after:
            query = query.filter(created_at__gt=after)

        return await query.order_by("-created_at").limit(limit)

    async def search_messages(
        self,
        tenant_id: str,
        query_text: str,
        thread_id: Optional[UUID] = None,
        sender_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[ChatMessage]:
        """Search messages by text content"""
        query = ChatMessage.filter(
            tenant_id=tenant_id,
            text__icontains=query_text,
        )

        if thread_id:
            query = query.filter(thread_id=thread_id)
        if sender_id:
            query = query.filter(sender_id=sender_id)

        return await query.order_by("-created_at").limit(limit)

    # ─────────────────────────────────────────────────────────────
    # Participant Operations
    # ─────────────────────────────────────────────────────────────

    async def add_participant(
        self,
        tenant_id: str,
        thread_id: UUID,
        user_id: str,
    ) -> ChatParticipant:
        """Add participant to thread (idempotent)"""
        participant, _ = await ChatParticipant.get_or_create(
            tenant_id=tenant_id,
            thread_id=thread_id,
            user_id=user_id,
            defaults={"id": uuid4()},
        )
        return participant

    async def remove_participant(
        self,
        thread_id: UUID,
        user_id: str,
    ) -> bool:
        """Remove participant from thread"""
        deleted = await ChatParticipant.filter(
            thread_id=thread_id,
            user_id=user_id,
        ).delete()
        return deleted > 0

    async def mark_read(
        self,
        thread_id: UUID,
        user_id: str,
        message_id: Optional[UUID] = None,
    ) -> bool:
        """Mark thread as read up to message"""
        now = datetime.utcnow()
        updated = await ChatParticipant.filter(
            thread_id=thread_id,
            user_id=user_id,
        ).update(
            last_read_at=now,
            last_read_message_id=message_id,
            unread_count=0,
        )
        return updated > 0

    async def get_unread_counts(
        self,
        tenant_id: str,
        user_id: str,
    ) -> dict[str, int]:
        """Get unread counts for all threads"""
        participants = await ChatParticipant.filter(
            tenant_id=tenant_id,
            user_id=user_id,
        ).values("thread_id", "unread_count")

        return {str(p["thread_id"]): p["unread_count"] for p in participants}

    # ─────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────

    def _generate_title(self, scope_type: str, scope_id: str) -> str:
        """Generate default thread title"""
        titles = {
            "field": "محادثة الحقل | Field Chat",
            "task": "محادثة المهمة | Task Chat",
            "incident": "محادثة الحادثة | Incident Chat",
        }
        return titles.get(scope_type, "محادثة | Chat")
