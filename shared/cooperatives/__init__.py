"""
SAHOOL Cooperatives Module
==========================
وحدة التعاونيات الزراعية

Agricultural cooperatives support module for SAHOOL platform.

Features:
- Cooperative/group management with hierarchical structure
- Member management with roles and contributions
- Shared resource pooling (equipment, storage, transport)
- Resource booking and scheduling
- Group purchasing support
- Revenue sharing calculations (multiple methods)
- Financial period management and reporting

Supported Revenue Sharing Methods:
- EQUAL: Equal distribution among all members
- CONTRIBUTION: Based on financial contribution (share value)
- PRODUCTION: Based on production volume
- LAND_AREA: Based on contributed land area
- WEIGHTED: Custom weights per member
- HYBRID: Combination of multiple methods

Example Usage:
    from shared.cooperatives import (
        Cooperative,
        CooperativeMember,
        SharedResource,
        ResourcePoolService,
        RevenueService,
        RevenueShareMethod,
    )

    # Create cooperative
    coop = Cooperative.create(
        tenant_id="sahool",
        name="Al-Falah Cooperative",
        name_ar="تعاونية الفلاح",
        type=CooperativeType.MULTI_PURPOSE,
    )

    # Add member
    member = CooperativeMember.create(
        cooperative_id=coop.cooperative_id,
        farmer_id="FRM-001",
        name="Ahmed Hassan",
        name_ar="أحمد حسن",
        phone="+966501234567",
        share_count=5,
        land_area_ha=10.5,
    )

    # Setup resource pool
    pool = ResourcePoolService(cooperative_id=coop.cooperative_id)
    tractor = await pool.register_resource(
        name="John Deere 5075E",
        name_ar="جون دير 5075E",
        type=ResourceType.EQUIPMENT,
        capacity=75,
        capacity_unit="HP",
    )

    # Book resource
    booking = await pool.create_booking(
        resource_id=tractor.resource_id,
        member_id=member.member_id,
        purpose="Land preparation",
        purpose_ar="اعداد الارض",
        start_time=datetime(2026, 2, 1, 8, 0),
        duration_hours=4,
    )

    # Setup revenue service
    revenue = RevenueService(cooperative_id=coop.cooperative_id)

    # Create distribution plan
    plan = await revenue.create_distribution_plan(
        period_id=period.period_id,
        method=RevenueShareMethod.PRODUCTION,
        members=[member],
        production_data={member.member_id: 50.0},  # tons
    )

Author: SAHOOL Platform Team
Updated: January 2026
"""

# Models - Core data structures
from .models import (
    # Enums
    CooperativeType,
    CooperativeStatus,
    MemberRole,
    MemberStatus,
    ResourceType,
    ResourceStatus,
    PurchaseOrderStatus,
    RevenueShareMethod,
    # Data classes
    Address,
    CooperativeConfig,
    Cooperative,
    CooperativeMember,
    SharedResource,
    ResourceBooking,
    GroupPurchaseOrder,
    MemberOrderLine,
)

# Resource Pool - Equipment and storage management
from .resource_pool import (
    # Service
    ResourcePoolService,
    # Data classes
    ResourceAvailability,
    UsageStatistics,
    MaintenanceRecord,
    # Exceptions
    BookingConflictError,
    ResourceNotAvailableError,
    InsufficientPriorityError,
    # Convenience functions
    create_resource_pool,
)

# Revenue - Financial management
from .revenue import (
    # Enums
    TransactionType,
    PeriodStatus,
    PaymentStatus,
    # Data classes
    FinancialPeriod,
    Transaction,
    MemberShare,
    DistributionPlan,
    MemberPayment,
    # Services
    RevenueShareCalculator,
    RevenueService,
    # Convenience functions
    create_revenue_service,
)

__all__ = [
    # === Models - Enums ===
    "CooperativeType",
    "CooperativeStatus",
    "MemberRole",
    "MemberStatus",
    "ResourceType",
    "ResourceStatus",
    "PurchaseOrderStatus",
    "RevenueShareMethod",
    # === Models - Data Classes ===
    "Address",
    "CooperativeConfig",
    "Cooperative",
    "CooperativeMember",
    "SharedResource",
    "ResourceBooking",
    "GroupPurchaseOrder",
    "MemberOrderLine",
    # === Resource Pool ===
    "ResourcePoolService",
    "ResourceAvailability",
    "UsageStatistics",
    "MaintenanceRecord",
    "BookingConflictError",
    "ResourceNotAvailableError",
    "InsufficientPriorityError",
    "create_resource_pool",
    # === Revenue - Enums ===
    "TransactionType",
    "PeriodStatus",
    "PaymentStatus",
    # === Revenue - Data Classes ===
    "FinancialPeriod",
    "Transaction",
    "MemberShare",
    "DistributionPlan",
    "MemberPayment",
    # === Revenue - Services ===
    "RevenueShareCalculator",
    "RevenueService",
    "create_revenue_service",
]

__version__ = "16.0.0"
