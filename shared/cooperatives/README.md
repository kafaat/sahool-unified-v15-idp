# shared/cooperatives

Agricultural cooperative management for the SAHOOL platform. Supports the full lifecycle
of farmer cooperatives: entity creation with hierarchical federation structure, member
management with roles and contributions, shared resource pooling with conflict-aware
booking, group purchasing, and multi-method revenue distribution.

## File Structure

```
shared/cooperatives/
├── __init__.py       # Public API exports
├── models.py         # Core data classes and enumerations
├── resource_pool.py  # Equipment/storage booking and availability management
└── revenue.py        # Revenue sharing, financial periods, member payments
```

## Key Components

### models.py

All domain entities and enumerations.

**Cooperative types (`CooperativeType`):**
PRODUCTION (joint farming), MARKETING (joint selling), SERVICE (shared services),
MULTI_PURPOSE, CREDIT (financing), IRRIGATION (water management).

**Resource types (`ResourceType`):**
EQUIPMENT, STORAGE, TRANSPORT, PROCESSING, IRRIGATION, LAND, SEEDS, FERTILIZER, PESTICIDE.

**Revenue sharing methods (`RevenueShareMethod`):**
EQUAL, CONTRIBUTION (by share value), PRODUCTION (by volume), LAND_AREA, WEIGHTED, HYBRID.

**Core data classes:**

| Class | Purpose |
|-------|---------|
| `Cooperative` | Main cooperative entity with address, config, stats, and hierarchy |
| `CooperativeConfig` | Rules: min/max members, fees, booking limits, reserve % |
| `CooperativeMember` | Member with role, shares, land area, voting rights, dues |
| `SharedResource` | Pooled asset with specs, availability, usage fees, maintenance |
| `ResourceBooking` | Booking record with timing, fee calculation, status workflow |
| `GroupPurchaseOrder` | Bulk purchasing order with per-member line items |
| `MemberOrderLine` | Individual member allocation within a group purchase |
| `Address` | Bilingual address with governorate, district, village, coordinates |

`Cooperative.create()`, `CooperativeMember.create()`, `SharedResource.create()`,
`ResourceBooking.create()`, `GroupPurchaseOrder.create()`, and `MemberOrderLine.create()`
are factory methods that auto-generate prefixed IDs (COOP-*, MEM-*, RES-*, BKG-*, GPO-*, OL-*).

**Helper methods:**
- `Cooperative.can_accept_members()` - checks status and max_members cap
- `CooperativeMember.can_vote()` - active, non-observer, no outstanding dues required
- `SharedResource.is_available()` - checks status and availability window
- `SharedResource.needs_maintenance()` - checks maintenance schedule
- `SharedResource.calculate_usage_fee(hours, hectares, is_member)` - applies member discount
- `GroupPurchaseOrder.calculate_savings()` - bulk vs. unit price delta

### resource_pool.py

Equipment booking and conflict resolution service.

**Exceptions:**

| Exception | Trigger |
|-----------|---------|
| `BookingConflictError` | Overlapping booking for same resource |
| `ResourceNotAvailableError` | Resource is in maintenance or retired |
| `InsufficientPriorityError` | Member access level too low for resource |

**Core classes:**

| Class | Description |
|-------|-------------|
| `ResourceAvailability` | Availability window with bookings and free slots |
| `UsageStatistics` | Utilization metrics per resource (hours, members, revenue) |
| `MaintenanceRecord` | Maintenance log entry with cost and downtime |
| `ResourcePoolService` | Main service: register resources, create/cancel bookings, check availability |

**Convenience function:** `create_resource_pool(cooperative_id)` returns a new service instance.

### revenue.py

Revenue sharing calculations and financial period management.

**Transaction types (`TransactionType`):**
REVENUE, EXPENSE, DISTRIBUTION, MEMBERSHIP_FEE, ANNUAL_DUES, RESOURCE_FEE,
RESERVE_TRANSFER, LOAN, LOAN_REPAYMENT, ADJUSTMENT.

| Class | Description |
|-------|-------------|
| `FinancialPeriod` | Accounting period (monthly/quarterly/annual) with status |
| `Transaction` | Single financial transaction with amount, type, reference |
| `MemberShare` | Member's share of a distribution: basis value, percentage, amount |
| `DistributionPlan` | Full distribution plan with all member shares and deductions |
| `MemberPayment` | Payment record to a member with status and bank details |
| `RevenueShareCalculator` | Computes shares by EQUAL, CONTRIBUTION, PRODUCTION, LAND_AREA, HYBRID |
| `RevenueService` | Orchestrates periods, transactions, distributions, and payments |

**Convenience function:** `create_revenue_service(cooperative_id)` returns a service instance.

## Usage Example

```python
from datetime import datetime
from shared.cooperatives import (
    Cooperative, CooperativeMember, SharedResource,
    CooperativeType, ResourceType, RevenueShareMethod,
    ResourcePoolService, RevenueService,
    create_resource_pool, create_revenue_service,
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

# Register shared resource
pool = create_resource_pool(coop.cooperative_id)
tractor = SharedResource.create(
    cooperative_id=coop.cooperative_id,
    name="John Deere 5075E",
    name_ar="جون دير 5075E",
    type=ResourceType.EQUIPMENT,
    capacity=75,
    capacity_unit="HP",
    usage_fee_per_hour=150,  # SAR/hour
    member_discount_percent=20,
)

# Check availability and book
availability = await pool.get_availability(
    resource_id=tractor.resource_id,
    date=datetime(2026, 3, 1),
)

booking = await pool.create_booking(
    resource_id=tractor.resource_id,
    member_id=member.member_id,
    purpose="Land preparation for wheat",
    purpose_ar="تحضير الأرض للقمح",
    start_time=datetime(2026, 3, 1, 8, 0),
    duration_hours=6,
)
fee = tractor.calculate_usage_fee(hours=6, is_member=True)
print(f"Member fee: {fee} SAR")  # 720 SAR (with 20% discount)

# Revenue distribution
revenue_svc = create_revenue_service(coop.cooperative_id)
period = await revenue_svc.open_period(name="Q1 2026", name_ar="الربع الأول 2026")
await revenue_svc.record_transaction(
    period_id=period.period_id,
    amount=85000,
    description="Wheat sales",
)
plan = await revenue_svc.create_distribution_plan(
    period_id=period.period_id,
    method=RevenueShareMethod.PRODUCTION,
    members=[member],
    production_data={member.member_id: 42.5},  # tons
)
print(f"Net distributable: {plan.net_distributable} SAR")
```

## Cooperative Hierarchy

Cooperatives support three levels for federated structures:

| Level | Description |
|-------|-------------|
| 0 | Primary cooperative (village/district level) |
| 1 | Regional federation (groups primary cooperatives) |
| 2 | National union |

Set `parent_id` and `level` on `Cooperative` to build the hierarchy.
