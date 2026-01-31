"""Notification utilities for Supply Chain Service."""

from datetime import datetime
from typing import Optional
from uuid import UUID

import structlog

from ..core.config import settings

logger = structlog.get_logger()


class NotificationService:
    """Service for sending notifications to farmers."""

    def __init__(self) -> None:
        """Initialize notification service."""
        self.notification_url = settings.NOTIFICATION_SERVICE_URL
        self.sms_enabled = settings.SMS_ENABLED
        self.push_enabled = settings.PUSH_ENABLED
        self.email_enabled = settings.EMAIL_ENABLED

    async def send_order_confirmation(
        self,
        farmer_id: UUID,
        order_id: UUID,
        order_total: float,
        estimated_delivery: datetime,
        phone: str | None = None,
        email: str | None = None,
    ) -> dict:
        """Send order confirmation notification.

        Args:
            farmer_id: Farmer UUID
            order_id: Order UUID
            order_total: Total order amount
            estimated_delivery: Estimated delivery date
            phone: Optional phone for SMS
            email: Optional email address

        Returns:
            Notification result
        """
        logger.info(
            "sending_order_confirmation",
            farmer_id=str(farmer_id),
            order_id=str(order_id),
        )

        message_en = (
            f"Your order #{str(order_id)[:8]} has been confirmed. "
            f"Total: {order_total:.2f} SAR. "
            f"Estimated delivery: {estimated_delivery.strftime('%Y-%m-%d')}."
        )

        message_ar = (
            f"تم تأكيد طلبك رقم #{str(order_id)[:8]}. "
            f"المجموع: {order_total:.2f} ريال. "
            f"التوصيل المتوقع: {estimated_delivery.strftime('%Y-%m-%d')}."
        )

        results = {
            "sms": None,
            "push": None,
            "email": None,
        }

        if self.sms_enabled and phone:
            results["sms"] = await self._send_sms(phone, message_ar)

        if self.push_enabled:
            results["push"] = await self._send_push(
                farmer_id,
                title="Order Confirmed | تم تأكيد الطلب",
                body=message_ar,
                data={"order_id": str(order_id)},
            )

        if self.email_enabled and email:
            results["email"] = await self._send_email(
                email,
                subject="Order Confirmed | تم تأكيد الطلب",
                body_en=message_en,
                body_ar=message_ar,
            )

        return results

    async def send_delivery_update(
        self,
        farmer_id: UUID,
        order_id: UUID,
        status: str,
        status_ar: str,
        eta: datetime | None = None,
        phone: str | None = None,
    ) -> dict:
        """Send delivery status update.

        Args:
            farmer_id: Farmer UUID
            order_id: Order UUID
            status: Delivery status in English
            status_ar: Delivery status in Arabic
            eta: Estimated time of arrival
            phone: Optional phone for SMS

        Returns:
            Notification result
        """
        logger.info(
            "sending_delivery_update",
            farmer_id=str(farmer_id),
            order_id=str(order_id),
            status=status,
        )

        message_ar = f"تحديث الطلب #{str(order_id)[:8]}: {status_ar}"
        if eta:
            message_ar += f". الوصول المتوقع: {eta.strftime('%H:%M')}"

        results = {
            "sms": None,
            "push": None,
        }

        if self.sms_enabled and phone:
            results["sms"] = await self._send_sms(phone, message_ar)

        if self.push_enabled:
            results["push"] = await self._send_push(
                farmer_id,
                title="Delivery Update | تحديث التوصيل",
                body=message_ar,
                data={
                    "order_id": str(order_id),
                    "status": status,
                },
            )

        return results

    async def send_order_shipped(
        self,
        farmer_id: UUID,
        order_id: UUID,
        tracking_url: str,
        phone: str | None = None,
    ) -> dict:
        """Send notification when order is shipped.

        Args:
            farmer_id: Farmer UUID
            order_id: Order UUID
            tracking_url: Tracking URL
            phone: Optional phone for SMS

        Returns:
            Notification result
        """
        logger.info(
            "sending_order_shipped",
            farmer_id=str(farmer_id),
            order_id=str(order_id),
        )

        message_ar = (
            f"تم شحن طلبك رقم #{str(order_id)[:8]}. "
            f"تتبع شحنتك: {tracking_url}"
        )

        results = {
            "sms": None,
            "push": None,
        }

        if self.sms_enabled and phone:
            results["sms"] = await self._send_sms(phone, message_ar)

        if self.push_enabled:
            results["push"] = await self._send_push(
                farmer_id,
                title="Order Shipped | تم الشحن",
                body=message_ar,
                data={
                    "order_id": str(order_id),
                    "tracking_url": tracking_url,
                },
            )

        return results

    async def send_order_delivered(
        self,
        farmer_id: UUID,
        order_id: UUID,
        phone: str | None = None,
    ) -> dict:
        """Send notification when order is delivered.

        Args:
            farmer_id: Farmer UUID
            order_id: Order UUID
            phone: Optional phone for SMS

        Returns:
            Notification result
        """
        logger.info(
            "sending_order_delivered",
            farmer_id=str(farmer_id),
            order_id=str(order_id),
        )

        message_ar = (
            f"تم توصيل طلبك رقم #{str(order_id)[:8]} بنجاح. "
            f"شكراً لتعاملك معنا!"
        )

        results = {
            "sms": None,
            "push": None,
        }

        if self.sms_enabled and phone:
            results["sms"] = await self._send_sms(phone, message_ar)

        if self.push_enabled:
            results["push"] = await self._send_push(
                farmer_id,
                title="Order Delivered | تم التوصيل",
                body=message_ar,
                data={"order_id": str(order_id)},
            )

        return results

    async def send_price_alert(
        self,
        farmer_id: UUID,
        product_name: str,
        product_name_ar: str,
        old_price: float,
        new_price: float,
        supplier_name: str,
    ) -> dict:
        """Send price drop alert.

        Args:
            farmer_id: Farmer UUID
            product_name: Product name in English
            product_name_ar: Product name in Arabic
            old_price: Previous price
            new_price: New price
            supplier_name: Supplier name

        Returns:
            Notification result
        """
        logger.info(
            "sending_price_alert",
            farmer_id=str(farmer_id),
            product=product_name,
            old_price=old_price,
            new_price=new_price,
        )

        discount = ((old_price - new_price) / old_price) * 100

        message_ar = (
            f"تنبيه سعر: {product_name_ar} "
            f"انخفض من {old_price:.2f} إلى {new_price:.2f} ريال "
            f"(خصم {discount:.0f}%) عند {supplier_name}"
        )

        if self.push_enabled:
            return await self._send_push(
                farmer_id,
                title="Price Alert | تنبيه سعر",
                body=message_ar,
                data={
                    "type": "price_alert",
                    "product_name": product_name,
                    "new_price": str(new_price),
                },
            )

        return {"push": None}

    async def _send_sms(self, phone: str, message: str) -> dict:
        """Send SMS message.

        Args:
            phone: Phone number
            message: Message content

        Returns:
            SMS result
        """
        logger.info("sending_sms", phone=phone[:4] + "****")

        # Mock SMS sending
        # In production, integrate with SMS gateway
        return {
            "status": "sent",
            "phone": phone,
            "message_id": f"sms_{datetime.utcnow().timestamp()}",
        }

    async def _send_push(
        self,
        farmer_id: UUID,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> dict:
        """Send push notification.

        Args:
            farmer_id: Farmer UUID
            title: Notification title
            body: Notification body
            data: Additional data payload

        Returns:
            Push notification result
        """
        logger.info("sending_push", farmer_id=str(farmer_id), title=title)

        # Mock push notification
        # In production, call notification-service
        return {
            "status": "sent",
            "farmer_id": str(farmer_id),
            "notification_id": f"push_{datetime.utcnow().timestamp()}",
        }

    async def _send_email(
        self,
        email: str,
        subject: str,
        body_en: str,
        body_ar: str,
    ) -> dict:
        """Send email notification.

        Args:
            email: Email address
            subject: Email subject
            body_en: Email body in English
            body_ar: Email body in Arabic

        Returns:
            Email result
        """
        logger.info("sending_email", email=email.split("@")[0] + "@****")

        # Mock email sending
        # In production, integrate with email service
        return {
            "status": "sent",
            "email": email,
            "message_id": f"email_{datetime.utcnow().timestamp()}",
        }
