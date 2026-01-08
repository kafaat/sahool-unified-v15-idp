"""
Field Chat Data Models
Tortoise ORM models for chat threads and messages
"""

from enum import Enum

from tortoise import fields
from tortoise.models import Model


class ScopeType(str, Enum):
    """Scope types for chat threads"""

    FIELD = "field"
    TASK = "task"
    INCIDENT = "incident"


class ChatThread(Model):
    """
    Chat thread linked to a field, task, or incident

    Each scope (field/task/incident) has exactly one thread.
    Threads are created on-demand when first message is sent.
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    scope_type = fields.CharField(max_length=16, index=True)  # field|task|incident
    scope_id = fields.CharField(max_length=128, index=True)
    created_by = fields.CharField(max_length=64)
    created_at = fields.DatetimeField(auto_now_add=True)

    # Optional metadata
    title = fields.CharField(max_length=255, null=True)
    is_archived = fields.BooleanField(default=False)
    last_message_at = fields.DatetimeField(null=True)
    message_count = fields.IntField(default=0)

    class Meta:
        table = "chat_threads"
        unique_together = ("tenant_id", "scope_type", "scope_id")
        indexes = [
            ("tenant_id", "scope_type"),
            ("tenant_id", "last_message_at"),
        ]

    def __str__(self):
        return f"Thread({self.scope_type}:{self.scope_id})"


class ChatMessage(Model):
    """
    Individual chat message within a thread

    Supports text, attachments (URLs), and metadata.
    All messages are immutable for audit purposes.
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    thread_id = fields.UUIDField(index=True)
    sender_id = fields.CharField(max_length=64, index=True)

    # Content
    text = fields.TextField(null=True)
    attachments = fields.JSONField(null=True)  # List of URLs

    # Metadata
    reply_to_id = fields.UUIDField(null=True)  # For threaded replies
    message_type = fields.CharField(max_length=32, default="text")  # text|image|file|system
    is_edited = fields.BooleanField(default=False)
    edited_at = fields.DatetimeField(null=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"
        indexes = [
            ("thread_id", "created_at"),
            ("tenant_id", "sender_id"),
        ]

    def __str__(self):
        preview = (self.text or "")[:30]
        return f"Message({self.sender_id}: {preview}...)"


class ChatParticipant(Model):
    """
    Participants in a chat thread

    Tracks who has access and their last read position.
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    thread_id = fields.UUIDField(index=True)
    user_id = fields.CharField(max_length=64, index=True)

    # Read tracking
    last_read_at = fields.DatetimeField(null=True)
    last_read_message_id = fields.UUIDField(null=True)
    unread_count = fields.IntField(default=0)

    # Preferences
    is_muted = fields.BooleanField(default=False)
    joined_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_participants"
        unique_together = ("thread_id", "user_id")
        indexes = [
            ("tenant_id", "user_id"),
        ]


class ChatAttachment(Model):
    """
    Attachment metadata for chat messages

    Stores file metadata; actual files stored in object storage.
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    message_id = fields.UUIDField(index=True)

    # File info
    file_name = fields.CharField(max_length=255)
    file_type = fields.CharField(max_length=64)  # image/jpeg, application/pdf
    file_size = fields.IntField()  # bytes
    file_url = fields.TextField()

    # Image-specific
    width = fields.IntField(null=True)
    height = fields.IntField(null=True)
    thumbnail_url = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_attachments"
