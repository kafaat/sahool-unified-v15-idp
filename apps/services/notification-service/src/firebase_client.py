"""
SAHOOL Firebase Cloud Messaging Client
عميل إرسال الإشعارات عبر Firebase

Features:
- Firebase Admin SDK integration
- Send individual notifications
- Send to topics (broadcast)
- Send multicast to multiple tokens
- Topic subscription management
- Retry logic for failed sends
- Arabic/English bilingual support
"""

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Any

logger = logging.getLogger(__name__)

# Firebase Admin SDK imports
try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    _FIREBASE_AVAILABLE = True
except ImportError:
    _FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not installed. Install with: pip install firebase-admin")


class NotificationPriority(StrEnum):
    """أولوية الإشعار"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FirebaseNotification:
    """نموذج إشعار Firebase"""

    title: str
    body: str
    title_ar: str | None = None
    body_ar: str | None = None
    image_url: str | None = None

    def to_dict(self, language: str = "ar") -> dict[str, str]:
        """تحويل إلى قاموس لـ Firebase"""
        if language == "ar" and self.title_ar:
            return {
                "title": self.title_ar,
                "body": self.body_ar or self.body,
            }
        return {
            "title": self.title,
            "body": self.body,
        }


@dataclass
class FirebaseData:
    """بيانات إضافية للإشعار"""

    notification_type: str
    priority: NotificationPriority
    action_url: str | None = None
    field_id: str | None = None
    crop_type: str | None = None
    extra: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, str]:
        """تحويل إلى قاموس (كل القيم نصية)"""
        data = {
            "type": self.notification_type,
            "priority": self.priority.value,
        }

        if self.action_url:
            data["action_url"] = self.action_url
        if self.field_id:
            data["field_id"] = self.field_id
        if self.crop_type:
            data["crop_type"] = self.crop_type
        if self.extra:
            # Convert extra dict to JSON string
            data["extra"] = json.dumps(self.extra)

        return data


class FirebaseClient:
    """
    عميل Firebase للإشعارات

    Example:
        client = FirebaseClient()
        client.initialize("path/to/service-account.json")

        # Send to single device
        client.send_notification(
            token="device_fcm_token",
            title="Weather Alert",
            body="Frost expected tonight",
            data={"type": "weather_alert", "severity": "high"}
        )

        # Send to topic
        client.send_to_topic(
            topic="weather_alerts_sanaa",
            title="تنبيه طقس",
            body="صقيع متوقع الليلة"
        )
    """

    def __init__(self):
        self._initialized = False
        self._app = None

    def initialize(
        self,
        credentials_path: str | None = None,
        credentials_dict: dict[str, Any] | None = None,
    ) -> bool:
        """
        تهيئة Firebase Admin SDK

        Args:
            credentials_path: مسار ملف service account JSON
            credentials_dict: بيانات service account كـ dictionary

        Returns:
            True if initialization successful
        """
        if not _FIREBASE_AVAILABLE:
            logger.error("Firebase Admin SDK not available")
            return False

        if self._initialized:
            logger.info("Firebase already initialized")
            return True

        try:
            # Get credentials from environment if not provided
            if not credentials_path and not credentials_dict:
                credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

                if credentials_json:
                    credentials_dict = json.loads(credentials_json)
                elif not credentials_path:
                    logger.error("No Firebase credentials provided")
                    return False

            # Initialize Firebase
            if credentials_dict:
                cred = credentials.Certificate(credentials_dict)
            else:
                cred = credentials.Certificate(credentials_path)

            self._app = firebase_admin.initialize_app(cred)
            self._initialized = True

            logger.info("✅ Firebase Admin SDK initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False

    def _check_initialized(self) -> bool:
        """تحقق من التهيئة"""
        if not self._initialized:
            logger.warning("Firebase not initialized. Call initialize() first.")
            return False
        return True

    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        title_ar: str | None = None,
        body_ar: str | None = None,
        data: dict[str, str] | None = None,
        image_url: str | None = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        ttl: int = 86400,  # 24 hours
    ) -> str | None:
        """
        إرسال إشعار لجهاز واحد

        Args:
            token: FCM token للجهاز
            title: عنوان الإشعار (English)
            body: نص الإشعار (English)
            title_ar: عنوان الإشعار (Arabic)
            body_ar: نص الإشعار (Arabic)
            data: بيانات إضافية
            image_url: رابط صورة
            priority: أولوية الإشعار
            ttl: Time to live بالثواني

        Returns:
            Message ID if successful, None otherwise
        """
        if not self._check_initialized():
            return None

        try:
            # Build notification
            notification = messaging.Notification(
                title=title_ar or title,
                body=body_ar or body,
                image=image_url,
            )

            # Build data payload
            data_payload = data or {}
            if title_ar and body_ar:
                data_payload["title_en"] = title
                data_payload["body_en"] = body

            # Build Android config
            android_config = messaging.AndroidConfig(
                priority=(
                    "high" if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else "normal"
                ),
                ttl=ttl,
                notification=messaging.AndroidNotification(
                    sound="default",
                    priority=("high" if priority == NotificationPriority.CRITICAL else "default"),
                    channel_id=("sahool_alerts" if priority == NotificationPriority.CRITICAL else "sahool_main"),
                ),
            )

            # Build iOS config
            apns_config = messaging.APNSConfig(
                headers={
                    "apns-priority": (
                        "10" if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL] else "5"
                    ),
                },
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title_ar or title,
                            body=body_ar or body,
                        ),
                        badge=1,
                        sound="default",
                    ),
                ),
            )

            # Build message
            message = messaging.Message(
                token=token,
                notification=notification,
                data=data_payload,
                android=android_config,
                apns=apns_config,
            )

            # Send message
            response = messaging.send(message)
            logger.info(f"📬 Notification sent successfully: {response}")
            return response

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return None

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        title_ar: str | None = None,
        body_ar: str | None = None,
        data: dict[str, str] | None = None,
        image_url: str | None = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> str | None:
        """
        إرسال إشعار لموضوع (topic)

        Args:
            topic: اسم الموضوع (e.g., "weather_sanaa", "all_farmers")
            title: عنوان الإشعار
            body: نص الإشعار
            title_ar: عنوان بالعربية
            body_ar: نص بالعربية
            data: بيانات إضافية
            image_url: رابط صورة
            priority: أولوية الإشعار

        Returns:
            Message ID if successful
        """
        if not self._check_initialized():
            return None

        try:
            # Build notification
            notification = messaging.Notification(
                title=title_ar or title,
                body=body_ar or body,
                image=image_url,
            )

            # Build data payload
            data_payload = data or {}

            # Build message
            message = messaging.Message(
                topic=topic,
                notification=notification,
                data=data_payload,
            )

            # Send message
            response = messaging.send(message)
            logger.info(f"📢 Topic notification sent to '{topic}': {response}")
            return response

        except Exception as e:
            logger.error(f"Failed to send topic notification: {e}")
            return None

    def send_multicast(
        self,
        tokens: list[str],
        title: str,
        body: str,
        title_ar: str | None = None,
        body_ar: str | None = None,
        data: dict[str, str] | None = None,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
    ) -> dict[str, Any]:
        """
        إرسال إشعار لعدة أجهزة

        Args:
            tokens: قائمة FCM tokens
            title: عنوان الإشعار
            body: نص الإشعار
            title_ar: عنوان بالعربية
            body_ar: نص بالعربية
            data: بيانات إضافية
            priority: أولوية الإشعار

        Returns:
            Dict with success_count, failure_count, responses
        """
        if not self._check_initialized():
            return {"success_count": 0, "failure_count": len(tokens), "responses": []}

        if not tokens:
            return {"success_count": 0, "failure_count": 0, "responses": []}

        try:
            # Build notification
            notification = messaging.Notification(
                title=title_ar or title,
                body=body_ar or body,
            )

            # Build data payload
            data_payload = data or {}

            # Build multicast message
            message = messaging.MulticastMessage(
                tokens=tokens,
                notification=notification,
                data=data_payload,
            )

            # Send multicast
            response = messaging.send_multicast(message)

            logger.info(
                f"📬 Multicast sent: {response.success_count} successful, "
                f"{response.failure_count} failed out of {len(tokens)} tokens"
            )

            # Log failed tokens
            if response.failure_count > 0:
                failed_tokens = []
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        failed_tokens.append(tokens[idx])
                        logger.warning(f"Failed to send to token {idx}: {resp.exception}")

                logger.warning(f"Failed tokens: {failed_tokens}")

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [
                    {
                        "success": r.success,
                        "message_id": r.message_id if r.success else None,
                        "error": str(r.exception) if not r.success else None,
                    }
                    for r in response.responses
                ],
            }

        except Exception as e:
            logger.error(f"Failed to send multicast: {e}")
            return {
                "success_count": 0,
                "failure_count": len(tokens),
                "responses": [],
                "error": str(e),
            }

    def subscribe_to_topic(self, tokens: str | list[str], topic: str) -> dict[str, int]:
        """
        اشتراك أجهزة في موضوع

        Args:
            tokens: FCM token أو قائمة tokens
            topic: اسم الموضوع

        Returns:
            Dict with success_count and failure_count
        """
        if not self._check_initialized():
            return {"success_count": 0, "failure_count": 1}

        if isinstance(tokens, str):
            tokens = [tokens]

        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logger.info(f"✅ Subscribed {response.success_count} devices to topic '{topic}'")

            if response.failure_count > 0:
                logger.warning(f"Failed to subscribe {response.failure_count} devices")

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }

        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {e}")
            return {"success_count": 0, "failure_count": len(tokens)}

    def unsubscribe_from_topic(self, tokens: str | list[str], topic: str) -> dict[str, int]:
        """
        إلغاء اشتراك أجهزة من موضوع

        Args:
            tokens: FCM token أو قائمة tokens
            topic: اسم الموضوع

        Returns:
            Dict with success_count and failure_count
        """
        if not self._check_initialized():
            return {"success_count": 0, "failure_count": 1}

        if isinstance(tokens, str):
            tokens = [tokens]

        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logger.info(f"✅ Unsubscribed {response.success_count} devices from topic '{topic}'")

            if response.failure_count > 0:
                logger.warning(f"Failed to unsubscribe {response.failure_count} devices")

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
            }

        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic: {e}")
            return {"success_count": 0, "failure_count": len(tokens)}

    def send_with_retry(self, token: str, title: str, body: str, max_retries: int = 3, **kwargs) -> str | None:
        """
        إرسال إشعار مع إعادة المحاولة

        Args:
            token: FCM token
            title: عنوان الإشعار
            body: نص الإشعار
            max_retries: عدد المحاولات
            **kwargs: معاملات إضافية لـ send_notification

        Returns:
            Message ID if successful
        """
        for attempt in range(max_retries):
            result = self.send_notification(token, title, body, **kwargs)
            if result:
                return result

            if attempt < max_retries - 1:
                logger.warning(f"Retry {attempt + 1}/{max_retries} for token {token[:20]}...")

        logger.error(f"Failed to send notification after {max_retries} attempts")
        return None


# Global client instance
_firebase_client: FirebaseClient | None = None


def get_firebase_client() -> FirebaseClient:
    """
    الحصول على instance عام من FirebaseClient

    Returns:
        FirebaseClient instance
    """
    global _firebase_client

    if _firebase_client is None:
        _firebase_client = FirebaseClient()

        # Auto-initialize if credentials available
        credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

        if credentials_path or credentials_json:
            _firebase_client.initialize()

    return _firebase_client
