"""
Field Chat API Endpoints
REST API for chat thread and message operations
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .events.publish import ChatPublisher
from .repository import ChatRepository

router = APIRouter(prefix="/chat", tags=["Chat"])


# Dependency injection
def get_repository() -> ChatRepository:
    return ChatRepository()


def get_publisher() -> ChatPublisher:
    return ChatPublisher()


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────


class CreateThreadRequest(BaseModel):
    """Request to create a new chat thread"""

    tenant_id: str = Field(..., description="Tenant identifier")
    scope_type: str = Field(..., description="Scope type: field|task|incident")
    scope_id: str = Field(..., description="ID of the scope entity")
    created_by: str = Field(..., description="User ID creating the thread")
    title: str | None = Field(None, description="Optional thread title")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")


class ThreadResponse(BaseModel):
    """Thread response model"""

    thread_id: str
    tenant_id: str
    scope_type: str
    scope_id: str
    created_by: str
    title: str | None
    is_archived: bool
    message_count: int
    last_message_at: str | None
    created_at: str


class SendMessageRequest(BaseModel):
    """Request to send a message"""

    tenant_id: str = Field(..., description="Tenant identifier")
    sender_id: str = Field(..., description="User ID sending the message")
    text: str | None = Field(None, description="Message text")
    attachments: list[str] | None = Field(None, description="List of attachment URLs")
    reply_to_id: str | None = Field(None, description="Message ID being replied to")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")


class MessageResponse(BaseModel):
    """Message response model"""

    message_id: str
    thread_id: str
    sender_id: str
    text: str | None
    attachments: list[str]
    reply_to_id: str | None
    message_type: str
    created_at: str


class MarkReadRequest(BaseModel):
    """Request to mark messages as read"""

    user_id: str = Field(..., description="User ID marking as read")
    last_read_message_id: str | None = Field(None, description="Last read message ID")


class AddParticipantRequest(BaseModel):
    """Request to add participant to thread"""

    tenant_id: str
    user_id: str = Field(..., description="User ID to add")
    added_by: str | None = Field(None, description="User ID who added them")
    correlation_id: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# Thread Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    req: CreateThreadRequest,
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    """
    Create a new chat thread for a field, task, or incident.
    Idempotent: returns existing thread if one already exists for the scope.
    """
    if req.scope_type not in ("field", "task", "incident"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_scope_type",
                "message_ar": "نوع النطاق غير صالح",
                "message_en": "Invalid scope type. Must be: field, task, or incident",
            },
        )

    thread, created = await repo.get_or_create_thread(
        tenant_id=req.tenant_id,
        scope_type=req.scope_type,
        scope_id=req.scope_id,
        created_by=req.created_by,
        title=req.title,
    )

    if created:
        await pub.publish_thread_created(
            tenant_id=req.tenant_id,
            thread_id=str(thread.id),
            scope_type=thread.scope_type,
            scope_id=thread.scope_id,
            created_by=thread.created_by,
            title=thread.title,
            correlation_id=req.correlation_id,
        )
        await pub.close()

    return ThreadResponse(
        thread_id=str(thread.id),
        tenant_id=thread.tenant_id,
        scope_type=thread.scope_type,
        scope_id=thread.scope_id,
        created_by=thread.created_by,
        title=thread.title,
        is_archived=thread.is_archived,
        message_count=thread.message_count,
        last_message_at=(
            thread.last_message_at.isoformat() if thread.last_message_at else None
        ),
        created_at=thread.created_at.isoformat(),
    )


@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: UUID,
    tenant_id: str = Query(..., description="Tenant identifier"),
    repo: ChatRepository = Depends(get_repository),
):
    """Get a specific thread by ID"""
    thread = await repo.get_thread(thread_id, tenant_id)
    if not thread:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "thread_not_found",
                "message_ar": "المحادثة غير موجودة",
                "message_en": "Thread not found",
            },
        )

    return ThreadResponse(
        thread_id=str(thread.id),
        tenant_id=thread.tenant_id,
        scope_type=thread.scope_type,
        scope_id=thread.scope_id,
        created_by=thread.created_by,
        title=thread.title,
        is_archived=thread.is_archived,
        message_count=thread.message_count,
        last_message_at=(
            thread.last_message_at.isoformat() if thread.last_message_at else None
        ),
        created_at=thread.created_at.isoformat(),
    )


@router.get("/threads/by-scope/{scope_type}/{scope_id}", response_model=ThreadResponse)
async def get_thread_by_scope(
    scope_type: str,
    scope_id: str,
    tenant_id: str = Query(..., description="Tenant identifier"),
    repo: ChatRepository = Depends(get_repository),
):
    """Get thread by scope (field/task/incident ID)"""
    thread = await repo.get_thread_by_scope(tenant_id, scope_type, scope_id)
    if not thread:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "thread_not_found",
                "message_ar": "المحادثة غير موجودة لهذا النطاق",
                "message_en": "No thread found for this scope",
            },
        )

    return ThreadResponse(
        thread_id=str(thread.id),
        tenant_id=thread.tenant_id,
        scope_type=thread.scope_type,
        scope_id=thread.scope_id,
        created_by=thread.created_by,
        title=thread.title,
        is_archived=thread.is_archived,
        message_count=thread.message_count,
        last_message_at=(
            thread.last_message_at.isoformat() if thread.last_message_at else None
        ),
        created_at=thread.created_at.isoformat(),
    )


@router.get("/threads", response_model=list[ThreadResponse])
async def list_threads(
    tenant_id: str = Query(..., description="Tenant identifier"),
    user_id: str | None = Query(None, description="Filter by participant user ID"),
    scope_type: str | None = Query(None, description="Filter by scope type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: ChatRepository = Depends(get_repository),
):
    """List chat threads with optional filters"""
    threads = await repo.list_threads(
        tenant_id=tenant_id,
        user_id=user_id,
        scope_type=scope_type,
        limit=limit,
        offset=offset,
    )

    return [
        ThreadResponse(
            thread_id=str(t.id),
            tenant_id=t.tenant_id,
            scope_type=t.scope_type,
            scope_id=t.scope_id,
            created_by=t.created_by,
            title=t.title,
            is_archived=t.is_archived,
            message_count=t.message_count,
            last_message_at=(
                t.last_message_at.isoformat() if t.last_message_at else None
            ),
            created_at=t.created_at.isoformat(),
        )
        for t in threads
    ]


@router.post("/threads/{thread_id}/archive")
async def archive_thread(
    thread_id: UUID,
    tenant_id: str = Query(..., description="Tenant identifier"),
    archived_by: str = Query(..., description="User ID archiving the thread"),
    correlation_id: str | None = Query(None),
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    """Archive a chat thread"""
    success = await repo.archive_thread(thread_id, tenant_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "thread_not_found",
                "message_ar": "المحادثة غير موجودة",
                "message_en": "Thread not found",
            },
        )

    await pub.publish_thread_archived(
        tenant_id=tenant_id,
        thread_id=str(thread_id),
        archived_by=archived_by,
        correlation_id=correlation_id,
    )
    await pub.close()

    return {"status": "archived", "thread_id": str(thread_id)}


# ─────────────────────────────────────────────────────────────────────────────
# Message Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/threads/{thread_id}/messages", response_model=MessageResponse)
async def send_message(
    thread_id: UUID,
    req: SendMessageRequest,
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    """Send a message to a chat thread"""
    # Verify thread exists
    thread = await repo.get_thread(thread_id, req.tenant_id)
    if not thread:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "thread_not_found",
                "message_ar": "المحادثة غير موجودة",
                "message_en": "Thread not found",
            },
        )

    if thread.is_archived:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "thread_archived",
                "message_ar": "المحادثة مؤرشفة ولا يمكن إضافة رسائل",
                "message_en": "Cannot send messages to archived thread",
            },
        )

    # Validate content
    if not req.text and not req.attachments:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "empty_message",
                "message_ar": "الرسالة فارغة",
                "message_en": "Message must have text or attachments",
            },
        )

    # Determine message type
    message_type = "text"
    if req.attachments and not req.text:
        message_type = "attachment"
    elif req.attachments and req.text:
        message_type = "mixed"

    # Create message
    message = await repo.create_message(
        tenant_id=req.tenant_id,
        thread_id=thread_id,
        sender_id=req.sender_id,
        text=req.text,
        attachments=req.attachments,
        reply_to_id=UUID(req.reply_to_id) if req.reply_to_id else None,
        message_type=message_type,
    )

    # Publish event
    await pub.publish_message_sent(
        tenant_id=req.tenant_id,
        thread_id=str(thread_id),
        message_id=str(message.id),
        sender_id=req.sender_id,
        text=req.text,
        attachments=req.attachments,
        reply_to_id=req.reply_to_id,
        correlation_id=req.correlation_id,
    )
    await pub.close()

    return MessageResponse(
        message_id=str(message.id),
        thread_id=str(message.thread_id),
        sender_id=message.sender_id,
        text=message.text,
        attachments=message.attachments or [],
        reply_to_id=str(message.reply_to_id) if message.reply_to_id else None,
        message_type=message.message_type,
        created_at=message.created_at.isoformat(),
    )


@router.get("/threads/{thread_id}/messages", response_model=list[MessageResponse])
async def list_messages(
    thread_id: UUID,
    tenant_id: str = Query(..., description="Tenant identifier"),
    limit: int = Query(50, ge=1, le=100),
    before: datetime | None = Query(
        None, description="Get messages before this timestamp"
    ),
    after: datetime | None = Query(
        None, description="Get messages after this timestamp"
    ),
    repo: ChatRepository = Depends(get_repository),
):
    """List messages in a thread with pagination"""
    messages = await repo.list_messages(
        thread_id=thread_id,
        tenant_id=tenant_id,
        limit=limit,
        before=before,
        after=after,
    )

    return [
        MessageResponse(
            message_id=str(m.id),
            thread_id=str(m.thread_id),
            sender_id=m.sender_id,
            text=m.text,
            attachments=m.attachments or [],
            reply_to_id=str(m.reply_to_id) if m.reply_to_id else None,
            message_type=m.message_type,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


@router.get("/messages/search", response_model=list[MessageResponse])
async def search_messages(
    tenant_id: str = Query(..., description="Tenant identifier"),
    q: str = Query(..., min_length=2, description="Search query"),
    thread_id: UUID | None = Query(None, description="Limit to specific thread"),
    sender_id: str | None = Query(None, description="Filter by sender"),
    limit: int = Query(50, ge=1, le=100),
    repo: ChatRepository = Depends(get_repository),
):
    """Search messages by text content"""
    messages = await repo.search_messages(
        tenant_id=tenant_id,
        query_text=q,
        thread_id=thread_id,
        sender_id=sender_id,
        limit=limit,
    )

    return [
        MessageResponse(
            message_id=str(m.id),
            thread_id=str(m.thread_id),
            sender_id=m.sender_id,
            text=m.text,
            attachments=m.attachments or [],
            reply_to_id=str(m.reply_to_id) if m.reply_to_id else None,
            message_type=m.message_type,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Participant Endpoints
# ─────────────────────────────────────────────────────────────────────────────


@router.post("/threads/{thread_id}/participants")
async def add_participant(
    thread_id: UUID,
    req: AddParticipantRequest,
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    """Add a participant to a chat thread"""
    thread = await repo.get_thread(thread_id, req.tenant_id)
    if not thread:
        raise HTTPException(status_code=404, detail="thread_not_found")

    await repo.add_participant(req.tenant_id, thread_id, req.user_id)

    await pub.publish_participant_joined(
        tenant_id=req.tenant_id,
        thread_id=str(thread_id),
        user_id=req.user_id,
        added_by=req.added_by,
        correlation_id=req.correlation_id,
    )
    await pub.close()

    return {"status": "added", "user_id": req.user_id, "thread_id": str(thread_id)}


@router.delete("/threads/{thread_id}/participants/{user_id}")
async def remove_participant(
    thread_id: UUID,
    user_id: str,
    tenant_id: str = Query(...),
    correlation_id: str | None = Query(None),
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    """Remove a participant from a chat thread"""
    success = await repo.remove_participant(thread_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="participant_not_found")

    await pub.publish_participant_left(
        tenant_id=tenant_id,
        thread_id=str(thread_id),
        user_id=user_id,
        correlation_id=correlation_id,
    )
    await pub.close()

    return {"status": "removed", "user_id": user_id}


@router.post("/threads/{thread_id}/read")
async def mark_as_read(
    thread_id: UUID,
    req: MarkReadRequest,
    tenant_id: str = Query(...),
    correlation_id: str | None = Query(None),
    repo: ChatRepository = Depends(get_repository),
    pub: ChatPublisher = Depends(get_publisher),
):
    """Mark messages in a thread as read"""
    success = await repo.mark_read(
        thread_id=thread_id,
        user_id=req.user_id,
        message_id=UUID(req.last_read_message_id) if req.last_read_message_id else None,
    )

    if success and req.last_read_message_id:
        await pub.publish_messages_read(
            tenant_id=tenant_id,
            thread_id=str(thread_id),
            user_id=req.user_id,
            last_read_message_id=req.last_read_message_id,
            correlation_id=correlation_id,
        )
        await pub.close()

    return {"status": "marked_read", "thread_id": str(thread_id)}


@router.get("/unread-counts")
async def get_unread_counts(
    tenant_id: str = Query(...),
    user_id: str = Query(...),
    repo: ChatRepository = Depends(get_repository),
):
    """Get unread message counts for all threads"""
    counts = await repo.get_unread_counts(tenant_id, user_id)
    total = sum(counts.values())

    return {
        "total_unread": total,
        "threads": counts,
    }
