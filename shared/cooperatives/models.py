"""
SAHOOL Cooperatives Module - Data Models
=========================================
نماذج البيانات لوحدة التعاونيات

Data models for agricultural cooperatives management including:
- Cooperative entities with hierarchical structure
- Member management with roles
- Shared resources (equipment, storage)
- Group purchasing records
- Revenue sharing configurations

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any


class CooperativeType(StrEnum):
    """Types of agricultural cooperatives | انواع التعاونيات الزراعية"""

    PRODUCTION = "production"  # تعاونية انتاجية - Joint farming
    MARKETING = "marketing"  # تعاونية تسويقية - Joint selling
    SERVICE = "service"  # تعاونية خدمية - Shared services
    MULTI_PURPOSE = "multi_purpose"  # تعاونية متعددة الاغراض
    CREDIT = "credit"  # تعاونية ائتمانية - Financing
    IRRIGATION = "irrigation"  # تعاونية ري - Water management


class CooperativeStatus(StrEnum):
    """Cooperative lifecycle status | حالة دورة حياة التعاونية"""

    FORMING = "forming"  # قيد التشكيل - Being established
    ACTIVE = "active"  # نشطة - Operating normally
    SUSPENDED = "suspended"  # معلقة - Temporarily inactive
    DISSOLVED = "dissolved"  # منحلة - No longer operating


class MemberRole(StrEnum):
    """Roles within a cooperative | الادوار داخل التعاونية"""

    CHAIRMAN = "chairman"  # رئيس - Head of cooperative
    VICE_CHAIRMAN = "vice_chairman"  # نائب الرئيس
    TREASURER = "treasurer"  # امين الصندوق - Financial manager
    SECRETARY = "secretary"  # السكرتير - Administrative
    BOARD_MEMBER = "board_member"  # عضو مجلس الادارة
    MEMBER = "member"  # عضو - Regular member
    OBSERVER = "observer"  # مراقب - Non-voting participant


class MemberStatus(StrEnum):
    """Member participation status | حالة مشاركة العضو"""

    PENDING = "pending"  # معلق - Awaiting approval
    ACTIVE = "active"  # نشط - Fully participating
    SUSPENDED = "suspended"  # موقوف - Temporarily inactive
    WITHDRAWN = "withdrawn"  # منسحب - Left voluntarily
    EXPELLED = "expelled"  # مطرود - Removed


class ResourceType(StrEnum):
    """Types of shared resources | انواع الموارد المشتركة"""

    EQUIPMENT = "equipment"  # معدات - Tractors, harvesters
    STORAGE = "storage"  # تخزين - Warehouses, silos
    TRANSPORT = "transport"  # نقل - Trucks, logistics
    PROCESSING = "processing"  # معالجة - Mills, packhouses
    IRRIGATION = "irrigation"  # ري - Pumps, pivots
    LAND = "land"  # ارض - Shared plots
    SEEDS = "seeds"  # بذور - Seed bank
    FERTILIZER = "fertilizer"  # اسمدة - Bulk fertilizer
    PESTICIDE = "pesticide"  # مبيدات - Crop protection


class ResourceStatus(StrEnum):
    """Status of shared resources | حالة الموارد المشتركة"""

    AVAILABLE = "available"  # متاح - Ready for use
    IN_USE = "in_use"  # قيد الاستخدام
    MAINTENANCE = "maintenance"  # صيانة - Under repair
    RESERVED = "reserved"  # محجوز - Booked for future
    RETIRED = "retired"  # متقاعد - No longer in service


class PurchaseOrderStatus(StrEnum):
    """Group purchase order status | حالة امر الشراء الجماعي"""

    DRAFT = "draft"  # مسودة - Being prepared
    COLLECTING = "collecting"  # جمع - Collecting orders
    CONFIRMED = "confirmed"  # مؤكد - Orders finalized
    ORDERED = "ordered"  # تم الطلب - Placed with supplier
    DELIVERED = "delivered"  # تم التسليم
    DISTRIBUTED = "distributed"  # تم التوزيع - Given to members
    CANCELLED = "cancelled"  # ملغي


class RevenueShareMethod(StrEnum):
    """Methods for distributing revenue | طرق توزيع الايرادات"""

    EQUAL = "equal"  # بالتساوي - Equal shares
    CONTRIBUTION = "contribution"  # حسب المساهمة - By contribution
    PRODUCTION = "production"  # حسب الانتاج - By production volume
    LAND_AREA = "land_area"  # حسب المساحة - By land area
    WEIGHTED = "weighted"  # موزون - Custom weights
    HYBRID = "hybrid"  # هجين - Multiple methods


@dataclass
class Address:
    """
    Physical address for cooperative or resource.
    العنوان الفعلي للتعاونية او المورد
    """

    governorate: str  # المحافظة
    district: str  # المركز
    village: str | None = None  # القرية
    street: str | None = None  # الشارع
    postal_code: str | None = None  # الرمز البريدي
    coordinates: tuple[float, float] | None = None  # الاحداثيات

    def to_dict(self) -> dict[str, Any]:
        return {
            "governorate": self.governorate,
            "district": self.district,
            "village": self.village,
            "street": self.street,
            "postal_code": self.postal_code,
            "coordinates": self.coordinates,
        }

    @property
    def full_address(self) -> str:
        """Get full address string"""
        parts = [self.village, self.district, self.governorate]
        return ", ".join(p for p in parts if p)

    @property
    def full_address_ar(self) -> str:
        """Get full address in Arabic format"""
        parts = [self.governorate, self.district, self.village]
        return "، ".join(p for p in parts if p)


@dataclass
class CooperativeConfig:
    """
    Configuration for cooperative operations.
    اعدادات عمليات التعاونية
    """

    # Membership settings
    min_members: int = 7  # Minimum members required
    max_members: int | None = None  # Maximum members (None = unlimited)
    membership_fee: Decimal = Decimal("0")  # رسوم العضوية
    annual_dues: Decimal = Decimal("0")  # الاشتراك السنوي

    # Revenue sharing defaults
    default_share_method: RevenueShareMethod = RevenueShareMethod.CONTRIBUTION
    management_fee_percent: Decimal = Decimal("5.0")  # نسبة الرسوم الادارية
    reserve_fund_percent: Decimal = Decimal("10.0")  # نسبة صندوق الاحتياطي

    # Resource access rules
    max_equipment_hours_per_member: int | None = None
    priority_by_seniority: bool = True  # اولوية حسب الاقدمية
    advance_booking_days: int = 7

    # Group purchasing
    min_order_value: Decimal = Decimal("0")
    bulk_discount_threshold: Decimal = Decimal("10000")

    def to_dict(self) -> dict[str, Any]:
        return {
            "min_members": self.min_members,
            "max_members": self.max_members,
            "membership_fee": str(self.membership_fee),
            "annual_dues": str(self.annual_dues),
            "default_share_method": self.default_share_method.value,
            "management_fee_percent": str(self.management_fee_percent),
            "reserve_fund_percent": str(self.reserve_fund_percent),
            "max_equipment_hours_per_member": self.max_equipment_hours_per_member,
            "priority_by_seniority": self.priority_by_seniority,
            "advance_booking_days": self.advance_booking_days,
            "min_order_value": str(self.min_order_value),
            "bulk_discount_threshold": str(self.bulk_discount_threshold),
        }


@dataclass
class Cooperative:
    """
    Agricultural cooperative entity.
    كيان التعاونية الزراعية

    Supports hierarchical structure with parent-child relationships.
    """

    # Identification
    cooperative_id: str
    tenant_id: str

    # Basic info - bilingual
    name: str
    name_ar: str
    description: str | None = None
    description_ar: str | None = None

    # Classification
    type: CooperativeType = CooperativeType.MULTI_PURPOSE
    status: CooperativeStatus = CooperativeStatus.FORMING

    # Hierarchy (for federated cooperatives)
    parent_id: str | None = None  # التعاونية الام
    level: int = 0  # 0=primary, 1=regional, 2=national

    # Location
    address: Address | None = None
    service_area_km: float | None = None  # نطاق الخدمة

    # Registration
    registration_number: str | None = None  # رقم التسجيل
    registration_date: datetime | None = None
    license_expiry: datetime | None = None

    # Contact
    phone: str | None = None
    email: str | None = None
    website: str | None = None

    # Configuration
    config: CooperativeConfig = field(default_factory=CooperativeConfig)

    # Financial
    share_capital: Decimal = Decimal("0")  # راس المال
    currency: str = "SAR"

    # Statistics (denormalized for performance)
    member_count: int = 0
    active_member_count: int = 0
    resource_count: int = 0
    total_land_area_ha: float = 0.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: list[str] = field(default_factory=list)
    custom_fields: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        tenant_id: str,
        name: str,
        name_ar: str,
        type: CooperativeType = CooperativeType.MULTI_PURPOSE,
        **kwargs,
    ) -> Cooperative:
        """Factory method to create a new cooperative"""
        return cls(
            cooperative_id=f"COOP-{uuid.uuid4().hex[:8].upper()}",
            tenant_id=tenant_id,
            name=name,
            name_ar=name_ar,
            type=type,
            **kwargs,
        )

    def is_primary(self) -> bool:
        """Check if this is a primary (base-level) cooperative"""
        return self.level == 0 and self.parent_id is None

    def is_federation(self) -> bool:
        """Check if this is a federation (has child cooperatives)"""
        return self.level > 0

    def can_accept_members(self) -> bool:
        """Check if cooperative can accept new members"""
        if self.status != CooperativeStatus.ACTIVE:
            return False
        if self.config.max_members and self.member_count >= self.config.max_members:
            return False
        return True

    def to_dict(self, include_config: bool = False) -> dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "cooperative_id": self.cooperative_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "type": self.type.value,
            "status": self.status.value,
            "parent_id": self.parent_id,
            "level": self.level,
            "address": self.address.to_dict() if self.address else None,
            "registration_number": self.registration_number,
            "member_count": self.member_count,
            "active_member_count": self.active_member_count,
            "resource_count": self.resource_count,
            "total_land_area_ha": self.total_land_area_ha,
            "share_capital": str(self.share_capital),
            "currency": self.currency,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
        }
        if include_config:
            data["config"] = self.config.to_dict()
        return data

    def to_summary(self) -> dict[str, Any]:
        """Compact summary for lists"""
        return {
            "cooperative_id": self.cooperative_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.type.value,
            "status": self.status.value,
            "member_count": self.member_count,
        }


@dataclass
class CooperativeMember:
    """
    Member of an agricultural cooperative.
    عضو في التعاونية الزراعية

    Tracks membership, contributions, and access rights.
    """

    # Identification
    member_id: str
    cooperative_id: str
    farmer_id: str  # Reference to farmer entity

    # Personal info - bilingual
    name: str
    name_ar: str
    phone: str
    email: str | None = None

    # Membership details
    role: MemberRole = MemberRole.MEMBER
    status: MemberStatus = MemberStatus.PENDING
    join_date: datetime | None = None
    exit_date: datetime | None = None

    # Contribution
    share_count: int = 1  # عدد الاسهم
    share_value: Decimal = Decimal("0")  # قيمة الاسهم
    land_area_ha: float = 0.0  # المساحة المساهمة
    contribution_percent: Decimal = Decimal("0")  # نسبة المساهمة

    # Farm details
    farm_id: str | None = None
    primary_crops: list[str] = field(default_factory=list)
    farm_location: tuple[float, float] | None = None

    # Access and voting
    voting_rights: bool = True
    resource_access_level: int = 1  # 1-5 priority level
    access_restrictions: list[str] = field(default_factory=list)

    # Financial tracking
    outstanding_dues: Decimal = Decimal("0")  # المستحقات المتأخرة
    total_distributions: Decimal = Decimal("0")  # اجمالي التوزيعات
    last_payment_date: datetime | None = None

    # Engagement
    meetings_attended: int = 0
    last_activity_date: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None
    notes_ar: str | None = None

    @classmethod
    def create(
        cls,
        cooperative_id: str,
        farmer_id: str,
        name: str,
        name_ar: str,
        phone: str,
        **kwargs,
    ) -> CooperativeMember:
        """Factory method to create a new member"""
        return cls(
            member_id=f"MEM-{uuid.uuid4().hex[:8].upper()}",
            cooperative_id=cooperative_id,
            farmer_id=farmer_id,
            name=name,
            name_ar=name_ar,
            phone=phone,
            **kwargs,
        )

    def is_board_member(self) -> bool:
        """Check if member is on the board"""
        return self.role in [
            MemberRole.CHAIRMAN,
            MemberRole.VICE_CHAIRMAN,
            MemberRole.TREASURER,
            MemberRole.SECRETARY,
            MemberRole.BOARD_MEMBER,
        ]

    def is_active(self) -> bool:
        """Check if member is actively participating"""
        return self.status == MemberStatus.ACTIVE

    def can_vote(self) -> bool:
        """Check if member has voting rights"""
        return self.status == MemberStatus.ACTIVE and self.voting_rights and self.role != MemberRole.OBSERVER

    def has_outstanding_dues(self) -> bool:
        """Check if member has unpaid dues"""
        return self.outstanding_dues > Decimal("0")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "member_id": self.member_id,
            "cooperative_id": self.cooperative_id,
            "farmer_id": self.farmer_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "phone": self.phone,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "join_date": self.join_date.isoformat() if self.join_date else None,
            "share_count": self.share_count,
            "share_value": str(self.share_value),
            "land_area_ha": self.land_area_ha,
            "contribution_percent": str(self.contribution_percent),
            "voting_rights": self.voting_rights,
            "outstanding_dues": str(self.outstanding_dues),
            "total_distributions": str(self.total_distributions),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_summary(self) -> dict[str, Any]:
        """Compact summary for lists"""
        return {
            "member_id": self.member_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "role": self.role.value,
            "status": self.status.value,
            "contribution_percent": str(self.contribution_percent),
        }


@dataclass
class SharedResource:
    """
    Shared resource owned/managed by a cooperative.
    مورد مشترك مملوك/مدار من التعاونية

    Includes equipment, storage, transport, etc.
    """

    # Identification
    resource_id: str
    cooperative_id: str

    # Basic info - bilingual
    name: str
    name_ar: str

    # Classification (required field must come before optional fields)
    type: ResourceType

    # Optional fields
    description: str | None = None
    description_ar: str | None = None
    status: ResourceStatus = ResourceStatus.AVAILABLE
    category: str | None = None  # Sub-category

    # Specifications
    make: str | None = None  # الشركة المصنعة
    model: str | None = None  # الموديل
    year: int | None = None  # سنة الصنع
    serial_number: str | None = None  # الرقم التسلسلي

    # Capacity/size
    capacity: float | None = None  # السعة
    capacity_unit: str | None = None  # وحدة السعة
    area_sqm: float | None = None  # المساحة (للتخزين)

    # Location
    location: Address | None = None
    is_mobile: bool = False  # Can be moved to fields

    # Ownership
    ownership_type: str = "cooperative"  # cooperative, leased, donated
    acquisition_date: datetime | None = None
    acquisition_cost: Decimal = Decimal("0")
    current_value: Decimal = Decimal("0")

    # Usage tracking
    total_usage_hours: float = 0.0
    usage_this_season: float = 0.0
    last_used_date: datetime | None = None
    last_used_by: str | None = None  # member_id

    # Maintenance
    next_maintenance_date: datetime | None = None
    maintenance_interval_hours: int | None = None
    total_maintenance_cost: Decimal = Decimal("0")

    # Availability rules
    available_from: datetime | None = None
    available_until: datetime | None = None
    booking_required: bool = True
    min_booking_hours: int = 1
    max_booking_hours: int | None = None

    # Pricing
    usage_fee_per_hour: Decimal = Decimal("0")
    usage_fee_per_ha: Decimal = Decimal("0")
    deposit_required: Decimal = Decimal("0")
    member_discount_percent: Decimal = Decimal("0")

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    images: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        cooperative_id: str,
        name: str,
        name_ar: str,
        type: ResourceType,
        **kwargs,
    ) -> SharedResource:
        """Factory method to create a new shared resource"""
        return cls(
            resource_id=f"RES-{uuid.uuid4().hex[:8].upper()}",
            cooperative_id=cooperative_id,
            name=name,
            name_ar=name_ar,
            type=type,
            **kwargs,
        )

    def is_available(self) -> bool:
        """Check if resource is currently available"""
        if self.status != ResourceStatus.AVAILABLE:
            return False
        now = datetime.now(UTC)
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return True

    def needs_maintenance(self) -> bool:
        """Check if resource needs maintenance"""
        if self.next_maintenance_date:
            return datetime.now(UTC) >= self.next_maintenance_date
        if self.maintenance_interval_hours:
            return self.total_usage_hours >= self.maintenance_interval_hours
        return False

    def calculate_usage_fee(
        self,
        hours: float | None = None,
        hectares: float | None = None,
        is_member: bool = True,
    ) -> Decimal:
        """Calculate usage fee for resource"""
        fee = Decimal("0")

        if hours and self.usage_fee_per_hour:
            fee += self.usage_fee_per_hour * Decimal(str(hours))

        if hectares and self.usage_fee_per_ha:
            fee += self.usage_fee_per_ha * Decimal(str(hectares))

        if is_member and self.member_discount_percent:
            discount = fee * (self.member_discount_percent / Decimal("100"))
            fee -= discount

        return fee

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "resource_id": self.resource_id,
            "cooperative_id": self.cooperative_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "type": self.type.value,
            "status": self.status.value,
            "category": self.category,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "capacity": self.capacity,
            "capacity_unit": self.capacity_unit,
            "location": self.location.to_dict() if self.location else None,
            "is_mobile": self.is_mobile,
            "total_usage_hours": self.total_usage_hours,
            "is_available": self.is_available(),
            "needs_maintenance": self.needs_maintenance(),
            "usage_fee_per_hour": str(self.usage_fee_per_hour),
            "usage_fee_per_ha": str(self.usage_fee_per_ha),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
        }

    def to_summary(self) -> dict[str, Any]:
        """Compact summary for lists"""
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.type.value,
            "status": self.status.value,
            "is_available": self.is_available(),
        }


@dataclass
class ResourceBooking:
    """
    Booking record for a shared resource.
    سجل حجز لمورد مشترك
    """

    # Identification
    booking_id: str
    resource_id: str
    member_id: str
    cooperative_id: str

    # Booking details
    purpose: str
    purpose_ar: str
    field_id: str | None = None  # Target field for equipment

    # Timing
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime | None = None
    duration_hours: float = 0.0

    # Status
    status: str = "pending"  # pending, confirmed, in_progress, completed, cancelled

    # Usage
    actual_hours: float | None = None
    hectares_covered: float | None = None
    operator_id: str | None = None  # If different from member

    # Financial
    estimated_fee: Decimal = Decimal("0")
    actual_fee: Decimal = Decimal("0")
    deposit_paid: Decimal = Decimal("0")
    payment_status: str = "pending"  # pending, paid, refunded

    # Notes
    notes: str | None = None
    completion_notes: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        resource_id: str,
        member_id: str,
        cooperative_id: str,
        purpose: str,
        purpose_ar: str,
        start_time: datetime,
        duration_hours: float,
        **kwargs,
    ) -> ResourceBooking:
        """Factory method to create a new booking"""
        return cls(
            booking_id=f"BKG-{uuid.uuid4().hex[:8].upper()}",
            resource_id=resource_id,
            member_id=member_id,
            cooperative_id=cooperative_id,
            purpose=purpose,
            purpose_ar=purpose_ar,
            start_time=start_time,
            duration_hours=duration_hours,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "booking_id": self.booking_id,
            "resource_id": self.resource_id,
            "member_id": self.member_id,
            "cooperative_id": self.cooperative_id,
            "purpose": self.purpose,
            "purpose_ar": self.purpose_ar,
            "field_id": self.field_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_hours": self.duration_hours,
            "status": self.status,
            "actual_hours": self.actual_hours,
            "hectares_covered": self.hectares_covered,
            "estimated_fee": str(self.estimated_fee),
            "actual_fee": str(self.actual_fee),
            "payment_status": self.payment_status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class GroupPurchaseOrder:
    """
    Group purchase order for bulk buying.
    امر شراء جماعي للشراء بالجملة
    """

    # Identification
    order_id: str
    cooperative_id: str

    # Order details - bilingual
    title: str
    title_ar: str

    # Product info (required fields)
    product_type: str  # seeds, fertilizer, pesticide, equipment
    product_name: str
    product_name_ar: str

    # Optional fields
    description: str | None = None
    description_ar: str | None = None
    supplier_id: str | None = None
    supplier_name: str | None = None

    # Quantities and pricing
    unit: str = "kg"  # kg, bag, liter, piece
    unit_price: Decimal = Decimal("0")  # سعر الوحدة
    bulk_price: Decimal | None = None  # سعر الجملة
    min_order_quantity: float = 0.0
    total_quantity_ordered: float = 0.0
    total_quantity_received: float | None = None

    # Financial
    total_value: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")
    delivery_cost: Decimal = Decimal("0")
    final_amount: Decimal = Decimal("0")

    # Timing
    order_deadline: datetime | None = None
    expected_delivery: datetime | None = None
    actual_delivery: datetime | None = None

    # Status
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    payment_status: str = "pending"  # pending, partial, paid

    # Distribution tracking
    distributed_quantity: float = 0.0
    distribution_date: datetime | None = None

    # Quality
    quality_certificate: str | None = None
    batch_number: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None
    notes: str | None = None

    @classmethod
    def create(
        cls,
        cooperative_id: str,
        title: str,
        title_ar: str,
        product_type: str,
        product_name: str,
        product_name_ar: str,
        **kwargs,
    ) -> GroupPurchaseOrder:
        """Factory method to create a new group purchase order"""
        return cls(
            order_id=f"GPO-{uuid.uuid4().hex[:8].upper()}",
            cooperative_id=cooperative_id,
            title=title,
            title_ar=title_ar,
            product_type=product_type,
            product_name=product_name,
            product_name_ar=product_name_ar,
            **kwargs,
        )

    def calculate_savings(self) -> Decimal:
        """Calculate savings from bulk purchase"""
        if self.bulk_price and self.unit_price:
            per_unit_savings = self.unit_price - self.bulk_price
            return per_unit_savings * Decimal(str(self.total_quantity_ordered))
        return self.discount_amount

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "order_id": self.order_id,
            "cooperative_id": self.cooperative_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "product_type": self.product_type,
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "supplier_name": self.supplier_name,
            "unit": self.unit,
            "unit_price": str(self.unit_price),
            "bulk_price": str(self.bulk_price) if self.bulk_price else None,
            "total_quantity_ordered": self.total_quantity_ordered,
            "total_value": str(self.total_value),
            "discount_amount": str(self.discount_amount),
            "final_amount": str(self.final_amount),
            "savings": str(self.calculate_savings()),
            "status": self.status.value,
            "order_deadline": self.order_deadline.isoformat() if self.order_deadline else None,
            "expected_delivery": self.expected_delivery.isoformat() if self.expected_delivery else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class MemberOrderLine:
    """
    Individual member's order within a group purchase.
    طلب العضو الفردي ضمن الشراء الجماعي
    """

    # Identification
    line_id: str
    order_id: str
    member_id: str

    # Order details
    quantity: float
    unit_price: Decimal = Decimal("0")
    line_total: Decimal = Decimal("0")

    # Allocation
    quantity_allocated: float = 0.0
    quantity_received: float = 0.0

    # Payment
    amount_paid: Decimal = Decimal("0")
    payment_date: datetime | None = None

    # Status
    status: str = "pending"  # pending, confirmed, allocated, delivered

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: str | None = None

    @classmethod
    def create(
        cls,
        order_id: str,
        member_id: str,
        quantity: float,
        unit_price: Decimal,
        **kwargs,
    ) -> MemberOrderLine:
        """Factory method to create a new order line"""
        return cls(
            line_id=f"OL-{uuid.uuid4().hex[:8].upper()}",
            order_id=order_id,
            member_id=member_id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=unit_price * Decimal(str(quantity)),
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "line_id": self.line_id,
            "order_id": self.order_id,
            "member_id": self.member_id,
            "quantity": self.quantity,
            "unit_price": str(self.unit_price),
            "line_total": str(self.line_total),
            "quantity_allocated": self.quantity_allocated,
            "quantity_received": self.quantity_received,
            "amount_paid": str(self.amount_paid),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
