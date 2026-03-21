"""
SAHOOL Cooperatives Module - Resource Pool Management
======================================================
ادارة مجمع الموارد المشتركة

Manages shared resources for agricultural cooperatives including:
- Equipment pool management (tractors, harvesters, sprayers)
- Storage facility management (warehouses, silos, cold storage)
- Resource booking and scheduling
- Availability tracking and conflict resolution
- Usage analytics and optimization

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from .models import (
    CooperativeMember,
    ResourceBooking,
    ResourceStatus,
    ResourceType,
    SharedResource,
)


class BookingConflictError(Exception):
    """Raised when a booking conflicts with an existing reservation."""

    pass


class ResourceNotAvailableError(Exception):
    """Raised when a resource is not available for booking."""

    pass


class InsufficientPriorityError(Exception):
    """Raised when member doesn't have sufficient priority for booking."""

    pass


@dataclass
class ResourceAvailability:
    """
    Availability window for a resource.
    نافذة توفر المورد
    """

    resource_id: str
    date: datetime
    available_hours: list[int]  # Hours of day (0-23) available
    booked_slots: list[tuple[int, int]]  # (start_hour, end_hour) pairs
    maintenance_scheduled: bool = False

    def is_available_at(self, hour: int) -> bool:
        """Check if resource is available at a specific hour"""
        if hour not in self.available_hours:
            return False
        return all(not start <= hour < end for start, end in self.booked_slots)

    def get_available_slots(self) -> list[tuple[int, int]]:
        """Get list of available time slots"""
        available = []
        in_slot = False
        slot_start = 0

        for hour in range(24):
            if self.is_available_at(hour):
                if not in_slot:
                    slot_start = hour
                    in_slot = True
            else:
                if in_slot:
                    available.append((slot_start, hour))
                    in_slot = False

        if in_slot:
            available.append((slot_start, 24))

        return available

    def to_dict(self) -> dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "date": self.date.isoformat(),
            "available_hours": self.available_hours,
            "booked_slots": self.booked_slots,
            "available_slots": self.get_available_slots(),
            "maintenance_scheduled": self.maintenance_scheduled,
        }


@dataclass
class UsageStatistics:
    """
    Usage statistics for a resource or member.
    احصائيات الاستخدام للمورد او العضو
    """

    total_bookings: int = 0
    total_hours: float = 0.0
    total_hectares: float = 0.0
    total_fees_collected: Decimal = Decimal("0")
    total_fees_outstanding: Decimal = Decimal("0")
    average_utilization_percent: float = 0.0
    most_active_day: str | None = None
    peak_usage_month: str | None = None

    # By period
    usage_this_month: float = 0.0
    usage_this_season: float = 0.0
    usage_this_year: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_bookings": self.total_bookings,
            "total_hours": self.total_hours,
            "total_hectares": self.total_hectares,
            "total_fees_collected": str(self.total_fees_collected),
            "total_fees_outstanding": str(self.total_fees_outstanding),
            "average_utilization_percent": self.average_utilization_percent,
            "most_active_day": self.most_active_day,
            "peak_usage_month": self.peak_usage_month,
            "usage_this_month": self.usage_this_month,
            "usage_this_season": self.usage_this_season,
            "usage_this_year": self.usage_this_year,
        }


@dataclass
class MaintenanceRecord:
    """
    Maintenance record for a resource.
    سجل صيانة للمورد
    """

    record_id: str
    resource_id: str

    # Maintenance details
    type: str  # scheduled, emergency, preventive
    description: str
    description_ar: str

    # Timing
    scheduled_date: datetime
    completed_date: datetime | None = None
    duration_hours: float = 0.0

    # Cost
    cost: Decimal = Decimal("0")
    parts_replaced: list[str] = field(default_factory=list)

    # Technician
    technician_name: str | None = None
    technician_contact: str | None = None

    # Status
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None

    @classmethod
    def create(
        cls,
        resource_id: str,
        type: str,
        description: str,
        description_ar: str,
        scheduled_date: datetime,
        **kwargs,
    ) -> MaintenanceRecord:
        """Factory method to create a maintenance record"""
        return cls(
            record_id=f"MNT-{uuid.uuid4().hex[:8].upper()}",
            resource_id=resource_id,
            type=type,
            description=description,
            description_ar=description_ar,
            scheduled_date=scheduled_date,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "resource_id": self.resource_id,
            "type": self.type,
            "description": self.description,
            "description_ar": self.description_ar,
            "scheduled_date": self.scheduled_date.isoformat(),
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "duration_hours": self.duration_hours,
            "cost": str(self.cost),
            "parts_replaced": self.parts_replaced,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


class ResourcePoolService:
    """
    Service for managing shared resource pools in cooperatives.
    خدمة ادارة مجمعات الموارد المشتركة في التعاونيات

    Features:
    - Resource registration and lifecycle management
    - Booking and scheduling with conflict detection
    - Priority-based allocation
    - Maintenance scheduling
    - Usage tracking and analytics

    Example:
        pool = ResourcePoolService(cooperative_id="COOP-001")

        # Register a tractor
        tractor = await pool.register_resource(
            name="John Deere 5075E",
            name_ar="جون دير 5075E",
            type=ResourceType.EQUIPMENT,
            capacity=75,
            capacity_unit="HP",
        )

        # Book for member
        booking = await pool.create_booking(
            resource_id=tractor.resource_id,
            member_id="MEM-001",
            purpose="Land preparation",
            purpose_ar="اعداد الارض",
            start_time=datetime(2026, 2, 1, 8, 0),
            duration_hours=4,
        )

        # Get availability
        availability = await pool.get_availability(
            resource_id=tractor.resource_id,
            date=datetime(2026, 2, 1),
        )
    """

    def __init__(self, cooperative_id: str, tenant_id: str = ""):
        if not tenant_id:
            raise ValueError("tenant_id is required for ResourcePoolService")
        self.cooperative_id = cooperative_id
        self.tenant_id = tenant_id

        # In-memory storage (production would use database)
        self._resources: dict[str, SharedResource] = {}
        self._bookings: dict[str, ResourceBooking] = {}
        self._maintenance: dict[str, MaintenanceRecord] = {}
        self._members: dict[str, CooperativeMember] = {}

        # Lock for atomic booking operations (prevents race conditions)
        self._booking_lock = asyncio.Lock()

        # Configuration
        self._default_operating_hours = list(range(6, 20))  # 6 AM to 8 PM
        self._advance_booking_days = 7
        self._cancellation_window_hours = 24

    # ===== Resource Management =====

    async def register_resource(
        self,
        name: str,
        name_ar: str,
        type: ResourceType,
        **kwargs,
    ) -> SharedResource:
        """
        Register a new shared resource.
        تسجيل مورد مشترك جديد
        """
        resource = SharedResource.create(
            cooperative_id=self.cooperative_id,
            name=name,
            name_ar=name_ar,
            type=type,
            **kwargs,
        )
        self._resources[resource.resource_id] = resource
        return resource

    async def get_resource(self, resource_id: str) -> SharedResource | None:
        """Get resource by ID"""
        return self._resources.get(resource_id)

    async def update_resource_status(
        self,
        resource_id: str,
        status: ResourceStatus,
        notes: str | None = None,
    ) -> SharedResource | None:
        """Update resource status"""
        resource = self._resources.get(resource_id)
        if resource:
            resource.status = status
            resource.updated_at = datetime.now(UTC)
        return resource

    async def list_resources(
        self,
        type: ResourceType | None = None,
        status: ResourceStatus | None = None,
        available_only: bool = False,
    ) -> list[SharedResource]:
        """
        List resources with optional filters.
        عرض الموارد مع فلاتر اختيارية
        """
        resources = list(self._resources.values())

        if type:
            resources = [r for r in resources if r.type == type]

        if status:
            resources = [r for r in resources if r.status == status]

        if available_only:
            resources = [r for r in resources if r.is_available()]

        return resources

    async def list_equipment(self, available_only: bool = False) -> list[SharedResource]:
        """List all equipment resources"""
        return await self.list_resources(
            type=ResourceType.EQUIPMENT,
            available_only=available_only,
        )

    async def list_storage(self, available_only: bool = False) -> list[SharedResource]:
        """List all storage facilities"""
        return await self.list_resources(
            type=ResourceType.STORAGE,
            available_only=available_only,
        )

    # ===== Booking Management =====

    async def create_booking(
        self,
        resource_id: str,
        member_id: str,
        purpose: str,
        purpose_ar: str,
        start_time: datetime,
        duration_hours: float,
        field_id: str | None = None,
        check_conflicts: bool = True,
        **kwargs,
    ) -> ResourceBooking:
        """
        Create a booking for a shared resource.
        انشاء حجز لمورد مشترك

        Args:
            resource_id: Resource to book
            member_id: Member making the booking
            purpose: Purpose description (English)
            purpose_ar: Purpose description (Arabic)
            start_time: When to start using the resource
            duration_hours: Duration of booking
            field_id: Target field (for mobile equipment)
            check_conflicts: Whether to check for conflicts

        Returns:
            ResourceBooking object

        Raises:
            ResourceNotAvailableError: If resource is not available
            BookingConflictError: If booking conflicts with existing reservation
        """
        async with self._booking_lock:
            # Validate resource exists and is available
            resource = self._resources.get(resource_id)
            if not resource:
                raise ValueError(f"Resource {resource_id} not found")

            if not resource.is_available():
                raise ResourceNotAvailableError(
                    f"Resource {resource.name} is not available (status: {resource.status.value})"
                )

            # Validate booking duration
            if resource.min_booking_hours and duration_hours < resource.min_booking_hours:
                raise ValueError(f"Minimum booking duration is {resource.min_booking_hours} hours")
            if resource.max_booking_hours and duration_hours > resource.max_booking_hours:
                raise ValueError(f"Maximum booking duration is {resource.max_booking_hours} hours")

            # Check for conflicts
            if check_conflicts:
                end_time = start_time + timedelta(hours=duration_hours)
                conflicts = await self._check_booking_conflicts(resource_id, start_time, end_time)
                if conflicts:
                    conflict_info = conflicts[0]
                    raise BookingConflictError(
                        f"Booking conflicts with existing reservation: {conflict_info.booking_id}"
                    )

            # Calculate fee
            estimated_fee = resource.calculate_usage_fee(
                hours=duration_hours,
                is_member=True,
            )

            # Create booking
            booking = ResourceBooking.create(
                resource_id=resource_id,
                member_id=member_id,
                cooperative_id=self.cooperative_id,
                purpose=purpose,
                purpose_ar=purpose_ar,
                start_time=start_time,
                duration_hours=duration_hours,
                estimated_fee=estimated_fee,
                field_id=field_id,
                **kwargs,
            )
            booking.end_time = start_time + timedelta(hours=duration_hours)
            booking.status = "confirmed"

            self._bookings[booking.booking_id] = booking
            return booking

    async def _check_booking_conflicts(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: str | None = None,
    ) -> list[ResourceBooking]:
        """Check for booking conflicts"""
        conflicts = []

        for booking in self._bookings.values():
            if booking.resource_id != resource_id:
                continue
            if booking.status in ["cancelled", "completed"]:
                continue
            if exclude_booking_id and booking.booking_id == exclude_booking_id:
                continue

            booking_end = booking.start_time + timedelta(hours=booking.duration_hours)

            # Check overlap
            if start_time < booking_end and end_time > booking.start_time:
                conflicts.append(booking)

        return conflicts

    async def get_booking(self, booking_id: str) -> ResourceBooking | None:
        """Get booking by ID"""
        return self._bookings.get(booking_id)

    async def cancel_booking(
        self,
        booking_id: str,
        reason: str | None = None,
    ) -> ResourceBooking | None:
        """
        Cancel a booking.
        الغاء حجز
        """
        booking = self._bookings.get(booking_id)
        if not booking:
            return None

        # Check cancellation window
        hours_until_start = (booking.start_time - datetime.now(UTC)).total_seconds() / 3600
        if hours_until_start < self._cancellation_window_hours:
            # Late cancellation - may apply penalty
            booking.notes = f"Late cancellation. {reason or ''}"

        booking.status = "cancelled"
        booking.updated_at = datetime.now(UTC)

        return booking

    async def complete_booking(
        self,
        booking_id: str,
        actual_hours: float,
        hectares_covered: float | None = None,
        completion_notes: str | None = None,
    ) -> ResourceBooking | None:
        """
        Mark a booking as completed and record actual usage.
        تحديد الحجز كمكتمل وتسجيل الاستخدام الفعلي
        """
        booking = self._bookings.get(booking_id)
        if not booking:
            return None

        resource = self._resources.get(booking.resource_id)
        if not resource:
            return None

        # Update booking
        booking.status = "completed"
        booking.actual_hours = actual_hours
        booking.hectares_covered = hectares_covered
        booking.completion_notes = completion_notes
        booking.updated_at = datetime.now(UTC)

        # Calculate actual fee
        booking.actual_fee = resource.calculate_usage_fee(
            hours=actual_hours,
            hectares=hectares_covered,
            is_member=True,
        )

        # Update resource usage statistics
        resource.total_usage_hours += actual_hours
        resource.usage_this_season += actual_hours
        resource.last_used_date = datetime.now(UTC)
        resource.last_used_by = booking.member_id
        resource.updated_at = datetime.now(UTC)

        return booking

    async def list_bookings(
        self,
        resource_id: str | None = None,
        member_id: str | None = None,
        status: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[ResourceBooking]:
        """
        List bookings with optional filters.
        عرض الحجوزات مع فلاتر اختيارية
        """
        bookings = list(self._bookings.values())

        if resource_id:
            bookings = [b for b in bookings if b.resource_id == resource_id]

        if member_id:
            bookings = [b for b in bookings if b.member_id == member_id]

        if status:
            bookings = [b for b in bookings if b.status == status]

        if from_date:
            bookings = [b for b in bookings if b.start_time >= from_date]

        if to_date:
            bookings = [b for b in bookings if b.start_time <= to_date]

        return sorted(bookings, key=lambda b: b.start_time)

    # ===== Availability =====

    async def get_availability(
        self,
        resource_id: str,
        date: datetime,
    ) -> ResourceAvailability:
        """
        Get availability for a resource on a specific date.
        الحصول على توفر المورد في تاريخ محدد
        """
        resource = self._resources.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")

        # Get operating hours (could be customized per resource)
        available_hours = self._default_operating_hours.copy()

        # Check for maintenance
        maintenance_scheduled = any(
            m.resource_id == resource_id
            and m.scheduled_date.date() == date.date()
            and m.status in ["scheduled", "in_progress"]
            for m in self._maintenance.values()
        )

        # Get booked slots
        booked_slots = []
        day_start = datetime(date.year, date.month, date.day, tzinfo=UTC)
        day_end = day_start + timedelta(days=1)

        for booking in self._bookings.values():
            if booking.resource_id != resource_id:
                continue
            if booking.status in ["cancelled"]:
                continue

            booking_end = booking.start_time + timedelta(hours=booking.duration_hours)

            # Check if booking overlaps with this day
            if booking.start_time < day_end and booking_end > day_start:
                start_hour = max(0, booking.start_time.hour if booking.start_time >= day_start else 0)
                end_hour = min(24, booking_end.hour if booking_end <= day_end else 24)
                booked_slots.append((start_hour, end_hour))

        return ResourceAvailability(
            resource_id=resource_id,
            date=date,
            available_hours=available_hours,
            booked_slots=booked_slots,
            maintenance_scheduled=maintenance_scheduled,
        )

    async def get_availability_range(
        self,
        resource_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[ResourceAvailability]:
        """Get availability for a date range"""
        availability = []
        current = start_date

        while current <= end_date:
            avail = await self.get_availability(resource_id, current)
            availability.append(avail)
            current += timedelta(days=1)

        return availability

    async def find_available_slot(
        self,
        resource_id: str,
        duration_hours: float,
        preferred_date: datetime | None = None,
        search_days: int = 7,
    ) -> tuple[datetime, datetime] | None:
        """
        Find the next available slot for a resource.
        البحث عن الفترة المتاحة التالية للمورد

        Args:
            resource_id: Resource to find slot for
            duration_hours: Required duration
            preferred_date: Start searching from this date
            search_days: Number of days to search

        Returns:
            Tuple of (start_time, end_time) or None if no slot found
        """
        start_date = preferred_date or datetime.now(UTC)

        for day_offset in range(search_days):
            search_date = start_date + timedelta(days=day_offset)
            availability = await self.get_availability(resource_id, search_date)

            if availability.maintenance_scheduled:
                continue

            for slot_start, slot_end in availability.get_available_slots():
                slot_duration = slot_end - slot_start
                if slot_duration >= duration_hours:
                    # Found a suitable slot
                    start_time = datetime(
                        search_date.year,
                        search_date.month,
                        search_date.day,
                        slot_start,
                    )
                    end_time = start_time + timedelta(hours=duration_hours)
                    return (start_time, end_time)

        return None

    # ===== Maintenance =====

    async def schedule_maintenance(
        self,
        resource_id: str,
        type: str,
        description: str,
        description_ar: str,
        scheduled_date: datetime,
        estimated_duration_hours: float = 4.0,
        **kwargs,
    ) -> MaintenanceRecord:
        """
        Schedule maintenance for a resource.
        جدولة صيانة لمورد
        """
        resource = self._resources.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")

        # Check for booking conflicts
        end_time = scheduled_date + timedelta(hours=estimated_duration_hours)
        conflicts = await self._check_booking_conflicts(resource_id, scheduled_date, end_time)

        if conflicts:
            # Notify about conflicts (in production, would send notifications)
            pass

        record = MaintenanceRecord.create(
            resource_id=resource_id,
            type=type,
            description=description,
            description_ar=description_ar,
            scheduled_date=scheduled_date,
            duration_hours=estimated_duration_hours,
            **kwargs,
        )

        self._maintenance[record.record_id] = record

        # Update resource maintenance date
        resource.next_maintenance_date = scheduled_date

        return record

    async def complete_maintenance(
        self,
        record_id: str,
        actual_duration_hours: float,
        cost: Decimal,
        parts_replaced: list[str] | None = None,
        notes: str | None = None,
    ) -> MaintenanceRecord | None:
        """
        Mark maintenance as completed.
        تحديد الصيانة كمكتملة
        """
        record = self._maintenance.get(record_id)
        if not record:
            return None

        record.status = "completed"
        record.completed_date = datetime.now(UTC)
        record.duration_hours = actual_duration_hours
        record.cost = cost
        record.parts_replaced = parts_replaced or []
        record.notes = notes

        # Update resource
        resource = self._resources.get(record.resource_id)
        if resource:
            resource.total_maintenance_cost += cost
            resource.status = ResourceStatus.AVAILABLE

            # Schedule next maintenance
            if resource.maintenance_interval_hours:
                # Reset hours counter after maintenance
                resource.total_usage_hours = 0

        return record

    async def list_maintenance(
        self,
        resource_id: str | None = None,
        status: str | None = None,
    ) -> list[MaintenanceRecord]:
        """List maintenance records"""
        records = list(self._maintenance.values())

        if resource_id:
            records = [r for r in records if r.resource_id == resource_id]

        if status:
            records = [r for r in records if r.status == status]

        return sorted(records, key=lambda r: r.scheduled_date)

    # ===== Statistics =====

    async def get_resource_statistics(
        self,
        resource_id: str,
    ) -> UsageStatistics:
        """
        Get usage statistics for a resource.
        الحصول على احصائيات الاستخدام للمورد
        """
        resource = self._resources.get(resource_id)
        if not resource:
            raise ValueError(f"Resource {resource_id} not found")

        # Calculate statistics from bookings
        bookings = [b for b in self._bookings.values() if b.resource_id == resource_id]
        completed = [b for b in bookings if b.status == "completed"]

        now = datetime.now(UTC)
        month_start = datetime(now.year, now.month, 1, tzinfo=UTC)
        year_start = datetime(now.year, 1, 1, tzinfo=UTC)

        # Determine season (simplified)
        if now.month in [10, 11, 12, 1, 2, 3]:
            season_start = datetime(now.year if now.month >= 10 else now.year - 1, 10, 1, tzinfo=UTC)
        else:
            season_start = datetime(now.year, 4, 1, tzinfo=UTC)

        stats = UsageStatistics(
            total_bookings=len(completed),
            total_hours=sum(b.actual_hours or 0 for b in completed),
            total_hectares=sum(b.hectares_covered or 0 for b in completed),
            total_fees_collected=sum(b.actual_fee for b in completed if b.payment_status == "paid"),
            total_fees_outstanding=sum(b.actual_fee for b in completed if b.payment_status != "paid"),
        )

        # Usage by period
        for booking in completed:
            if booking.start_time >= month_start:
                stats.usage_this_month += booking.actual_hours or 0
            if booking.start_time >= season_start:
                stats.usage_this_season += booking.actual_hours or 0
            if booking.start_time >= year_start:
                stats.usage_this_year += booking.actual_hours or 0

        # Calculate utilization (simplified - assumes 10 hours/day operating)
        days_in_service = (now - resource.created_at).days or 1
        max_hours = days_in_service * 10
        stats.average_utilization_percent = (stats.total_hours / max_hours) * 100 if max_hours > 0 else 0

        return stats

    async def get_member_usage_statistics(
        self,
        member_id: str,
    ) -> UsageStatistics:
        """
        Get usage statistics for a member.
        الحصول على احصائيات الاستخدام للعضو
        """
        bookings = [b for b in self._bookings.values() if b.member_id == member_id]
        completed = [b for b in bookings if b.status == "completed"]

        now = datetime.now(UTC)
        month_start = datetime(now.year, now.month, 1, tzinfo=UTC)
        year_start = datetime(now.year, 1, 1, tzinfo=UTC)

        stats = UsageStatistics(
            total_bookings=len(completed),
            total_hours=sum(b.actual_hours or 0 for b in completed),
            total_hectares=sum(b.hectares_covered or 0 for b in completed),
            total_fees_collected=sum(b.actual_fee for b in completed if b.payment_status == "paid"),
            total_fees_outstanding=sum(b.actual_fee for b in completed if b.payment_status != "paid"),
        )

        # Usage by period
        for booking in completed:
            if booking.start_time >= month_start:
                stats.usage_this_month += booking.actual_hours or 0
            if booking.start_time >= year_start:
                stats.usage_this_year += booking.actual_hours or 0

        return stats

    async def get_pool_summary(self) -> dict[str, Any]:
        """
        Get summary of the resource pool.
        الحصول على ملخص مجمع الموارد
        """
        now = datetime.now(UTC)
        resources = list(self._resources.values())

        # Group by type
        by_type = {}
        for resource in resources:
            type_name = resource.type.value
            if type_name not in by_type:
                by_type[type_name] = {"count": 0, "available": 0, "total_value": Decimal("0")}
            by_type[type_name]["count"] += 1
            if resource.is_available():
                by_type[type_name]["available"] += 1
            by_type[type_name]["total_value"] += resource.current_value

        # Pending bookings
        pending_bookings = [b for b in self._bookings.values() if b.status == "confirmed"]
        upcoming_bookings = sorted(
            [b for b in pending_bookings if b.start_time > now],
            key=lambda b: b.start_time,
        )[:5]

        # Maintenance needed
        needs_maintenance = [r for r in resources if r.needs_maintenance()]

        return {
            "cooperative_id": self.cooperative_id,
            "total_resources": len(resources),
            "available_resources": len([r for r in resources if r.is_available()]),
            "by_type": {
                k: {
                    "count": v["count"],
                    "available": v["available"],
                    "total_value": str(v["total_value"]),
                }
                for k, v in by_type.items()
            },
            "total_value": str(sum(r.current_value for r in resources)),
            "pending_bookings": len(pending_bookings),
            "upcoming_bookings": [b.to_dict() for b in upcoming_bookings],
            "needs_maintenance": [r.to_summary() for r in needs_maintenance],
            "utilization_summary": {
                "total_hours_this_month": sum(
                    b.actual_hours or 0
                    for b in self._bookings.values()
                    if b.status == "completed" and b.start_time >= datetime(now.year, now.month, 1, tzinfo=UTC)
                ),
            },
        }


# Convenience functions for standalone usage
async def create_resource_pool(cooperative_id: str, tenant_id: str = "") -> ResourcePoolService:
    """Create a new resource pool service"""
    return ResourcePoolService(cooperative_id=cooperative_id, tenant_id=tenant_id)
