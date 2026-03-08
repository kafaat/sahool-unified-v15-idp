# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Pydantic schemas for WhatsApp Bot Service.
نماذج Pydantic لخدمة روبوت واتساب.

These models represent:
- Incoming webhook payloads from WhatsApp Cloud API
- Outgoing message requests
- Conversation state management
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Enums
# ============================================================================


class MessageType(StrEnum):
    """نوع الرسالة"""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACTS = "contacts"
    STICKER = "sticker"
    INTERACTIVE = "interactive"
    BUTTON = "button"
    REACTION = "reaction"
    ORDER = "order"
    UNKNOWN = "unknown"


class InteractiveType(StrEnum):
    """نوع الرسالة التفاعلية"""

    BUTTON = "button"
    LIST = "list"
    BUTTON_REPLY = "button_reply"
    LIST_REPLY = "list_reply"


class ConversationIntent(StrEnum):
    """نية المحادثة"""

    GREETING = "greeting"
    CROP_DISEASE = "crop_disease"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    PEST_DETECTION = "pest_detection"
    WEATHER = "weather"
    YIELD_PREDICTION = "yield_prediction"
    GENERAL_ADVISORY = "general_advisory"
    FIELD_ANALYSIS = "field_analysis"
    MARKET_PRICES = "market_prices"
    MENU = "menu"
    HELP = "help"
    LANGUAGE_SWITCH = "language_switch"
    UNKNOWN = "unknown"


class Language(StrEnum):
    """اللغة"""

    ARABIC = "ar"
    ENGLISH = "en"


# ============================================================================
# WhatsApp Webhook Payload Models (Incoming)
# ============================================================================


class WhatsAppTextMessage(BaseModel):
    """نص الرسالة"""

    body: str


class WhatsAppImageMessage(BaseModel):
    """صورة الرسالة"""

    id: str
    mime_type: str = Field(alias="mime_type", default="image/jpeg")
    sha256: str | None = None
    caption: str | None = None


class WhatsAppLocationMessage(BaseModel):
    """موقع الرسالة"""

    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None


class WhatsAppButtonReply(BaseModel):
    """رد الزر"""

    id: str
    title: str


class WhatsAppListReply(BaseModel):
    """رد القائمة"""

    id: str
    title: str
    description: str | None = None


class WhatsAppInteractiveResponse(BaseModel):
    """استجابة تفاعلية"""

    type: str
    button_reply: WhatsAppButtonReply | None = None
    list_reply: WhatsAppListReply | None = None


class WhatsAppContact(BaseModel):
    """جهة اتصال"""

    wa_id: str = Field(description="WhatsApp ID (phone number)")
    profile: dict[str, Any] | None = None


class WhatsAppMessage(BaseModel):
    """رسالة واتساب واردة"""

    from_: str = Field(alias="from", description="Sender phone number")
    id: str = Field(description="Message ID")
    timestamp: str = Field(description="Message timestamp")
    type: MessageType = Field(description="Message type")

    # Optional message content based on type
    text: WhatsAppTextMessage | None = None
    image: WhatsAppImageMessage | None = None
    location: WhatsAppLocationMessage | None = None
    interactive: WhatsAppInteractiveResponse | None = None
    button: WhatsAppButtonReply | None = None

    # Context for replies
    context: dict[str, Any] | None = None

    class Config:
        populate_by_name = True


class WhatsAppMetadata(BaseModel):
    """بيانات تعريفية"""

    display_phone_number: str
    phone_number_id: str


class WhatsAppStatus(BaseModel):
    """حالة الرسالة"""

    id: str
    status: str  # sent, delivered, read, failed
    timestamp: str
    recipient_id: str
    conversation: dict[str, Any] | None = None
    pricing: dict[str, Any] | None = None


class WhatsAppValue(BaseModel):
    """قيمة webhook"""

    messaging_product: str = "whatsapp"
    metadata: WhatsAppMetadata
    contacts: list[WhatsAppContact] | None = None
    messages: list[WhatsAppMessage] | None = None
    statuses: list[WhatsAppStatus] | None = None


class WhatsAppChange(BaseModel):
    """تغيير webhook"""

    field: str
    value: WhatsAppValue


class WhatsAppEntry(BaseModel):
    """مدخل webhook"""

    id: str
    changes: list[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    """
    Payload from WhatsApp Cloud API webhook.
    حمولة webhook من واتساب السحابي.
    """

    object: str = "whatsapp_business_account"
    entry: list[WhatsAppEntry]


# ============================================================================
# Outgoing Message Models
# ============================================================================


class SendTextContent(BaseModel):
    """محتوى نص للإرسال"""

    body: str
    preview_url: bool = False


class SendImageContent(BaseModel):
    """محتوى صورة للإرسال"""

    link: str | None = None
    id: str | None = None
    caption: str | None = None


class SendLocationContent(BaseModel):
    """محتوى موقع للإرسال"""

    latitude: float
    longitude: float
    name: str | None = None
    address: str | None = None


class InteractiveButton(BaseModel):
    """زر تفاعلي"""

    type: str = "reply"
    reply: dict[str, str]  # {"id": "btn_id", "title": "Button Title"}


class InteractiveAction(BaseModel):
    """إجراء تفاعلي"""

    buttons: list[InteractiveButton] | None = None
    button: str | None = None  # For list messages
    sections: list[dict[str, Any]] | None = None  # For list messages


class InteractiveHeader(BaseModel):
    """رأس تفاعلي"""

    type: str = "text"  # text, image, video, document
    text: str | None = None
    image: dict[str, str] | None = None


class InteractiveBody(BaseModel):
    """جسم تفاعلي"""

    text: str


class InteractiveFooter(BaseModel):
    """تذييل تفاعلي"""

    text: str


class SendInteractiveContent(BaseModel):
    """محتوى تفاعلي للإرسال"""

    type: InteractiveType  # button or list
    header: InteractiveHeader | None = None
    body: InteractiveBody
    footer: InteractiveFooter | None = None
    action: InteractiveAction


class SendTemplateComponent(BaseModel):
    """مكون قالب"""

    type: str  # header, body, button
    parameters: list[dict[str, Any]]


class SendTemplateContent(BaseModel):
    """محتوى قالب للإرسال"""

    name: str
    language: dict[str, str]  # {"code": "ar" or "en"}
    components: list[SendTemplateComponent] | None = None


class SendMessageRequest(BaseModel):
    """
    Request to send a message via WhatsApp.
    طلب إرسال رسالة عبر واتساب.
    """

    to: str = Field(description="Recipient phone number | رقم هاتف المستلم")
    type: MessageType = Field(default=MessageType.TEXT, description="Message type")

    # Content based on type
    text: SendTextContent | None = None
    image: SendImageContent | None = None
    location: SendLocationContent | None = None
    interactive: SendInteractiveContent | None = None
    template: SendTemplateContent | None = None

    # Optional
    context: dict[str, str] | None = None  # For replies: {"message_id": "..."}


class SendMessageResponse(BaseModel):
    """
    Response after sending a message.
    استجابة بعد إرسال رسالة.
    """

    success: bool
    message_id: str | None = None
    error: str | None = None
    error_ar: str | None = None


class SendTemplateRequest(BaseModel):
    """
    Request to send a template message.
    طلب إرسال رسالة قالب.
    """

    to: str = Field(description="Recipient phone number | رقم هاتف المستلم")
    template_name: str = Field(description="Template name | اسم القالب")
    language_code: str = Field(default="ar", description="Language code (ar/en)")
    components: list[SendTemplateComponent] | None = None


# ============================================================================
# Conversation State Models
# ============================================================================


class MessageContext(BaseModel):
    """سياق الرسالة"""

    message_id: str
    role: str  # user or assistant
    content: str
    content_type: MessageType = MessageType.TEXT
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] | None = None


class FarmerProfile(BaseModel):
    """ملف المزارع"""

    phone_number: str
    name: str | None = None
    name_ar: str | None = None
    language: Language = Language.ARABIC
    location: dict[str, float] | None = None  # {"lat": ..., "lng": ...}
    crops: list[str] | None = None
    field_ids: list[str] | None = None
    registered_at: datetime | None = None


class ConversationState(BaseModel):
    """
    Conversation state for session management.
    حالة المحادثة لإدارة الجلسات.
    """

    phone_number: str = Field(description="User phone number | رقم هاتف المستخدم")
    session_id: str = Field(description="Session ID | معرف الجلسة")

    # User profile
    profile: FarmerProfile | None = None

    # Current conversation context
    current_intent: ConversationIntent = ConversationIntent.UNKNOWN
    language: Language = Language.ARABIC

    # Message history for context
    messages: list[MessageContext] = Field(default_factory=list)

    # Session metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None

    # Custom data for intent handlers
    custom_data: dict[str, Any] = Field(default_factory=dict)

    def add_message(
        self,
        message_id: str,
        role: str,
        content: str,
        content_type: MessageType = MessageType.TEXT,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a message to the conversation history."""
        self.messages.append(
            MessageContext(
                message_id=message_id,
                role=role,
                content=content,
                content_type=content_type,
                metadata=metadata,
            )
        )
        self.updated_at = datetime.utcnow()

    def get_recent_messages(self, limit: int = 10) -> list[MessageContext]:
        """Get the most recent messages."""
        return self.messages[-limit:]

    def get_context_for_llm(self, limit: int = 10) -> list[dict[str, str]]:
        """Get conversation context formatted for LLM."""
        return [{"role": msg.role, "content": msg.content} for msg in self.get_recent_messages(limit)]


# ============================================================================
# Menu & Quick Reply Models
# ============================================================================


class QuickReplyButton(BaseModel):
    """زر رد سريع"""

    id: str
    title: str
    title_ar: str


class MenuSection(BaseModel):
    """قسم القائمة"""

    title: str
    title_ar: str
    rows: list[dict[str, str]]  # [{"id": "...", "title": "...", "description": "..."}]


# Predefined quick reply buttons
MAIN_MENU_BUTTONS = [
    QuickReplyButton(id="btn_disease", title="Crop Disease", title_ar="مرض المحصول"),
    QuickReplyButton(id="btn_irrigation", title="Irrigation", title_ar="الري"),
    QuickReplyButton(id="btn_weather", title="Weather", title_ar="الطقس"),
]

HELP_BUTTONS = [
    QuickReplyButton(id="btn_menu", title="Main Menu", title_ar="القائمة الرئيسية"),
    QuickReplyButton(id="btn_language", title="Change Language", title_ar="تغيير اللغة"),
    QuickReplyButton(id="btn_contact", title="Contact Support", title_ar="تواصل مع الدعم"),
]
