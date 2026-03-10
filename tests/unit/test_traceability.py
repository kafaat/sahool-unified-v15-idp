"""
Unit Tests for SAHOOL Traceability Module
Tests for farm-to-table tracking, QR code generation, and supply chain events.

اختبارات وحدة لوحدة التتبع في سهول
اختبارات لتتبع من المزرعة إلى المائدة، وإنشاء رموز QR، وأحداث سلسلة التوريد.
"""

import hashlib
import json
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from shared.traceability import (
    # Enums
    EventType,
    BatchStatus,
    CertificationType,
    QualityGrade,
    StorageCondition,
    TransportMode,
    QRFormat,
    QRSize,
    # Location models
    GeoLocation,
    Address,
    # Actor models
    Producer,
    ProcessingFacility,
    Transporter,
    Retailer,
    # Certification models
    Certification,
    ComplianceRecord,
    # Batch models
    ProduceBatch,
    BatchSplit,
    BatchMerge,
    # Event models
    SupplyChainEvent,
    HarvestEvent,
    ProcessingEvent,
    StorageEvent,
    TransportEvent,
    RetailEvent,
    ConsumerScanEvent,
    # Consumer-facing models
    ProductJourneyStep,
    ProductJourney,
    QRCodeData,
    # Report models
    BatchTraceReport,
    # QR Generator
    QRGenerationConfig,
    GeneratedQRCode,
    QRCodeGenerator,
    LabelData,
    LabelGenerator,
    # Chain tracker
    ChainConfig,
    SupplyChainTracker,
    EVENT_DISPLAY_INFO,
    # Utility functions
    generate_batch_code,
    decode_qr_data,
    verify_qr_checksum,
    calculate_carbon_footprint,
    estimate_shelf_life,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures - إعدادات الاختبار
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_address():
    """Create a sample address for testing."""
    return Address(
        address_line1_en="123 Farm Road",
        address_line1_ar="123 طريق المزرعة",
        city_en="Riyadh",
        city_ar="الرياض",
        region_en="Riyadh Region",
        region_ar="منطقة الرياض",
        country_code="SA",
        postal_code="12345",
    )


@pytest.fixture
def sample_location():
    """Create a sample geo location for testing."""
    return GeoLocation(
        latitude=24.7136,
        longitude=46.6753,
        altitude_m=620.0,
        accuracy_m=5.0,
    )


@pytest.fixture
def sample_producer(sample_address, sample_location):
    """Create a sample producer for testing."""
    return Producer(
        id="producer_001",
        name_en="Ahmed Al-Rashid",
        name_ar="أحمد الراشد",
        farm_name_en="Al-Rashid Organic Farm",
        farm_name_ar="مزرعة الراشد العضوية",
        registration_number="SA-FARM-001",
        address=sample_address,
        location=sample_location,
        contact_phone="+966501234567",
        contact_email="ahmed@alrashid-farm.com",
        certifications=["cert_001", "cert_002"],
    )


@pytest.fixture
def sample_certification():
    """Create a sample certification for testing."""
    return Certification(
        id="cert_001",
        certification_type=CertificationType.GLOBALGAP,
        certificate_number="GG-SA-2025-001",
        name_en="GlobalGAP IFA v6",
        name_ar="GlobalGAP IFA v6",
        issuing_body_en="GlobalGAP c/o FoodPLUS GmbH",
        issuing_body_ar="GlobalGAP",
        issue_date=datetime(2024, 1, 1, tzinfo=UTC),
        expiry_date=datetime(2026, 12, 31, tzinfo=UTC),
        scope_en="Fresh vegetables and fruits",
        scope_ar="الخضروات والفواكه الطازجة",
        is_valid=True,
        verification_url="https://database.globalgap.org/verify",
    )


@pytest.fixture
def sample_expired_certification():
    """Create an expired certification for testing."""
    return Certification(
        id="cert_expired",
        certification_type=CertificationType.ORGANIC,
        certificate_number="ORG-SA-2020-001",
        name_en="Organic Certification",
        name_ar="شهادة عضوية",
        issuing_body_en="Organic Council",
        issuing_body_ar="مجلس العضوية",
        issue_date=datetime(2020, 1, 1, tzinfo=UTC),
        expiry_date=datetime(2021, 12, 31, tzinfo=UTC),
        scope_en="Organic produce",
        scope_ar="منتجات عضوية",
        is_valid=True,
    )


@pytest.fixture
def sample_batch():
    """Create a sample produce batch for testing."""
    return ProduceBatch(
        id="batch_001",
        batch_code="TM-ALR-25-001",
        tenant_id="tenant_001",
        farm_id="farm_001",
        field_id="field_001",
        product_name_en="Tomatoes",
        product_name_ar="طماطم",
        variety_en="Beefsteak",
        variety_ar="بيفستيك",
        quantity=500.0,
        quantity_unit="kg",
        quality_grade=QualityGrade.GRADE_A,
        status=BatchStatus.CREATED,
        harvest_date=datetime.now(UTC) - timedelta(days=2),
        producer_id="producer_001",
        certification_ids=["cert_001"],
    )


@pytest.fixture
def supply_chain_tracker():
    """Create a supply chain tracker instance."""
    config = ChainConfig(
        min_temp_threshold_c=0.0,
        max_temp_threshold_c=8.0,
        max_transport_hours=24,
        auto_update_batch_status=True,
    )
    return SupplyChainTracker(config)


@pytest.fixture
def qr_generator():
    """Create a QR code generator instance."""
    config = QRGenerationConfig(
        base_url="https://trace.sahool.app",
        format=QRFormat.PNG,
        size=QRSize.MEDIUM,
    )
    return QRCodeGenerator(config)


# ═══════════════════════════════════════════════════════════════════════════════
# Model Tests - اختبارات النماذج
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnums:
    """Test enum values and types."""

    def test_event_type_values(self):
        """Test EventType enum has expected values."""
        assert EventType.HARVEST.value == "harvest"
        assert EventType.PROCESSING.value == "processing"
        assert EventType.STORAGE.value == "storage"
        assert EventType.TRANSPORT.value == "transport"
        assert EventType.RETAIL.value == "retail"
        assert EventType.CONSUMER_SCAN.value == "consumer_scan"

    def test_batch_status_values(self):
        """Test BatchStatus enum has expected values."""
        assert BatchStatus.CREATED.value == "created"
        assert BatchStatus.HARVESTED.value == "harvested"
        assert BatchStatus.RECALLED.value == "recalled"
        assert BatchStatus.EXPIRED.value == "expired"

    def test_quality_grade_values(self):
        """Test QualityGrade enum has expected values."""
        assert QualityGrade.PREMIUM.value == "premium"
        assert QualityGrade.GRADE_A.value == "grade_a"
        assert QualityGrade.REJECTED.value == "rejected"

    def test_certification_type_values(self):
        """Test CertificationType enum has expected values."""
        assert CertificationType.GLOBALGAP.value == "globalgap"
        assert CertificationType.HALAL.value == "halal"
        assert CertificationType.ORGANIC.value == "organic"
        assert CertificationType.SFDA.value == "sfda"

    def test_storage_condition_values(self):
        """Test StorageCondition enum has expected values."""
        assert StorageCondition.CHILLED.value == "chilled"
        assert StorageCondition.FROZEN.value == "frozen"
        assert StorageCondition.AMBIENT.value == "ambient"

    def test_transport_mode_values(self):
        """Test TransportMode enum has expected values."""
        assert TransportMode.TRUCK_REFRIGERATED.value == "truck_refrigerated"
        assert TransportMode.AIR_FREIGHT.value == "air_freight"


@pytest.mark.unit
class TestGeoLocation:
    """Test GeoLocation model."""

    def test_create_geolocation(self, sample_location):
        """Test creating a geo location."""
        assert sample_location.latitude == 24.7136
        assert sample_location.longitude == 46.6753
        assert sample_location.altitude_m == 620.0
        assert sample_location.accuracy_m == 5.0

    def test_geolocation_optional_fields(self):
        """Test geo location with optional fields."""
        location = GeoLocation(latitude=24.7136, longitude=46.6753)
        assert location.altitude_m is None
        assert location.accuracy_m is None


@pytest.mark.unit
class TestAddress:
    """Test Address model."""

    def test_create_address(self, sample_address):
        """Test creating an address."""
        assert sample_address.address_line1_en == "123 Farm Road"
        assert sample_address.city_en == "Riyadh"
        assert sample_address.city_ar == "الرياض"
        assert sample_address.country_code == "SA"

    def test_address_optional_fields(self):
        """Test address with optional fields."""
        address = Address(
            address_line1_en="Test Street",
            address_line1_ar="شارع تجريبي",
            city_en="Jeddah",
            city_ar="جدة",
            region_en="Makkah",
            region_ar="مكة",
            country_code="SA",
        )
        assert address.postal_code is None
        assert address.address_line2_en is None


# ═══════════════════════════════════════════════════════════════════════════════
# Batch Model Tests - اختبارات نموذج الدفعة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProduceBatch:
    """Test ProduceBatch model creation and behavior."""

    def test_create_batch_with_defaults(self):
        """Test creating a batch with default values."""
        batch = ProduceBatch()
        assert batch.id  # UUID should be auto-generated
        assert batch.batch_code == ""
        assert batch.status == BatchStatus.CREATED
        assert batch.quality_grade == QualityGrade.GRADE_A
        assert batch.quantity == 0.0
        assert batch.quantity_unit == "kg"

    def test_create_batch_with_values(self, sample_batch):
        """Test creating a batch with specific values."""
        assert sample_batch.id == "batch_001"
        assert sample_batch.batch_code == "TM-ALR-25-001"
        assert sample_batch.tenant_id == "tenant_001"
        assert sample_batch.product_name_en == "Tomatoes"
        assert sample_batch.product_name_ar == "طماطم"
        assert sample_batch.quantity == 500.0
        assert sample_batch.quality_grade == QualityGrade.GRADE_A
        assert sample_batch.producer_id == "producer_001"
        assert "cert_001" in sample_batch.certification_ids

    def test_batch_attributes_dict(self, sample_batch):
        """Test batch attributes dictionary."""
        sample_batch.attributes["origin_country"] = "SA"
        sample_batch.attributes["organic"] = True
        assert sample_batch.attributes["origin_country"] == "SA"
        assert sample_batch.attributes["organic"] is True


@pytest.mark.unit
class TestBatchSplitMerge:
    """Test BatchSplit and BatchMerge models."""

    def test_create_batch_split(self):
        """Test creating a batch split record."""
        split = BatchSplit(
            id="split_001",
            parent_batch_id="batch_001",
            child_batch_ids=["batch_001a", "batch_001b"],
            split_date=datetime.now(UTC),
            reason_en="Split for different retailers",
            reason_ar="تقسيم لتجار مختلفين",
            performed_by="user_001",
        )
        assert split.parent_batch_id == "batch_001"
        assert len(split.child_batch_ids) == 2
        assert "batch_001a" in split.child_batch_ids

    def test_create_batch_merge(self):
        """Test creating a batch merge record."""
        merge = BatchMerge(
            id="merge_001",
            source_batch_ids=["batch_001", "batch_002"],
            target_batch_id="batch_003",
            merge_date=datetime.now(UTC),
            reason_en="Combine for bulk shipment",
            reason_ar="دمج للشحن بالجملة",
            performed_by="user_001",
        )
        assert len(merge.source_batch_ids) == 2
        assert merge.target_batch_id == "batch_003"


# ═══════════════════════════════════════════════════════════════════════════════
# Certification Tests - اختبارات الشهادات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCertification:
    """Test Certification model and validation."""

    def test_create_certification(self, sample_certification):
        """Test creating a certification."""
        assert sample_certification.certification_type == CertificationType.GLOBALGAP
        assert sample_certification.certificate_number == "GG-SA-2025-001"
        assert sample_certification.is_valid is True

    def test_certification_is_currently_valid(self, sample_certification):
        """Test certification validity check."""
        assert sample_certification.is_currently_valid() is True

    def test_expired_certification_not_valid(self, sample_expired_certification):
        """Test expired certification returns False."""
        assert sample_expired_certification.is_currently_valid() is False

    def test_certification_marked_invalid(self, sample_certification):
        """Test certification marked as invalid returns False."""
        sample_certification.is_valid = False
        assert sample_certification.is_currently_valid() is False


@pytest.mark.unit
class TestComplianceRecord:
    """Test ComplianceRecord model."""

    def test_create_compliance_record(self):
        """Test creating a compliance record."""
        record = ComplianceRecord(
            id="compliance_001",
            certification_id="cert_001",
            inspection_date=datetime.now(UTC),
            inspector_name="John Smith",
            is_compliant=True,
            score=95.0,
            findings_en="Minor documentation issues",
            findings_ar="مشاكل توثيق بسيطة",
            corrective_actions_en=["Update pest control records"],
            corrective_actions_ar=["تحديث سجلات مكافحة الآفات"],
        )
        assert record.is_compliant is True
        assert record.score == 95.0
        assert len(record.corrective_actions_en) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Supply Chain Event Tests - اختبارات أحداث سلسلة التوريد
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSupplyChainEvents:
    """Test supply chain event models."""

    def test_create_harvest_event(self, sample_location):
        """Test creating a harvest event."""
        event = HarvestEvent(
            batch_id="batch_001",
            field_id="field_001",
            field_name_en="Field A",
            field_name_ar="الحقل أ",
            crop_type="tomato",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
            temperature_c=25.0,
            humidity_percent=60.0,
            location=sample_location,
            actor_id="farmer_001",
            actor_name_en="Ahmed",
            actor_name_ar="أحمد",
        )
        assert event.event_type == EventType.HARVEST
        assert event.field_id == "field_001"
        assert event.temperature_c == 25.0

    def test_create_processing_event(self):
        """Test creating a processing event."""
        event = ProcessingEvent(
            batch_id="batch_001",
            facility_id="facility_001",
            facility_name_en="Al-Rashid Packing",
            facility_name_ar="تعبئة الراشد",
            processing_type_en="Washing and Grading",
            processing_type_ar="غسل وتصنيف",
            input_quantity=500.0,
            output_quantity=480.0,
            quantity_unit="kg",
            quality_grade=QualityGrade.GRADE_A,
        )
        assert event.event_type == EventType.PROCESSING
        assert event.input_quantity == 500.0
        assert event.output_quantity == 480.0
        assert event.loss_percentage == 0.0  # Need to calculate

    def test_create_storage_event(self):
        """Test creating a storage event."""
        event = StorageEvent(
            batch_id="batch_001",
            facility_id="storage_001",
            facility_name_en="Cold Storage A",
            facility_name_ar="التخزين البارد أ",
            storage_unit_id="unit_003",
            storage_condition=StorageCondition.CHILLED,
            target_temperature_c=4.0,
            actual_temperature_c=3.8,
            target_humidity_percent=90.0,
            actual_humidity_percent=88.0,
        )
        assert event.event_type == EventType.STORAGE
        assert event.storage_condition == StorageCondition.CHILLED
        assert event.actual_temperature_c == 3.8

    def test_create_transport_event(self, sample_location):
        """Test creating a transport event."""
        event = TransportEvent(
            batch_id="batch_001",
            transporter_id="transport_001",
            transporter_name_en="Cool Logistics",
            transporter_name_ar="الخدمات اللوجستية الباردة",
            vehicle_id="VH-001",
            origin_en="Al-Rashid Farm",
            origin_ar="مزرعة الراشد",
            destination_en="Riyadh Distribution Center",
            destination_ar="مركز توزيع الرياض",
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
            target_temperature_c=4.0,
            distance_km=150.0,
            origin_location=sample_location,
        )
        assert event.event_type == EventType.TRANSPORT
        assert event.transport_mode == TransportMode.TRUCK_REFRIGERATED
        assert event.distance_km == 150.0

    def test_create_retail_event(self):
        """Test creating a retail event."""
        event = RetailEvent(
            batch_id="batch_001",
            retailer_id="retailer_001",
            retailer_name_en="Fresh Market",
            retailer_name_ar="السوق الطازج",
            store_location_en="Riyadh Mall",
            store_location_ar="الرياض مول",
            received_quantity=100.0,
            temperature_at_receipt_c=4.2,
            quality_check_passed=True,
            unit_price=12.50,
            currency="SAR",
        )
        assert event.event_type == EventType.RETAIL
        assert event.received_quantity == 100.0
        assert event.quality_check_passed is True
        assert event.unit_price == 12.50

    def test_create_consumer_scan_event(self, sample_location):
        """Test creating a consumer scan event."""
        event = ConsumerScanEvent(
            batch_id="batch_001",
            session_id="session_12345",
            device_type="mobile",
            scan_location=sample_location,
            rating=5,
            feedback_en="Very fresh tomatoes!",
            feedback_ar="طماطم طازجة جداً!",
        )
        assert event.event_type == EventType.CONSUMER_SCAN
        assert event.session_id == "session_12345"
        assert event.rating == 5


# ═══════════════════════════════════════════════════════════════════════════════
# Supply Chain Tracker Tests - اختبارات متتبع سلسلة التوريد
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSupplyChainTrackerBatchManagement:
    """Test SupplyChainTracker batch management."""

    def test_create_batch(self, supply_chain_tracker):
        """Test creating a batch through tracker."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Tomatoes",
            product_name_ar="طماطم",
            batch_code="TM-25-001",
            quantity=500.0,
            variety_en="Cherry",
            variety_ar="كرزي",
        )
        assert batch.id is not None
        assert batch.batch_code == "TM-25-001"
        assert batch.status == BatchStatus.CREATED
        assert batch.quantity == 500.0

    def test_get_batch_by_id(self, supply_chain_tracker):
        """Test retrieving batch by ID."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Cucumbers",
            product_name_ar="خيار",
            batch_code="CU-25-001",
            quantity=300.0,
        )
        retrieved = supply_chain_tracker.get_batch(batch.id)
        assert retrieved is not None
        assert retrieved.batch_code == "CU-25-001"

    def test_get_batch_by_code(self, supply_chain_tracker):
        """Test retrieving batch by code."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Lettuce",
            product_name_ar="خس",
            batch_code="LT-25-001",
            quantity=200.0,
        )
        retrieved = supply_chain_tracker.get_batch_by_code("LT-25-001")
        assert retrieved is not None
        assert retrieved.id == batch.id

    def test_get_nonexistent_batch(self, supply_chain_tracker):
        """Test retrieving non-existent batch returns None."""
        assert supply_chain_tracker.get_batch("nonexistent") is None
        assert supply_chain_tracker.get_batch_by_code("NONE-00-000") is None

    def test_update_batch_status(self, supply_chain_tracker):
        """Test updating batch status."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Peppers",
            product_name_ar="فلفل",
            batch_code="PP-25-001",
            quantity=150.0,
        )
        updated = supply_chain_tracker.update_batch_status(batch.id, BatchStatus.RECALLED)
        assert updated is not None
        assert updated.status == BatchStatus.RECALLED


@pytest.mark.unit
class TestSupplyChainTrackerEventRecording:
    """Test SupplyChainTracker event recording."""

    def test_record_harvest_event(self, supply_chain_tracker, sample_location):
        """Test recording harvest event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Tomatoes",
            product_name_ar="طماطم",
            batch_code="TM-25-002",
            quantity=500.0,
        )
        event = supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field A",
            field_name_ar="الحقل أ",
            crop_type="tomato",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
            location=sample_location,
            temperature_c=28.0,
            humidity_percent=55.0,
        )
        assert event is not None
        assert event.event_type == EventType.HARVEST
        assert event.temperature_c == 28.0

        # Check batch status updated
        batch = supply_chain_tracker.get_batch(batch.id)
        assert batch.status == BatchStatus.HARVESTED

    def test_record_harvest_for_nonexistent_batch(self, supply_chain_tracker):
        """Test recording harvest for non-existent batch returns None."""
        event = supply_chain_tracker.record_harvest(
            batch_id="nonexistent",
            field_name_en="Field A",
            field_name_ar="الحقل أ",
            crop_type="tomato",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )
        assert event is None

    def test_record_processing_event(self, supply_chain_tracker):
        """Test recording processing event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Apples",
            product_name_ar="تفاح",
            batch_code="AP-25-001",
            quantity=1000.0,
        )
        event = supply_chain_tracker.record_processing(
            batch_id=batch.id,
            facility_id="facility_001",
            facility_name_en="Apple Packing House",
            facility_name_ar="دار تعبئة التفاح",
            processing_type_en="Washing and Waxing",
            processing_type_ar="غسل وتشميع",
            input_quantity=1000.0,
            output_quantity=950.0,
            quality_grade=QualityGrade.PREMIUM,
        )
        assert event is not None
        assert event.event_type == EventType.PROCESSING
        assert event.loss_percentage == 5.0  # 50/1000 * 100

        # Check batch updated
        batch = supply_chain_tracker.get_batch(batch.id)
        assert batch.status == BatchStatus.IN_PROCESSING
        assert batch.quantity == 950.0
        assert batch.quality_grade == QualityGrade.PREMIUM

    def test_record_storage_event(self, supply_chain_tracker):
        """Test recording storage event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Dates",
            product_name_ar="تمور",
            batch_code="DT-25-001",
            quantity=2000.0,
        )
        event = supply_chain_tracker.record_storage(
            batch_id=batch.id,
            facility_id="storage_001",
            facility_name_en="Cold Room 3",
            facility_name_ar="غرفة التبريد 3",
            storage_unit_id="CR-003",
            storage_condition=StorageCondition.CHILLED,
            target_temperature_c=4.0,
            actual_temperature_c=3.5,
        )
        assert event is not None
        assert event.storage_condition == StorageCondition.CHILLED

        # Check batch status
        batch = supply_chain_tracker.get_batch(batch.id)
        assert batch.status == BatchStatus.IN_STORAGE

    def test_record_transport_event(self, supply_chain_tracker):
        """Test recording transport event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Oranges",
            product_name_ar="برتقال",
            batch_code="OR-25-001",
            quantity=800.0,
        )
        event = supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="transport_001",
            transporter_name_en="Saudi Logistics",
            transporter_name_ar="الخدمات اللوجستية السعودية",
            vehicle_id="VH-123",
            origin_en="Jeddah Farm",
            origin_ar="مزرعة جدة",
            destination_en="Riyadh Market",
            destination_ar="سوق الرياض",
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
            target_temperature_c=4.0,
            distance_km=950.0,
        )
        assert event is not None
        assert event.transport_mode == TransportMode.TRUCK_REFRIGERATED
        assert event.distance_km == 950.0

        # Check batch status
        batch = supply_chain_tracker.get_batch(batch.id)
        assert batch.status == BatchStatus.IN_TRANSIT

    def test_complete_transport(self, supply_chain_tracker):
        """Test completing a transport event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Bananas",
            product_name_ar="موز",
            batch_code="BN-25-001",
            quantity=500.0,
        )
        transport_event = supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="transport_001",
            transporter_name_en="Quick Delivery",
            transporter_name_ar="التوصيل السريع",
            vehicle_id="VH-456",
            origin_en="Dammam Port",
            origin_ar="ميناء الدمام",
            destination_en="Riyadh DC",
            destination_ar="مركز توزيع الرياض",
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
        )
        completed = supply_chain_tracker.complete_transport(
            transport_event_id=transport_event.id,
            min_temperature_c=3.0,
            max_temperature_c=5.5,
        )
        assert completed is not None
        assert completed.arrival_time is not None
        assert completed.min_recorded_temperature_c == 3.0
        assert completed.max_recorded_temperature_c == 5.5

    def test_record_retail_event(self, supply_chain_tracker):
        """Test recording retail event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Strawberries",
            product_name_ar="فراولة",
            batch_code="ST-25-001",
            quantity=100.0,
        )
        event = supply_chain_tracker.record_retail(
            batch_id=batch.id,
            retailer_id="retailer_001",
            retailer_name_en="Tamimi Markets",
            retailer_name_ar="أسواق التميمي",
            store_location_en="Olaya Street Branch",
            store_location_ar="فرع شارع العليا",
            received_quantity=100.0,
            temperature_at_receipt_c=4.5,
            quality_check_passed=True,
            unit_price=25.0,
        )
        assert event is not None
        assert event.event_type == EventType.RETAIL
        assert event.received_quantity == 100.0

        # Check batch status
        batch = supply_chain_tracker.get_batch(batch.id)
        assert batch.status == BatchStatus.AT_RETAIL

    def test_record_consumer_scan(self, supply_chain_tracker, sample_location):
        """Test recording consumer scan event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Grapes",
            product_name_ar="عنب",
            batch_code="GR-25-001",
            quantity=50.0,
        )
        event = supply_chain_tracker.record_consumer_scan(
            batch_id=batch.id,
            session_id="scan_session_001",
            device_type="mobile",
            scan_location=sample_location,
            rating=5,
            feedback_en="Excellent quality!",
            feedback_ar="جودة ممتازة!",
        )
        assert event is not None
        assert event.event_type == EventType.CONSUMER_SCAN
        assert event.rating == 5
        assert event.session_id == "scan_session_001"


@pytest.mark.unit
class TestEventOrderingAndIntegrity:
    """Test event ordering and integrity in the supply chain."""

    def test_events_sorted_by_timestamp(self, supply_chain_tracker):
        """Test that events are returned sorted by timestamp."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Corn",
            product_name_ar="ذرة",
            batch_code="CN-25-001",
            quantity=1000.0,
        )

        # Record events (they should be in chronological order)
        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field B",
            field_name_ar="الحقل ب",
            crop_type="corn",
            harvest_method_en="Mechanical",
            harvest_method_ar="آلي",
        )
        supply_chain_tracker.record_processing(
            batch_id=batch.id,
            facility_id="facility_002",
            facility_name_en="Corn Processor",
            facility_name_ar="معالج الذرة",
            processing_type_en="Drying",
            processing_type_ar="تجفيف",
            input_quantity=1000.0,
            output_quantity=900.0,
        )

        events = supply_chain_tracker.get_events(batch.id)
        assert len(events) == 2
        assert events[0].event_type == EventType.HARVEST
        assert events[1].event_type == EventType.PROCESSING
        # Verify timestamps are in order
        assert events[0].timestamp <= events[1].timestamp

    def test_filter_events_by_type(self, supply_chain_tracker):
        """Test filtering events by type."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Wheat",
            product_name_ar="قمح",
            batch_code="WH-25-001",
            quantity=5000.0,
        )

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field C",
            field_name_ar="الحقل ج",
            crop_type="wheat",
            harvest_method_en="Combine",
            harvest_method_ar="حصادة",
        )
        supply_chain_tracker.record_storage(
            batch_id=batch.id,
            facility_id="silo_001",
            facility_name_en="Grain Silo",
            facility_name_ar="صومعة الحبوب",
            storage_unit_id="SILO-1",
            storage_condition=StorageCondition.AMBIENT,
        )

        # Get only harvest events
        harvest_events = supply_chain_tracker.get_events(batch.id, EventType.HARVEST)
        assert len(harvest_events) == 1
        assert harvest_events[0].event_type == EventType.HARVEST

        # Get only storage events
        storage_events = supply_chain_tracker.get_events(batch.id, EventType.STORAGE)
        assert len(storage_events) == 1
        assert storage_events[0].event_type == EventType.STORAGE

    def test_get_latest_event(self, supply_chain_tracker):
        """Test getting the latest event."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Barley",
            product_name_ar="شعير",
            batch_code="BL-25-001",
            quantity=3000.0,
        )

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field D",
            field_name_ar="الحقل د",
            crop_type="barley",
            harvest_method_en="Combine",
            harvest_method_ar="حصادة",
        )
        supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="t_001",
            transporter_name_en="Grain Transport",
            transporter_name_ar="نقل الحبوب",
            vehicle_id="VH-789",
            origin_en="Farm",
            origin_ar="المزرعة",
            destination_en="Mill",
            destination_ar="المطحنة",
            transport_mode=TransportMode.TRUCK_AMBIENT,
        )

        latest = supply_chain_tracker.get_latest_event(batch.id)
        assert latest is not None
        assert latest.event_type == EventType.TRANSPORT


@pytest.mark.unit
class TestEventListeners:
    """Test event listener functionality."""

    def test_add_event_listener(self, supply_chain_tracker):
        """Test adding an event listener."""
        events_received = []

        def listener(event):
            events_received.append(event)

        supply_chain_tracker.add_event_listener(listener)

        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Test",
            product_name_ar="اختبار",
            batch_code="TS-25-001",
            quantity=100.0,
        )
        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )

        assert len(events_received) == 1
        assert events_received[0].event_type == EventType.HARVEST

    def test_remove_event_listener(self, supply_chain_tracker):
        """Test removing an event listener."""
        events_received = []

        def listener(event):
            events_received.append(event)

        supply_chain_tracker.add_event_listener(listener)
        supply_chain_tracker.remove_event_listener(listener)

        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Test2",
            product_name_ar="اختبار2",
            batch_code="TS-25-002",
            quantity=100.0,
        )
        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )

        assert len(events_received) == 0

    def test_listener_error_does_not_break_chain(self, supply_chain_tracker):
        """Test that listener errors don't break event recording."""

        def failing_listener(event):
            raise Exception("Listener error")

        supply_chain_tracker.add_event_listener(failing_listener)

        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Test3",
            product_name_ar="اختبار3",
            batch_code="TS-25-003",
            quantity=100.0,
        )
        # Should not raise exception
        event = supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )
        assert event is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Product Journey Tests - اختبارات رحلة المنتج
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestProductJourney:
    """Test consumer-facing product journey generation."""

    def test_build_product_journey(self, supply_chain_tracker, sample_producer):
        """Test building a complete product journey."""
        supply_chain_tracker.add_producer(sample_producer)

        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Tomatoes",
            product_name_ar="طماطم",
            batch_code="TM-JRN-001",
            quantity=500.0,
            producer_id=sample_producer.id,
        )

        # Record full journey
        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field A",
            field_name_ar="الحقل أ",
            crop_type="tomato",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )
        supply_chain_tracker.record_processing(
            batch_id=batch.id,
            facility_id="facility_001",
            facility_name_en="Packing House",
            facility_name_ar="دار التعبئة",
            processing_type_en="Washing and Packing",
            processing_type_ar="غسل وتعبئة",
            input_quantity=500.0,
            output_quantity=480.0,
        )
        supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="transport_001",
            transporter_name_en="Fresh Transport",
            transporter_name_ar="النقل الطازج",
            vehicle_id="VH-001",
            origin_en="Farm",
            origin_ar="المزرعة",
            destination_en="Market",
            destination_ar="السوق",
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
            distance_km=100.0,
        )
        supply_chain_tracker.record_retail(
            batch_id=batch.id,
            retailer_id="retailer_001",
            retailer_name_en="Fresh Market",
            retailer_name_ar="السوق الطازج",
            store_location_en="Riyadh",
            store_location_ar="الرياض",
            received_quantity=480.0,
        )

        journey = supply_chain_tracker.build_product_journey(batch.id)

        assert journey is not None
        assert journey.batch_code == "TM-JRN-001"
        assert journey.product_name_en == "Tomatoes"
        assert journey.product_name_ar == "طماطم"
        assert journey.producer_name_en == sample_producer.name_en
        assert journey.farm_name_en == sample_producer.farm_name_en
        assert len(journey.steps) == 4
        assert journey.steps[0].event_type == EventType.HARVEST
        assert journey.steps[1].event_type == EventType.PROCESSING
        assert journey.steps[2].event_type == EventType.TRANSPORT
        assert journey.steps[3].event_type == EventType.RETAIL
        assert journey.transport_distance_km == 100.0
        assert journey.journey_duration_hours >= 0

    def test_build_journey_no_events(self, supply_chain_tracker):
        """Test building journey with no events returns None."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Empty",
            product_name_ar="فارغ",
            batch_code="EM-25-001",
            quantity=100.0,
        )
        journey = supply_chain_tracker.build_product_journey(batch.id)
        assert journey is None

    def test_journey_freshness_score(self, supply_chain_tracker):
        """Test freshness score calculation in journey."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Fresh Produce",
            product_name_ar="منتج طازج",
            batch_code="FP-25-001",
            quantity=100.0,
        )

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="produce",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )

        journey = supply_chain_tracker.build_product_journey(batch.id)
        assert journey is not None
        # Fresh harvest should have high freshness score
        assert journey.freshness_score >= 90


# ═══════════════════════════════════════════════════════════════════════════════
# Trace Report Tests - اختبارات تقرير التتبع
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBatchTraceReport:
    """Test batch trace report generation."""

    def test_generate_trace_report(self, supply_chain_tracker, sample_certification):
        """Test generating a complete trace report."""
        supply_chain_tracker.add_certification(sample_certification)

        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Certified Tomatoes",
            product_name_ar="طماطم معتمدة",
            batch_code="CT-25-001",
            quantity=500.0,
        )
        supply_chain_tracker.link_certification_to_batch(batch.id, sample_certification.id)

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field A",
            field_name_ar="الحقل أ",
            crop_type="tomato",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
            actor_id="farmer_001",
        )
        supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="transport_001",
            transporter_name_en="Transporter",
            transporter_name_ar="الناقل",
            vehicle_id="VH-001",
            origin_en="Farm",
            origin_ar="المزرعة",
            destination_en="Market",
            destination_ar="السوق",
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
            distance_km=200.0,
        )

        # Complete transport with temperature data
        events = supply_chain_tracker.get_events(batch.id, EventType.TRANSPORT)
        supply_chain_tracker.complete_transport(
            transport_event_id=events[0].id,
            min_temperature_c=2.0,
            max_temperature_c=6.0,
        )

        report = supply_chain_tracker.generate_trace_report(batch.id, "admin_001")

        assert report is not None
        assert report.batch.batch_code == "CT-25-001"
        assert len(report.events) == 2
        assert len(report.certifications) == 1
        assert report.total_distance_km == 200.0
        assert report.number_of_handlers == 2  # farmer and transporter
        assert report.min_temperature_c == 2.0
        assert report.max_temperature_c == 6.0
        assert report.all_certifications_valid is True
        assert report.generated_by == "admin_001"

    def test_trace_report_temperature_excursion(self, supply_chain_tracker):
        """Test trace report detects temperature excursions."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Cold Chain Test",
            product_name_ar="اختبار السلسلة الباردة",
            batch_code="CC-25-001",
            quantity=100.0,
        )

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )

        # Record storage with temperature above threshold (8.0)
        supply_chain_tracker.record_storage(
            batch_id=batch.id,
            facility_id="storage_001",
            facility_name_en="Storage",
            facility_name_ar="التخزين",
            storage_unit_id="UNIT-1",
            storage_condition=StorageCondition.CHILLED,
            actual_temperature_c=10.0,  # Above 8.0 threshold
        )

        report = supply_chain_tracker.generate_trace_report(batch.id)

        assert report is not None
        assert report.temperature_excursions == 1
        assert "Temperature excursion" in report.compliance_issues[0]

    def test_trace_report_expired_certification(self, supply_chain_tracker, sample_expired_certification):
        """Test trace report detects expired certifications."""
        supply_chain_tracker.add_certification(sample_expired_certification)

        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Expired Cert Test",
            product_name_ar="اختبار شهادة منتهية",
            batch_code="EC-25-001",
            quantity=100.0,
        )
        supply_chain_tracker.link_certification_to_batch(batch.id, sample_expired_certification.id)

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )

        report = supply_chain_tracker.generate_trace_report(batch.id)

        assert report is not None
        assert report.all_certifications_valid is False
        assert "certifications are expired" in report.compliance_issues[-1]


# ═══════════════════════════════════════════════════════════════════════════════
# QR Code Generator Tests - اختبارات مولد رمز QR
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestQRCodeGenerator:
    """Test QR code generation functionality."""

    def test_qr_generator_initialization(self, qr_generator):
        """Test QR generator initialization."""
        assert qr_generator.config.base_url == "https://trace.sahool.app"
        assert qr_generator.config.format == QRFormat.PNG
        assert qr_generator.config.size == QRSize.MEDIUM

    def test_generate_for_batch(self, qr_generator, sample_batch):
        """Test generating QR code for a batch."""
        result = qr_generator.generate_for_batch(sample_batch)

        assert result is not None
        assert result.batch_id == sample_batch.id
        assert result.batch_code == sample_batch.batch_code
        assert result.verification_url.startswith("https://trace.sahool.app/verify/")
        assert sample_batch.batch_code in result.verification_url
        assert result.qr_data  # Should have data
        assert result.checksum  # Should have checksum

    def test_generate_verification_url(self, qr_generator, sample_batch):
        """Test verification URL generation."""
        result = qr_generator.generate_for_batch(sample_batch)

        assert "sig=" in result.verification_url
        assert "lang=ar" in result.verification_url

    def test_qr_data_json_format(self, qr_generator, sample_batch):
        """Test QR data is in JSON format."""
        result = qr_generator.generate_for_batch(sample_batch)

        data = json.loads(result.qr_data)
        assert data["v"] == 1  # Version
        assert data["t"] == "SAHOOL"  # Type
        assert data["b"] == sample_batch.batch_code
        assert "u" in data  # URL

    def test_generate_bulk(self, qr_generator):
        """Test bulk QR code generation."""
        batches = [
            ProduceBatch(
                id=f"batch_{i}",
                batch_code=f"TM-25-{i:03d}",
                product_name_en="Tomatoes",
                product_name_ar="طماطم",
                harvest_date=datetime.now(UTC),
            )
            for i in range(3)
        ]

        results = qr_generator.generate_bulk(batches)

        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.batch_code == f"TM-25-{i:03d}"

    def test_generate_from_qr_data(self, qr_generator):
        """Test generating QR from QRCodeData object."""
        qr_data = QRCodeData(
            batch_id="batch_001",
            batch_code="TM-25-001",
            product_name_en="Tomatoes",
            product_name_ar="طماطم",
            producer_name_en="Al-Rashid Farm",
            producer_name_ar="مزرعة الراشد",
            harvest_date="2025-01-15",
            verification_url="https://trace.sahool.app/verify/TM-25-001",
        )

        result = qr_generator.generate_from_data(qr_data)

        assert result is not None
        assert result.batch_code == "TM-25-001"
        assert "SAHOOL|TM-25-001" in result.qr_data

    def test_qr_checksum_calculation(self, qr_generator, sample_batch):
        """Test QR checksum is correctly calculated."""
        result = qr_generator.generate_for_batch(sample_batch)

        # Verify checksum matches (using SHA256, truncated to 32 chars)
        expected_data = f"{result.batch_id}|{result.batch_code}|{result.qr_data}"
        expected_checksum = hashlib.sha256(expected_data.encode()).hexdigest()[:32]

        assert result.checksum == expected_checksum


@pytest.mark.unit
class TestQRCodeData:
    """Test QRCodeData model."""

    def test_qr_code_data_compact_string(self):
        """Test QRCodeData compact string generation."""
        data = QRCodeData(
            batch_id="batch_001",
            batch_code="TM-25-001",
            product_name_en="Tomatoes",
            product_name_ar="طماطم",
            producer_name_en="Farm",
            producer_name_ar="مزرعة",
            harvest_date="2025-01-15",
            verification_url="https://trace.sahool.app/v/TM-25-001",
        )

        compact = data.to_compact_string()

        assert compact.startswith("SAHOOL|")
        assert "TM-25-001" in compact
        assert "Tomatoes" in compact
        assert "2025-01-15" in compact


@pytest.mark.unit
class TestQRUtilityFunctions:
    """Test QR utility functions."""

    def test_generate_batch_code_with_farm(self):
        """Test batch code generation with farm code."""
        code = generate_batch_code("TM", 2025, 1, "ALR")
        assert code == "TM-ALR-25-001"

    def test_generate_batch_code_without_farm(self):
        """Test batch code generation without farm code."""
        code = generate_batch_code("WH", 2025, 15)
        assert code == "WH-25-015"

    def test_generate_batch_code_sequence_padding(self):
        """Test batch code sequence is padded to 3 digits."""
        code = generate_batch_code("CU", 2025, 5)
        assert code == "CU-25-005"

        code = generate_batch_code("CU", 2025, 999)
        assert code == "CU-25-999"

    def test_decode_qr_data_json(self):
        """Test decoding JSON QR data."""
        json_data = '{"v":1,"t":"SAHOOL","b":"TM-25-001","p":"Tomatoes","h":"2025-01-15","u":"https://trace.sahool.app/v/TM-25-001"}'
        result = decode_qr_data(json_data)

        assert result is not None
        assert result["v"] == 1
        assert result["b"] == "TM-25-001"

    def test_decode_qr_data_compact(self):
        """Test decoding compact SAHOOL format."""
        compact_data = "SAHOOL|TM-25-001|Tomatoes|2025-01-15|https://trace.sahool.app/v/TM-25-001"
        result = decode_qr_data(compact_data)

        assert result is not None
        assert result["t"] == "SAHOOL"
        assert result["b"] == "TM-25-001"
        assert result["p"] == "Tomatoes"

    def test_decode_qr_data_invalid(self):
        """Test decoding invalid QR data returns None."""
        result = decode_qr_data("invalid data")
        assert result is None

    def test_verify_qr_checksum_valid(self, qr_generator, sample_batch):
        """Test QR checksum verification for valid checksum."""
        generated = qr_generator.generate_for_batch(sample_batch)
        assert verify_qr_checksum(generated) is True

    def test_verify_qr_checksum_invalid(self, qr_generator, sample_batch):
        """Test QR checksum verification for tampered data."""
        generated = qr_generator.generate_for_batch(sample_batch)
        generated.checksum = "invalid_checksum"
        assert verify_qr_checksum(generated) is False


# ═══════════════════════════════════════════════════════════════════════════════
# Label Generator Tests - اختبارات مولد الملصقات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLabelGenerator:
    """Test label generation functionality."""

    def test_generate_label_data(self, sample_batch):
        """Test generating label data for a batch."""
        label_gen = LabelGenerator()

        label_data = label_gen.generate_label_data(
            batch=sample_batch,
            producer_name_en="Al-Rashid Farm",
            producer_name_ar="مزرعة الراشد",
            certifications=["GlobalGAP", "Organic"],
        )

        assert label_data.batch_code == sample_batch.batch_code
        assert label_data.product_name_en == "Tomatoes"
        assert label_data.product_name_ar == "طماطم"
        assert label_data.producer_name_en == "Al-Rashid Farm"
        assert label_data.quality_grade == QualityGrade.GRADE_A.value
        assert len(label_data.certifications) == 2

    def test_generate_html_label(self, sample_batch):
        """Test generating HTML label."""
        label_gen = LabelGenerator()

        label_data = label_gen.generate_label_data(
            batch=sample_batch,
            producer_name_en="Farm",
            producer_name_ar="مزرعة",
        )
        html = label_gen.generate_html_label(label_data)

        assert "<!DOCTYPE html>" in html
        assert sample_batch.batch_code in html
        assert sample_batch.product_name_en in html
        assert sample_batch.product_name_ar in html


# ═══════════════════════════════════════════════════════════════════════════════
# Utility Function Tests - اختبارات الدوال المساعدة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCarbonFootprintCalculation:
    """Test carbon footprint calculation utility."""

    def test_calculate_carbon_refrigerated_truck(self):
        """Test carbon footprint for refrigerated truck."""
        co2 = calculate_carbon_footprint(
            distance_km=100.0,
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
            weight_kg=1000.0,  # 1 ton
        )
        # 100 km * 1 ton * 0.15 factor = 15 kg CO2
        assert co2 == 15.0

    def test_calculate_carbon_air_freight(self):
        """Test carbon footprint for air freight."""
        co2 = calculate_carbon_footprint(
            distance_km=1000.0,
            transport_mode=TransportMode.AIR_FREIGHT,
            weight_kg=500.0,  # 0.5 ton
        )
        # 1000 km * 0.5 ton * 0.60 factor = 300 kg CO2
        assert co2 == 300.0

    def test_calculate_carbon_sea_freight(self):
        """Test carbon footprint for sea freight (lowest emission)."""
        co2 = calculate_carbon_footprint(
            distance_km=5000.0,
            transport_mode=TransportMode.SEA_FREIGHT,
            weight_kg=10000.0,  # 10 tons
        )
        # 5000 km * 10 ton * 0.015 factor = 750 kg CO2
        assert co2 == 750.0

    def test_calculate_carbon_rail(self):
        """Test carbon footprint for rail transport."""
        co2 = calculate_carbon_footprint(
            distance_km=500.0,
            transport_mode=TransportMode.RAIL,
            weight_kg=5000.0,  # 5 tons
        )
        # 500 km * 5 ton * 0.03 factor = 75 kg CO2
        assert co2 == 75.0


@pytest.mark.unit
class TestShelfLifeEstimation:
    """Test shelf life estimation utility."""

    def test_estimate_shelf_life_tomato_chilled(self):
        """Test shelf life for tomato in chilled storage."""
        days = estimate_shelf_life(
            product_type="tomato",
            storage_condition=StorageCondition.CHILLED,
            quality_grade=QualityGrade.GRADE_A,
        )
        # Base 14 days * 1.0 chilled * 1.0 grade A = 14 days
        assert days == 14

    def test_estimate_shelf_life_date_ambient(self):
        """Test shelf life for dates in ambient storage."""
        days = estimate_shelf_life(
            product_type="date",
            storage_condition=StorageCondition.AMBIENT,
            quality_grade=QualityGrade.PREMIUM,
        )
        # Base 180 days * 0.3 ambient * 1.1 premium = 59 days
        assert days == 59

    def test_estimate_shelf_life_wheat_ambient(self):
        """Test shelf life for wheat in ambient storage."""
        days = estimate_shelf_life(
            product_type="wheat",
            storage_condition=StorageCondition.AMBIENT,
            quality_grade=QualityGrade.GRADE_A,
        )
        # Base 365 days * 0.3 ambient * 1.0 grade A = 109 days
        assert days == 109

    def test_estimate_shelf_life_frozen(self):
        """Test shelf life multiplier for frozen storage."""
        days = estimate_shelf_life(
            product_type="tomato",
            storage_condition=StorageCondition.FROZEN,
            quality_grade=QualityGrade.GRADE_A,
        )
        # Base 14 days * 4.0 frozen * 1.0 grade A = 56 days
        assert days == 56

    def test_estimate_shelf_life_rejected_grade(self):
        """Test shelf life for rejected grade products."""
        days = estimate_shelf_life(
            product_type="tomato",
            storage_condition=StorageCondition.CHILLED,
            quality_grade=QualityGrade.REJECTED,
        )
        # Should be 0 for rejected products
        assert days == 0

    def test_estimate_shelf_life_unknown_product(self):
        """Test shelf life for unknown product type uses default."""
        days = estimate_shelf_life(
            product_type="unknown_product",
            storage_condition=StorageCondition.CHILLED,
            quality_grade=QualityGrade.GRADE_A,
        )
        # Default 14 days * 1.0 * 1.0 = 14 days
        assert days == 14


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Cases and Error Handling - حالات الحافة ومعالجة الأخطاء
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_batch_code(self):
        """Test batch with empty batch code."""
        batch = ProduceBatch(batch_code="")
        assert batch.batch_code == ""
        assert batch.id is not None

    def test_zero_quantity_processing(self, supply_chain_tracker):
        """Test processing event with zero input quantity."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Test",
            product_name_ar="اختبار",
            batch_code="ZQ-25-001",
            quantity=0.0,
        )
        event = supply_chain_tracker.record_processing(
            batch_id=batch.id,
            facility_id="facility_001",
            facility_name_en="Facility",
            facility_name_ar="المنشأة",
            processing_type_en="Processing",
            processing_type_ar="معالجة",
            input_quantity=0.0,
            output_quantity=0.0,
        )
        # Should handle division by zero gracefully
        assert event is not None
        assert event.loss_percentage == 0.0

    def test_negative_coordinates(self):
        """Test geo location with negative coordinates."""
        location = GeoLocation(latitude=-33.8688, longitude=151.2093)  # Sydney
        assert location.latitude < 0
        assert location.longitude > 0

    def test_unicode_product_names(self):
        """Test batch with Unicode characters in names."""
        batch = ProduceBatch(
            product_name_en="Pomegranate",
            product_name_ar="رمان",
            variety_en="Wonderful",
            variety_ar="ونديرفول",
        )
        assert batch.product_name_ar == "رمان"
        assert batch.variety_ar == "ونديرفول"

    def test_very_long_product_name_truncation(self, qr_generator):
        """Test QR data truncates very long product names."""
        batch = ProduceBatch(
            id="batch_long",
            batch_code="LN-25-001",
            product_name_en="A" * 100,  # Very long name
            product_name_ar="ا" * 100,
            harvest_date=datetime.now(UTC),
        )
        result = qr_generator.generate_for_batch(batch)
        data = json.loads(result.qr_data)
        # Product name should be truncated to 30 chars
        assert len(data["p"]) <= 30

    def test_certification_exactly_at_expiry(self):
        """Test certification validity at exact expiry timestamp."""
        cert = Certification(
            id="cert_edge",
            certification_type=CertificationType.ORGANIC,
            certificate_number="ORG-001",
            name_en="Test",
            name_ar="اختبار",
            issuing_body_en="Body",
            issuing_body_ar="جهة",
            issue_date=datetime.now(UTC) - timedelta(days=365),
            expiry_date=datetime.now(UTC),  # Expires now
            scope_en="Test",
            scope_ar="اختبار",
        )
        # At exact expiry, should be invalid (datetime.now(UTC) < self.expiry_date)
        assert cert.is_currently_valid() is False

    def test_batch_with_max_certifications(self):
        """Test batch with many certifications."""
        batch = ProduceBatch(
            id="batch_many_certs",
            batch_code="MC-25-001",
            certification_ids=[f"cert_{i:03d}" for i in range(50)],
        )
        assert len(batch.certification_ids) == 50

    def test_transport_without_distance(self, supply_chain_tracker):
        """Test transport event without distance."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Test",
            product_name_ar="اختبار",
            batch_code="ND-25-001",
            quantity=100.0,
        )
        event = supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="t_001",
            transporter_name_en="Transport",
            transporter_name_ar="النقل",
            vehicle_id="VH-001",
            origin_en="A",
            origin_ar="أ",
            destination_en="B",
            destination_ar="ب",
            transport_mode=TransportMode.LOCAL_DELIVERY,
            distance_km=None,  # No distance
        )
        assert event is not None
        assert event.distance_km is None

    def test_qr_generation_config_custom_colors(self):
        """Test QR generation with custom colors."""
        config = QRGenerationConfig(
            foreground_color="#FF0000",
            background_color="#00FF00",
        )
        gen = QRCodeGenerator(config)
        assert gen.config.foreground_color == "#FF0000"
        assert gen.config.background_color == "#00FF00"

    def test_chain_config_custom_thresholds(self):
        """Test chain config with custom thresholds."""
        config = ChainConfig(
            min_temp_threshold_c=-5.0,
            max_temp_threshold_c=15.0,
            max_transport_hours=48,
            max_storage_days=90,
        )
        tracker = SupplyChainTracker(config)
        assert tracker.config.min_temp_threshold_c == -5.0
        assert tracker.config.max_temp_threshold_c == 15.0

    def test_event_display_info_complete(self):
        """Test EVENT_DISPLAY_INFO has all event types."""
        for event_type in EventType:
            assert event_type in EVENT_DISPLAY_INFO
            info = EVENT_DISPLAY_INFO[event_type]
            assert "title_en" in info
            assert "title_ar" in info
            assert "icon" in info
            assert "description_en" in info
            assert "description_ar" in info


@pytest.mark.unit
class TestRecallScope:
    """Test batch recall functionality and scope determination."""

    def test_update_batch_to_recalled(self, supply_chain_tracker):
        """Test updating batch status to recalled."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Recalled Product",
            product_name_ar="منتج مسترجع",
            batch_code="RC-25-001",
            quantity=500.0,
        )

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )

        recalled = supply_chain_tracker.update_batch_status(batch.id, BatchStatus.RECALLED)

        assert recalled is not None
        assert recalled.status == BatchStatus.RECALLED

    def test_recalled_batch_events_preserved(self, supply_chain_tracker):
        """Test that events are preserved when batch is recalled."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Recall Events Test",
            product_name_ar="اختبار أحداث الاسترجاع",
            batch_code="RE-25-001",
            quantity=200.0,
        )

        supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Field",
            field_name_ar="حقل",
            crop_type="test",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
        )
        supply_chain_tracker.record_processing(
            batch_id=batch.id,
            facility_id="f_001",
            facility_name_en="Facility",
            facility_name_ar="منشأة",
            processing_type_en="Process",
            processing_type_ar="معالجة",
            input_quantity=200.0,
            output_quantity=190.0,
        )

        supply_chain_tracker.update_batch_status(batch.id, BatchStatus.RECALLED)

        # Events should still be retrievable
        events = supply_chain_tracker.get_events(batch.id)
        assert len(events) == 2

        # Trace report should still work
        report = supply_chain_tracker.generate_trace_report(batch.id)
        assert report is not None
        assert report.batch.status == BatchStatus.RECALLED

    def test_batch_expired_status(self, supply_chain_tracker):
        """Test updating batch status to expired."""
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Expired Product",
            product_name_ar="منتج منتهي الصلاحية",
            batch_code="EX-25-001",
            quantity=100.0,
        )
        batch.expiry_date = datetime.now(UTC) - timedelta(days=1)

        updated = supply_chain_tracker.update_batch_status(batch.id, BatchStatus.EXPIRED)

        assert updated is not None
        assert updated.status == BatchStatus.EXPIRED


# ═══════════════════════════════════════════════════════════════════════════════
# Integration-like Tests (Still Unit Tests) - اختبارات شبيهة بالتكامل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestFullSupplyChainFlow:
    """Test complete supply chain flow scenarios."""

    def test_complete_farm_to_consumer_flow(
        self, supply_chain_tracker, sample_producer, sample_certification, sample_location
    ):
        """Test complete flow from farm to consumer."""
        # Setup
        supply_chain_tracker.add_producer(sample_producer)
        supply_chain_tracker.add_certification(sample_certification)

        # Create batch
        batch = supply_chain_tracker.create_batch(
            tenant_id="tenant_001",
            farm_id="farm_001",
            field_id="field_001",
            product_name_en="Premium Tomatoes",
            product_name_ar="طماطم ممتازة",
            batch_code="PT-25-001",
            quantity=1000.0,
            variety_en="Roma",
            variety_ar="روما",
            producer_id=sample_producer.id,
        )
        supply_chain_tracker.link_certification_to_batch(batch.id, sample_certification.id)

        # 1. Harvest
        harvest = supply_chain_tracker.record_harvest(
            batch_id=batch.id,
            field_name_en="Tomato Field",
            field_name_ar="حقل الطماطم",
            crop_type="tomato",
            harvest_method_en="Manual",
            harvest_method_ar="يدوي",
            location=sample_location,
            temperature_c=25.0,
            humidity_percent=60.0,
            quality_notes_en="Excellent quality",
            quality_notes_ar="جودة ممتازة",
        )
        assert harvest is not None
        assert supply_chain_tracker.get_batch(batch.id).status == BatchStatus.HARVESTED

        # 2. Processing
        processing = supply_chain_tracker.record_processing(
            batch_id=batch.id,
            facility_id="facility_001",
            facility_name_en="Premium Packing House",
            facility_name_ar="دار التعبئة الممتازة",
            processing_type_en="Washing, Grading, Packing",
            processing_type_ar="غسل، تصنيف، تعبئة",
            input_quantity=1000.0,
            output_quantity=950.0,
            quality_grade=QualityGrade.PREMIUM,
        )
        assert processing is not None
        assert supply_chain_tracker.get_batch(batch.id).status == BatchStatus.IN_PROCESSING

        # 3. Storage
        storage = supply_chain_tracker.record_storage(
            batch_id=batch.id,
            facility_id="storage_001",
            facility_name_en="Cold Storage Facility",
            facility_name_ar="منشأة التخزين البارد",
            storage_unit_id="CR-001",
            storage_condition=StorageCondition.CHILLED,
            target_temperature_c=4.0,
            actual_temperature_c=3.8,
        )
        assert storage is not None
        assert supply_chain_tracker.get_batch(batch.id).status == BatchStatus.IN_STORAGE

        # 4. Transport
        transport = supply_chain_tracker.record_transport(
            batch_id=batch.id,
            transporter_id="transport_001",
            transporter_name_en="Cool Chain Logistics",
            transporter_name_ar="الخدمات اللوجستية للسلسلة الباردة",
            vehicle_id="VH-001",
            origin_en="Riyadh Farm",
            origin_ar="مزرعة الرياض",
            destination_en="Jeddah Distribution Center",
            destination_ar="مركز توزيع جدة",
            transport_mode=TransportMode.TRUCK_REFRIGERATED,
            target_temperature_c=4.0,
            distance_km=950.0,
        )
        assert transport is not None
        assert supply_chain_tracker.get_batch(batch.id).status == BatchStatus.IN_TRANSIT

        # Complete transport
        supply_chain_tracker.complete_transport(
            transport_event_id=transport.id,
            min_temperature_c=3.0,
            max_temperature_c=5.0,
        )

        # 5. Retail
        retail = supply_chain_tracker.record_retail(
            batch_id=batch.id,
            retailer_id="retailer_001",
            retailer_name_en="Fresh Mart",
            retailer_name_ar="فريش مارت",
            store_location_en="Jeddah Mall",
            store_location_ar="جدة مول",
            received_quantity=950.0,
            temperature_at_receipt_c=4.2,
            quality_check_passed=True,
            unit_price=15.0,
        )
        assert retail is not None
        assert supply_chain_tracker.get_batch(batch.id).status == BatchStatus.AT_RETAIL

        # 6. Consumer Scan
        scan = supply_chain_tracker.record_consumer_scan(
            batch_id=batch.id,
            session_id="consumer_session_001",
            device_type="mobile",
            rating=5,
            feedback_en="Fresh and delicious!",
            feedback_ar="طازج ولذيذ!",
        )
        assert scan is not None

        # Generate journey
        journey = supply_chain_tracker.build_product_journey(batch.id)
        assert journey is not None
        assert len(journey.steps) == 6
        assert journey.producer_name_en == sample_producer.name_en
        assert len(journey.certifications) == 1
        assert journey.transport_distance_km == 950.0

        # Generate trace report
        report = supply_chain_tracker.generate_trace_report(batch.id, "quality_manager")
        assert report is not None
        assert report.batch.batch_code == "PT-25-001"
        assert report.total_distance_km == 950.0
        assert report.temperature_excursions == 0
        assert report.all_certifications_valid is True
        assert len(report.compliance_issues) == 0
        assert report.quality_checks_passed >= 1

        # Generate QR Code
        qr_gen = QRCodeGenerator()
        qr = qr_gen.generate_for_batch(supply_chain_tracker.get_batch(batch.id))
        assert qr is not None
        assert verify_qr_checksum(qr) is True
