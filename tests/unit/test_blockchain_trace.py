"""
Tests for Blockchain Traceability | اختبارات التتبع بالبلوكتشين

Tests cover trace creation, event chaining, chain validation,
QR code generation, and origin certificate issuance.
"""
from __future__ import annotations

import pytest

from shared.smart_agriculture.blockchain_trace import (
    CERT_TYPE_AR,
    TRACE_EVENT_AR,
    BlockchainTraceability,
    CertificationType,
    OriginCertificate,
    ProductTrace,
    TraceEvent,
    TraceEventType,
)


class TestTraceCreation:
    """Tests for product trace creation | اختبارات إنشاء سجل التتبع"""

    def setup_method(self) -> None:
        self.bc = BlockchainTraceability()

    def test_create_trace_returns_product_trace(self) -> None:
        """Create trace returns a valid ProductTrace object."""
        trace = self.bc.create_trace(
            "P-001", "wheat", "قمح", "Farm A", "مزرعة أ", "F-001", "T-001",
        )
        assert isinstance(trace, ProductTrace)
        assert trace.trace_id != ""
        assert trace.product_id == "P-001"

    def test_trace_has_bilingual_names(self) -> None:
        """Trace stores bilingual crop and farm names | أسماء ثنائية اللغة"""
        trace = self.bc.create_trace(
            "P-002", "wheat", "قمح", "Al-Rashid Farm", "مزرعة الراشد", "F-002", "T-001",
        )
        assert trace.crop_type == "wheat"
        assert trace.crop_type_ar == "قمح"
        assert trace.farm_name == "Al-Rashid Farm"
        assert trace.farm_name_ar == "مزرعة الراشد"

    def test_trace_id_contains_product_id(self) -> None:
        """Trace ID should contain the product ID."""
        trace = self.bc.create_trace(
            "PROD-123", "date", "تمر", "Farm B", "مزرعة ب", "F-003", "T-001",
        )
        assert "PROD-123" in trace.trace_id
        assert trace.trace_id.startswith("TRC-")

    def test_trace_starts_with_empty_events(self) -> None:
        """New trace should have an empty event list."""
        trace = self.bc.create_trace(
            "P-003", "barley", "شعير", "Farm C", "مزرعة ج", "F-004", "T-001",
        )
        assert trace.events == []
        assert trace.chain_valid is True

    def test_trace_has_created_at_timestamp(self) -> None:
        """Trace should have a created_at timestamp."""
        trace = self.bc.create_trace(
            "P-004", "coffee", "بُن", "Farm D", "مزرعة د", "F-005", "T-001",
        )
        assert trace.created_at != ""

    def test_trace_stored_internally(self) -> None:
        """Created trace should be retrievable via internal storage."""
        trace = self.bc.create_trace(
            "P-005", "rice", "أرز", "Farm E", "مزرعة هـ", "F-006", "T-001",
        )
        assert trace.trace_id in self.bc._traces


class TestEventChaining:
    """Tests for event addition and hash chaining | اختبارات إضافة الأحداث والتسلسل"""

    def setup_method(self) -> None:
        self.bc = BlockchainTraceability()
        self.trace = self.bc.create_trace(
            "P-010", "wheat", "قمح", "Farm X", "مزرعة X", "F-010", "T-001",
        )

    def test_add_event_returns_trace_event(self) -> None:
        """Add event returns a TraceEvent object."""
        evt = self.bc.add_event(self.trace.trace_id, TraceEventType.PLANTING)
        assert isinstance(evt, TraceEvent)
        assert evt.event_id == "EVT-001"

    def test_first_event_has_genesis_previous(self) -> None:
        """First event's previous_hash should be 'genesis'."""
        evt = self.bc.add_event(self.trace.trace_id, TraceEventType.PLANTING)
        assert evt.previous_hash == "genesis"

    def test_second_event_chains_to_first(self) -> None:
        """Second event's previous_hash should equal first event's hash."""
        evt1 = self.bc.add_event(self.trace.trace_id, TraceEventType.PLANTING)
        evt2 = self.bc.add_event(self.trace.trace_id, TraceEventType.FERTILIZING)
        assert evt2.previous_hash == evt1.hash

    def test_event_has_arabic_type(self) -> None:
        """Event should have an Arabic type label | نوع الحدث بالعربية"""
        evt = self.bc.add_event(self.trace.trace_id, TraceEventType.HARVESTING)
        assert evt.event_type_ar == "حصاد"

    def test_event_stores_location(self) -> None:
        """Event stores bilingual location."""
        evt = self.bc.add_event(
            self.trace.trace_id,
            TraceEventType.PLANTING,
            location="Field 1",
            location_ar="الحقل 1",
        )
        assert evt.location == "Field 1"
        assert evt.location_ar == "الحقل 1"

    def test_add_event_to_nonexistent_trace(self) -> None:
        """Adding event to nonexistent trace returns None."""
        result = self.bc.add_event("INVALID-ID", TraceEventType.PLANTING)
        assert result is None

    def test_event_details_passed(self) -> None:
        """Custom details dict is stored in the event."""
        details = {"variety": "Sakha 95", "seed_rate_kg": 120}
        evt = self.bc.add_event(
            self.trace.trace_id,
            TraceEventType.PLANTING,
            details=details,
        )
        assert evt.details["variety"] == "Sakha 95"

    def test_multiple_events_sequential_ids(self) -> None:
        """Events should have sequential IDs."""
        self.bc.add_event(self.trace.trace_id, TraceEventType.PLANTING)
        self.bc.add_event(self.trace.trace_id, TraceEventType.IRRIGATING)
        self.bc.add_event(self.trace.trace_id, TraceEventType.FERTILIZING)
        events = self.trace.events
        assert events[0].event_id == "EVT-001"
        assert events[1].event_id == "EVT-002"
        assert events[2].event_id == "EVT-003"


class TestChainVerification:
    """Tests for chain integrity verification | اختبارات التحقق من سلامة السلسلة"""

    def setup_method(self) -> None:
        self.bc = BlockchainTraceability()

    def test_empty_chain_is_valid(self) -> None:
        """Empty chain should be valid."""
        trace = self.bc.create_trace(
            "P-020", "wheat", "قمح", "Farm V", "مزرعة ف", "F-020", "T-001",
        )
        assert self.bc.verify_chain(trace.trace_id) is True

    def test_single_event_chain_valid(self) -> None:
        """Chain with one event should be valid."""
        trace = self.bc.create_trace(
            "P-021", "date", "تمر", "Farm W", "مزرعة و", "F-021", "T-001",
        )
        self.bc.add_event(trace.trace_id, TraceEventType.PLANTING)
        assert self.bc.verify_chain(trace.trace_id) is True

    def test_multi_event_chain_valid(self) -> None:
        """Chain with multiple events should be valid if not tampered."""
        trace = self.bc.create_trace(
            "P-022", "wheat", "قمح", "Farm Y", "مزرعة ي", "F-022", "T-001",
        )
        self.bc.add_event(trace.trace_id, TraceEventType.PLANTING)
        self.bc.add_event(trace.trace_id, TraceEventType.FERTILIZING)
        self.bc.add_event(trace.trace_id, TraceEventType.IRRIGATING)
        self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING)
        assert self.bc.verify_chain(trace.trace_id) is True

    def test_tampered_chain_invalid(self) -> None:
        """Tampered chain should be detected as invalid."""
        trace = self.bc.create_trace(
            "P-023", "coffee", "بُن", "Farm Z", "مزرعة ز", "F-023", "T-001",
        )
        self.bc.add_event(trace.trace_id, TraceEventType.PLANTING)
        self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING)
        # Tamper with the first event's hash
        trace.events[0].hash = "TAMPERED_HASH"
        assert self.bc.verify_chain(trace.trace_id) is False
        assert trace.chain_valid is False

    def test_nonexistent_trace_returns_true(self) -> None:
        """Verifying nonexistent trace returns True (vacuous truth)."""
        assert self.bc.verify_chain("NONEXISTENT") is True


class TestQRCodeGeneration:
    """Tests for QR code data generation | اختبارات توليد بيانات QR"""

    def setup_method(self) -> None:
        self.bc = BlockchainTraceability()

    def test_qr_contains_trace_id(self) -> None:
        """QR data should contain the trace ID."""
        trace = self.bc.create_trace(
            "P-030", "wheat", "قمح", "Farm Q", "مزرعة ق", "F-030", "T-001",
        )
        qr = self.bc.generate_qr_data(trace.trace_id)
        assert "SAHOOL-TRACE" in qr
        assert trace.trace_id in qr

    def test_qr_contains_product_and_crop(self) -> None:
        """QR data should contain product ID and crop type."""
        trace = self.bc.create_trace(
            "P-031", "date", "تمر", "Farm R", "مزرعة ر", "F-031", "T-001",
        )
        qr = self.bc.generate_qr_data(trace.trace_id)
        assert "PRODUCT:P-031" in qr
        assert "CROP:date" in qr

    def test_qr_event_count(self) -> None:
        """QR data should reflect the number of events."""
        trace = self.bc.create_trace(
            "P-032", "wheat", "قمح", "Farm S", "مزرعة س", "F-032", "T-001",
        )
        self.bc.add_event(trace.trace_id, TraceEventType.PLANTING)
        self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING)
        qr = self.bc.generate_qr_data(trace.trace_id)
        assert "EVENTS:2" in qr

    def test_qr_nonexistent_trace_empty(self) -> None:
        """QR for nonexistent trace returns empty string."""
        assert self.bc.generate_qr_data("INVALID") == ""

    def test_qr_stored_on_trace(self) -> None:
        """Generated QR data is stored on the trace object."""
        trace = self.bc.create_trace(
            "P-033", "rice", "أرز", "Farm T", "مزرعة ت", "F-033", "T-001",
        )
        qr = self.bc.generate_qr_data(trace.trace_id)
        assert trace.qr_code_data == qr


class TestOriginCertificate:
    """Tests for origin certificate issuance | اختبارات شهادة المنشأ"""

    def setup_method(self) -> None:
        self.bc = BlockchainTraceability()

    def test_issue_certificate(self) -> None:
        """Certificate is issued with correct fields."""
        trace = self.bc.create_trace(
            "P-040", "coffee", "بُن", "Farm U", "مزرعة ع", "F-040", "T-001",
        )
        self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING, "Yemen", "اليمن")
        cert = self.bc.issue_origin_certificate(
            trace.trace_id, "Yemen", "اليمن", "Highlands", "المرتفعات",
        )
        assert isinstance(cert, OriginCertificate)
        assert cert.certificate_id.startswith("CERT-")
        assert cert.country == "Yemen"
        assert cert.country_ar == "اليمن"

    def test_certificate_has_verification_hash(self) -> None:
        """Certificate should have a non-empty verification hash."""
        trace = self.bc.create_trace(
            "P-041", "wheat", "قمح", "Farm V", "مزرعة ف", "F-041", "T-001",
        )
        cert = self.bc.issue_origin_certificate(
            trace.trace_id, "Iraq", "العراق", "Central", "الوسط",
        )
        assert cert.verification_hash != ""

    def test_certificate_harvest_date_from_event(self) -> None:
        """Certificate should pick up harvest date from events."""
        trace = self.bc.create_trace(
            "P-042", "date", "تمر", "Farm W", "مزرعة و", "F-042", "T-001",
        )
        harvest_evt = self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING)
        cert = self.bc.issue_origin_certificate(
            trace.trace_id, "Oman", "عُمان", "Interior", "الداخلية",
        )
        assert cert.harvest_date == harvest_evt.timestamp

    def test_certificate_no_harvest_empty_date(self) -> None:
        """Certificate without harvest event should have empty harvest_date."""
        trace = self.bc.create_trace(
            "P-043", "wheat", "قمح", "Farm X", "مزرعة X", "F-043", "T-001",
        )
        self.bc.add_event(trace.trace_id, TraceEventType.PLANTING)
        cert = self.bc.issue_origin_certificate(
            trace.trace_id, "Egypt", "مصر", "Delta", "الدلتا",
        )
        assert cert.harvest_date == ""

    def test_certificate_nonexistent_trace(self) -> None:
        """Certificate for nonexistent trace returns None."""
        assert self.bc.issue_origin_certificate(
            "INVALID", "Yemen", "اليمن", "North", "الشمال",
        ) is None

    def test_certificate_quality_grade(self) -> None:
        """Certificate accepts custom quality grade."""
        trace = self.bc.create_trace(
            "P-044", "coffee", "بُن", "Farm Y", "مزرعة ي", "F-044", "T-001",
        )
        cert = self.bc.issue_origin_certificate(
            trace.trace_id, "Yemen", "اليمن", "Highlands", "المرتفعات",
            quality_grade="Premium",
        )
        assert cert.quality_grade == "Premium"


class TestArabicTranslations:
    """Tests for Arabic translation completeness | اختبارات اكتمال الترجمة العربية"""

    def test_all_trace_events_have_arabic(self) -> None:
        """Every TraceEventType should have an Arabic translation."""
        for event_type in TraceEventType:
            assert event_type in TRACE_EVENT_AR, f"{event_type} missing Arabic"

    def test_all_cert_types_have_arabic(self) -> None:
        """Every CertificationType should have an Arabic translation."""
        for cert_type in CertificationType:
            assert cert_type in CERT_TYPE_AR, f"{cert_type} missing Arabic"
