"""Tests for blockchain traceability."""
import pytest
from shared.smart_agriculture.blockchain_trace import (
    BlockchainTraceability, TraceEventType
)


class TestBlockchainTrace:
    def setup_method(self):
        self.bc = BlockchainTraceability()

    def test_create_trace(self):
        trace = self.bc.create_trace("P-001", "wheat", "قمح", "Farm A", "مزرعة أ", "F-001", "T-001")
        assert trace.trace_id != ""
        assert trace.crop_type_ar == "قمح"

    def test_add_events(self):
        trace = self.bc.create_trace("P-002", "wheat", "قمح", "Farm A", "مزرعة أ", "F-001", "T-001")
        evt1 = self.bc.add_event(trace.trace_id, TraceEventType.PLANTING, "Field 1", "الحقل 1")
        evt2 = self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING, "Field 1", "الحقل 1")
        assert evt1.hash != ""
        assert evt2.previous_hash == evt1.hash

    def test_verify_chain(self):
        trace = self.bc.create_trace("P-003", "date", "تمر", "Farm B", "مزرعة ب", "F-002", "T-001")
        self.bc.add_event(trace.trace_id, TraceEventType.PLANTING)
        self.bc.add_event(trace.trace_id, TraceEventType.FERTILIZING)
        self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING)
        assert self.bc.verify_chain(trace.trace_id) is True

    def test_generate_qr(self):
        trace = self.bc.create_trace("P-004", "wheat", "قمح", "Farm C", "مزرعة ج", "F-003", "T-001")
        qr = self.bc.generate_qr_data(trace.trace_id)
        assert "SAHOOL-TRACE" in qr

    def test_origin_certificate(self):
        trace = self.bc.create_trace("P-005", "coffee", "بُن", "Farm D", "مزرعة د", "F-004", "T-001")
        self.bc.add_event(trace.trace_id, TraceEventType.HARVESTING, "Yemen", "اليمن")
        cert = self.bc.issue_origin_certificate(
            trace.trace_id, "Yemen", "اليمن", "Highlands", "المرتفعات"
        )
        assert cert is not None
        assert cert.verification_hash != ""
