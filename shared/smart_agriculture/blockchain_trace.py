"""
Blockchain Traceability Module | وحدة التتبع بالبلوكتشين

Provides farm-to-consumer traceability:
- QR codes with complete product history
- Digital origin certificates
- Export market integration
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class TraceEventType(str, Enum):
    PLANTING = "planting"
    FERTILIZING = "fertilizing"
    IRRIGATING = "irrigating"
    SPRAYING = "spraying"
    HARVESTING = "harvesting"
    PROCESSING = "processing"
    PACKAGING = "packaging"
    STORAGE = "storage"
    TRANSPORT = "transport"
    DELIVERY = "delivery"


class CertificationType(str, Enum):
    ORGANIC = "organic"
    GLOBALGAP = "globalgap"
    FAIR_TRADE = "fair_trade"
    LOCAL_ORIGIN = "local_origin"
    PESTICIDE_FREE = "pesticide_free"


TRACE_EVENT_AR = {
    TraceEventType.PLANTING: "زراعة",
    TraceEventType.FERTILIZING: "تسميد",
    TraceEventType.IRRIGATING: "ري",
    TraceEventType.SPRAYING: "رش",
    TraceEventType.HARVESTING: "حصاد",
    TraceEventType.PROCESSING: "معالجة",
    TraceEventType.PACKAGING: "تعبئة",
    TraceEventType.STORAGE: "تخزين",
    TraceEventType.TRANSPORT: "نقل",
    TraceEventType.DELIVERY: "تسليم",
}

CERT_TYPE_AR = {
    CertificationType.ORGANIC: "عضوي",
    CertificationType.GLOBALGAP: "ممارسات زراعية جيدة",
    CertificationType.FAIR_TRADE: "تجارة عادلة",
    CertificationType.LOCAL_ORIGIN: "منشأ محلي",
    CertificationType.PESTICIDE_FREE: "خالي من المبيدات",
}


@dataclass
class TraceEvent:
    """A single traceability event | حدث تتبع واحد"""
    event_id: str = ""
    event_type: TraceEventType = TraceEventType.PLANTING
    event_type_ar: str = ""
    timestamp: str = ""
    location: str = ""
    location_ar: str = ""
    operator: str = ""
    details: dict = field(default_factory=dict)
    hash: str = ""
    previous_hash: str = ""


@dataclass
class ProductTrace:
    """Complete product traceability record | سجل تتبع المنتج الكامل"""
    trace_id: str = ""
    product_id: str = ""
    crop_type: str = ""
    crop_type_ar: str = ""
    farm_name: str = ""
    farm_name_ar: str = ""
    field_id: str = ""
    tenant_id: str = ""
    events: list[TraceEvent] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    certifications_ar: list[str] = field(default_factory=list)
    qr_code_data: str = ""
    chain_valid: bool = True
    created_at: str = ""


@dataclass
class OriginCertificate:
    """Digital origin certificate | شهادة المنشأ الرقمية"""
    certificate_id: str = ""
    product_id: str = ""
    farm_name: str = ""
    farm_name_ar: str = ""
    country: str = ""
    country_ar: str = ""
    region: str = ""
    region_ar: str = ""
    crop_type: str = ""
    crop_type_ar: str = ""
    harvest_date: str = ""
    quality_grade: str = ""
    certifications: list[str] = field(default_factory=list)
    verification_hash: str = ""
    issued_date: str = ""


class BlockchainTraceability:
    """Blockchain-based farm-to-consumer traceability.

    تتبع من المزرعة للمستهلك مبني على البلوكتشين.
    """

    def __init__(self):
        self._traces: dict[str, ProductTrace] = {}

    def _compute_hash(self, data: str, previous_hash: str = "") -> str:
        """Compute SHA-256 hash for chain integrity."""
        content = f"{previous_hash}{data}"
        return hashlib.sha256(content.encode()).hexdigest()

    def create_trace(
        self,
        product_id: str,
        crop_type: str,
        crop_type_ar: str,
        farm_name: str,
        farm_name_ar: str,
        field_id: str,
        tenant_id: str,
    ) -> ProductTrace:
        """Create a new product trace.

        إنشاء سجل تتبع جديد للمنتج.
        """
        trace = ProductTrace(
            trace_id=f"TRC-{product_id}-{datetime.now().strftime('%Y%m%d')}",
            product_id=product_id,
            crop_type=crop_type,
            crop_type_ar=crop_type_ar,
            farm_name=farm_name,
            farm_name_ar=farm_name_ar,
            field_id=field_id,
            tenant_id=tenant_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._traces[trace.trace_id] = trace
        return trace

    def add_event(
        self,
        trace_id: str,
        event_type: TraceEventType,
        location: str = "",
        location_ar: str = "",
        operator: str = "",
        details: dict | None = None,
    ) -> TraceEvent | None:
        """Add an event to the trace chain.

        إضافة حدث إلى سلسلة التتبع.
        """
        trace = self._traces.get(trace_id)
        if not trace:
            return None

        previous_hash = trace.events[-1].hash if trace.events else "genesis"

        event_data = f"{event_type.value}{location}{datetime.now().isoformat()}"
        event_hash = self._compute_hash(event_data, previous_hash)

        event = TraceEvent(
            event_id=f"EVT-{len(trace.events) + 1:03d}",
            event_type=event_type,
            event_type_ar=TRACE_EVENT_AR.get(event_type, ""),
            timestamp=datetime.now(timezone.utc).isoformat(),
            location=location,
            location_ar=location_ar,
            operator=operator,
            details=details or {},
            hash=event_hash,
            previous_hash=previous_hash,
        )

        trace.events.append(event)
        return event

    def verify_chain(self, trace_id: str) -> bool:
        """Verify the integrity of the trace chain.

        التحقق من سلامة سلسلة التتبع.
        """
        trace = self._traces.get(trace_id)
        if not trace or not trace.events:
            return True

        for i in range(1, len(trace.events)):
            if trace.events[i].previous_hash != trace.events[i - 1].hash:
                trace.chain_valid = False
                return False

        trace.chain_valid = True
        return True

    def generate_qr_data(self, trace_id: str) -> str:
        """Generate QR code data for the product.

        توليد بيانات رمز QR للمنتج.
        """
        trace = self._traces.get(trace_id)
        if not trace:
            return ""

        qr_data = (
            f"SAHOOL-TRACE:{trace.trace_id}|"
            f"PRODUCT:{trace.product_id}|"
            f"CROP:{trace.crop_type}|"
            f"FARM:{trace.farm_name}|"
            f"EVENTS:{len(trace.events)}|"
            f"VALID:{trace.chain_valid}"
        )
        trace.qr_code_data = qr_data
        return qr_data

    def issue_origin_certificate(
        self,
        trace_id: str,
        country: str,
        country_ar: str,
        region: str,
        region_ar: str,
        quality_grade: str = "A",
        certifications: list[str] | None = None,
    ) -> OriginCertificate | None:
        """Issue a digital origin certificate.

        إصدار شهادة منشأ رقمية.
        """
        trace = self._traces.get(trace_id)
        if not trace:
            return None

        cert_data = f"{trace.trace_id}{country}{datetime.now().isoformat()}"
        verification_hash = self._compute_hash(cert_data)

        harvest_event = None
        for event in trace.events:
            if event.event_type == TraceEventType.HARVESTING:
                harvest_event = event
                break

        return OriginCertificate(
            certificate_id=f"CERT-{trace.product_id}-{datetime.now().strftime('%Y%m%d')}",
            product_id=trace.product_id,
            farm_name=trace.farm_name,
            farm_name_ar=trace.farm_name_ar,
            country=country,
            country_ar=country_ar,
            region=region,
            region_ar=region_ar,
            crop_type=trace.crop_type,
            crop_type_ar=trace.crop_type_ar,
            harvest_date=harvest_event.timestamp if harvest_event else "",
            quality_grade=quality_grade,
            certifications=certifications or [],
            verification_hash=verification_hash,
            issued_date=datetime.now(timezone.utc).isoformat(),
        )
