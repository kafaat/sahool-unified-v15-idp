"""
SAHOOL Notification Service - Multi-channel Notification Management
====================================================================
Layer: Execution (Layer 4)
Purpose: Send notifications via email, SMS, push, in-app; manage templates and preferences
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import uuid
import json

from fastapi import FastAPI, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Integer,
    select,
    update,
    func,
    delete,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import enum
from jinja2 import Environment, BaseLoader
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx

# Shared imports
import sys

sys.path.insert(0, "/app/shared")
from database import Database, BaseModel as DBBaseModel
from events.base_event import BaseEvent, EventBus
from utils.logging import setup_logging
from metrics import MetricsManager

# ============================================================================
# Configuration
# ============================================================================


class Settings:
    """Notification service configuration"""

    SERVICE_NAME = "notification-service"
    SERVICE_PORT = int(os.getenv("NOTIFICATION_SERVICE_PORT", "8086"))

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_notifications",
    )
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")

    # Email Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@sahool.app")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "SAHOOL Platform")

    # SMS Configuration (Twilio-like)
    SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio")
    SMS_API_KEY = os.getenv("SMS_API_KEY", "")
    SMS_API_SECRET = os.getenv("SMS_API_SECRET", "")
    SMS_FROM_NUMBER = os.getenv("SMS_FROM_NUMBER", "")

    # Push Notification (Firebase)
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "")

    # Rate Limiting
    MAX_NOTIFICATIONS_PER_HOUR = int(os.getenv("MAX_NOTIFICATIONS_PER_HOUR", "100"))

    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 60


settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

notifications_sent = Counter(
    "notifications_sent_total", "Notifications sent", ["channel", "status", "template"]
)
notification_latency = Histogram(
    "notification_latency_seconds", "Notification delivery latency", ["channel"]
)

# ============================================================================
# Database Models
# ============================================================================


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationTemplate(DBBaseModel):
    """Notification templates for different event types"""

    __tablename__ = "notification_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Event type this template handles
    event_type = Column(String(100), nullable=False, index=True)

    # Channel-specific templates
    email_subject = Column(String(255), nullable=True)
    email_subject_ar = Column(String(255), nullable=True)
    email_body_html = Column(Text, nullable=True)
    email_body_html_ar = Column(Text, nullable=True)
    email_body_text = Column(Text, nullable=True)
    email_body_text_ar = Column(Text, nullable=True)

    sms_body = Column(String(500), nullable=True)
    sms_body_ar = Column(String(500), nullable=True)

    push_title = Column(String(100), nullable=True)
    push_title_ar = Column(String(100), nullable=True)
    push_body = Column(String(255), nullable=True)
    push_body_ar = Column(String(255), nullable=True)
    push_data = Column(JSON, nullable=True)

    in_app_title = Column(String(255), nullable=True)
    in_app_title_ar = Column(String(255), nullable=True)
    in_app_body = Column(Text, nullable=True)
    in_app_body_ar = Column(Text, nullable=True)
    in_app_action_url = Column(String(500), nullable=True)
    in_app_icon = Column(String(100), nullable=True)

    # Default settings
    default_channels = Column(ARRAY(String), default=["in_app"])
    default_priority = Column(String(20), default=NotificationPriority.NORMAL.value)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(DBBaseModel):
    """Individual notification record"""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Template reference
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("notification_templates.id"), nullable=True
    )
    template_code = Column(String(100), nullable=True)

    # Content
    title = Column(String(255), nullable=False)
    title_ar = Column(String(255), nullable=True)
    body = Column(Text, nullable=False)
    body_ar = Column(Text, nullable=True)

    # Delivery
    channel = Column(String(20), nullable=False)
    priority = Column(String(20), default=NotificationPriority.NORMAL.value)
    status = Column(String(20), default=NotificationStatus.PENDING.value)

    # Channel-specific data
    recipient = Column(String(255), nullable=True)  # email, phone, device_token
    channel_data = Column(JSON, nullable=True)

    # Related entity
    entity_type = Column(String(50), nullable=True)  # field, task, alert, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    action_url = Column(String(500), nullable=True)

    # Metadata
    metadata = Column(JSON, default={})

    # Tracking
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Retry
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)


class NotificationBatch(DBBaseModel):
    """Batch notification for bulk sends"""

    __tablename__ = "notification_batches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    template_id = Column(
        UUID(as_uuid=True), ForeignKey("notification_templates.id"), nullable=True
    )

    # Recipients
    recipient_filter = Column(JSON, nullable=True)  # Query to filter recipients
    recipient_count = Column(Integer, default=0)

    # Progress
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)

    status = Column(
        String(20), default="pending"
    )  # pending, processing, completed, failed

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class UserDevice(DBBaseModel):
    """User devices for push notifications"""

    __tablename__ = "user_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    device_token = Column(String(500), unique=True, nullable=False)
    device_type = Column(String(20), nullable=False)  # ios, android, web
    device_name = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# Pydantic Schemas
# ============================================================================


class TemplateCreate(BaseModel):
    """Create notification template"""

    code: str = Field(..., min_length=3, max_length=100)
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None
    event_type: str

    email_subject: Optional[str] = None
    email_subject_ar: Optional[str] = None
    email_body_html: Optional[str] = None
    email_body_html_ar: Optional[str] = None
    email_body_text: Optional[str] = None
    email_body_text_ar: Optional[str] = None

    sms_body: Optional[str] = None
    sms_body_ar: Optional[str] = None

    push_title: Optional[str] = None
    push_title_ar: Optional[str] = None
    push_body: Optional[str] = None
    push_body_ar: Optional[str] = None
    push_data: Optional[Dict[str, Any]] = None

    in_app_title: Optional[str] = None
    in_app_title_ar: Optional[str] = None
    in_app_body: Optional[str] = None
    in_app_body_ar: Optional[str] = None
    in_app_action_url: Optional[str] = None
    in_app_icon: Optional[str] = None

    default_channels: List[str] = ["in_app"]
    default_priority: str = "normal"


class TemplateResponse(BaseModel):
    """Template response"""

    id: uuid.UUID
    code: str
    name: str
    name_ar: Optional[str]
    description: Optional[str]
    event_type: str
    default_channels: List[str]
    default_priority: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SendNotificationRequest(BaseModel):
    """Send notification request"""

    user_id: uuid.UUID
    template_code: Optional[str] = None
    channels: Optional[List[str]] = None
    priority: str = "normal"

    # Direct content (if not using template)
    title: Optional[str] = None
    title_ar: Optional[str] = None
    body: Optional[str] = None
    body_ar: Optional[str] = None

    # Template variables
    variables: Dict[str, Any] = {}

    # Related entity
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    action_url: Optional[str] = None

    metadata: Dict[str, Any] = {}


class NotificationResponse(BaseModel):
    """Notification response"""

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    title_ar: Optional[str]
    body: str
    body_ar: Optional[str]
    channel: str
    priority: str
    status: str
    entity_type: Optional[str]
    entity_id: Optional[uuid.UUID]
    action_url: Optional[str]
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Notification list response"""

    items: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class DeviceRegisterRequest(BaseModel):
    """Register device for push notifications"""

    device_token: str
    device_type: str
    device_name: Optional[str] = None


class BulkNotificationRequest(BaseModel):
    """Bulk notification request"""

    template_code: str
    recipient_user_ids: Optional[List[uuid.UUID]] = None
    recipient_filter: Optional[Dict[str, Any]] = None
    variables: Dict[str, Any] = {}
    channels: Optional[List[str]] = None


# ============================================================================
# Notification Providers
# ============================================================================


class EmailProvider:
    """Email notification provider"""

    def __init__(self):
        self.jinja_env = Environment(loader=BaseLoader())

    async def send(
        self, to_email: str, subject: str, body_html: str, body_text: str
    ) -> bool:
        """Send email notification"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message["To"] = to_email
            message["Subject"] = subject

            # Add text and HTML parts
            message.attach(MIMEText(body_text, "plain", "utf-8"))
            message.attach(MIMEText(body_html, "html", "utf-8"))

            async with aiosmtplib.SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                use_tls=False,
                start_tls=True,
            ) as smtp:
                await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                await smtp.send_message(message)

            logger.info("Email sent", to=to_email, subject=subject)
            return True

        except Exception as e:
            logger.error("Email send failed", to=to_email, error=str(e))
            return False

    def render_template(self, template: str, variables: Dict) -> str:
        """Render Jinja2 template"""
        try:
            tpl = self.jinja_env.from_string(template)
            return tpl.render(**variables)
        except Exception as e:
            logger.error("Template render failed", error=str(e))
            return template


class SMSProvider:
    """SMS notification provider"""

    async def send(self, to_phone: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            # Implement based on SMS provider (Twilio, etc.)
            # This is a placeholder implementation

            if settings.SMS_PROVIDER == "twilio":
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"https://api.twilio.com/2010-04-01/Accounts/{settings.SMS_API_KEY}/Messages.json",
                        auth=(settings.SMS_API_KEY, settings.SMS_API_SECRET),
                        data={
                            "From": settings.SMS_FROM_NUMBER,
                            "To": to_phone,
                            "Body": message,
                        },
                    )
                    return response.status_code == 201

            logger.info("SMS sent", to=to_phone)
            return True

        except Exception as e:
            logger.error("SMS send failed", to=to_phone, error=str(e))
            return False


class PushProvider:
    """Push notification provider (Firebase)"""

    async def send(
        self, device_token: str, title: str, body: str, data: Optional[Dict] = None
    ) -> bool:
        """Send push notification"""
        try:
            # Firebase Cloud Messaging implementation
            if not settings.FIREBASE_PROJECT_ID:
                logger.warning("Firebase not configured")
                return False

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://fcm.googleapis.com/v1/projects/{settings.FIREBASE_PROJECT_ID}/messages:send",
                    headers={
                        "Authorization": f"Bearer {await self._get_access_token()}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "message": {
                            "token": device_token,
                            "notification": {"title": title, "body": body},
                            "data": data or {},
                        }
                    },
                )
                return response.status_code == 200

        except Exception as e:
            logger.error("Push send failed", token=device_token[:20], error=str(e))
            return False

    async def _get_access_token(self) -> str:
        """Get Firebase access token"""
        # Implementation depends on Firebase setup
        return ""


# ============================================================================
# Notification Service
# ============================================================================


class NotificationService:
    """Core notification service"""

    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.email_provider = EmailProvider()
        self.sms_provider = SMSProvider()
        self.push_provider = PushProvider()

    async def send_notification(
        self,
        tenant_id: uuid.UUID,
        request: SendNotificationRequest,
        user_email: Optional[str] = None,
        user_phone: Optional[str] = None,
        user_language: str = "ar",
    ) -> List[Notification]:
        """Send notification through specified channels"""
        notifications = []

        async with self.db.session() as session:
            # Get template if specified
            template = None
            if request.template_code:
                result = await session.execute(
                    select(NotificationTemplate).where(
                        NotificationTemplate.code == request.template_code,
                        NotificationTemplate.is_active == True,
                    )
                )
                template = result.scalar_one_or_none()

            # Determine channels
            channels = request.channels
            if not channels and template:
                channels = template.default_channels
            if not channels:
                channels = ["in_app"]

            # Get user devices for push
            devices = []
            if "push" in channels:
                device_result = await session.execute(
                    select(UserDevice).where(
                        UserDevice.user_id == request.user_id,
                        UserDevice.is_active == True,
                    )
                )
                devices = device_result.scalars().all()

            # Create notification for each channel
            for channel in channels:
                notification = await self._create_channel_notification(
                    session=session,
                    tenant_id=tenant_id,
                    request=request,
                    template=template,
                    channel=channel,
                    user_email=user_email,
                    user_phone=user_phone,
                    user_language=user_language,
                    devices=devices,
                )
                if notification:
                    notifications.append(notification)

            await session.commit()

        # Send notifications asynchronously
        for notification in notifications:
            asyncio.create_task(self._deliver_notification(notification))

        return notifications

    async def _create_channel_notification(
        self,
        session,
        tenant_id: uuid.UUID,
        request: SendNotificationRequest,
        template: Optional[NotificationTemplate],
        channel: str,
        user_email: Optional[str],
        user_phone: Optional[str],
        user_language: str,
        devices: List[UserDevice],
    ) -> Optional[Notification]:
        """Create notification record for specific channel"""

        # Determine content based on template and language
        title = request.title
        title_ar = request.title_ar
        body = request.body
        body_ar = request.body_ar
        recipient = None
        channel_data = {}

        if template:
            variables = request.variables

            if channel == "email":
                if user_language == "ar" and template.email_subject_ar:
                    title = self.email_provider.render_template(
                        template.email_subject_ar, variables
                    )
                elif template.email_subject:
                    title = self.email_provider.render_template(
                        template.email_subject, variables
                    )

                if user_language == "ar" and template.email_body_html_ar:
                    body = self.email_provider.render_template(
                        template.email_body_html_ar, variables
                    )
                elif template.email_body_html:
                    body = self.email_provider.render_template(
                        template.email_body_html, variables
                    )

                channel_data["body_text"] = (
                    self.email_provider.render_template(
                        (
                            template.email_body_text_ar
                            if user_language == "ar"
                            else template.email_body_text
                        ),
                        variables,
                    )
                    if (template.email_body_text_ar or template.email_body_text)
                    else ""
                )

                recipient = user_email

            elif channel == "sms":
                if user_language == "ar" and template.sms_body_ar:
                    body = self.email_provider.render_template(
                        template.sms_body_ar, variables
                    )
                elif template.sms_body:
                    body = self.email_provider.render_template(
                        template.sms_body, variables
                    )
                title = ""
                recipient = user_phone

            elif channel == "push":
                if user_language == "ar" and template.push_title_ar:
                    title = self.email_provider.render_template(
                        template.push_title_ar, variables
                    )
                elif template.push_title:
                    title = self.email_provider.render_template(
                        template.push_title, variables
                    )

                if user_language == "ar" and template.push_body_ar:
                    body = self.email_provider.render_template(
                        template.push_body_ar, variables
                    )
                elif template.push_body:
                    body = self.email_provider.render_template(
                        template.push_body, variables
                    )

                channel_data["push_data"] = template.push_data
                channel_data["device_tokens"] = [d.device_token for d in devices]

            elif channel == "in_app":
                if user_language == "ar" and template.in_app_title_ar:
                    title = self.email_provider.render_template(
                        template.in_app_title_ar, variables
                    )
                elif template.in_app_title:
                    title = self.email_provider.render_template(
                        template.in_app_title, variables
                    )

                if user_language == "ar" and template.in_app_body_ar:
                    body = self.email_provider.render_template(
                        template.in_app_body_ar, variables
                    )
                elif template.in_app_body:
                    body = self.email_provider.render_template(
                        template.in_app_body, variables
                    )

                channel_data["action_url"] = template.in_app_action_url
                channel_data["icon"] = template.in_app_icon

        if not title and not body:
            return None

        notification = Notification(
            tenant_id=tenant_id,
            user_id=request.user_id,
            template_id=template.id if template else None,
            template_code=request.template_code,
            title=title or "",
            title_ar=title_ar,
            body=body or "",
            body_ar=body_ar,
            channel=channel,
            priority=request.priority,
            recipient=recipient,
            channel_data=channel_data,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            action_url=request.action_url,
            metadata=request.metadata,
        )

        session.add(notification)
        await session.flush()

        return notification

    async def _deliver_notification(self, notification: Notification):
        """Deliver notification through its channel"""
        try:
            success = False

            if notification.channel == "email" and notification.recipient:
                success = await self.email_provider.send(
                    to_email=notification.recipient,
                    subject=notification.title,
                    body_html=notification.body,
                    body_text=notification.channel_data.get("body_text", ""),
                )

            elif notification.channel == "sms" and notification.recipient:
                success = await self.sms_provider.send(
                    to_phone=notification.recipient, message=notification.body
                )

            elif notification.channel == "push":
                device_tokens = notification.channel_data.get("device_tokens", [])
                for token in device_tokens:
                    await self.push_provider.send(
                        device_token=token,
                        title=notification.title,
                        body=notification.body,
                        data=notification.channel_data.get("push_data"),
                    )
                success = len(device_tokens) > 0

            elif notification.channel == "in_app":
                # In-app notifications are stored in database, no external delivery needed
                success = True

            # Update notification status
            async with self.db.session() as session:
                result = await session.execute(
                    select(Notification).where(Notification.id == notification.id)
                )
                notif = result.scalar_one_or_none()

                if notif:
                    if success:
                        notif.status = NotificationStatus.SENT.value
                        notif.sent_at = datetime.utcnow()
                    else:
                        notif.status = NotificationStatus.FAILED.value
                        notif.failed_at = datetime.utcnow()
                        notif.retry_count += 1

                        if notif.retry_count < settings.MAX_RETRIES:
                            notif.next_retry_at = datetime.utcnow() + timedelta(
                                seconds=settings.RETRY_DELAY_SECONDS * notif.retry_count
                            )

                    await session.commit()

            # Update metrics
            notifications_sent.labels(
                channel=notification.channel,
                status="success" if success else "failed",
                template=notification.template_code or "direct",
            ).inc()

        except Exception as e:
            logger.error(
                "Notification delivery failed",
                notification_id=str(notification.id),
                error=str(e),
            )

    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        channel: Optional[str] = None,
        unread_only: bool = False,
    ) -> Tuple[List[Notification], int, int]:
        """Get user notifications"""
        async with self.db.session() as session:
            query = select(Notification).where(
                Notification.user_id == user_id,
                Notification.tenant_id == tenant_id,
                Notification.channel == "in_app",  # Only in-app for user queries
            )
            count_query = select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.tenant_id == tenant_id,
                Notification.channel == "in_app",
            )

            if unread_only:
                query = query.where(Notification.read_at.is_(None))
                count_query = count_query.where(Notification.read_at.is_(None))

            # Get total and unread counts
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            unread_result = await session.execute(
                select(func.count(Notification.id)).where(
                    Notification.user_id == user_id,
                    Notification.tenant_id == tenant_id,
                    Notification.channel == "in_app",
                    Notification.read_at.is_(None),
                )
            )
            unread_count = unread_result.scalar()

            # Apply pagination
            offset = (page - 1) * page_size
            query = (
                query.offset(offset)
                .limit(page_size)
                .order_by(Notification.created_at.desc())
            )

            result = await session.execute(query)
            notifications = result.scalars().all()

            return notifications, total, unread_count

    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID):
        """Mark notification as read"""
        async with self.db.session() as session:
            result = await session.execute(
                select(Notification).where(
                    Notification.id == notification_id, Notification.user_id == user_id
                )
            )
            notification = result.scalar_one_or_none()

            if notification and not notification.read_at:
                notification.read_at = datetime.utcnow()
                notification.status = NotificationStatus.READ.value
                await session.commit()

    async def mark_all_as_read(self, user_id: uuid.UUID, tenant_id: uuid.UUID):
        """Mark all notifications as read"""
        async with self.db.session() as session:
            await session.execute(
                update(Notification)
                .where(
                    Notification.user_id == user_id,
                    Notification.tenant_id == tenant_id,
                    Notification.channel == "in_app",
                    Notification.read_at.is_(None),
                )
                .values(read_at=datetime.utcnow(), status=NotificationStatus.READ.value)
            )
            await session.commit()

    async def register_device(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        device_token: str,
        device_type: str,
        device_name: Optional[str] = None,
    ) -> UserDevice:
        """Register device for push notifications"""
        async with self.db.session() as session:
            # Check if device exists
            result = await session.execute(
                select(UserDevice).where(UserDevice.device_token == device_token)
            )
            device = result.scalar_one_or_none()

            if device:
                # Update existing device
                device.user_id = user_id
                device.tenant_id = tenant_id
                device.is_active = True
                device.last_used = datetime.utcnow()
            else:
                # Create new device
                device = UserDevice(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    device_token=device_token,
                    device_type=device_type,
                    device_name=device_name,
                )
                session.add(device)

            await session.commit()
            await session.refresh(device)

            return device

    async def unregister_device(self, device_token: str):
        """Unregister device"""
        async with self.db.session() as session:
            await session.execute(
                delete(UserDevice).where(UserDevice.device_token == device_token)
            )
            await session.commit()

    async def create_template(self, data: TemplateCreate) -> NotificationTemplate:
        """Create notification template"""
        async with self.db.session() as session:
            template = NotificationTemplate(**data.dict())
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template

    async def get_templates(
        self, event_type: Optional[str] = None
    ) -> List[NotificationTemplate]:
        """Get notification templates"""
        async with self.db.session() as session:
            query = select(NotificationTemplate).where(
                NotificationTemplate.is_active == True
            )

            if event_type:
                query = query.where(NotificationTemplate.event_type == event_type)

            result = await session.execute(query)
            return result.scalars().all()


# ============================================================================
# Event Handlers
# ============================================================================


async def handle_alert_created(event: Dict[str, Any], service: NotificationService):
    """Handle alert created event"""
    try:
        await service.send_notification(
            tenant_id=uuid.UUID(event["tenant_id"]),
            request=SendNotificationRequest(
                user_id=uuid.UUID(event.get("user_id", event["tenant_id"])),
                template_code="alert_created",
                variables={
                    "alert_type": event.get("alert_type"),
                    "severity": event.get("severity"),
                    "field_name": event.get("field_name"),
                    "message": event.get("message"),
                },
                entity_type="alert",
                entity_id=(
                    uuid.UUID(event["alert_id"]) if event.get("alert_id") else None
                ),
                priority=(
                    "high"
                    if event.get("severity") in ["high", "critical"]
                    else "normal"
                ),
            ),
        )
    except Exception as e:
        logger.error("Failed to handle alert event", error=str(e))


async def handle_task_assigned(event: Dict[str, Any], service: NotificationService):
    """Handle task assigned event"""
    try:
        await service.send_notification(
            tenant_id=uuid.UUID(event["tenant_id"]),
            request=SendNotificationRequest(
                user_id=uuid.UUID(event["assignee_id"]),
                template_code="task_assigned",
                variables={
                    "task_title": event.get("title"),
                    "field_name": event.get("field_name"),
                    "due_date": event.get("due_date"),
                    "priority": event.get("priority"),
                },
                entity_type="task",
                entity_id=uuid.UUID(event["task_id"]) if event.get("task_id") else None,
            ),
        )
    except Exception as e:
        logger.error("Failed to handle task event", error=str(e))


# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
notification_service: NotificationService = None

# ============================================================================
# FastAPI Application
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, notification_service

    logger.info("Starting Notification Service...")

    db = Database(settings.DATABASE_URL)
    await db.connect()

    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()

    notification_service = NotificationService(db, event_bus)

    # Subscribe to events
    await event_bus.subscribe(
        "alert.created", lambda e: handle_alert_created(e, notification_service)
    )
    await event_bus.subscribe(
        "task.assigned", lambda e: handle_task_assigned(e, notification_service)
    )

    logger.info("Notification Service started successfully")

    yield

    logger.info("Shutting down Notification Service...")
    await event_bus.close()
    await db.disconnect()


app = FastAPI(
    title="SAHOOL Notification Service",
    description="Multi-channel Notification Management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Send Notifications
@app.post("/api/v1/notifications/send", response_model=List[NotificationResponse])
async def send_notification(
    tenant_id: uuid.UUID,
    request: SendNotificationRequest,
    user_email: Optional[str] = None,
    user_phone: Optional[str] = None,
    user_language: str = "ar",
):
    """Send notification to user"""
    notifications = await notification_service.send_notification(
        tenant_id=tenant_id,
        request=request,
        user_email=user_email,
        user_phone=user_phone,
        user_language=user_language,
    )
    return notifications


# User Notifications
@app.get("/api/v1/notifications", response_model=NotificationListResponse)
async def get_notifications(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
):
    """Get user notifications"""
    notifications, total, unread = await notification_service.get_user_notifications(
        user_id=user_id,
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
    )

    return NotificationListResponse(
        items=notifications,
        total=total,
        unread_count=unread,
        page=page,
        page_size=page_size,
    )


@app.post(
    "/api/v1/notifications/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_notification_read(notification_id: uuid.UUID, user_id: uuid.UUID):
    """Mark notification as read"""
    await notification_service.mark_as_read(notification_id, user_id)


@app.post("/api/v1/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(user_id: uuid.UUID, tenant_id: uuid.UUID):
    """Mark all notifications as read"""
    await notification_service.mark_all_as_read(user_id, tenant_id)


# Device Management
@app.post("/api/v1/devices")
async def register_device(
    user_id: uuid.UUID, tenant_id: uuid.UUID, data: DeviceRegisterRequest
):
    """Register device for push notifications"""
    device = await notification_service.register_device(
        user_id=user_id,
        tenant_id=tenant_id,
        device_token=data.device_token,
        device_type=data.device_type,
        device_name=data.device_name,
    )
    return {"id": str(device.id), "status": "registered"}


@app.delete("/api/v1/devices/{device_token}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_device(device_token: str):
    """Unregister device"""
    await notification_service.unregister_device(device_token)


# Templates
@app.post(
    "/api/v1/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(data: TemplateCreate):
    """Create notification template"""
    template = await notification_service.create_template(data)
    return template


@app.get("/api/v1/templates", response_model=List[TemplateResponse])
async def get_templates(event_type: Optional[str] = None):
    """Get notification templates"""
    templates = await notification_service.get_templates(event_type)
    return templates


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
