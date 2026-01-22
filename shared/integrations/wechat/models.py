"""
WeChat Integration Models
=========================
نماذج تكامل WeChat

Pydantic models for WeChat MCP integration with SAHOOL platform.
All models support bilingual (Arabic/English/Chinese) content.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Enums
# =============================================================================

class MessageType(str, Enum):
    """
    WeChat message types.
    أنواع رسائل WeChat
    """
    TEXT = "text"
    IMAGE = "image"
    VOICE = "voice"
    VIDEO = "video"
    FILE = "file"
    LOCATION = "location"
    LINK = "link"
    MINIPROGRAM = "miniprogram"
    SYSTEM = "system"
    RECALLED = "recalled"


class MessageDirection(str, Enum):
    """
    Message direction.
    اتجاه الرسالة
    """
    INCOMING = "incoming"
    OUTGOING = "outgoing"


class ContactType(str, Enum):
    """
    Contact types.
    أنواع جهات الاتصال
    """
    INDIVIDUAL = "individual"
    GROUP = "group"
    OFFICIAL_ACCOUNT = "official_account"
    MINI_PROGRAM = "mini_program"


class MomentVisibility(str, Enum):
    """
    Moment visibility settings.
    إعدادات رؤية اللحظات
    """
    PUBLIC = "public"
    FRIENDS_ONLY = "friends_only"
    PRIVATE = "private"
    SELECTED_FRIENDS = "selected_friends"


class SentimentType(str, Enum):
    """
    Sentiment analysis result.
    نتيجة تحليل المشاعر
    """
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class PriorityLevel(str, Enum):
    """
    Message priority level.
    مستوى أولوية الرسالة
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TopicCategory(str, Enum):
    """
    Agricultural topic categories.
    فئات الموضوعات الزراعية
    """
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST_DISEASE = "pest_disease"
    WEATHER = "weather"
    HARVEST = "harvest"
    MARKET = "market"
    EQUIPMENT = "equipment"
    GENERAL = "general"
    URGENT = "urgent"


class AgentType(str, Enum):
    """
    WeChat agent types.
    أنواع وكلاء WeChat
    """
    CHAT_SUMMARIZER = "chat_summarizer"
    AUTO_REPLIER = "auto_replier"
    MESSAGE_SEARCHER = "message_searcher"
    MULTI_CHAT_CHECKER = "multi_chat_checker"
    CHAT_INSIGHTS = "chat_insights"


# =============================================================================
# Base Models
# =============================================================================

class BilingualText(BaseModel):
    """
    Bilingual text content.
    محتوى نص ثنائي اللغة
    """
    model_config = ConfigDict(extra="allow")

    en: str = ""
    ar: str = ""
    zh: str = ""

    def get(self, language: str = "ar") -> str:
        """Get text in specified language, fallback to English."""
        if language == "ar" and self.ar:
            return self.ar
        if language == "zh" and self.zh:
            return self.zh
        return self.en or self.ar or self.zh


class Location(BaseModel):
    """
    Geographic location.
    الموقع الجغرافي
    """
    latitude: float
    longitude: float
    name: str | None = None
    name_ar: str | None = None
    address: str | None = None
    address_ar: str | None = None


class Attachment(BaseModel):
    """
    Message attachment.
    مرفق الرسالة
    """
    model_config = ConfigDict(extra="allow")

    type: str
    url: str | None = None
    file_path: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    mime_type: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: int | None = None  # For voice/video
    width: int | None = None  # For images/videos
    height: int | None = None


# =============================================================================
# Contact Models
# =============================================================================

class WeChatContact(BaseModel):
    """
    WeChat contact model.
    نموذج جهة اتصال WeChat

    Represents a WeChat contact (individual or group).
    """
    model_config = ConfigDict(extra="allow")

    id: str = Field(..., description="Unique contact identifier | معرف جهة الاتصال الفريد")
    wechat_id: str | None = Field(None, description="WeChat ID (username)")
    name: str = Field(..., description="Display name")
    name_ar: str | None = Field(None, description="Arabic name | الاسم بالعربية")
    avatar_url: str | None = None
    type: ContactType = ContactType.INDIVIDUAL

    # Additional info
    phone: str | None = None
    email: str | None = None
    company: str | None = None
    company_ar: str | None = None
    department: str | None = None
    title: str | None = None

    # Location
    location: Location | None = None
    region: str | None = None  # Province/State

    # Agricultural context (SAHOOL-specific)
    farmer_id: str | None = Field(None, description="SAHOOL farmer ID | معرف المزارع في سهول")
    farm_id: str | None = Field(None, description="Associated farm ID | معرف المزرعة المرتبطة")
    crops: list[str] = Field(default_factory=list, description="Crops grown | المحاصيل المزروعة")
    preferred_language: str = "ar"

    # Metadata
    is_friend: bool = True
    is_blocked: bool = False
    is_starred: bool = False
    notes: str | None = None
    notes_ar: str | None = None
    tags: list[str] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: datetime | None = None

    # Statistics
    message_count: int = 0
    unread_count: int = 0

    def get_display_name(self, language: str = "ar") -> str:
        """Get display name in preferred language."""
        if language == "ar" and self.name_ar:
            return self.name_ar
        return self.name


class WeChatGroup(BaseModel):
    """
    WeChat group model.
    نموذج مجموعة WeChat
    """
    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    name_ar: str | None = None
    avatar_url: str | None = None
    owner_id: str | None = None
    admin_ids: list[str] = Field(default_factory=list)
    member_ids: list[str] = Field(default_factory=list)
    member_count: int = 0

    # Settings
    is_muted: bool = False
    is_pinned: bool = False
    announcement: str | None = None
    announcement_ar: str | None = None

    # Agricultural context
    farm_ids: list[str] = Field(default_factory=list)
    topic: TopicCategory = TopicCategory.GENERAL
    region: str | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Message Models
# =============================================================================

class WeChatMessage(BaseModel):
    """
    WeChat message model.
    نموذج رسالة WeChat

    Represents a single message in WeChat.
    """
    model_config = ConfigDict(extra="allow")

    id: str = Field(..., description="Unique message ID | معرف الرسالة الفريد")
    type: MessageType = MessageType.TEXT
    direction: MessageDirection = MessageDirection.INCOMING

    # Participants
    sender_id: str = Field(..., description="Sender contact ID")
    sender_name: str | None = None
    sender_name_ar: str | None = None
    receiver_id: str = Field(..., description="Receiver contact/group ID")
    chat_id: str = Field(..., description="Chat/conversation ID")
    is_group_message: bool = False

    # Content
    content: str = Field("", description="Message text content")
    content_ar: str | None = Field(None, description="Arabic translation | الترجمة العربية")
    attachments: list[Attachment] = Field(default_factory=list)
    location: Location | None = None

    # Reply context
    reply_to_id: str | None = Field(None, description="ID of message being replied to")
    mentions: list[str] = Field(default_factory=list, description="Mentioned contact IDs")

    # Analysis (populated by agents)
    sentiment: SentimentType | None = None
    sentiment_score: float | None = Field(None, ge=-1.0, le=1.0)
    priority: PriorityLevel | None = None
    topics: list[TopicCategory] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    keywords_ar: list[str] = Field(default_factory=list)
    intent: str | None = None
    intent_ar: str | None = None

    # Agricultural context (SAHOOL-specific)
    field_id: str | None = None
    crop_type: str | None = None
    crop_type_ar: str | None = None
    requires_action: bool = False
    action_deadline: datetime | None = None

    # Status
    is_read: bool = False
    is_recalled: bool = False
    is_edited: bool = False

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read_at: datetime | None = None
    edited_at: datetime | None = None

    def is_urgent(self) -> bool:
        """Check if message is urgent."""
        return (
            self.priority == PriorityLevel.CRITICAL or
            self.priority == PriorityLevel.HIGH or
            TopicCategory.URGENT in self.topics
        )


class WeChatMoment(BaseModel):
    """
    WeChat Moments (朋友圈) post model.
    نموذج منشور لحظات WeChat
    """
    model_config = ConfigDict(extra="allow")

    id: str
    author_id: str
    author_name: str | None = None
    author_name_ar: str | None = None

    # Content
    content: str = ""
    content_ar: str | None = None
    images: list[str] = Field(default_factory=list)
    video_url: str | None = None
    location: Location | None = None
    link_url: str | None = None
    link_title: str | None = None

    # Visibility
    visibility: MomentVisibility = MomentVisibility.FRIENDS_ONLY
    visible_to: list[str] = Field(default_factory=list)
    hidden_from: list[str] = Field(default_factory=list)

    # Engagement
    like_count: int = 0
    comment_count: int = 0
    liked_by: list[str] = Field(default_factory=list)

    # Agricultural context
    farm_id: str | None = None
    crop_type: str | None = None
    topics: list[TopicCategory] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Analysis Models
# =============================================================================

class MessageAnalysis(BaseModel):
    """
    Single message analysis result.
    نتيجة تحليل رسالة واحدة
    """
    message_id: str
    sentiment: SentimentType
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    priority: PriorityLevel
    topics: list[TopicCategory]
    keywords: list[str]
    keywords_ar: list[str] = Field(default_factory=list)
    intent: str
    intent_ar: str
    requires_action: bool
    confidence: float = Field(ge=0.0, le=1.0)


class ChatSummary(BaseModel):
    """
    Chat conversation summary.
    ملخص محادثة الدردشة

    Generated by ChatSummarizerAgent.
    """
    model_config = ConfigDict(extra="allow")

    chat_id: str
    contact_id: str
    contact_name: str | None = None
    contact_name_ar: str | None = None

    # Time range
    start_time: datetime
    end_time: datetime
    message_count: int

    # Summary content
    summary: str = Field(..., description="English summary")
    summary_ar: str = Field(..., description="Arabic summary | الملخص بالعربية")

    # Key points
    key_points: list[str] = Field(default_factory=list)
    key_points_ar: list[str] = Field(default_factory=list)

    # Extracted information
    action_items: list[str] = Field(default_factory=list)
    action_items_ar: list[str] = Field(default_factory=list)
    decisions_made: list[str] = Field(default_factory=list)
    questions_unanswered: list[str] = Field(default_factory=list)

    # Topics and sentiment
    main_topics: list[TopicCategory] = Field(default_factory=list)
    overall_sentiment: SentimentType = SentimentType.NEUTRAL
    sentiment_trend: str | None = None  # "improving", "declining", "stable"

    # Agricultural context
    crops_mentioned: list[str] = Field(default_factory=list)
    fields_mentioned: list[str] = Field(default_factory=list)
    weather_concerns: list[str] = Field(default_factory=list)
    irrigation_discussed: bool = False
    pest_issues: list[str] = Field(default_factory=list)

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class ChatInsight(BaseModel):
    """
    Chat relationship and dynamics insight.
    رؤية علاقات وديناميكيات الدردشة

    Generated by ChatInsightsAgent.
    """
    model_config = ConfigDict(extra="allow")

    chat_id: str
    contact_id: str
    contact_name: str | None = None

    # Relationship metrics
    relationship_strength: float = Field(ge=0.0, le=1.0, description="0-1 strength score")
    relationship_type: str  # "farmer", "supplier", "advisor", "buyer", "peer"
    relationship_type_ar: str

    # Communication patterns
    avg_response_time_minutes: float | None = None
    messages_per_week: float = 0
    peak_activity_hours: list[int] = Field(default_factory=list)
    preferred_message_type: MessageType = MessageType.TEXT

    # Sentiment analysis
    overall_sentiment: SentimentType = SentimentType.NEUTRAL
    sentiment_history: list[dict[str, Any]] = Field(default_factory=list)
    positive_interaction_rate: float = Field(ge=0.0, le=1.0, default=0.5)

    # Topics of interest
    frequent_topics: list[TopicCategory] = Field(default_factory=list)
    topic_distribution: dict[str, float] = Field(default_factory=dict)

    # Agricultural insights
    crops_of_interest: list[str] = Field(default_factory=list)
    common_issues: list[str] = Field(default_factory=list)
    seasonal_patterns: dict[str, str] = Field(default_factory=dict)

    # Recommendations
    engagement_suggestions: list[str] = Field(default_factory=list)
    engagement_suggestions_ar: list[str] = Field(default_factory=list)

    # Metadata
    analysis_period_days: int = 30
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MultiChatStatus(BaseModel):
    """
    Status summary across multiple chats.
    ملخص الحالة عبر محادثات متعددة

    Generated by MultiChatCheckerAgent.
    """
    model_config = ConfigDict(extra="allow")

    # Overall stats
    total_chats: int
    total_unread: int
    total_messages_today: int

    # Prioritized chats
    urgent_chats: list[dict[str, Any]] = Field(default_factory=list)
    high_priority_chats: list[dict[str, Any]] = Field(default_factory=list)
    pending_responses: list[dict[str, Any]] = Field(default_factory=list)

    # Summary
    summary: str
    summary_ar: str

    # Recommendations
    recommended_actions: list[str] = Field(default_factory=list)
    recommended_actions_ar: list[str] = Field(default_factory=list)

    # Agricultural alerts
    agricultural_alerts: list[dict[str, Any]] = Field(default_factory=list)

    # Timestamps
    checked_at: datetime = Field(default_factory=datetime.utcnow)


class SearchResult(BaseModel):
    """
    Message search result.
    نتيجة البحث في الرسائل

    Returned by MessageSearcherAgent.
    """
    model_config = ConfigDict(extra="allow")

    query: str
    query_ar: str | None = None
    total_results: int
    messages: list[WeChatMessage] = Field(default_factory=list)

    # Filters applied
    filters: dict[str, Any] = Field(default_factory=dict)

    # Search metadata
    search_time_ms: float = 0
    relevance_scores: dict[str, float] = Field(default_factory=dict)

    # Grouped results
    by_contact: dict[str, int] = Field(default_factory=dict)
    by_topic: dict[str, int] = Field(default_factory=dict)
    by_date: dict[str, int] = Field(default_factory=dict)


# =============================================================================
# Agent Response Models
# =============================================================================

class AgentResponse(BaseModel):
    """
    Generic agent response model.
    نموذج استجابة الوكيل العام

    Used by all WeChat agents to return results.
    """
    model_config = ConfigDict(extra="allow")

    agent_type: AgentType
    success: bool
    status: str  # "completed", "partial", "failed"
    status_ar: str

    # Response content
    message: str
    message_ar: str
    data: dict[str, Any] = Field(default_factory=dict)

    # Execution info
    execution_time_ms: float = 0
    tokens_used: int | None = None
    model_used: str | None = None

    # Error handling
    error: str | None = None
    error_ar: str | None = None
    error_code: str | None = None

    # Metadata
    request_id: str | None = None
    tenant_id: str = "sahool"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AutoReplyResponse(AgentResponse):
    """
    Auto-reply agent response.
    استجابة وكيل الرد التلقائي
    """
    agent_type: AgentType = AgentType.AUTO_REPLIER

    # Reply content
    reply_text: str = ""
    reply_text_ar: str = ""
    suggested_replies: list[str] = Field(default_factory=list)
    suggested_replies_ar: list[str] = Field(default_factory=list)

    # Context
    original_message_id: str | None = None
    detected_intent: str | None = None
    detected_intent_ar: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)

    # Agricultural context
    related_advisory: dict[str, Any] | None = None
    requires_human_review: bool = False
    escalation_reason: str | None = None


class SummaryResponse(AgentResponse):
    """
    Summary agent response.
    استجابة وكيل الملخص
    """
    agent_type: AgentType = AgentType.CHAT_SUMMARIZER

    summary: ChatSummary | None = None
    summaries: list[ChatSummary] = Field(default_factory=list)


class InsightsResponse(AgentResponse):
    """
    Insights agent response.
    استجابة وكيل الرؤى
    """
    agent_type: AgentType = AgentType.CHAT_INSIGHTS

    insight: ChatInsight | None = None
    insights: list[ChatInsight] = Field(default_factory=list)


# =============================================================================
# Request Models
# =============================================================================

class FetchMessagesRequest(BaseModel):
    """
    Request to fetch messages.
    طلب جلب الرسائل
    """
    chat_id: str
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    since: datetime | None = None
    until: datetime | None = None
    message_types: list[MessageType] | None = None
    include_attachments: bool = True


class SendMessageRequest(BaseModel):
    """
    Request to send a message.
    طلب إرسال رسالة
    """
    chat_id: str
    content: str
    content_ar: str | None = None
    type: MessageType = MessageType.TEXT
    reply_to_id: str | None = None
    mentions: list[str] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)
    location: Location | None = None


class SearchMessagesRequest(BaseModel):
    """
    Request to search messages.
    طلب البحث في الرسائل
    """
    query: str
    chat_ids: list[str] | None = None
    contact_ids: list[str] | None = None
    since: datetime | None = None
    until: datetime | None = None
    message_types: list[MessageType] | None = None
    topics: list[TopicCategory] | None = None
    priority: PriorityLevel | None = None
    limit: int = Field(default=50, ge=1, le=200)
    include_context: bool = True


class PublishMomentRequest(BaseModel):
    """
    Request to publish a moment.
    طلب نشر لحظة
    """
    content: str
    content_ar: str | None = None
    images: list[str] = Field(default_factory=list)
    video_url: str | None = None
    location: Location | None = None
    visibility: MomentVisibility = MomentVisibility.FRIENDS_ONLY
    visible_to: list[str] = Field(default_factory=list)
