"""
SAHOOL GlobalGAP Integration - NATS Events
أحداث NATS لتكامل GlobalGAP
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import uuid4

import nats
from nats.aio.client import Client as NATSClient


class GlobalGAPTopics:
    """موضوعات NATS لتكامل GlobalGAP"""

    # أحداث الامتثال - Compliance Events
    COMPLIANCE_UPDATED = "sahool.globalgap.compliance.updated"
    COMPLIANCE_CHECK_REQUIRED = "sahool.globalgap.compliance.check_required"
    COMPLIANCE_VERIFIED = "sahool.globalgap.compliance.verified"

    # أحداث التدقيق - Audit Events
    AUDIT_SCHEDULED = "sahool.globalgap.audit.scheduled"
    AUDIT_STARTED = "sahool.globalgap.audit.started"
    AUDIT_COMPLETED = "sahool.globalgap.audit.completed"
    AUDIT_FAILED = "sahool.globalgap.audit.failed"

    # أحداث عدم المطابقة - Non-Conformance Events
    NON_CONFORMANCE_DETECTED = "sahool.globalgap.nonconformance.detected"
    NON_CONFORMANCE_RESOLVED = "sahool.globalgap.nonconformance.resolved"
    NON_CONFORMANCE_ESCALATED = "sahool.globalgap.nonconformance.escalated"

    # أحداث الشهادات - Certificate Events
    CERTIFICATE_EXPIRING = "sahool.globalgap.certificate.expiring"
    CERTIFICATE_RENEWED = "sahool.globalgap.certificate.renewed"
    CERTIFICATE_REVOKED = "sahool.globalgap.certificate.revoked"

    # أحداث التكامل - Integration Events
    IRRIGATION_DATA_SYNCED = "sahool.globalgap.integration.irrigation.synced"
    CROP_HEALTH_DATA_SYNCED = "sahool.globalgap.integration.crop_health.synced"
    FERTILIZER_DATA_SYNCED = "sahool.globalgap.integration.fertilizer.synced"
    FIELD_OPS_DATA_SYNCED = "sahool.globalgap.integration.field_ops.synced"

    # الاشتراكات الواردة - Incoming Subscriptions
    IRRIGATION_APPLIED = "sahool.irrigation.applied"
    PEST_DETECTED = "sahool.crop_health.pest.detected"
    DISEASE_DETECTED = "sahool.crop_health.disease.detected"
    FERTILIZER_APPLIED = "sahool.fertilizer.applied"
    HARVEST_COMPLETED = "sahool.field_ops.harvest.completed"
    FIELD_ACTIVITY_RECORDED = "sahool.field_ops.activity.recorded"


class GlobalGAPEventPublisher:
    """ناشر أحداث GlobalGAP"""

    def __init__(self, nc: NATSClient):
        self.nc = nc

    async def close(self):
        """إغلاق الاتصال"""
        if self.nc and self.nc.is_connected:
            await self.nc.close()

    def _create_event(
        self,
        event_type: str,
        tenant_id: str,
        data: dict,
        correlation_id: Optional[str] = None
    ) -> dict:
        """إنشاء حدث موحد"""
        return {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "globalgap-integration",
            "version": "1.0.0",
            "tenant_id": tenant_id,
            "correlation_id": correlation_id or str(uuid4()),
            "data": data,
        }

    async def _publish(self, topic: str, event: dict) -> str:
        """نشر الحدث"""
        await self.nc.publish(topic, json.dumps(event).encode())
        return event["event_id"]

    # ============== Compliance Events ==============

    async def publish_compliance_updated(
        self,
        tenant_id: str,
        farm_id: str,
        control_point: str,
        compliance_status: str,
        previous_status: Optional[str] = None,
        assessment_data: Optional[dict] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث تحديث الامتثال
        Publish compliance update event
        """
        event = self._create_event(
            event_type="globalgap.compliance.updated",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "control_point": control_point,
                "compliance_status": compliance_status,
                "previous_status": previous_status,
                "assessment_data": assessment_data or {},
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.COMPLIANCE_UPDATED, event)

    async def publish_compliance_check_required(
        self,
        tenant_id: str,
        farm_id: str,
        control_point: str,
        reason: str,
        priority: str = "medium",
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث الحاجة لفحص الامتثال
        Publish compliance check required event
        """
        event = self._create_event(
            event_type="globalgap.compliance.check_required",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "control_point": control_point,
                "reason": reason,
                "priority": priority,
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.COMPLIANCE_CHECK_REQUIRED, event)

    # ============== Audit Events ==============

    async def publish_audit_scheduled(
        self,
        tenant_id: str,
        farm_id: str,
        audit_id: str,
        audit_type: str,
        scheduled_date: str,
        auditor_info: Optional[dict] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث جدولة تدقيق
        Publish audit scheduled event
        """
        event = self._create_event(
            event_type="globalgap.audit.scheduled",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "audit_id": audit_id,
                "audit_type": audit_type,
                "scheduled_date": scheduled_date,
                "auditor_info": auditor_info or {},
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.AUDIT_SCHEDULED, event)

    async def publish_audit_completed(
        self,
        tenant_id: str,
        farm_id: str,
        audit_id: str,
        result: str,
        findings: list,
        score: Optional[float] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث اكتمال التدقيق
        Publish audit completed event
        """
        event = self._create_event(
            event_type="globalgap.audit.completed",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "audit_id": audit_id,
                "result": result,
                "findings": findings,
                "score": score,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.AUDIT_COMPLETED, event)

    # ============== Non-Conformance Events ==============

    async def publish_non_conformance_detected(
        self,
        tenant_id: str,
        farm_id: str,
        control_point: str,
        severity: str,
        description: str,
        field_id: Optional[str] = None,
        detected_at: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث اكتشاف عدم مطابقة
        Publish non-conformance detected event
        """
        event = self._create_event(
            event_type="globalgap.nonconformance.detected",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "field_id": field_id,
                "control_point": control_point,
                "severity": severity,
                "description": description,
                "detected_at": detected_at or datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.NON_CONFORMANCE_DETECTED, event)

    async def publish_non_conformance_resolved(
        self,
        tenant_id: str,
        farm_id: str,
        non_conformance_id: str,
        resolution_notes: str,
        resolved_by: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث حل عدم المطابقة
        Publish non-conformance resolved event
        """
        event = self._create_event(
            event_type="globalgap.nonconformance.resolved",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "non_conformance_id": non_conformance_id,
                "resolution_notes": resolution_notes,
                "resolved_by": resolved_by,
                "resolved_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.NON_CONFORMANCE_RESOLVED, event)

    # ============== Certificate Events ==============

    async def publish_certificate_expiring(
        self,
        tenant_id: str,
        farm_id: str,
        certificate_id: str,
        certificate_type: str,
        expiry_date: str,
        days_until_expiry: int,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث قرب انتهاء الشهادة
        Publish certificate expiring event
        """
        event = self._create_event(
            event_type="globalgap.certificate.expiring",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "certificate_id": certificate_id,
                "certificate_type": certificate_type,
                "expiry_date": expiry_date,
                "days_until_expiry": days_until_expiry,
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.CERTIFICATE_EXPIRING, event)

    async def publish_certificate_renewed(
        self,
        tenant_id: str,
        farm_id: str,
        certificate_id: str,
        certificate_type: str,
        new_expiry_date: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث تجديد الشهادة
        Publish certificate renewed event
        """
        event = self._create_event(
            event_type="globalgap.certificate.renewed",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "certificate_id": certificate_id,
                "certificate_type": certificate_type,
                "new_expiry_date": new_expiry_date,
                "renewed_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=correlation_id
        )
        return await self._publish(GlobalGAPTopics.CERTIFICATE_RENEWED, event)

    # ============== Integration Sync Events ==============

    async def publish_integration_synced(
        self,
        tenant_id: str,
        integration_type: str,
        farm_id: str,
        records_synced: int,
        sync_status: str,
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        نشر حدث مزامنة التكامل
        Publish integration synced event
        """
        topic_map = {
            "irrigation": GlobalGAPTopics.IRRIGATION_DATA_SYNCED,
            "crop_health": GlobalGAPTopics.CROP_HEALTH_DATA_SYNCED,
            "fertilizer": GlobalGAPTopics.FERTILIZER_DATA_SYNCED,
            "field_ops": GlobalGAPTopics.FIELD_OPS_DATA_SYNCED,
        }

        topic = topic_map.get(integration_type, GlobalGAPTopics.IRRIGATION_DATA_SYNCED)

        event = self._create_event(
            event_type=f"globalgap.integration.{integration_type}.synced",
            tenant_id=tenant_id,
            data={
                "farm_id": farm_id,
                "integration_type": integration_type,
                "records_synced": records_synced,
                "sync_status": sync_status,
                "error_message": error_message,
                "synced_at": datetime.now(timezone.utc).isoformat(),
            },
            correlation_id=correlation_id
        )
        return await self._publish(topic, event)


async def get_publisher() -> Optional[GlobalGAPEventPublisher]:
    """
    الحصول على ناشر أحداث GlobalGAP
    Get GlobalGAP event publisher
    """
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")

    try:
        nc = await nats.connect(nats_url)
        return GlobalGAPEventPublisher(nc)
    except Exception as e:
        print(f"Failed to connect to NATS: {e}")
        return None
