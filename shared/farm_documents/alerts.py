"""
Farm Document Alerts Module
وحدة تنبيهات وثائق المزرعة

Provides document expiry alerts, renewal reminders,
and compliance notification functionality.

توفر تنبيهات انتهاء صلاحية الوثائق، وتذكيرات التجديد،
ووظائف إشعارات الامتثال.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import structlog

from .models import (
    AlertPriority,
    Certification,
    CertificationStatus,
    DocumentAlert,
    FarmDocument,
)

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Alert Configuration - إعدادات التنبيهات
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AlertConfig:
    """
    Alert configuration
    إعدادات التنبيهات
    """

    # Expiry alert thresholds (days before expiry)
    critical_threshold: int = 7  # 7 days
    high_threshold: int = 14  # 14 days
    medium_threshold: int = 30  # 30 days
    low_threshold: int = 60  # 60 days

    # Certification-specific thresholds
    certification_critical: int = 30  # 30 days
    certification_high: int = 60  # 60 days
    certification_medium: int = 90  # 90 days

    # Renewal reminders
    send_renewal_reminder: bool = True
    renewal_reminder_days: list[int] = None

    # Notification settings
    auto_notify: bool = True
    notification_channels: list[str] = None

    # Alert deduplication
    alert_cooldown_hours: int = 24

    def __post_init__(self):
        if self.renewal_reminder_days is None:
            self.renewal_reminder_days = [90, 60, 30, 14, 7]
        if self.notification_channels is None:
            self.notification_channels = ["email", "push"]


# ─────────────────────────────────────────────────────────────────────────────
# Alert Service - خدمة التنبيهات
# ─────────────────────────────────────────────────────────────────────────────


class AlertService:
    """
    Document alert service
    خدمة تنبيهات الوثائق

    Manages document expiry alerts, renewal reminders, and notifications.
    تدير تنبيهات انتهاء الوثائق، وتذكيرات التجديد، والإشعارات.
    """

    def __init__(
        self,
        config: AlertConfig | None = None,
        notification_callback: Callable | None = None,
    ):
        self.config = config or AlertConfig()
        self.notification_callback = notification_callback

        # In-memory storage for demo/testing
        self._alerts: dict[str, DocumentAlert] = {}
        self._alert_history: list[dict] = []

    # ─────────────────────────────────────────────────────────────────────────
    # Alert Creation - إنشاء التنبيهات
    # ─────────────────────────────────────────────────────────────────────────

    async def create_alert(
        self,
        tenant_id: str,
        farm_id: str,
        alert_type: str,
        title_en: str,
        title_ar: str,
        message_en: str,
        message_ar: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
        document_id: str | None = None,
        certification_id: str | None = None,
        compliance_document_id: str | None = None,
        action_required_en: str | None = None,
        action_required_ar: str | None = None,
        action_due_date: date | None = None,
        recipient_user_ids: list[str] | None = None,
    ) -> DocumentAlert:
        """
        Create a new alert
        إنشاء تنبيه جديد
        """
        alert = DocumentAlert(
            tenant_id=tenant_id,
            farm_id=farm_id,
            document_id=document_id,
            certification_id=certification_id,
            compliance_document_id=compliance_document_id,
            alert_type=alert_type,
            priority=priority,
            title_en=title_en,
            title_ar=title_ar,
            message_en=message_en,
            message_ar=message_ar,
            action_required_en=action_required_en,
            action_required_ar=action_required_ar,
            action_due_date=action_due_date,
            recipient_user_ids=recipient_user_ids or [],
        )

        self._alerts[alert.id] = alert

        logger.info(
            "alert_created",
            alert_id=alert.id,
            alert_type=alert_type,
            priority=priority.value,
            farm_id=farm_id,
        )

        # Send notification if auto-notify enabled
        if self.config.auto_notify and self.notification_callback:
            await self._send_notification(alert)

        return alert

    async def create_expiry_alert(
        self,
        document: FarmDocument,
        recipient_user_ids: list[str] | None = None,
    ) -> DocumentAlert | None:
        """
        Create expiry alert for a document
        إنشاء تنبيه انتهاء للوثيقة
        """
        if document.expiry_date is None:
            return None

        days_until_expiry = document.days_until_expiry
        if days_until_expiry is None or days_until_expiry < 0:
            # Already expired
            priority = AlertPriority.CRITICAL
            title_en = f"Document Expired: {document.title_en}"
            title_ar = f"وثيقة منتهية الصلاحية: {document.title_ar}"
            message_en = (
                f"The document '{document.title_en}' has expired on {document.expiry_date}. Immediate renewal required."
            )
            message_ar = f"انتهت صلاحية الوثيقة '{document.title_ar}' في {document.expiry_date}. مطلوب تجديد فوري."
        elif days_until_expiry <= self.config.critical_threshold:
            priority = AlertPriority.CRITICAL
            title_en = f"Document Expiring Soon: {document.title_en}"
            title_ar = f"وثيقة تنتهي قريباً: {document.title_ar}"
            message_en = (
                f"The document '{document.title_en}' will expire in {days_until_expiry} days ({document.expiry_date})."
            )
            message_ar = (
                f"ستنتهي صلاحية الوثيقة '{document.title_ar}' خلال {days_until_expiry} أيام ({document.expiry_date})."
            )
        elif days_until_expiry <= self.config.high_threshold:
            priority = AlertPriority.HIGH
            title_en = f"Document Expiring: {document.title_en}"
            title_ar = f"وثيقة تنتهي: {document.title_ar}"
            message_en = f"The document '{document.title_en}' will expire in {days_until_expiry} days."
            message_ar = f"ستنتهي صلاحية الوثيقة '{document.title_ar}' خلال {days_until_expiry} يوماً."
        elif days_until_expiry <= self.config.medium_threshold:
            priority = AlertPriority.MEDIUM
            title_en = f"Document Renewal Reminder: {document.title_en}"
            title_ar = f"تذكير تجديد الوثيقة: {document.title_ar}"
            message_en = (
                f"The document '{document.title_en}' will expire in {days_until_expiry} days. Please plan for renewal."
            )
            message_ar = (
                f"ستنتهي صلاحية الوثيقة '{document.title_ar}' خلال {days_until_expiry} يوماً. يرجى التخطيط للتجديد."
            )
        elif days_until_expiry <= self.config.low_threshold:
            priority = AlertPriority.LOW
            title_en = f"Upcoming Document Expiry: {document.title_en}"
            title_ar = f"انتهاء صلاحية قادم: {document.title_ar}"
            message_en = f"The document '{document.title_en}' will expire in {days_until_expiry} days."
            message_ar = f"ستنتهي صلاحية الوثيقة '{document.title_ar}' خلال {days_until_expiry} يوماً."
        else:
            return None  # Not within alert threshold

        # Check for duplicate alerts
        if await self._has_recent_alert(
            document_id=document.id,
            alert_type="EXPIRY",
        ):
            return None

        return await self.create_alert(
            tenant_id=document.tenant_id,
            farm_id=document.farm_id,
            alert_type="EXPIRY",
            priority=priority,
            document_id=document.id,
            title_en=title_en,
            title_ar=title_ar,
            message_en=message_en,
            message_ar=message_ar,
            action_required_en="Renew or replace the document before expiry",
            action_required_ar="تجديد أو استبدال الوثيقة قبل انتهاء الصلاحية",
            action_due_date=document.expiry_date,
            recipient_user_ids=recipient_user_ids,
        )

    async def create_certification_alert(
        self,
        certification: Certification,
        recipient_user_ids: list[str] | None = None,
    ) -> DocumentAlert | None:
        """
        Create expiry alert for a certification
        إنشاء تنبيه انتهاء للشهادة
        """
        days_until_expiry = certification.days_until_expiry

        if days_until_expiry < 0:
            # Already expired
            priority = AlertPriority.CRITICAL
            title_en = f"Certification Expired: {certification.name_en}"
            title_ar = f"شهادة منتهية الصلاحية: {certification.name_ar}"
            message_en = f"The certification '{certification.name_en}' has expired on {certification.expiry_date}. Farm operations may be affected."
            message_ar = f"انتهت صلاحية الشهادة '{certification.name_ar}' في {certification.expiry_date}. قد تتأثر عمليات المزرعة."
        elif days_until_expiry <= self.config.certification_critical:
            priority = AlertPriority.CRITICAL
            title_en = f"Certification Expiring Soon: {certification.name_en}"
            title_ar = f"شهادة تنتهي قريباً: {certification.name_ar}"
            message_en = f"The certification '{certification.name_en}' will expire in {days_until_expiry} days. Schedule renewal audit immediately."
            message_ar = f"ستنتهي صلاحية الشهادة '{certification.name_ar}' خلال {days_until_expiry} يوماً. حدد موعد تدقيق التجديد فوراً."
        elif days_until_expiry <= self.config.certification_high:
            priority = AlertPriority.HIGH
            title_en = f"Certification Renewal Required: {certification.name_en}"
            title_ar = f"مطلوب تجديد الشهادة: {certification.name_ar}"
            message_en = f"The certification '{certification.name_en}' will expire in {days_until_expiry} days. Contact certification body."
            message_ar = (
                f"ستنتهي صلاحية الشهادة '{certification.name_ar}' خلال {days_until_expiry} يوماً. تواصل مع جهة الشهادة."
            )
        elif days_until_expiry <= self.config.certification_medium:
            priority = AlertPriority.MEDIUM
            title_en = f"Certification Renewal Reminder: {certification.name_en}"
            title_ar = f"تذكير تجديد الشهادة: {certification.name_ar}"
            message_en = f"The certification '{certification.name_en}' will expire in {days_until_expiry} days. Start renewal process."
            message_ar = (
                f"ستنتهي صلاحية الشهادة '{certification.name_ar}' خلال {days_until_expiry} يوماً. ابدأ عملية التجديد."
            )
        else:
            return None

        # Check for duplicate alerts
        if await self._has_recent_alert(
            certification_id=certification.id,
            alert_type="CERTIFICATION_EXPIRY",
        ):
            return None

        return await self.create_alert(
            tenant_id=certification.tenant_id,
            farm_id=certification.farm_id,
            alert_type="CERTIFICATION_EXPIRY",
            priority=priority,
            certification_id=certification.id,
            title_en=title_en,
            title_ar=title_ar,
            message_en=message_en,
            message_ar=message_ar,
            action_required_en="Contact certification body and schedule renewal audit",
            action_required_ar="تواصل مع جهة الشهادة وحدد موعد تدقيق التجديد",
            action_due_date=certification.expiry_date,
            recipient_user_ids=recipient_user_ids,
        )

    async def create_compliance_alert(
        self,
        tenant_id: str,
        farm_id: str,
        requirement_code: str,
        requirement_title_en: str,
        requirement_title_ar: str,
        alert_subtype: str,  # "MISSING", "EXPIRED", "NON_COMPLIANT"
        recipient_user_ids: list[str] | None = None,
    ) -> DocumentAlert:
        """
        Create compliance-related alert
        إنشاء تنبيه متعلق بالامتثال
        """
        if alert_subtype == "MISSING":
            priority = AlertPriority.HIGH
            title_en = f"Missing Compliance Document: {requirement_title_en}"
            title_ar = f"وثيقة امتثال مفقودة: {requirement_title_ar}"
            message_en = f"Required document for '{requirement_title_en}' ({requirement_code}) is missing."
            message_ar = f"الوثيقة المطلوبة لـ '{requirement_title_ar}' ({requirement_code}) مفقودة."
            action_en = "Upload the required document to maintain compliance"
            action_ar = "تحميل الوثيقة المطلوبة للحفاظ على الامتثال"
        elif alert_subtype == "EXPIRED":
            priority = AlertPriority.HIGH
            title_en = f"Expired Compliance Document: {requirement_title_en}"
            title_ar = f"وثيقة امتثال منتهية: {requirement_title_ar}"
            message_en = f"The document for '{requirement_title_en}' ({requirement_code}) has expired."
            message_ar = f"انتهت صلاحية الوثيقة لـ '{requirement_title_ar}' ({requirement_code})."
            action_en = "Upload a renewed document to maintain compliance"
            action_ar = "تحميل وثيقة متجددة للحفاظ على الامتثال"
        else:  # NON_COMPLIANT
            priority = AlertPriority.MEDIUM
            title_en = f"Non-Compliant: {requirement_title_en}"
            title_ar = f"غير متوافق: {requirement_title_ar}"
            message_en = f"Requirement '{requirement_title_en}' ({requirement_code}) is marked as non-compliant."
            message_ar = f"المتطلب '{requirement_title_ar}' ({requirement_code}) مصنف كغير متوافق."
            action_en = "Review and address the compliance issue"
            action_ar = "مراجعة ومعالجة مشكلة الامتثال"

        return await self.create_alert(
            tenant_id=tenant_id,
            farm_id=farm_id,
            alert_type="COMPLIANCE",
            priority=priority,
            title_en=title_en,
            title_ar=title_ar,
            message_en=message_en,
            message_ar=message_ar,
            action_required_en=action_en,
            action_required_ar=action_ar,
            recipient_user_ids=recipient_user_ids,
        )

    async def create_audit_reminder(
        self,
        certification: Certification,
        days_until_audit: int,
        recipient_user_ids: list[str] | None = None,
    ) -> DocumentAlert:
        """
        Create reminder for upcoming audit
        إنشاء تذكير للتدقيق القادم
        """
        if days_until_audit <= 7:
            priority = AlertPriority.CRITICAL
        elif days_until_audit <= 14:
            priority = AlertPriority.HIGH
        elif days_until_audit <= 30:
            priority = AlertPriority.MEDIUM
        else:
            priority = AlertPriority.LOW

        return await self.create_alert(
            tenant_id=certification.tenant_id,
            farm_id=certification.farm_id,
            alert_type="AUDIT_REMINDER",
            priority=priority,
            certification_id=certification.id,
            title_en=f"Upcoming Audit: {certification.name_en}",
            title_ar=f"تدقيق قادم: {certification.name_ar}",
            message_en=f"Certification audit for '{certification.name_en}' is scheduled in {days_until_audit} days.",
            message_ar=f"تدقيق الشهادة '{certification.name_ar}' مجدول خلال {days_until_audit} أيام.",
            action_required_en="Ensure all compliance documents are ready for audit",
            action_required_ar="تأكد من أن جميع وثائق الامتثال جاهزة للتدقيق",
            action_due_date=certification.next_audit_date,
            recipient_user_ids=recipient_user_ids,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Alert Management - إدارة التنبيهات
    # ─────────────────────────────────────────────────────────────────────────

    async def get_alert(self, alert_id: str) -> DocumentAlert | None:
        """Get alert by ID"""
        return self._alerts.get(alert_id)

    async def list_alerts(
        self,
        tenant_id: str,
        farm_id: str | None = None,
        alert_type: str | None = None,
        priority: AlertPriority | None = None,
        is_read: bool | None = None,
        is_resolved: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DocumentAlert]:
        """
        List alerts with filters
        قائمة التنبيهات مع الفلاتر
        """
        results = []

        for alert in self._alerts.values():
            if alert.tenant_id != tenant_id:
                continue
            if farm_id and alert.farm_id != farm_id:
                continue
            if alert_type and alert.alert_type != alert_type:
                continue
            if priority and alert.priority != priority:
                continue
            if is_read is not None and alert.is_read != is_read:
                continue
            if is_resolved is not None and alert.is_resolved != is_resolved:
                continue

            results.append(alert)

        # Sort by priority and created_at
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3,
            AlertPriority.INFORMATIONAL: 4,
        }
        results.sort(key=lambda a: (priority_order.get(a.priority, 5), -a.created_at.timestamp()))

        return results[offset : offset + limit]

    async def get_active_alerts(
        self,
        tenant_id: str,
        farm_id: str | None = None,
    ) -> list[DocumentAlert]:
        """
        Get active (unresolved) alerts
        الحصول على التنبيهات النشطة (غير المحلولة)
        """
        return await self.list_alerts(
            tenant_id=tenant_id,
            farm_id=farm_id,
            is_resolved=False,
        )

    async def get_alert_counts(
        self,
        tenant_id: str,
        farm_id: str | None = None,
    ) -> dict:
        """
        Get alert counts by priority and status
        الحصول على عدد التنبيهات حسب الأولوية والحالة
        """
        alerts = await self.list_alerts(
            tenant_id=tenant_id,
            farm_id=farm_id,
        )

        counts = {
            "total": len(alerts),
            "unread": sum(1 for a in alerts if not a.is_read),
            "unresolved": sum(1 for a in alerts if not a.is_resolved),
            "by_priority": {
                "critical": sum(1 for a in alerts if a.priority == AlertPriority.CRITICAL and not a.is_resolved),
                "high": sum(1 for a in alerts if a.priority == AlertPriority.HIGH and not a.is_resolved),
                "medium": sum(1 for a in alerts if a.priority == AlertPriority.MEDIUM and not a.is_resolved),
                "low": sum(1 for a in alerts if a.priority == AlertPriority.LOW and not a.is_resolved),
            },
            "by_type": {},
        }

        for alert in alerts:
            if alert.is_resolved:
                continue
            alert_type = alert.alert_type
            counts["by_type"][alert_type] = counts["by_type"].get(alert_type, 0) + 1

        return counts

    async def mark_as_read(
        self,
        alert_id: str,
        user_id: str,
    ) -> DocumentAlert | None:
        """
        Mark alert as read
        تحديد التنبيه كمقروء
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert.is_read = True
        alert.updated_at = datetime.now(UTC)

        logger.info(
            "alert_marked_read",
            alert_id=alert_id,
            user_id=user_id,
        )

        return alert

    async def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
    ) -> DocumentAlert | None:
        """
        Acknowledge alert
        الإقرار بالتنبيه
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert.is_read = True
        alert.is_acknowledged = True
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now(UTC)
        alert.updated_at = datetime.now(UTC)

        logger.info(
            "alert_acknowledged",
            alert_id=alert_id,
            user_id=user_id,
        )

        return alert

    async def resolve_alert(
        self,
        alert_id: str,
        user_id: str,
        resolution_notes: str | None = None,
    ) -> DocumentAlert | None:
        """
        Resolve alert
        حل التنبيه
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return None

        alert.is_resolved = True
        alert.resolved_by = user_id
        alert.resolved_at = datetime.now(UTC)
        alert.resolution_notes = resolution_notes
        alert.updated_at = datetime.now(UTC)

        logger.info(
            "alert_resolved",
            alert_id=alert_id,
            user_id=user_id,
        )

        return alert

    async def bulk_resolve(
        self,
        alert_ids: list[str],
        user_id: str,
        resolution_notes: str | None = None,
    ) -> int:
        """
        Resolve multiple alerts
        حل عدة تنبيهات
        """
        resolved_count = 0
        for alert_id in alert_ids:
            if await self.resolve_alert(alert_id, user_id, resolution_notes):
                resolved_count += 1
        return resolved_count

    # ─────────────────────────────────────────────────────────────────────────
    # Alert Scanning - فحص التنبيهات
    # ─────────────────────────────────────────────────────────────────────────

    async def scan_documents_for_expiry(
        self,
        documents: list[FarmDocument],
        recipient_user_ids: list[str] | None = None,
    ) -> list[DocumentAlert]:
        """
        Scan documents and create expiry alerts
        فحص الوثائق وإنشاء تنبيهات الانتهاء
        """
        alerts = []

        for doc in documents:
            if doc.expiry_date is None:
                continue

            alert = await self.create_expiry_alert(
                document=doc,
                recipient_user_ids=recipient_user_ids,
            )

            if alert:
                alerts.append(alert)

        logger.info(
            "document_expiry_scan_complete",
            documents_scanned=len(documents),
            alerts_created=len(alerts),
        )

        return alerts

    async def scan_certifications_for_expiry(
        self,
        certifications: list[Certification],
        recipient_user_ids: list[str] | None = None,
    ) -> list[DocumentAlert]:
        """
        Scan certifications and create expiry alerts
        فحص الشهادات وإنشاء تنبيهات الانتهاء
        """
        alerts = []

        for cert in certifications:
            if cert.status not in [
                CertificationStatus.ACTIVE,
                CertificationStatus.RENEWAL_IN_PROGRESS,
            ]:
                continue

            alert = await self.create_certification_alert(
                certification=cert,
                recipient_user_ids=recipient_user_ids,
            )

            if alert:
                alerts.append(alert)

            # Check for upcoming audits
            if cert.next_audit_date:
                days_until_audit = (cert.next_audit_date - date.today()).days
                if 0 < days_until_audit <= 30:
                    audit_alert = await self.create_audit_reminder(
                        certification=cert,
                        days_until_audit=days_until_audit,
                        recipient_user_ids=recipient_user_ids,
                    )
                    alerts.append(audit_alert)

        logger.info(
            "certification_expiry_scan_complete",
            certifications_scanned=len(certifications),
            alerts_created=len(alerts),
        )

        return alerts

    # ─────────────────────────────────────────────────────────────────────────
    # Notification - الإشعارات
    # ─────────────────────────────────────────────────────────────────────────

    async def _send_notification(self, alert: DocumentAlert) -> None:
        """
        Send notification for alert
        إرسال إشعار للتنبيه
        """
        if not self.notification_callback:
            return

        try:
            await self.notification_callback(
                alert_id=alert.id,
                tenant_id=alert.tenant_id,
                farm_id=alert.farm_id,
                priority=alert.priority.value,
                title_en=alert.title_en,
                title_ar=alert.title_ar,
                message_en=alert.message_en,
                message_ar=alert.message_ar,
                recipient_user_ids=alert.recipient_user_ids,
                channels=self.config.notification_channels,
            )

            alert.notification_sent = True
            alert.notification_sent_at = datetime.now(UTC)
            alert.notification_channels = self.config.notification_channels

            logger.info(
                "alert_notification_sent",
                alert_id=alert.id,
                channels=self.config.notification_channels,
            )

        except Exception as e:
            logger.error(
                "alert_notification_failed",
                alert_id=alert.id,
                error=str(e),
            )

    async def resend_notification(
        self,
        alert_id: str,
        channels: list[str] | None = None,
    ) -> bool:
        """
        Resend notification for an alert
        إعادة إرسال إشعار لتنبيه
        """
        alert = self._alerts.get(alert_id)
        if not alert:
            return False

        original_channels = self.config.notification_channels
        if channels:
            self.config.notification_channels = channels

        await self._send_notification(alert)

        self.config.notification_channels = original_channels
        return True

    # ─────────────────────────────────────────────────────────────────────────
    # Utility Methods - الدوال المساعدة
    # ─────────────────────────────────────────────────────────────────────────

    async def _has_recent_alert(
        self,
        document_id: str | None = None,
        certification_id: str | None = None,
        alert_type: str | None = None,
    ) -> bool:
        """
        Check if a similar alert was created recently
        التحقق مما إذا تم إنشاء تنبيه مماثل مؤخراً
        """
        cutoff = datetime.now(UTC) - timedelta(hours=self.config.alert_cooldown_hours)

        for alert in self._alerts.values():
            if alert.created_at < cutoff:
                continue
            if document_id and alert.document_id == document_id:
                if alert_type is None or alert.alert_type == alert_type:
                    return True
            if certification_id and alert.certification_id == certification_id:
                if alert_type is None or alert.alert_type == alert_type:
                    return True

        return False

    async def cleanup_old_alerts(
        self,
        days_to_keep: int = 90,
    ) -> int:
        """
        Remove old resolved alerts
        إزالة التنبيهات القديمة المحلولة
        """
        cutoff = datetime.now(UTC) - timedelta(days=days_to_keep)
        removed = 0

        alert_ids_to_remove = []
        for alert_id, alert in self._alerts.items():
            if alert.is_resolved and alert.resolved_at and alert.resolved_at < cutoff:
                alert_ids_to_remove.append(alert_id)

        for alert_id in alert_ids_to_remove:
            del self._alerts[alert_id]
            removed += 1

        logger.info(
            "old_alerts_cleaned",
            removed_count=removed,
            days_threshold=days_to_keep,
        )

        return removed

    async def get_alert_summary(
        self,
        tenant_id: str,
        farm_id: str | None = None,
    ) -> dict:
        """
        Get alert summary
        الحصول على ملخص التنبيهات
        """
        alerts = await self.list_alerts(
            tenant_id=tenant_id,
            farm_id=farm_id,
        )

        today = date.today()
        upcoming_expirations = []

        for alert in alerts:
            if alert.is_resolved:
                continue
            if alert.action_due_date and alert.action_due_date >= today:
                upcoming_expirations.append(
                    {
                        "alert_id": alert.id,
                        "type": alert.alert_type,
                        "title_en": alert.title_en,
                        "title_ar": alert.title_ar,
                        "due_date": alert.action_due_date.isoformat(),
                        "priority": alert.priority.value,
                    }
                )

        # Sort by due date
        upcoming_expirations.sort(key=lambda x: x["due_date"])

        counts = await self.get_alert_counts(tenant_id, farm_id)

        return {
            "counts": counts,
            "upcoming_expirations": upcoming_expirations[:10],
            "requires_immediate_attention": counts["by_priority"]["critical"] > 0,
        }
