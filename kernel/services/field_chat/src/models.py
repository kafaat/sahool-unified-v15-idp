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
    message_type = fields.CharField(
        max_length=32, default="text"
    )  # text|image|file|system
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


# ═══════════════════════════════════════════════════════════════════════════════
# Expert Support System - نظام دعم الخبراء
# ═══════════════════════════════════════════════════════════════════════════════


class ExpertRequestStatus(str, Enum):
    """Status of expert support request"""

    PENDING = "pending"  # في انتظار خبير
    ACCEPTED = "accepted"  # تم القبول
    IN_PROGRESS = "in_progress"  # جاري التنفيذ
    RESOLVED = "resolved"  # تم الحل
    CANCELLED = "cancelled"  # ملغي


class ExpertSpecialty(str, Enum):
    """Expert specialties"""

    CROP_DISEASES = "crop_diseases"  # أمراض المحاصيل
    IRRIGATION = "irrigation"  # الري
    SOIL = "soil"  # التربة
    PEST_CONTROL = "pest_control"  # مكافحة الآفات
    FERTILIZATION = "fertilization"  # التسميد
    GENERAL = "general"  # عام


class ExpertProfile(Model):
    """
    Expert profile for agricultural consultants
    ملف تعريف الخبير الزراعي
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    user_id = fields.CharField(max_length=64, unique=True, index=True)

    # Profile info
    name = fields.CharField(max_length=128)
    name_ar = fields.CharField(max_length=128, null=True)
    specialties = fields.JSONField(default=list)  # List of ExpertSpecialty values
    bio = fields.TextField(null=True)
    bio_ar = fields.TextField(null=True)

    # Availability
    is_available = fields.BooleanField(default=True)
    governorates = fields.JSONField(default=list)  # Covered governorates

    # Stats
    total_consultations = fields.IntField(default=0)
    avg_rating = fields.FloatField(default=5.0)
    rating_count = fields.IntField(default=0)

    # Status
    is_verified = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_online_at = fields.DatetimeField(null=True)

    class Meta:
        table = "expert_profiles"
        indexes = [
            ("tenant_id", "is_available"),
            ("tenant_id", "is_active"),
        ]


class ExpertSupportRequest(Model):
    """
    Support request from farmer to expert
    طلب دعم من المزارع للخبير
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)

    # Farmer info
    farmer_id = fields.CharField(max_length=64, index=True)
    farmer_name = fields.CharField(max_length=128)
    governorate = fields.CharField(max_length=64, null=True)

    # Request details
    topic = fields.CharField(max_length=255)
    topic_ar = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    specialty_needed = fields.CharField(max_length=32, default="general")

    # Linked resources
    field_id = fields.CharField(max_length=64, null=True)
    diagnosis_id = fields.CharField(max_length=64, null=True)  # Link to crop_health diagnosis
    thread_id = fields.UUIDField(null=True, index=True)  # Chat thread for this request

    # Expert assignment
    expert_id = fields.CharField(max_length=64, null=True, index=True)
    expert_name = fields.CharField(max_length=128, null=True)

    # Status
    status = fields.CharField(max_length=16, default="pending", index=True)
    priority = fields.CharField(max_length=16, default="normal")  # low|normal|high|urgent

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    accepted_at = fields.DatetimeField(null=True)
    resolved_at = fields.DatetimeField(null=True)

    # Resolution
    resolution_notes = fields.TextField(null=True)
    resolution_notes_ar = fields.TextField(null=True)
    farmer_rating = fields.IntField(null=True)  # 1-5
    farmer_feedback = fields.TextField(null=True)

    class Meta:
        table = "expert_support_requests"
        indexes = [
            ("tenant_id", "status"),
            ("tenant_id", "farmer_id"),
            ("tenant_id", "created_at"),
        ]


class OnlineExpert(Model):
    """
    Track online experts for real-time availability
    تتبع الخبراء المتصلين
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=64, index=True)
    expert_id = fields.CharField(max_length=64, index=True)
    connection_id = fields.CharField(max_length=128, unique=True)

    # Status
    is_busy = fields.BooleanField(default=False)
    current_request_id = fields.UUIDField(null=True)

    connected_at = fields.DatetimeField(auto_now_add=True)
    last_heartbeat = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "online_experts"
        indexes = [
            ("tenant_id", "is_busy"),
        ]
