"""
Unit tests for shared/cooperatives/models.py
Tests cooperative data models including enums, Address, CooperativeConfig,
Cooperative, CooperativeMember, SharedResource, ResourceBooking,
GroupPurchaseOrder, and MemberOrderLine.
"""

import pytest
from datetime import datetime, UTC, timedelta
from decimal import Decimal

from shared.cooperatives.models import (
    # Enums
    CooperativeType,
    CooperativeStatus,
    MemberRole,
    MemberStatus,
    ResourceType,
    ResourceStatus,
    PurchaseOrderStatus,
    RevenueShareMethod,
    # Dataclasses
    Address,
    CooperativeConfig,
    Cooperative,
    CooperativeMember,
    SharedResource,
    ResourceBooking,
    GroupPurchaseOrder,
    MemberOrderLine,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_cooperative_type(self):
        assert CooperativeType.PRODUCTION == "production"
        assert CooperativeType.CREDIT == "credit"
        assert CooperativeType.IRRIGATION == "irrigation"

    def test_cooperative_status(self):
        assert CooperativeStatus.FORMING == "forming"
        assert CooperativeStatus.ACTIVE == "active"
        assert CooperativeStatus.DISSOLVED == "dissolved"

    def test_member_role(self):
        assert MemberRole.CHAIRMAN == "chairman"
        assert MemberRole.TREASURER == "treasurer"
        assert MemberRole.MEMBER == "member"
        assert MemberRole.OBSERVER == "observer"

    def test_member_status(self):
        assert MemberStatus.PENDING == "pending"
        assert MemberStatus.EXPELLED == "expelled"

    def test_resource_type(self):
        assert ResourceType.EQUIPMENT == "equipment"
        assert ResourceType.STORAGE == "storage"
        assert ResourceType.SEEDS == "seeds"

    def test_resource_status(self):
        assert ResourceStatus.AVAILABLE == "available"
        assert ResourceStatus.MAINTENANCE == "maintenance"
        assert ResourceStatus.RETIRED == "retired"

    def test_purchase_order_status(self):
        assert PurchaseOrderStatus.DRAFT == "draft"
        assert PurchaseOrderStatus.DISTRIBUTED == "distributed"

    def test_revenue_share_method(self):
        assert RevenueShareMethod.EQUAL == "equal"
        assert RevenueShareMethod.PRODUCTION == "production"
        assert RevenueShareMethod.HYBRID == "hybrid"


# =============================================================================
# Address Tests
# =============================================================================


class TestAddress:
    def test_creation(self):
        addr = Address(governorate="Riyadh", district="Al-Malaz")
        assert addr.governorate == "Riyadh"
        assert addr.village is None
        assert addr.coordinates is None

    def test_full_address(self):
        addr = Address(
            governorate="Riyadh",
            district="Al-Malaz",
            village="Al-Rawdah",
        )
        full = addr.full_address
        assert "Al-Rawdah" in full
        assert "Riyadh" in full

    def test_full_address_ar(self):
        addr = Address(
            governorate="الرياض",
            district="الملز",
            village="الروضة",
        )
        full = addr.full_address_ar
        assert "الرياض" in full
        assert "،" in full  # Arabic comma

    def test_full_address_no_village(self):
        addr = Address(governorate="Riyadh", district="Al-Malaz")
        full = addr.full_address
        assert "Riyadh" in full
        assert "Al-Malaz" in full

    def test_to_dict(self):
        addr = Address(
            governorate="Riyadh",
            district="Al-Malaz",
            coordinates=(24.7, 46.7),
        )
        d = addr.to_dict()
        assert d["governorate"] == "Riyadh"
        assert d["coordinates"] == (24.7, 46.7)


# =============================================================================
# CooperativeConfig Tests
# =============================================================================


class TestCooperativeConfig:
    def test_creation_defaults(self):
        config = CooperativeConfig()
        assert config.min_members == 7
        assert config.max_members is None
        assert config.membership_fee == Decimal("0")
        assert config.default_share_method == RevenueShareMethod.CONTRIBUTION
        assert config.priority_by_seniority is True
        assert config.advance_booking_days == 7

    def test_to_dict(self):
        config = CooperativeConfig(
            membership_fee=Decimal("100"),
            management_fee_percent=Decimal("10"),
        )
        d = config.to_dict()
        assert d["membership_fee"] == "100"
        assert d["management_fee_percent"] == "10"
        assert d["min_members"] == 7


# =============================================================================
# Cooperative Tests
# =============================================================================


class TestCooperative:
    def test_create_factory(self):
        coop = Cooperative.create(
            tenant_id="t1",
            name="Al-Rashid Coop",
            name_ar="تعاونية الراشد",
        )
        assert coop.cooperative_id.startswith("COOP-")
        assert coop.tenant_id == "t1"
        assert coop.type == CooperativeType.MULTI_PURPOSE
        assert coop.status == CooperativeStatus.FORMING

    def test_is_primary(self):
        coop = Cooperative(
            cooperative_id="COOP-001",
            tenant_id="t1",
            name="Test",
            name_ar="اختبار",
            level=0,
            parent_id=None,
        )
        assert coop.is_primary() is True

    def test_is_not_primary(self):
        coop = Cooperative(
            cooperative_id="COOP-002",
            tenant_id="t1",
            name="Test",
            name_ar="اختبار",
            level=1,
            parent_id="COOP-001",
        )
        assert coop.is_primary() is False

    def test_is_federation(self):
        coop = Cooperative(
            cooperative_id="COOP-003",
            tenant_id="t1",
            name="Federation",
            name_ar="اتحاد",
            level=2,
        )
        assert coop.is_federation() is True

    def test_can_accept_members_active(self):
        coop = Cooperative(
            cooperative_id="COOP-001",
            tenant_id="t1",
            name="Test",
            name_ar="اختبار",
            status=CooperativeStatus.ACTIVE,
            member_count=5,
        )
        assert coop.can_accept_members() is True

    def test_can_accept_members_not_active(self):
        coop = Cooperative(
            cooperative_id="COOP-001",
            tenant_id="t1",
            name="Test",
            name_ar="اختبار",
            status=CooperativeStatus.FORMING,
        )
        assert coop.can_accept_members() is False

    def test_can_accept_members_at_max(self):
        coop = Cooperative(
            cooperative_id="COOP-001",
            tenant_id="t1",
            name="Test",
            name_ar="اختبار",
            status=CooperativeStatus.ACTIVE,
            member_count=50,
            config=CooperativeConfig(max_members=50),
        )
        assert coop.can_accept_members() is False

    def test_to_dict(self):
        coop = Cooperative.create(
            tenant_id="t1",
            name="Test",
            name_ar="اختبار",
        )
        d = coop.to_dict()
        assert d["cooperative_id"].startswith("COOP-")
        assert d["type"] == "multi_purpose"
        assert d["status"] == "forming"
        assert "config" not in d

    def test_to_dict_include_config(self):
        coop = Cooperative.create(tenant_id="t1", name="Test", name_ar="اختبار")
        d = coop.to_dict(include_config=True)
        assert "config" in d

    def test_to_summary(self):
        coop = Cooperative.create(
            tenant_id="t1",
            name="Test Coop",
            name_ar="تعاونية اختبار",
        )
        s = coop.to_summary()
        assert "cooperative_id" in s
        assert s["name"] == "Test Coop"
        assert "member_count" in s


# =============================================================================
# CooperativeMember Tests
# =============================================================================


class TestCooperativeMember:
    def test_create_factory(self):
        member = CooperativeMember.create(
            cooperative_id="COOP-001",
            farmer_id="farmer-001",
            name="Ahmed",
            name_ar="أحمد",
            phone="+966501234567",
        )
        assert member.member_id.startswith("MEM-")
        assert member.role == MemberRole.MEMBER
        assert member.status == MemberStatus.PENDING

    def test_is_board_member(self):
        for role in [MemberRole.CHAIRMAN, MemberRole.VICE_CHAIRMAN, MemberRole.TREASURER, MemberRole.SECRETARY, MemberRole.BOARD_MEMBER]:
            m = CooperativeMember(
                member_id="M1", cooperative_id="C1",
                farmer_id="F1", name="T", name_ar="ت", phone="123",
                role=role,
            )
            assert m.is_board_member() is True

        m = CooperativeMember(
            member_id="M1", cooperative_id="C1",
            farmer_id="F1", name="T", name_ar="ت", phone="123",
            role=MemberRole.MEMBER,
        )
        assert m.is_board_member() is False

    def test_is_active(self):
        m = CooperativeMember(
            member_id="M1", cooperative_id="C1",
            farmer_id="F1", name="T", name_ar="ت", phone="123",
            status=MemberStatus.ACTIVE,
        )
        assert m.is_active() is True

    def test_can_vote(self):
        m = CooperativeMember(
            member_id="M1", cooperative_id="C1",
            farmer_id="F1", name="T", name_ar="ت", phone="123",
            status=MemberStatus.ACTIVE,
            voting_rights=True,
            role=MemberRole.MEMBER,
        )
        assert m.can_vote() is True

    def test_cannot_vote_observer(self):
        m = CooperativeMember(
            member_id="M1", cooperative_id="C1",
            farmer_id="F1", name="T", name_ar="ت", phone="123",
            status=MemberStatus.ACTIVE,
            role=MemberRole.OBSERVER,
        )
        assert m.can_vote() is False

    def test_cannot_vote_inactive(self):
        m = CooperativeMember(
            member_id="M1", cooperative_id="C1",
            farmer_id="F1", name="T", name_ar="ت", phone="123",
            status=MemberStatus.SUSPENDED,
        )
        assert m.can_vote() is False

    def test_has_outstanding_dues(self):
        m = CooperativeMember(
            member_id="M1", cooperative_id="C1",
            farmer_id="F1", name="T", name_ar="ت", phone="123",
            outstanding_dues=Decimal("500"),
        )
        assert m.has_outstanding_dues() is True

        m2 = CooperativeMember(
            member_id="M2", cooperative_id="C1",
            farmer_id="F2", name="T", name_ar="ت", phone="123",
        )
        assert m2.has_outstanding_dues() is False

    def test_to_dict(self):
        m = CooperativeMember.create(
            cooperative_id="C1", farmer_id="F1",
            name="Ahmed", name_ar="أحمد", phone="123",
        )
        d = m.to_dict()
        assert d["member_id"].startswith("MEM-")
        assert d["role"] == "member"
        assert d["status"] == "pending"


# =============================================================================
# SharedResource Tests
# =============================================================================


class TestSharedResource:
    def test_create_factory(self):
        res = SharedResource.create(
            cooperative_id="COOP-001",
            name="Tractor",
            name_ar="جرار",
            type=ResourceType.EQUIPMENT,
        )
        assert res.resource_id.startswith("RES-")
        assert res.status == ResourceStatus.AVAILABLE

    def test_is_available(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Tractor", name_ar="جرار",
            type=ResourceType.EQUIPMENT,
            status=ResourceStatus.AVAILABLE,
        )
        assert res.is_available() is True

    def test_not_available_maintenance(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Tractor", name_ar="جرار",
            type=ResourceType.EQUIPMENT,
            status=ResourceStatus.MAINTENANCE,
        )
        assert res.is_available() is False

    def test_needs_maintenance_by_date(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Tractor", name_ar="جرار",
            type=ResourceType.EQUIPMENT,
            next_maintenance_date=datetime(2020, 1, 1, tzinfo=UTC),
        )
        assert res.needs_maintenance() is True

    def test_needs_maintenance_by_hours(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Tractor", name_ar="جرار",
            type=ResourceType.EQUIPMENT,
            total_usage_hours=500,
            maintenance_interval_hours=400,
        )
        assert res.needs_maintenance() is True

    def test_no_maintenance_needed(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Silo", name_ar="صومعة",
            type=ResourceType.STORAGE,
        )
        assert res.needs_maintenance() is False

    def test_calculate_usage_fee(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Tractor", name_ar="جرار",
            type=ResourceType.EQUIPMENT,
            usage_fee_per_hour=Decimal("50"),
            usage_fee_per_ha=Decimal("100"),
            member_discount_percent=Decimal("10"),
        )
        fee = res.calculate_usage_fee(hours=4, hectares=2, is_member=True)
        # (50*4 + 100*2) = 400, discount 10% = 360
        assert fee == Decimal("360")

    def test_calculate_usage_fee_non_member(self):
        res = SharedResource(
            resource_id="R1", cooperative_id="C1",
            name="Tractor", name_ar="جرار",
            type=ResourceType.EQUIPMENT,
            usage_fee_per_hour=Decimal("50"),
            member_discount_percent=Decimal("10"),
        )
        fee = res.calculate_usage_fee(hours=2, is_member=False)
        assert fee == Decimal("100")

    def test_to_dict(self):
        res = SharedResource.create(
            cooperative_id="C1",
            name="Pump",
            name_ar="مضخة",
            type=ResourceType.IRRIGATION,
        )
        d = res.to_dict()
        assert d["type"] == "irrigation"
        assert "is_available" in d
        assert "needs_maintenance" in d


# =============================================================================
# ResourceBooking Tests
# =============================================================================


class TestResourceBooking:
    def test_create_factory(self):
        now = datetime.now(UTC)
        booking = ResourceBooking.create(
            resource_id="R1",
            member_id="M1",
            cooperative_id="C1",
            purpose="Field plowing",
            purpose_ar="حراثة الحقل",
            start_time=now,
            duration_hours=4.0,
        )
        assert booking.booking_id.startswith("BKG-")
        assert booking.duration_hours == 4.0
        assert booking.status == "pending"

    def test_to_dict(self):
        booking = ResourceBooking(
            booking_id="BKG-001",
            resource_id="R1",
            member_id="M1",
            cooperative_id="C1",
            purpose="Test",
            purpose_ar="اختبار",
        )
        d = booking.to_dict()
        assert d["booking_id"] == "BKG-001"
        assert d["status"] == "pending"
        assert d["payment_status"] == "pending"


# =============================================================================
# GroupPurchaseOrder Tests
# =============================================================================


class TestGroupPurchaseOrder:
    def test_create_factory(self):
        order = GroupPurchaseOrder.create(
            cooperative_id="C1",
            title="Bulk Fertilizer",
            title_ar="سماد بالجملة",
            product_type="fertilizer",
            product_name="Urea 46%",
            product_name_ar="يوريا 46%",
        )
        assert order.order_id.startswith("GPO-")
        assert order.status == PurchaseOrderStatus.DRAFT

    def test_calculate_savings_with_bulk_price(self):
        order = GroupPurchaseOrder(
            order_id="GPO-001",
            cooperative_id="C1",
            title="Test",
            title_ar="اختبار",
            product_type="seeds",
            product_name="Wheat Seeds",
            product_name_ar="بذور قمح",
            unit_price=Decimal("100"),
            bulk_price=Decimal("80"),
            total_quantity_ordered=50,
        )
        savings = order.calculate_savings()
        assert savings == Decimal("1000")  # (100-80) * 50

    def test_calculate_savings_no_bulk_price(self):
        order = GroupPurchaseOrder(
            order_id="GPO-001",
            cooperative_id="C1",
            title="Test",
            title_ar="اختبار",
            product_type="seeds",
            product_name="Wheat Seeds",
            product_name_ar="بذور قمح",
            discount_amount=Decimal("500"),
        )
        savings = order.calculate_savings()
        assert savings == Decimal("500")

    def test_to_dict(self):
        order = GroupPurchaseOrder.create(
            cooperative_id="C1",
            title="Test",
            title_ar="اختبار",
            product_type="fertilizer",
            product_name="DAP",
            product_name_ar="داب",
        )
        d = order.to_dict()
        assert d["order_id"].startswith("GPO-")
        assert d["status"] == "draft"
        assert "savings" in d


# =============================================================================
# MemberOrderLine Tests
# =============================================================================


class TestMemberOrderLine:
    def test_create_factory(self):
        line = MemberOrderLine.create(
            order_id="GPO-001",
            member_id="MEM-001",
            quantity=100.0,
            unit_price=Decimal("80"),
        )
        assert line.line_id.startswith("OL-")
        assert line.line_total == Decimal("8000")

    def test_to_dict(self):
        line = MemberOrderLine(
            line_id="OL-001",
            order_id="GPO-001",
            member_id="MEM-001",
            quantity=50.0,
            unit_price=Decimal("100"),
            line_total=Decimal("5000"),
        )
        d = line.to_dict()
        assert d["line_id"] == "OL-001"
        assert d["quantity"] == 50.0
        assert d["unit_price"] == "100"
        assert d["line_total"] == "5000"
