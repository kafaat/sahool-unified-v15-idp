"""
Unit Tests for SAHOOL Cooperatives Module
==========================================
Tests for agricultural cooperatives management including:
- Cooperative creation and membership
- Resource pool management
- Equipment sharing and scheduling
- Revenue distribution calculations
- Contribution tracking
- Voting and governance
- Billing and settlements
- Member quota management
- Edge cases (member departures, disputes)

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from shared.cooperatives import (
    # Data classes
    Address,
    # Exceptions
    BookingConflictError,
    Cooperative,
    CooperativeConfig,
    CooperativeMember,
    CooperativeStatus,
    # Enums
    CooperativeType,
    DistributionPlan,
    FinancialPeriod,
    GroupPurchaseOrder,
    MaintenanceRecord,
    MemberOrderLine,
    MemberPayment,
    MemberRole,
    MemberShare,
    MemberStatus,
    PaymentStatus,
    PeriodStatus,
    PurchaseOrderStatus,
    ResourceAvailability,
    ResourceBooking,
    ResourceNotAvailableError,
    # Services
    ResourcePoolService,
    ResourceStatus,
    ResourceType,
    RevenueService,
    RevenueShareCalculator,
    RevenueShareMethod,
    SharedResource,
    Transaction,
    TransactionType,
    UsageStatistics,
    # Convenience functions
    create_resource_pool,
    create_revenue_service,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_address():
    """Create a sample address for testing"""
    return Address(
        governorate="Riyadh",
        district="Al-Kharj",
        village="Al-Dilam",
        street="Main Street",
        postal_code="11942",
        coordinates=(24.1477, 47.2136),
    )


@pytest.fixture
def sample_config():
    """Create a sample cooperative configuration"""
    return CooperativeConfig(
        min_members=5,
        max_members=50,
        membership_fee=Decimal("500.00"),
        annual_dues=Decimal("200.00"),
        default_share_method=RevenueShareMethod.CONTRIBUTION,
        management_fee_percent=Decimal("5.0"),
        reserve_fund_percent=Decimal("10.0"),
        max_equipment_hours_per_member=100,
        priority_by_seniority=True,
        advance_booking_days=7,
    )


@pytest.fixture
def sample_cooperative(sample_address, sample_config):
    """Create a sample cooperative for testing"""
    coop = Cooperative.create(
        tenant_id="sahool",
        name="Al-Falah Agricultural Cooperative",
        name_ar="تعاونية الفلاح الزراعية",
        type=CooperativeType.MULTI_PURPOSE,
        description="Multi-purpose agricultural cooperative",
        description_ar="تعاونية زراعية متعددة الاغراض",
        address=sample_address,
        config=sample_config,
    )
    coop.status = CooperativeStatus.ACTIVE
    coop.member_count = 10
    coop.active_member_count = 8
    return coop


@pytest.fixture
def sample_members(sample_cooperative):
    """Create sample members for testing"""
    members = []
    for i in range(5):
        member = CooperativeMember.create(
            cooperative_id=sample_cooperative.cooperative_id,
            farmer_id=f"FRM-{i:03d}",
            name=f"Farmer {i}",
            name_ar=f"مزارع {i}",
            phone=f"+9665012345{i:02d}",
            share_count=i + 1,
            share_value=Decimal(str((i + 1) * 1000)),
            land_area_ha=float(i + 1) * 2.5,
            status=MemberStatus.ACTIVE,
        )
        member.join_date = datetime.now(UTC) - timedelta(days=(5 - i) * 30)
        members.append(member)
    return members


@pytest.fixture
def sample_resource(sample_cooperative):
    """Create a sample shared resource"""
    return SharedResource.create(
        cooperative_id=sample_cooperative.cooperative_id,
        name="John Deere 5075E Tractor",
        name_ar="جرار جون دير 5075E",
        type=ResourceType.EQUIPMENT,
        make="John Deere",
        model="5075E",
        year=2024,
        capacity=75.0,
        capacity_unit="HP",
        usage_fee_per_hour=Decimal("150.00"),
        usage_fee_per_ha=Decimal("200.00"),
        member_discount_percent=Decimal("10.0"),
        deposit_required=Decimal("500.00"),
        min_booking_hours=2,
        max_booking_hours=8,
    )


@pytest.fixture
def resource_pool_service(sample_cooperative):
    """Create a resource pool service for testing"""
    return ResourcePoolService(cooperative_id=sample_cooperative.cooperative_id)


@pytest.fixture
def revenue_service(sample_cooperative):
    """Create a revenue service for testing"""
    return RevenueService(cooperative_id=sample_cooperative.cooperative_id)


# ═══════════════════════════════════════════════════════════════════════════
# Address Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAddress:
    """Test Address data class"""

    def test_address_creation(self, sample_address):
        """Test creating an address"""
        assert sample_address.governorate == "Riyadh"
        assert sample_address.district == "Al-Kharj"
        assert sample_address.village == "Al-Dilam"
        assert sample_address.coordinates == (24.1477, 47.2136)

    def test_address_full_address(self, sample_address):
        """Test full address string generation"""
        full = sample_address.full_address
        assert "Al-Dilam" in full
        assert "Al-Kharj" in full
        assert "Riyadh" in full

    def test_address_full_address_ar(self, sample_address):
        """Test Arabic full address string generation"""
        full_ar = sample_address.full_address_ar
        # Arabic uses ، separator
        assert "، " in full_ar or sample_address.governorate in full_ar

    def test_address_to_dict(self, sample_address):
        """Test address serialization to dict"""
        data = sample_address.to_dict()
        assert data["governorate"] == "Riyadh"
        assert data["coordinates"] == (24.1477, 47.2136)

    def test_address_minimal(self):
        """Test address with minimal fields"""
        addr = Address(governorate="Riyadh", district="Central")
        assert addr.village is None
        assert addr.full_address == "Central, Riyadh"


# ═══════════════════════════════════════════════════════════════════════════
# Cooperative Creation and Configuration Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCooperativeConfig:
    """Test CooperativeConfig data class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = CooperativeConfig()
        assert config.min_members == 7
        assert config.max_members is None
        assert config.membership_fee == Decimal("0")
        assert config.default_share_method == RevenueShareMethod.CONTRIBUTION

    def test_custom_config(self, sample_config):
        """Test custom configuration"""
        assert sample_config.min_members == 5
        assert sample_config.max_members == 50
        assert sample_config.membership_fee == Decimal("500.00")

    def test_config_to_dict(self, sample_config):
        """Test config serialization"""
        data = sample_config.to_dict()
        assert data["min_members"] == 5
        assert data["max_members"] == 50
        assert data["membership_fee"] == "500.00"


@pytest.mark.unit
class TestCooperative:
    """Test Cooperative data class"""

    def test_cooperative_creation(self, sample_cooperative):
        """Test creating a cooperative"""
        assert sample_cooperative.cooperative_id.startswith("COOP-")
        assert sample_cooperative.tenant_id == "sahool"
        assert sample_cooperative.name == "Al-Falah Agricultural Cooperative"
        assert sample_cooperative.type == CooperativeType.MULTI_PURPOSE

    def test_cooperative_factory_method(self):
        """Test Cooperative.create factory method"""
        coop = Cooperative.create(
            tenant_id="test",
            name="Test Coop",
            name_ar="تعاونية اختبار",
            type=CooperativeType.PRODUCTION,
        )
        assert coop.cooperative_id.startswith("COOP-")
        assert len(coop.cooperative_id) == 13  # COOP- + 8 hex chars

    def test_cooperative_is_primary(self, sample_cooperative):
        """Test is_primary method"""
        assert sample_cooperative.is_primary() is True

        # Federation has level > 0
        sample_cooperative.level = 1
        assert sample_cooperative.is_primary() is False

    def test_cooperative_is_federation(self, sample_cooperative):
        """Test is_federation method"""
        assert sample_cooperative.is_federation() is False

        sample_cooperative.level = 2
        assert sample_cooperative.is_federation() is True

    def test_cooperative_can_accept_members(self, sample_cooperative):
        """Test can_accept_members method"""
        sample_cooperative.status = CooperativeStatus.ACTIVE
        sample_cooperative.member_count = 10
        sample_cooperative.config.max_members = 50
        assert sample_cooperative.can_accept_members() is True

    def test_cooperative_cannot_accept_members_when_full(self, sample_cooperative):
        """Test cooperative full rejection"""
        sample_cooperative.config.max_members = 10
        sample_cooperative.member_count = 10
        assert sample_cooperative.can_accept_members() is False

    def test_cooperative_cannot_accept_members_when_inactive(self, sample_cooperative):
        """Test inactive cooperative rejection"""
        sample_cooperative.status = CooperativeStatus.SUSPENDED
        assert sample_cooperative.can_accept_members() is False

    def test_cooperative_to_dict(self, sample_cooperative):
        """Test cooperative serialization"""
        data = sample_cooperative.to_dict()
        assert data["cooperative_id"] == sample_cooperative.cooperative_id
        assert data["type"] == "multi_purpose"
        assert data["status"] == "active"

    def test_cooperative_to_summary(self, sample_cooperative):
        """Test cooperative summary serialization"""
        summary = sample_cooperative.to_summary()
        assert "cooperative_id" in summary
        assert "name" in summary
        assert "name_ar" in summary
        assert "member_count" in summary


# ═══════════════════════════════════════════════════════════════════════════
# Membership Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCooperativeMember:
    """Test CooperativeMember data class"""

    def test_member_creation(self, sample_members):
        """Test creating a member"""
        member = sample_members[0]
        assert member.member_id.startswith("MEM-")
        assert member.name == "Farmer 0"
        assert member.status == MemberStatus.ACTIVE

    def test_member_factory_method(self, sample_cooperative):
        """Test CooperativeMember.create factory method"""
        member = CooperativeMember.create(
            cooperative_id=sample_cooperative.cooperative_id,
            farmer_id="FRM-999",
            name="Test Farmer",
            name_ar="مزارع اختبار",
            phone="+966501234567",
        )
        assert member.member_id.startswith("MEM-")
        assert member.status == MemberStatus.PENDING  # Default

    def test_member_is_board_member(self, sample_members):
        """Test is_board_member method"""
        member = sample_members[0]
        assert member.is_board_member() is False

        member.role = MemberRole.CHAIRMAN
        assert member.is_board_member() is True

        member.role = MemberRole.TREASURER
        assert member.is_board_member() is True

    def test_member_is_active(self, sample_members):
        """Test is_active method"""
        member = sample_members[0]
        assert member.is_active() is True

        member.status = MemberStatus.SUSPENDED
        assert member.is_active() is False

    def test_member_can_vote(self, sample_members):
        """Test can_vote method"""
        member = sample_members[0]
        assert member.can_vote() is True

        # Observer cannot vote
        member.role = MemberRole.OBSERVER
        assert member.can_vote() is False

        # Suspended member cannot vote
        member.role = MemberRole.MEMBER
        member.status = MemberStatus.SUSPENDED
        assert member.can_vote() is False

        # Member with voting rights disabled
        member.status = MemberStatus.ACTIVE
        member.voting_rights = False
        assert member.can_vote() is False

    def test_member_has_outstanding_dues(self, sample_members):
        """Test has_outstanding_dues method"""
        member = sample_members[0]
        assert member.has_outstanding_dues() is False

        member.outstanding_dues = Decimal("100.00")
        assert member.has_outstanding_dues() is True

    def test_member_to_dict(self, sample_members):
        """Test member serialization"""
        member = sample_members[0]
        data = member.to_dict()
        assert data["member_id"] == member.member_id
        assert data["role"] == "member"
        assert data["status"] == "active"

    def test_member_to_summary(self, sample_members):
        """Test member summary serialization"""
        member = sample_members[0]
        summary = member.to_summary()
        assert "member_id" in summary
        assert "name" in summary
        assert "role" in summary


# ═══════════════════════════════════════════════════════════════════════════
# Resource Pool Management Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSharedResource:
    """Test SharedResource data class"""

    def test_resource_creation(self, sample_resource):
        """Test creating a shared resource"""
        assert sample_resource.resource_id.startswith("RES-")
        assert sample_resource.name == "John Deere 5075E Tractor"
        assert sample_resource.type == ResourceType.EQUIPMENT

    def test_resource_is_available(self, sample_resource):
        """Test is_available method"""
        sample_resource.status = ResourceStatus.AVAILABLE
        assert sample_resource.is_available() is True

        sample_resource.status = ResourceStatus.IN_USE
        assert sample_resource.is_available() is False

        sample_resource.status = ResourceStatus.MAINTENANCE
        assert sample_resource.is_available() is False

    def test_resource_is_available_with_time_window(self, sample_resource):
        """Test is_available with time windows"""
        sample_resource.status = ResourceStatus.AVAILABLE
        now = datetime.now(UTC)

        # Available in future only
        sample_resource.available_from = now + timedelta(days=1)
        assert sample_resource.is_available() is False

        # Available in past only
        sample_resource.available_from = now - timedelta(days=10)
        sample_resource.available_until = now - timedelta(days=1)
        assert sample_resource.is_available() is False

    def test_resource_needs_maintenance(self, sample_resource):
        """Test needs_maintenance method"""
        assert sample_resource.needs_maintenance() is False

        # Maintenance date in past
        sample_resource.next_maintenance_date = datetime.now(UTC) - timedelta(days=1)
        assert sample_resource.needs_maintenance() is True

        # By hours
        sample_resource.next_maintenance_date = None
        sample_resource.maintenance_interval_hours = 100
        sample_resource.total_usage_hours = 150
        assert sample_resource.needs_maintenance() is True

    def test_resource_calculate_usage_fee(self, sample_resource):
        """Test calculate_usage_fee method"""
        # Per hour only
        fee = sample_resource.calculate_usage_fee(hours=4, is_member=True)
        # 4 * 150 = 600, with 10% discount = 540
        expected = Decimal("600.00") - Decimal("60.00")
        assert fee == expected

        # Non-member (no discount)
        fee = sample_resource.calculate_usage_fee(hours=4, is_member=False)
        assert fee == Decimal("600.00")

        # Per hectare
        fee = sample_resource.calculate_usage_fee(hectares=5, is_member=False)
        assert fee == Decimal("1000.00")  # 5 * 200

    def test_resource_to_dict(self, sample_resource):
        """Test resource serialization"""
        data = sample_resource.to_dict()
        assert data["resource_id"] == sample_resource.resource_id
        assert data["type"] == "equipment"
        assert "is_available" in data


# ═══════════════════════════════════════════════════════════════════════════
# Equipment Sharing and Scheduling Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestResourcePoolService:
    """Test ResourcePoolService"""

    @pytest.mark.asyncio
    async def test_register_resource(self, resource_pool_service):
        """Test registering a new resource"""
        resource = await resource_pool_service.register_resource(
            name="New Harvester",
            name_ar="حصادة جديدة",
            type=ResourceType.EQUIPMENT,
            capacity=200,
            capacity_unit="HP",
        )
        assert resource.resource_id.startswith("RES-")
        assert resource.name == "New Harvester"

    @pytest.mark.asyncio
    async def test_get_resource(self, resource_pool_service):
        """Test getting a resource by ID"""
        resource = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
        )

        fetched = await resource_pool_service.get_resource(resource.resource_id)
        assert fetched is not None
        assert fetched.resource_id == resource.resource_id

    @pytest.mark.asyncio
    async def test_update_resource_status(self, resource_pool_service):
        """Test updating resource status"""
        resource = await resource_pool_service.register_resource(
            name="Test Equipment",
            name_ar="معدات اختبار",
            type=ResourceType.EQUIPMENT,
        )

        updated = await resource_pool_service.update_resource_status(resource.resource_id, ResourceStatus.MAINTENANCE)
        assert updated.status == ResourceStatus.MAINTENANCE

    @pytest.mark.asyncio
    async def test_list_resources(self, resource_pool_service):
        """Test listing resources with filters"""
        await resource_pool_service.register_resource(name="Tractor 1", name_ar="جرار 1", type=ResourceType.EQUIPMENT)
        await resource_pool_service.register_resource(name="Storage 1", name_ar="مخزن 1", type=ResourceType.STORAGE)

        # List all
        all_resources = await resource_pool_service.list_resources()
        assert len(all_resources) == 2

        # Filter by type
        equipment = await resource_pool_service.list_resources(type=ResourceType.EQUIPMENT)
        assert len(equipment) == 1
        assert equipment[0].name == "Tractor 1"

    @pytest.mark.asyncio
    async def test_create_booking(self, resource_pool_service, sample_members):
        """Test creating a booking"""
        resource = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
            usage_fee_per_hour=Decimal("100.00"),
        )

        start_time = datetime.now(UTC) + timedelta(days=1)
        booking = await resource_pool_service.create_booking(
            resource_id=resource.resource_id,
            member_id=sample_members[0].member_id,
            purpose="Land preparation",
            purpose_ar="اعداد الارض",
            start_time=start_time,
            duration_hours=4,
        )

        assert booking.booking_id.startswith("BKG-")
        assert booking.status == "confirmed"
        assert booking.duration_hours == 4

    @pytest.mark.asyncio
    async def test_booking_conflict_detection(self, resource_pool_service, sample_members):
        """Test booking conflict detection"""
        resource = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
        )

        start_time = datetime.now(UTC) + timedelta(days=1)

        # First booking
        await resource_pool_service.create_booking(
            resource_id=resource.resource_id,
            member_id=sample_members[0].member_id,
            purpose="First booking",
            purpose_ar="الحجز الاول",
            start_time=start_time,
            duration_hours=4,
        )

        # Conflicting booking
        with pytest.raises(BookingConflictError):
            await resource_pool_service.create_booking(
                resource_id=resource.resource_id,
                member_id=sample_members[1].member_id,
                purpose="Conflicting booking",
                purpose_ar="حجز متعارض",
                start_time=start_time + timedelta(hours=2),  # Overlaps
                duration_hours=4,
            )

    @pytest.mark.asyncio
    async def test_booking_resource_not_available(self, resource_pool_service, sample_members):
        """Test booking unavailable resource"""
        resource = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
        )
        resource.status = ResourceStatus.MAINTENANCE

        with pytest.raises(ResourceNotAvailableError):
            await resource_pool_service.create_booking(
                resource_id=resource.resource_id,
                member_id=sample_members[0].member_id,
                purpose="Book maintenance equipment",
                purpose_ar="حجز معدات صيانة",
                start_time=datetime.now(UTC) + timedelta(days=1),
                duration_hours=4,
            )

    @pytest.mark.asyncio
    async def test_cancel_booking(self, resource_pool_service, sample_members):
        """Test cancelling a booking"""
        resource = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
        )

        booking = await resource_pool_service.create_booking(
            resource_id=resource.resource_id,
            member_id=sample_members[0].member_id,
            purpose="Test booking",
            purpose_ar="حجز اختبار",
            start_time=datetime.now(UTC) + timedelta(days=5),
            duration_hours=4,
        )

        cancelled = await resource_pool_service.cancel_booking(booking.booking_id, reason="Weather conditions")
        assert cancelled.status == "cancelled"

    @pytest.mark.asyncio
    async def test_complete_booking(self, resource_pool_service, sample_members):
        """Test completing a booking with actual usage"""
        resource = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
            usage_fee_per_hour=Decimal("100.00"),
        )

        booking = await resource_pool_service.create_booking(
            resource_id=resource.resource_id,
            member_id=sample_members[0].member_id,
            purpose="Plowing",
            purpose_ar="حرث",
            start_time=datetime.now(UTC) - timedelta(hours=6),
            duration_hours=4,
            check_conflicts=False,
        )

        completed = await resource_pool_service.complete_booking(
            booking.booking_id,
            actual_hours=5,
            hectares_covered=10.5,
            completion_notes="Completed successfully",
        )

        assert completed.status == "completed"
        assert completed.actual_hours == 5
        assert completed.hectares_covered == 10.5


@pytest.mark.unit
class TestResourceAvailability:
    """Test ResourceAvailability"""

    def test_is_available_at(self):
        """Test checking availability at specific hour"""
        avail = ResourceAvailability(
            resource_id="RES-001",
            date=datetime.now(UTC),
            available_hours=list(range(6, 20)),  # 6 AM to 8 PM
            booked_slots=[(8, 12), (14, 16)],
        )

        assert avail.is_available_at(6) is True
        assert avail.is_available_at(10) is False  # Booked 8-12
        assert avail.is_available_at(13) is True
        assert avail.is_available_at(15) is False  # Booked 14-16
        assert avail.is_available_at(22) is False  # Outside operating hours

    def test_get_available_slots(self):
        """Test getting available slots"""
        avail = ResourceAvailability(
            resource_id="RES-001",
            date=datetime.now(UTC),
            available_hours=list(range(6, 20)),
            booked_slots=[(8, 12)],
        )

        slots = avail.get_available_slots()
        # Should have slots: 6-8, 12-20
        assert (6, 8) in slots
        assert (12, 20) in slots


@pytest.mark.unit
class TestMaintenanceRecord:
    """Test MaintenanceRecord"""

    def test_create_maintenance_record(self):
        """Test creating a maintenance record"""
        record = MaintenanceRecord.create(
            resource_id="RES-001",
            type="scheduled",
            description="Oil change and filter replacement",
            description_ar="تغيير الزيت والفلتر",
            scheduled_date=datetime.now(UTC) + timedelta(days=7),
        )

        assert record.record_id.startswith("MNT-")
        assert record.type == "scheduled"
        assert record.status == "scheduled"


# ═══════════════════════════════════════════════════════════════════════════
# Revenue Distribution Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRevenueShareCalculator:
    """Test RevenueShareCalculator"""

    def test_calculate_equal_shares(self, sample_members):
        """Test equal distribution among members"""
        calculator = RevenueShareCalculator()
        shares = calculator.calculate_equal(
            total_amount=Decimal("10000.00"),
            members=sample_members,
        )

        assert len(shares) == 5
        total_distributed = sum(s.net_share for s in shares)
        assert total_distributed == Decimal("10000.00")

        # Each member gets ~2000
        for share in shares:
            assert share.net_share == Decimal("2000.00")

    def test_calculate_by_contribution(self, sample_members):
        """Test distribution by financial contribution"""
        calculator = RevenueShareCalculator()
        shares = calculator.calculate_by_contribution(
            total_amount=Decimal("15000.00"),
            members=sample_members,
        )

        assert len(shares) == 5
        total_distributed = sum(s.net_share for s in shares)
        assert total_distributed == Decimal("15000.00")

        # Higher share value = higher distribution
        # Members have share values: 1000, 2000, 3000, 4000, 5000
        # Total: 15000
        for i, share in enumerate(shares):
            expected_percent = (i + 1) * 1000 / 15000 * 100
            assert abs(float(share.contribution_percent) - expected_percent) < 0.1

    def test_calculate_by_production(self, sample_members):
        """Test distribution by production volume"""
        calculator = RevenueShareCalculator()
        production_data = {
            sample_members[0].member_id: 10.0,
            sample_members[1].member_id: 20.0,
            sample_members[2].member_id: 30.0,
            sample_members[3].member_id: 25.0,
            sample_members[4].member_id: 15.0,
        }

        shares = calculator.calculate_by_production(
            total_amount=Decimal("100000.00"),
            members=sample_members,
            production_data=production_data,
        )

        assert len(shares) == 5
        total_distributed = sum(s.net_share for s in shares)
        assert total_distributed == Decimal("100000.00")

        # Member with 30.0 production should get 30%
        member_30 = next(s for s in shares if s.production_volume == 30.0)
        assert abs(float(member_30.contribution_percent) - 30.0) < 0.1

    def test_calculate_by_land_area(self, sample_members):
        """Test distribution by land area"""
        calculator = RevenueShareCalculator()
        shares = calculator.calculate_by_land_area(
            total_amount=Decimal("50000.00"),
            members=sample_members,
        )

        assert len(shares) == 5
        total_distributed = sum(s.net_share for s in shares)
        assert total_distributed == Decimal("50000.00")

        # Members have land: 2.5, 5.0, 7.5, 10.0, 12.5 ha
        # Total: 37.5 ha
        for i, share in enumerate(shares):
            expected_percent = ((i + 1) * 2.5 / 37.5) * 100
            assert abs(float(share.contribution_percent) - expected_percent) < 0.1

    def test_calculate_weighted(self, sample_members):
        """Test distribution with custom weights"""
        calculator = RevenueShareCalculator()
        custom_weights = {
            sample_members[0].member_id: Decimal("1"),
            sample_members[1].member_id: Decimal("2"),
            sample_members[2].member_id: Decimal("3"),
            sample_members[3].member_id: Decimal("4"),
            sample_members[4].member_id: Decimal("5"),
        }

        shares = calculator.calculate_weighted(
            total_amount=Decimal("15000.00"),
            members=sample_members,
            custom_weights=custom_weights,
        )

        assert len(shares) == 5
        total_distributed = sum(s.net_share for s in shares)
        assert total_distributed == Decimal("15000.00")

    def test_calculate_hybrid(self, sample_members):
        """Test hybrid distribution (multiple methods)"""
        calculator = RevenueShareCalculator()
        production_data = {m.member_id: float(i + 1) * 10 for i, m in enumerate(sample_members)}

        shares = calculator.calculate_hybrid(
            total_amount=Decimal("100000.00"),
            members=sample_members,
            method_weights={"equal": 0.3, "production": 0.7},
            production_data=production_data,
        )

        assert len(shares) == 5
        total_distributed = sum(s.net_share for s in shares)
        # May have small rounding differences
        assert abs(total_distributed - Decimal("100000.00")) < Decimal("1.00")

    def test_calculate_empty_members(self, sample_members):
        """Test distribution with empty member list"""
        calculator = RevenueShareCalculator()
        shares = calculator.calculate_equal(
            total_amount=Decimal("10000.00"),
            members=[],
        )
        assert shares == []

    def test_calculate_filters_inactive_members(self, sample_members):
        """Test that inactive members are filtered out"""
        sample_members[0].status = MemberStatus.SUSPENDED
        sample_members[1].status = MemberStatus.WITHDRAWN

        calculator = RevenueShareCalculator()
        shares = calculator.calculate(
            method=RevenueShareMethod.EQUAL,
            total_amount=Decimal("9000.00"),
            members=sample_members,
        )

        # Only 3 active members
        assert len(shares) == 3
        for share in shares:
            assert share.net_share == Decimal("3000.00")


# ═══════════════════════════════════════════════════════════════════════════
# Contribution Tracking Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestContributionTracking:
    """Test contribution tracking in member shares"""

    def test_member_share_breakdown(self, sample_members):
        """Test member share breakdown details"""
        calculator = RevenueShareCalculator()
        shares = calculator.calculate_by_contribution(
            total_amount=Decimal("15000.00"),
            members=sample_members,
        )

        for share in shares:
            assert "contribution_share" in share.share_breakdown
            assert "share_value" in share.share_breakdown

    def test_member_share_calculate_net(self):
        """Test MemberShare.calculate_net method"""
        share = MemberShare(
            member_id="MEM-001",
            member_name="Test Member",
            member_name_ar="عضو اختبار",
            base_share=Decimal("1000.00"),
            bonus_share=Decimal("100.00"),
            deductions=Decimal("50.00"),
        )

        net = share.calculate_net()
        assert net == Decimal("1050.00")
        assert share.net_share == Decimal("1050.00")


# ═══════════════════════════════════════════════════════════════════════════
# Voting and Governance Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestVotingAndGovernance:
    """Test voting rights and governance"""

    def test_member_voting_rights(self, sample_members):
        """Test member voting rights"""
        # Regular active member can vote
        member = sample_members[0]
        member.status = MemberStatus.ACTIVE
        member.voting_rights = True
        member.role = MemberRole.MEMBER
        assert member.can_vote() is True

    def test_observer_cannot_vote(self, sample_members):
        """Test that observers cannot vote"""
        member = sample_members[0]
        member.role = MemberRole.OBSERVER
        assert member.can_vote() is False

    def test_board_members_roles(self, sample_members):
        """Test board member role detection"""
        member = sample_members[0]

        board_roles = [
            MemberRole.CHAIRMAN,
            MemberRole.VICE_CHAIRMAN,
            MemberRole.TREASURER,
            MemberRole.SECRETARY,
            MemberRole.BOARD_MEMBER,
        ]

        for role in board_roles:
            member.role = role
            assert member.is_board_member() is True

        member.role = MemberRole.MEMBER
        assert member.is_board_member() is False


# ═══════════════════════════════════════════════════════════════════════════
# Billing and Settlements Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBillingAndSettlements:
    """Test billing and settlement functionality"""

    @pytest.mark.asyncio
    async def test_record_revenue(self, revenue_service):
        """Test recording revenue"""
        period = await revenue_service.create_period(
            name="Test Period",
            name_ar="فترة اختبار",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 3, 31, tzinfo=UTC),
        )

        txn = await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("50000.00"),
            description="Wheat sales",
            description_ar="مبيعات القمح",
            source="crop_sales",
        )

        assert txn.transaction_id.startswith("TXN-")
        assert txn.type == TransactionType.REVENUE
        assert txn.amount == Decimal("50000.00")

        # Period should be updated
        period = await revenue_service.get_period(period.period_id)
        assert period.total_revenue == Decimal("50000.00")

    @pytest.mark.asyncio
    async def test_record_expense(self, revenue_service):
        """Test recording expense"""
        period = await revenue_service.create_period(
            name="Test Period",
            name_ar="فترة اختبار",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 3, 31, tzinfo=UTC),
        )

        txn = await revenue_service.record_expense(
            period_id=period.period_id,
            amount=Decimal("5000.00"),
            description="Fuel costs",
            description_ar="تكاليف الوقود",
            category="operations",
        )

        assert txn.type == TransactionType.EXPENSE
        assert txn.amount == Decimal("5000.00")

        period = await revenue_service.get_period(period.period_id)
        assert period.total_expenses == Decimal("5000.00")
        assert period.net_income == Decimal("-5000.00")

    @pytest.mark.asyncio
    async def test_distribution_plan_creation(self, revenue_service, sample_members):
        """Test creating a distribution plan"""
        period = await revenue_service.create_period(
            name="Winter Season",
            name_ar="موسم الشتاء",
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 3, 31),
        )

        await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("100000.00"),
            description="Season revenue",
            description_ar="ايرادات الموسم",
        )

        plan = await revenue_service.create_distribution_plan(
            period_id=period.period_id,
            method=RevenueShareMethod.CONTRIBUTION,
            members=sample_members,
        )

        assert plan.plan_id.startswith("DIST-")
        assert plan.total_amount == Decimal("100000.00")
        assert plan.management_fee_percent == Decimal("5.0")
        assert plan.reserve_fund_percent == Decimal("10.0")
        # Distributable = 100000 - 5000 - 10000 = 85000
        assert plan.distributable_amount == Decimal("85000.00")
        assert len(plan.member_shares) == 5

    @pytest.mark.asyncio
    async def test_distribution_execution(self, revenue_service, sample_members):
        """Test executing a distribution"""
        period = await revenue_service.create_period(
            name="Test Period",
            name_ar="فترة اختبار",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 3, 31, tzinfo=UTC),
        )

        await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("50000.00"),
            description="Revenue",
            description_ar="ايرادات",
        )

        plan = await revenue_service.create_distribution_plan(
            period_id=period.period_id,
            method=RevenueShareMethod.EQUAL,
            members=sample_members,
        )

        # Approve first
        await revenue_service.approve_distribution(plan.plan_id, approved_by="admin")

        # Execute
        payments = await revenue_service.execute_distribution(plan.plan_id)

        assert len(payments) == 5
        for payment in payments:
            assert payment.payment_id.startswith("PAY-")
            assert payment.status == PaymentStatus.PENDING

    @pytest.mark.asyncio
    async def test_process_payment(self, revenue_service, sample_members):
        """Test processing a member payment"""
        period = await revenue_service.create_period(
            name="Test Period",
            name_ar="فترة اختبار",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 3, 31, tzinfo=UTC),
        )

        await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("50000.00"),
            description="Revenue",
            description_ar="ايرادات",
        )

        plan = await revenue_service.create_distribution_plan(
            period_id=period.period_id,
            method=RevenueShareMethod.EQUAL,
            members=sample_members,
        )

        await revenue_service.approve_distribution(plan.plan_id, approved_by="admin")
        payments = await revenue_service.execute_distribution(plan.plan_id)

        # Process first payment
        processed = await revenue_service.process_payment(
            payment_id=payments[0].payment_id,
            payment_method="bank_transfer",
            reference="TRX-001",
            processed_by="treasurer",
        )

        assert processed.status == PaymentStatus.PAID
        assert processed.payment_method == "bank_transfer"
        assert processed.reference == "TRX-001"


# ═══════════════════════════════════════════════════════════════════════════
# Member Quota Management Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestMemberQuotaManagement:
    """Test member quota and resource access management"""

    def test_member_resource_access_level(self, sample_members):
        """Test member resource access levels"""
        member = sample_members[0]
        member.resource_access_level = 3
        assert member.resource_access_level == 3

    def test_member_access_restrictions(self, sample_members):
        """Test member access restrictions"""
        member = sample_members[0]
        member.access_restrictions = ["heavy_equipment", "storage_A"]
        assert "heavy_equipment" in member.access_restrictions

    @pytest.mark.asyncio
    async def test_booking_duration_limits(self, resource_pool_service, sample_members):
        """Test booking duration limits"""
        resource = await resource_pool_service.register_resource(
            name="Limited Tractor",
            name_ar="جرار محدود",
            type=ResourceType.EQUIPMENT,
            min_booking_hours=2,
            max_booking_hours=6,
        )

        # Too short
        with pytest.raises(ValueError) as exc_info:
            await resource_pool_service.create_booking(
                resource_id=resource.resource_id,
                member_id=sample_members[0].member_id,
                purpose="Short booking",
                purpose_ar="حجز قصير",
                start_time=datetime.utcnow() + timedelta(days=1),
                duration_hours=1,  # Less than minimum
            )
        assert "Minimum booking duration" in str(exc_info.value)

        # Too long
        with pytest.raises(ValueError) as exc_info:
            await resource_pool_service.create_booking(
                resource_id=resource.resource_id,
                member_id=sample_members[0].member_id,
                purpose="Long booking",
                purpose_ar="حجز طويل",
                start_time=datetime.utcnow() + timedelta(days=1),
                duration_hours=10,  # More than maximum
            )
        assert "Maximum booking duration" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════
# Edge Cases Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_member_departure(self, sample_members):
        """Test member departure handling"""
        member = sample_members[0]
        member.status = MemberStatus.WITHDRAWN
        member.exit_date = datetime.utcnow()

        assert member.is_active() is False
        assert member.can_vote() is False

    def test_member_expulsion(self, sample_members):
        """Test member expulsion handling"""
        member = sample_members[0]
        member.status = MemberStatus.EXPELLED
        member.exit_date = datetime.utcnow()

        assert member.is_active() is False
        assert member.can_vote() is False

    def test_cooperative_dissolution(self, sample_cooperative):
        """Test cooperative dissolution"""
        sample_cooperative.status = CooperativeStatus.DISSOLVED
        assert sample_cooperative.can_accept_members() is False

    @pytest.mark.asyncio
    async def test_closed_period_no_transactions(self, revenue_service):
        """Test that closed periods don't accept transactions"""
        period = await revenue_service.create_period(
            name="Closed Period",
            name_ar="فترة مغلقة",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 3, 31),
        )

        await revenue_service.close_period(period.period_id)

        with pytest.raises(ValueError) as exc_info:
            await revenue_service.record_revenue(
                period_id=period.period_id,
                amount=Decimal("1000.00"),
                description="Late revenue",
                description_ar="ايراد متأخر",
            )
        assert "not open" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unapproved_distribution_execution(self, revenue_service, sample_members):
        """Test that unapproved distributions cannot be executed"""
        period = await revenue_service.create_period(
            name="Test Period",
            name_ar="فترة اختبار",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
            end_date=datetime(2026, 3, 31, tzinfo=UTC),
        )

        await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("50000.00"),
            description="Revenue",
            description_ar="ايرادات",
        )

        plan = await revenue_service.create_distribution_plan(
            period_id=period.period_id,
            method=RevenueShareMethod.EQUAL,
            members=sample_members,
        )

        # Try to execute without approval
        with pytest.raises(ValueError) as exc_info:
            await revenue_service.execute_distribution(plan.plan_id)
        assert "approved" in str(exc_info.value).lower()

    def test_zero_contribution_fallback(self, sample_members):
        """Test fallback to equal distribution when contributions are zero"""
        for member in sample_members:
            member.share_value = Decimal("0")

        calculator = RevenueShareCalculator()
        shares = calculator.calculate_by_contribution(
            total_amount=Decimal("10000.00"),
            members=sample_members,
        )

        # Should fall back to equal distribution
        for share in shares:
            assert share.net_share == Decimal("2000.00")

    def test_zero_production_fallback(self, sample_members):
        """Test fallback when production data is zero"""
        calculator = RevenueShareCalculator()
        production_data = {m.member_id: 0.0 for m in sample_members}

        shares = calculator.calculate_by_production(
            total_amount=Decimal("10000.00"),
            members=sample_members,
            production_data=production_data,
        )

        # Should fall back to equal distribution
        for share in shares:
            assert share.net_share == Decimal("2000.00")

    def test_zero_land_area_fallback(self, sample_members):
        """Test fallback when land area is zero"""
        for member in sample_members:
            member.land_area_ha = 0.0

        calculator = RevenueShareCalculator()
        shares = calculator.calculate_by_land_area(
            total_amount=Decimal("10000.00"),
            members=sample_members,
        )

        # Should fall back to equal distribution
        for share in shares:
            assert share.net_share == Decimal("2000.00")

    @pytest.mark.asyncio
    async def test_resource_not_found(self, resource_pool_service, sample_members):
        """Test booking with non-existent resource"""
        with pytest.raises(ValueError) as exc_info:
            await resource_pool_service.create_booking(
                resource_id="RES-NONEXISTENT",
                member_id=sample_members[0].member_id,
                purpose="Test",
                purpose_ar="اختبار",
                start_time=datetime.utcnow() + timedelta(days=1),
                duration_hours=4,
            )
        assert "not found" in str(exc_info.value)


# ═══════════════════════════════════════════════════════════════════════════
# Group Purchase Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGroupPurchase:
    """Test group purchase order functionality"""

    def test_create_group_purchase_order(self, sample_cooperative):
        """Test creating a group purchase order"""
        order = GroupPurchaseOrder.create(
            cooperative_id=sample_cooperative.cooperative_id,
            title="Bulk Fertilizer Order",
            title_ar="طلب سماد بالجملة",
            product_type="fertilizer",
            product_name="Urea 46%",
            product_name_ar="يوريا 46%",
            unit="bag",
            unit_price=Decimal("85.00"),
            bulk_price=Decimal("75.00"),
            min_order_quantity=100,
        )

        assert order.order_id.startswith("GPO-")
        assert order.status == PurchaseOrderStatus.DRAFT

    def test_calculate_savings(self, sample_cooperative):
        """Test calculating bulk purchase savings"""
        order = GroupPurchaseOrder.create(
            cooperative_id=sample_cooperative.cooperative_id,
            title="Bulk Seeds",
            title_ar="بذور بالجملة",
            product_type="seeds",
            product_name="Wheat Seeds",
            product_name_ar="بذور قمح",
        )
        order.unit_price = Decimal("100.00")
        order.bulk_price = Decimal("80.00")
        order.total_quantity_ordered = 500

        savings = order.calculate_savings()
        # (100 - 80) * 500 = 10000
        assert savings == Decimal("10000.00")

    def test_member_order_line(self, sample_members):
        """Test creating member order lines"""
        order_line = MemberOrderLine.create(
            order_id="GPO-001",
            member_id=sample_members[0].member_id,
            quantity=50,
            unit_price=Decimal("75.00"),
        )

        assert order_line.line_id.startswith("OL-")
        assert order_line.line_total == Decimal("3750.00")


# ═══════════════════════════════════════════════════════════════════════════
# Financial Period Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFinancialPeriod:
    """Test FinancialPeriod functionality"""

    def test_create_financial_period(self, sample_cooperative):
        """Test creating a financial period"""
        period = FinancialPeriod.create(
            cooperative_id=sample_cooperative.cooperative_id,
            name="Winter Season 2025-26",
            name_ar="موسم الشتاء 2025-26",
            start_date=datetime(2025, 10, 1),
            end_date=datetime(2026, 3, 31),
        )

        assert period.period_id.startswith("FP-")
        assert period.status == PeriodStatus.OPEN

    def test_calculate_net_income(self):
        """Test net income calculation"""
        period = FinancialPeriod.create(
            cooperative_id="COOP-001",
            name="Test",
            name_ar="اختبار",
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 3, 31),
        )

        period.total_revenue = Decimal("100000.00")
        period.total_expenses = Decimal("30000.00")

        net = period.calculate_net_income()
        assert net == Decimal("70000.00")
        assert period.net_income == Decimal("70000.00")


# ═══════════════════════════════════════════════════════════════════════════
# Distribution Plan Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDistributionPlan:
    """Test DistributionPlan functionality"""

    def test_calculate_distributable(self, sample_cooperative):
        """Test distributable amount calculation"""
        plan = DistributionPlan.create(
            cooperative_id=sample_cooperative.cooperative_id,
            period_id="FP-001",
            method=RevenueShareMethod.EQUAL,
            total_amount=Decimal("100000.00"),
        )

        plan.management_fee_percent = Decimal("5.0")
        plan.reserve_fund_percent = Decimal("10.0")
        plan.other_deductions = Decimal("1000.00")

        distributable = plan.calculate_distributable()

        # 100000 - 5000 - 10000 - 1000 = 84000
        assert plan.management_fee_amount == Decimal("5000.00")
        assert plan.reserve_fund_amount == Decimal("10000.00")
        assert distributable == Decimal("84000.00")

    def test_distribution_plan_to_summary(self, sample_cooperative):
        """Test distribution plan summary"""
        plan = DistributionPlan.create(
            cooperative_id=sample_cooperative.cooperative_id,
            period_id="FP-001",
            method=RevenueShareMethod.PRODUCTION,
            total_amount=Decimal("50000.00"),
        )

        summary = plan.to_summary()
        assert "plan_id" in summary
        assert "method" in summary
        assert summary["method"] == "production"


# ═══════════════════════════════════════════════════════════════════════════
# Integration-like Tests (Still Unit Tests)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCooperativeWorkflow:
    """Test complete cooperative workflows"""

    @pytest.mark.asyncio
    async def test_full_resource_booking_workflow(self, resource_pool_service, sample_members):
        """Test complete resource booking workflow"""
        # 1. Register resource
        tractor = await resource_pool_service.register_resource(
            name="Test Tractor",
            name_ar="جرار اختبار",
            type=ResourceType.EQUIPMENT,
            usage_fee_per_hour=Decimal("100.00"),
            usage_fee_per_ha=Decimal("150.00"),
            member_discount_percent=Decimal("10.0"),
        )

        # 2. Check availability
        tomorrow = datetime.utcnow() + timedelta(days=1)
        availability = await resource_pool_service.get_availability(tractor.resource_id, tomorrow)
        assert len(availability.available_hours) > 0

        # 3. Create booking
        booking = await resource_pool_service.create_booking(
            resource_id=tractor.resource_id,
            member_id=sample_members[0].member_id,
            purpose="Plowing field A",
            purpose_ar="حرث الحقل أ",
            start_time=tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),
            duration_hours=4,
        )

        assert booking.status == "confirmed"

        # 4. Complete booking
        completed = await resource_pool_service.complete_booking(
            booking.booking_id,
            actual_hours=5,
            hectares_covered=8.0,
        )

        assert completed.status == "completed"
        assert completed.actual_fee > Decimal("0")

    @pytest.mark.asyncio
    async def test_full_revenue_distribution_workflow(self, revenue_service, sample_members):
        """Test complete revenue distribution workflow"""
        # 1. Create period
        period = await revenue_service.create_period(
            name="Winter Season 2025-26",
            name_ar="موسم الشتاء 2025-26",
            start_date=datetime(2025, 10, 1),
            end_date=datetime(2026, 3, 31),
        )

        # 2. Record multiple revenues
        await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("200000.00"),
            description="Wheat sales",
            description_ar="مبيعات القمح",
            source="crop_sales",
        )

        await revenue_service.record_revenue(
            period_id=period.period_id,
            amount=Decimal("50000.00"),
            description="Service fees",
            description_ar="رسوم خدمات",
            source="services",
        )

        # 3. Record expenses
        await revenue_service.record_expense(
            period_id=period.period_id,
            amount=Decimal("50000.00"),
            description="Operating costs",
            description_ar="تكاليف التشغيل",
            category="operations",
        )

        # 4. Verify period totals
        period = await revenue_service.get_period(period.period_id)
        assert period.total_revenue == Decimal("250000.00")
        assert period.total_expenses == Decimal("50000.00")
        assert period.net_income == Decimal("200000.00")

        # 5. Create distribution plan
        production_data = {sample_members[i].member_id: float((i + 1) * 20) for i in range(len(sample_members))}

        plan = await revenue_service.create_distribution_plan(
            period_id=period.period_id,
            method=RevenueShareMethod.HYBRID,
            members=sample_members,
            production_data=production_data,
            hybrid_weights={"equal": 0.3, "production": 0.5, "contribution": 0.2},
        )

        assert len(plan.member_shares) == 5

        # 6. Approve and execute
        await revenue_service.approve_distribution(plan.plan_id, approved_by="chairman")
        payments = await revenue_service.execute_distribution(plan.plan_id)

        assert len(payments) == 5

        # 7. Process payments
        for payment in payments:
            processed = await revenue_service.process_payment(
                payment.payment_id,
                payment_method="bank_transfer",
                processed_by="treasurer",
            )
            assert processed.status == PaymentStatus.PAID

        # 8. Get summary
        summary = await revenue_service.get_period_summary(period.period_id)
        assert summary["summary"]["total_revenue"] == "250000.00"


# ═══════════════════════════════════════════════════════════════════════════
# Serialization Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSerialization:
    """Test serialization of all data classes"""

    def test_booking_to_dict(self, sample_cooperative, sample_members):
        """Test ResourceBooking serialization"""
        booking = ResourceBooking.create(
            resource_id="RES-001",
            member_id=sample_members[0].member_id,
            cooperative_id=sample_cooperative.cooperative_id,
            purpose="Test",
            purpose_ar="اختبار",
            start_time=datetime.utcnow(),
            duration_hours=4,
        )

        data = booking.to_dict()
        assert "booking_id" in data
        assert "start_time" in data
        assert "duration_hours" in data

    def test_transaction_to_dict(self, sample_cooperative):
        """Test Transaction serialization"""
        txn = Transaction.create(
            cooperative_id=sample_cooperative.cooperative_id,
            type=TransactionType.REVENUE,
            description="Test revenue",
            description_ar="ايراد اختبار",
            amount=Decimal("1000.00"),
        )

        data = txn.to_dict()
        assert data["type"] == "revenue"
        assert data["amount"] == "1000.00"

    def test_member_payment_to_dict(self, sample_cooperative, sample_members):
        """Test MemberPayment serialization"""
        payment = MemberPayment.create(
            plan_id="DIST-001",
            member_id=sample_members[0].member_id,
            cooperative_id=sample_cooperative.cooperative_id,
            amount=Decimal("5000.00"),
        )

        data = payment.to_dict()
        assert data["payment_id"].startswith("PAY-")
        assert data["amount"] == "5000.00"
        assert data["status"] == "pending"

    def test_usage_statistics_to_dict(self):
        """Test UsageStatistics serialization"""
        stats = UsageStatistics(
            total_bookings=50,
            total_hours=200.5,
            total_hectares=150.0,
            total_fees_collected=Decimal("15000.00"),
            average_utilization_percent=65.5,
        )

        data = stats.to_dict()
        assert data["total_bookings"] == 50
        assert data["total_hours"] == 200.5
        assert data["total_fees_collected"] == "15000.00"


# ═══════════════════════════════════════════════════════════════════════════
# Convenience Function Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConvenienceFunctions:
    """Test convenience/factory functions"""

    @pytest.mark.asyncio
    async def test_create_resource_pool(self):
        """Test create_resource_pool convenience function"""
        pool = await create_resource_pool("COOP-001")
        assert isinstance(pool, ResourcePoolService)
        assert pool.cooperative_id == "COOP-001"

    @pytest.mark.asyncio
    async def test_create_revenue_service(self):
        """Test create_revenue_service convenience function"""
        service = await create_revenue_service("COOP-001")
        assert isinstance(service, RevenueService)
        assert service.cooperative_id == "COOP-001"
