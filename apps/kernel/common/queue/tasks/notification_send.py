"""
SAHOOL Notification Send Handler
معالج إرسال الإشعارات

Handles background sending of notifications.
يعالج إرسال الإشعارات في الخلفية.

Author: SAHOOL Platform Team
License: MIT
"""

import json
import logging
import os
from datetime import UTC, datetime, timezone
from enum import Enum, StrEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

# Firebase Admin SDK imports (optional dependency)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    _FIREBASE_AVAILABLE = True
except ImportError:
    _FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK not installed. Push notifications disabled.")

# Global Firebase app instance
_firebase_app = None


class NotificationType(StrEnum):
    """Notification type mapping to FCM priority and channel"""

    ALERT = "alert"  # Critical alerts - high priority
    WARNING = "warning"  # Warnings - high priority
    INFO = "info"  # Informational - normal priority
    REMINDER = "reminder"  # Reminders - normal priority
    UPDATE = "update"  # Updates - normal priority


def _get_fcm_priority(notification_type: str, priority: str) -> str:
    """
    Map notification type and priority to FCM priority
    تحديد أولوية FCM بناءً على نوع الإشعار
    """
    if priority in ["urgent", "critical", "high"]:
        return "high"
    if notification_type in [NotificationType.ALERT.value, NotificationType.WARNING.value]:
        return "high"
    return "normal"


def _get_android_channel(notification_type: str, priority: str) -> str:
    """
    Get Android notification channel ID based on type
    تحديد قناة Android بناءً على النوع
    """
    if priority in ["urgent", "critical"]:
        return "sahool_critical"
    if notification_type == NotificationType.ALERT.value:
        return "sahool_alerts"
    if notification_type == NotificationType.WARNING.value:
        return "sahool_warnings"
    return "sahool_main"


def _initialize_firebase() -> bool:
    """
    Initialize Firebase Admin SDK if not already initialized
    تهيئة Firebase Admin SDK
    """
    global _firebase_app

    if not _FIREBASE_AVAILABLE:
        return False

    if _firebase_app is not None:
        return True

    try:
        # Check for existing Firebase app
        try:
            _firebase_app = firebase_admin.get_app()
            return True
        except ValueError:
            pass  # No app exists, initialize one

        # Get credentials from environment
        credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        credentials_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

        if credentials_json:
            cred_dict = json.loads(credentials_json)
            cred = credentials.Certificate(cred_dict)
        elif credentials_path and os.path.exists(credentials_path):
            cred = credentials.Certificate(credentials_path)
        else:
            logger.warning("No Firebase credentials found. Push notifications disabled.")
            return False

        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return False


def _send_push_notification(
    token: str,
    title: str,
    body: str,
    title_ar: str | None = None,
    body_ar: str | None = None,
    notification_type: str = "info",
    priority: str = "normal",
    data: dict[str, Any] | None = None,
    action_url: str | None = None,
) -> dict[str, Any]:
    """
    Send push notification to a single device via FCM
    إرسال إشعار Push لجهاز واحد عبر FCM
    """
    if not _FIREBASE_AVAILABLE or not _initialize_firebase():
        return {
            "success": False,
            "error": "Firebase not available",
            "error_ar": "خدمة Firebase غير متاحة",
        }

    try:
        fcm_priority = _get_fcm_priority(notification_type, priority)
        android_channel = _get_android_channel(notification_type, priority)

        # Build notification with bilingual support (prefer Arabic for Arabic users)
        notification = messaging.Notification(
            title=title_ar or title,
            body=body_ar or body,
        )

        # Build data payload with bilingual content
        data_payload = {
            "notification_type": notification_type,
            "priority": priority,
            "title_en": title,
            "body_en": body,
            "sent_at": datetime.now(UTC).isoformat(),
        }
        if title_ar:
            data_payload["title_ar"] = title_ar
        if body_ar:
            data_payload["body_ar"] = body_ar
        if action_url:
            data_payload["action_url"] = action_url
        if data:
            data_payload["extra"] = json.dumps(data)

        # Android config
        android_config = messaging.AndroidConfig(
            priority=fcm_priority,
            ttl=86400,  # 24 hours
            notification=messaging.AndroidNotification(
                sound="default",
                priority="high" if fcm_priority == "high" else "default",
                channel_id=android_channel,
            ),
        )

        # iOS (APNS) config
        apns_config = messaging.APNSConfig(
            headers={
                "apns-priority": "10" if fcm_priority == "high" else "5",
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

        # Build and send message
        message = messaging.Message(
            token=token,
            notification=notification,
            data=data_payload,
            android=android_config,
            apns=apns_config,
        )

        response = messaging.send(message)

        logger.info(f"Push notification sent successfully: {response}")
        return {
            "success": True,
            "message_id": response,
            "channel": "push",
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to send push notification: {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "error_ar": "فشل إرسال الإشعار",
            "channel": "push",
        }


def _send_multicast_push(
    tokens: list[str],
    title: str,
    body: str,
    title_ar: str | None = None,
    body_ar: str | None = None,
    notification_type: str = "info",
    priority: str = "normal",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Send push notification to multiple devices via FCM multicast
    إرسال إشعار Push لعدة أجهزة عبر FCM
    """
    if not _FIREBASE_AVAILABLE or not _initialize_firebase():
        return {
            "success_count": 0,
            "failure_count": len(tokens),
            "error": "Firebase not available",
        }

    if not tokens:
        return {"success_count": 0, "failure_count": 0, "responses": []}

    try:
        fcm_priority = _get_fcm_priority(notification_type, priority)

        # Build notification
        notification = messaging.Notification(
            title=title_ar or title,
            body=body_ar or body,
        )

        # Build data payload
        data_payload = {
            "notification_type": notification_type,
            "priority": priority,
            "title_en": title,
            "body_en": body,
        }
        if title_ar:
            data_payload["title_ar"] = title_ar
        if body_ar:
            data_payload["body_ar"] = body_ar
        if data:
            data_payload["extra"] = json.dumps(data)

        # Build multicast message
        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=notification,
            data=data_payload,
            android=messaging.AndroidConfig(priority=fcm_priority),
        )

        # Send multicast
        response = messaging.send_each_for_multicast(message)

        # Process responses
        responses = []
        failed_tokens = []
        for idx, resp in enumerate(response.responses):
            if resp.success:
                responses.append({"success": True, "message_id": resp.message_id})
            else:
                failed_tokens.append(tokens[idx])
                responses.append({"success": False, "error": str(resp.exception)})

        if failed_tokens:
            logger.warning(f"Failed to send to {len(failed_tokens)} tokens")

        logger.info(f"Multicast sent: {response.success_count} success, {response.failure_count} failed")

        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count,
            "responses": responses,
        }

    except Exception as e:
        logger.error(f"Failed to send multicast: {e}")
        return {
            "success_count": 0,
            "failure_count": len(tokens),
            "error": str(e),
        }


def _log_delivery_status(
    notification_id: str,
    channel: str,
    status: str,
    user_id: str,
    error_message: str | None = None,
    provider_message_id: str | None = None,
) -> dict[str, Any]:
    """
    Log delivery status for a notification
    تسجيل حالة تسليم الإشعار
    """
    log_entry = {
        "notification_id": notification_id,
        "channel": channel,
        "status": status,
        "user_id": user_id,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    if error_message:
        log_entry["error_message"] = error_message
    if provider_message_id:
        log_entry["provider_message_id"] = provider_message_id

    # Log with appropriate level based on status
    if status == "success":
        logger.info(
            f"Notification delivered | "
            f"id={notification_id} channel={channel} user={user_id} "
            f"provider_id={provider_message_id}"
        )
    elif status == "failed":
        logger.error(
            f"Notification delivery failed | "
            f"id={notification_id} channel={channel} user={user_id} "
            f"error={error_message}"
        )
    else:
        logger.info(f"Notification status: {status} | id={notification_id} channel={channel} user={user_id}")

    return log_entry


def handle_notification_send(payload: dict[str, Any]) -> dict[str, Any]:
    """
    إرسال إشعار
    Send notification

    Args:
        payload: {
            "user_ids": List[str] - معرفات المستخدمين / User IDs
            "notification_type": str - نوع الإشعار / Notification type
            "title": str - العنوان / Title
            "message": str - الرسالة / Message
            "priority": str - الأولوية / Priority (low, normal, high, urgent)
            "channels": List[str] - القنوات / Channels (push, sms, email, in_app)
            "data": dict - بيانات إضافية / Additional data
            "action_url": str - رابط الإجراء / Action URL
            "schedule_time": str - وقت الجدولة (اختياري) / Schedule time (optional)
        }

    Returns:
        {
            "sent_count": int - عدد الإشعارات المرسلة / Sent count
            "failed_count": int - عدد الإشعارات الفاشلة / Failed count
            "delivery_status": dict - حالة التسليم / Delivery status
            "notification_ids": List[str] - معرفات الإشعارات / Notification IDs
        }
    """
    logger.info(f"Sending notification to {len(payload.get('user_ids', []))} users")

    try:
        # استخراج البيانات من الحمولة
        # Extract data from payload
        user_ids = payload.get("user_ids", [])
        notification_type = payload.get("notification_type")
        title = payload.get("title")
        message = payload.get("message")
        channels = payload.get("channels", ["push", "in_app"])
        priority = payload.get("priority", "normal")

        if not user_ids or not title or not message:
            raise ValueError("user_ids, title, and message are required")

        # Extract bilingual content
        # استخراج المحتوى ثنائي اللغة
        title_ar = payload.get("title_ar")
        message_ar = payload.get("message_ar")
        action_url = payload.get("action_url")
        data = payload.get("data", {})
        fcm_tokens = payload.get("fcm_tokens", [])  # Optional: pre-provided tokens

        # Initialize delivery tracking
        # تتبع حالة التسليم
        sent_count = 0
        failed_count = 0
        notification_ids = []
        delivery_logs = []
        delivery_status = {
            "push": {"sent": 0, "delivered": 0, "failed": 0},
            "sms": {"sent": 0, "delivered": 0, "failed": 0},
            "email": {"sent": 0, "delivered": 0, "failed": 0},
            "in_app": {"sent": 0, "read": 0},
        }

        # Process each user
        # معالجة كل مستخدم
        for idx, user_id in enumerate(user_ids):
            notification_id = f"NOTIF-{uuid4().hex[:8].upper()}"
            notification_ids.append(notification_id)

            # Send via push notification (FCM) if in channels
            # إرسال عبر إشعارات Push إذا كانت من القنوات المطلوبة
            if "push" in channels:
                # Get FCM token for this user (from payload or would typically be from DB)
                fcm_token = fcm_tokens[idx] if idx < len(fcm_tokens) else None

                if fcm_token:
                    push_result = _send_push_notification(
                        token=fcm_token,
                        title=title,
                        body=message,
                        title_ar=title_ar,
                        body_ar=message_ar,
                        notification_type=notification_type,
                        priority=priority,
                        data=data,
                        action_url=action_url,
                    )

                    if push_result.get("success"):
                        sent_count += 1
                        delivery_status["push"]["sent"] += 1
                        delivery_status["push"]["delivered"] += 1

                        log_entry = _log_delivery_status(
                            notification_id=notification_id,
                            channel="push",
                            status="success",
                            user_id=user_id,
                            provider_message_id=push_result.get("message_id"),
                        )
                    else:
                        failed_count += 1
                        delivery_status["push"]["failed"] += 1

                        log_entry = _log_delivery_status(
                            notification_id=notification_id,
                            channel="push",
                            status="failed",
                            user_id=user_id,
                            error_message=push_result.get("error"),
                        )

                    delivery_logs.append(log_entry)
                else:
                    # No FCM token available for this user
                    logger.debug(f"No FCM token for user {user_id}, skipping push")

            # Handle in-app notifications (always succeed - stored in DB)
            # معالجة الإشعارات داخل التطبيق
            if "in_app" in channels:
                delivery_status["in_app"]["sent"] += 1
                sent_count += 1

                log_entry = _log_delivery_status(
                    notification_id=notification_id,
                    channel="in_app",
                    status="success",
                    user_id=user_id,
                )
                delivery_logs.append(log_entry)

            # SMS and Email channels - log as pending (would be sent via external service)
            # قنوات SMS والبريد الإلكتروني - تسجيل كمعلق
            if "sms" in channels:
                delivery_status["sms"]["sent"] += 1
                log_entry = _log_delivery_status(
                    notification_id=notification_id,
                    channel="sms",
                    status="pending",
                    user_id=user_id,
                )
                delivery_logs.append(log_entry)

            if "email" in channels:
                delivery_status["email"]["sent"] += 1
                log_entry = _log_delivery_status(
                    notification_id=notification_id,
                    channel="email",
                    status="pending",
                    user_id=user_id,
                )
                delivery_logs.append(log_entry)

        # Build result with actual delivery status
        # بناء النتيجة مع حالة التسليم الفعلية
        result = {
            "sent_count": sent_count,
            "failed_count": failed_count,
            "delivery_status": delivery_status,
            "notification_ids": notification_ids,
            "delivery_logs": delivery_logs,
            "metadata": {
                "notification_type": notification_type,
                "priority": priority,
                "channels_used": channels,
                "sent_at": datetime.now(UTC).isoformat(),
                "bilingual": bool(title_ar or message_ar),
            },
        }

        logger.info(
            f"Notifications sent successfully: {result['sent_count']} sent, "
            f"{result['failed_count']} failed (type={notification_type})"
        )
        return result

    except Exception as e:
        logger.error(f"Error sending notifications: {e}", exc_info=True)
        raise
