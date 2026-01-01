"""
SAHOOL Field Service - Event Publishing
نشر أحداث خدمة الحقول
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import uuid4

import nats
from nats.aio.client import Client as NATSClient


class FieldTopics:
    """موضوعات NATS لخدمة الحقول"""

    # أحداث الحقول
    FIELD_CREATED = "sahool.fields.created"
    FIELD_UPDATED = "sahool.fields.updated"
    FIELD_DELETED = "sahool.fields.deleted"
    FIELD_BOUNDARY_UPDATED = "sahool.fields.boundary.updated"

    # أحداث المواسم
    SEASON_STARTED = "sahool.fields.season.started"
    SEASON_CLOSED = "sahool.fields.season.closed"

    # أحداث المناطق
    ZONE_CREATED = "sahool.fields.zone.created"
    ZONE_DELETED = "sahool.fields.zone.deleted"

    # أحداث NDVI
    NDVI_RECORDED = "sahool.fields.ndvi.recorded"

    # الاشتراكات الواردة
    NDVI_COMPUTED = "sahool.ndvi.computed"
    SATELLITE_DATA_READY = "sahool.satellite.data.ready"


class FieldEventPublisher:
    """ناشر أحداث الحقول"""

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
        correlation_id: Optional[str] = None,
    ) -> dict:
        """إنشاء حدث موحد"""
        return {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "field-service",
            "version": "16.0.0",
            "tenant_id": tenant_id,
            "correlation_id": correlation_id or str(uuid4()),
            "data": data,
        }

    async def _publish(self, topic: str, event: dict) -> str:
        """نشر الحدث"""
        await self.nc.publish(topic, json.dumps(event).encode())
        return event["event_id"]

    # ============== Field Events ==============

    async def publish_field_created(
        self,
        tenant_id: str,
        field_id: str,
        user_id: str,
        field_name: str,
        area_hectares: float,
        location: dict,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث إنشاء حقل"""
        event = self._create_event(
            event_type="field.created",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "user_id": user_id,
                "field_name": field_name,
                "area_hectares": area_hectares,
                "location": location,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.FIELD_CREATED, event)

    async def publish_field_updated(
        self,
        tenant_id: str,
        field_id: str,
        updated_fields: list,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث تحديث حقل"""
        event = self._create_event(
            event_type="field.updated",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "updated_fields": updated_fields,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.FIELD_UPDATED, event)

    async def publish_field_deleted(
        self,
        tenant_id: str,
        field_id: str,
        user_id: str,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث حذف حقل"""
        event = self._create_event(
            event_type="field.deleted",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "user_id": user_id,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.FIELD_DELETED, event)

    async def publish_boundary_updated(
        self,
        tenant_id: str,
        field_id: str,
        new_area_hectares: float,
        centroid: dict,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث تحديث الحدود"""
        event = self._create_event(
            event_type="field.boundary.updated",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "new_area_hectares": new_area_hectares,
                "centroid": centroid,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.FIELD_BOUNDARY_UPDATED, event)

    # ============== Season Events ==============

    async def publish_season_started(
        self,
        tenant_id: str,
        field_id: str,
        season_id: str,
        crop_type: str,
        planting_date: str,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث بدء موسم"""
        event = self._create_event(
            event_type="field.season.started",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "season_id": season_id,
                "crop_type": crop_type,
                "planting_date": planting_date,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.SEASON_STARTED, event)

    async def publish_season_closed(
        self,
        tenant_id: str,
        field_id: str,
        season_id: str,
        crop_type: str,
        harvest_date: str,
        actual_yield_kg: Optional[float],
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث إنهاء موسم"""
        event = self._create_event(
            event_type="field.season.closed",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "season_id": season_id,
                "crop_type": crop_type,
                "harvest_date": harvest_date,
                "actual_yield_kg": actual_yield_kg,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.SEASON_CLOSED, event)

    # ============== Zone Events ==============

    async def publish_zone_created(
        self,
        tenant_id: str,
        field_id: str,
        zone_id: str,
        zone_name: str,
        area_hectares: float,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث إنشاء منطقة"""
        event = self._create_event(
            event_type="field.zone.created",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "zone_id": zone_id,
                "zone_name": zone_name,
                "area_hectares": area_hectares,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.ZONE_CREATED, event)

    async def publish_zone_deleted(
        self,
        tenant_id: str,
        field_id: str,
        zone_id: str,
        correlation_id: Optional[str] = None,
    ) -> str:
        """نشر حدث حذف منطقة"""
        event = self._create_event(
            event_type="field.zone.deleted",
            tenant_id=tenant_id,
            data={
                "field_id": field_id,
                "zone_id": zone_id,
            },
            correlation_id=correlation_id,
        )
        return await self._publish(FieldTopics.ZONE_DELETED, event)


async def get_publisher() -> Optional[FieldEventPublisher]:
    """الحصول على ناشر الأحداث"""
    nats_url = os.getenv("NATS_URL", "nats://localhost:4222")

    try:
        nc = await nats.connect(nats_url)
        return FieldEventPublisher(nc)
    except Exception as e:
        print(f"Failed to connect to NATS: {e}")
        return None
