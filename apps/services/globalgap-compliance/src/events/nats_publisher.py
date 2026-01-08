"""
SAHOOL GlobalGAP Compliance Service - NATS Publisher
Publishes compliance-related events to NATS event bus
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import nats
from nats.aio.client import Client as NatsClient

logger = logging.getLogger(__name__)


class NatsPublisher:
    """NATS Event Publisher for Compliance Service"""

    def __init__(self):
        self.nc: Optional[NatsClient] = None
        self.connected = False

    async def connect(self, nats_url: str) -> bool:
        """
        Connect to NATS server

        Args:
            nats_url: NATS server URL

        Returns:
            bool: Connection success status
        """
        try:
            self.nc = await nats.connect(nats_url)
            self.connected = True
            logger.info(f"✅ NATS connected: {nats_url}")
            return True
        except Exception as e:
            logger.error(f"❌ NATS connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from NATS server"""
        if self.nc and self.connected:
            try:
                await self.nc.close()
                self.connected = False
                logger.info("NATS disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting from NATS: {e}")

    async def publish_event(
        self,
        subject: str,
        event_type: str,
        payload: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Publish event to NATS

        Args:
            subject: NATS subject/topic
            event_type: Type of event
            payload: Event data
            metadata: Additional metadata

        Returns:
            bool: Publish success status
        """
        if not self.nc or not self.connected:
            logger.warning(f"NATS not connected, skipping event publish: {event_type}")
            return False

        try:
            event = {
                "eventId": str(uuid4()),
                "eventType": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0",
                "payload": payload,
                "metadata": metadata or {},
            }

            message = json.dumps(event).encode()
            await self.nc.publish(subject, message)

            logger.info(f"📤 Event published: {event_type} to {subject}")
            return True

        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {e}")
            return False


# Global publisher instance
_publisher: Optional[NatsPublisher] = None


def get_publisher() -> Optional[NatsPublisher]:
    """Get global NATS publisher instance"""
    return _publisher


def set_publisher(publisher: NatsPublisher):
    """Set global NATS publisher instance"""
    global _publisher
    _publisher = publisher


# ============================================================================
# Compliance Event Publishers
# ============================================================================


async def publish_compliance_updated(
    farm_id: str,
    tenant_id: str,
    overall_status: str,
    compliance_percentage: float,
    changes: Optional[dict] = None,
) -> bool:
    """
    Publish compliance record updated event

    Args:
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        overall_status: Overall compliance status
        compliance_percentage: Compliance percentage (0-100)
        changes: Dictionary of changed fields

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.updated",
        event_type="compliance.updated",
        payload={
            "farmId": farm_id,
            "tenantId": tenant_id,
            "overallStatus": overall_status,
            "compliancePercentage": compliance_percentage,
            "changes": changes or {},
            "updatedAt": datetime.utcnow().isoformat(),
        },
    )


async def publish_audit_completed(
    audit_id: str,
    farm_id: str,
    tenant_id: str,
    audit_type: str,
    audit_status: str,
    overall_score: float,
    auditor_name: str,
) -> bool:
    """
    Publish audit completed event

    Args:
        audit_id: Audit identifier
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        audit_type: Type of audit (internal, external, certification)
        audit_status: Audit status
        overall_score: Overall audit score (0-100)
        auditor_name: Name of auditor

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.audit.completed",
        event_type="compliance.audit.completed",
        payload={
            "auditId": audit_id,
            "farmId": farm_id,
            "tenantId": tenant_id,
            "auditType": audit_type,
            "auditStatus": audit_status,
            "overallScore": overall_score,
            "auditorName": auditor_name,
            "completedAt": datetime.utcnow().isoformat(),
        },
    )


async def publish_non_conformity_created(
    non_conformity_id: str,
    farm_id: str,
    tenant_id: str,
    control_point_number: str,
    severity: str,
    description: str,
) -> bool:
    """
    Publish non-conformity created event

    Args:
        non_conformity_id: Non-conformity identifier
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        control_point_number: GlobalGAP control point number
        severity: Severity level (minor, major, critical)
        description: Non-conformity description

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.non_conformity.created",
        event_type="compliance.non_conformity.created",
        payload={
            "nonConformityId": non_conformity_id,
            "farmId": farm_id,
            "tenantId": tenant_id,
            "controlPointNumber": control_point_number,
            "severity": severity,
            "description": description,
            "createdAt": datetime.utcnow().isoformat(),
        },
    )


async def publish_non_conformity_resolved(
    non_conformity_id: str,
    farm_id: str,
    tenant_id: str,
    resolution_description: str,
    resolved_by: str,
) -> bool:
    """
    Publish non-conformity resolved event

    Args:
        non_conformity_id: Non-conformity identifier
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        resolution_description: Description of resolution
        resolved_by: User who resolved the non-conformity

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.non_conformity.resolved",
        event_type="compliance.non_conformity.resolved",
        payload={
            "nonConformityId": non_conformity_id,
            "farmId": farm_id,
            "tenantId": tenant_id,
            "resolutionDescription": resolution_description,
            "resolvedBy": resolved_by,
            "resolvedAt": datetime.utcnow().isoformat(),
        },
    )


async def publish_certificate_created(
    certificate_id: str,
    farm_id: str,
    tenant_id: str,
    ggn_number: str,
    certificate_type: str,
    issued_date: str,
    expiry_date: str,
) -> bool:
    """
    Publish certificate created event

    Args:
        certificate_id: Certificate identifier
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        ggn_number: GlobalGAP Number (GGN)
        certificate_type: Type of certificate
        issued_date: Certificate issue date
        expiry_date: Certificate expiry date

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.certificate.created",
        event_type="compliance.certificate.created",
        payload={
            "certificateId": certificate_id,
            "farmId": farm_id,
            "tenantId": tenant_id,
            "ggnNumber": ggn_number,
            "certificateType": certificate_type,
            "issuedDate": issued_date,
            "expiryDate": expiry_date,
            "createdAt": datetime.utcnow().isoformat(),
        },
    )


async def publish_certificate_renewed(
    certificate_id: str,
    farm_id: str,
    tenant_id: str,
    ggn_number: str,
    new_expiry_date: str,
) -> bool:
    """
    Publish certificate renewed event

    Args:
        certificate_id: Certificate identifier
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        ggn_number: GlobalGAP Number (GGN)
        new_expiry_date: New certificate expiry date

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.certificate.renewed",
        event_type="compliance.certificate.renewed",
        payload={
            "certificateId": certificate_id,
            "farmId": farm_id,
            "tenantId": tenant_id,
            "ggnNumber": ggn_number,
            "newExpiryDate": new_expiry_date,
            "renewedAt": datetime.utcnow().isoformat(),
        },
    )


async def publish_certificate_expired(
    certificate_id: str,
    farm_id: str,
    tenant_id: str,
    ggn_number: str,
    expired_date: str,
) -> bool:
    """
    Publish certificate expired event

    Args:
        certificate_id: Certificate identifier
        farm_id: Farm identifier
        tenant_id: Tenant identifier
        ggn_number: GlobalGAP Number (GGN)
        expired_date: Date certificate expired

    Returns:
        bool: Success status
    """
    publisher = get_publisher()
    if not publisher:
        return False

    return await publisher.publish_event(
        subject="compliance.certificate.expired",
        event_type="compliance.certificate.expired",
        payload={
            "certificateId": certificate_id,
            "farmId": farm_id,
            "tenantId": tenant_id,
            "ggnNumber": ggn_number,
            "expiredDate": expired_date,
        },
    )
