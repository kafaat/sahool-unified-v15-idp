"""
SAHOOL Traceability Module - Farm-to-Table Tracking
وحدة تتبع سهول - من المزرعة إلى المائدة

Provides complete traceability for agricultural produce from
harvest through the supply chain to the consumer.

يوفر تتبعاً كاملاً للمنتجات الزراعية من الحصاد
عبر سلسلة التوريد إلى المستهلك.

Features:
- QR code generation for produce batches
- Supply chain event tracking
- Consumer-facing product journey display
- Certifications and compliance records
- Temperature and quality monitoring

الميزات:
- إنشاء رموز QR لدفعات المنتجات
- تتبع أحداث سلسلة التوريد
- عرض رحلة المنتج للمستهلك
- سجلات الشهادات والامتثال
- مراقبة درجة الحرارة والجودة

Usage:
    from shared.traceability import (
        SupplyChainTracker,
        QRCodeGenerator,
        ProduceBatch,
        EventType,
    )

    # Create tracker
    tracker = SupplyChainTracker()

    # Create batch
    batch = tracker.create_batch(
        tenant_id="farm_001",
        farm_id="farm_001",
        field_id="field_001",
        product_name_en="Tomatoes",
        product_name_ar="طماطم",
        batch_code="TM-25-001",
        quantity=500,
    )

    # Record harvest event
    tracker.record_harvest(
        batch_id=batch.id,
        field_name_en="Field A",
        field_name_ar="الحقل أ",
        crop_type="tomato",
        harvest_method_en="Manual",
        harvest_method_ar="يدوي",
    )

    # Generate QR code
    qr_gen = QRCodeGenerator()
    qr_result = qr_gen.generate_for_batch(batch)

    # Get consumer journey
    journey = tracker.build_product_journey(batch.id)
"""

from .chain import (
    # Event display info
    EVENT_DISPLAY_INFO,
    # Config
    ChainConfig,
    # Main tracker
    SupplyChainTracker,
    # Utility functions
    calculate_carbon_footprint,
    estimate_shelf_life,
)
from .models import (
    Address,
    BatchMerge,
    BatchSplit,
    BatchStatus,
    # Report models
    BatchTraceReport,
    # Certification models
    Certification,
    CertificationType,
    ComplianceRecord,
    ConsumerScanEvent,
    # Enums
    EventType,
    # Location models
    GeoLocation,
    HarvestEvent,
    ProcessingEvent,
    ProcessingFacility,
    # Batch models
    ProduceBatch,
    # Actor models
    Producer,
    ProductJourney,
    # Consumer-facing models
    ProductJourneyStep,
    QRCodeData,
    QualityGrade,
    Retailer,
    RetailEvent,
    StorageCondition,
    StorageEvent,
    # Event models
    SupplyChainEvent,
    Transporter,
    TransportEvent,
    TransportMode,
)
from .qr_generator import (
    GeneratedQRCode,
    LabelData,
    LabelGenerator,
    # Generators
    QRCodeGenerator,
    # Config and enums
    QRFormat,
    QRGenerationConfig,
    QRSize,
    decode_qr_data,
    # Utility functions
    generate_batch_code,
    verify_qr_checksum,
)

__all__ = [
    # Enums
    "EventType",
    "BatchStatus",
    "CertificationType",
    "QualityGrade",
    "StorageCondition",
    "TransportMode",
    "QRFormat",
    "QRSize",
    # Location models
    "GeoLocation",
    "Address",
    # Actor models
    "Producer",
    "ProcessingFacility",
    "Transporter",
    "Retailer",
    # Certification models
    "Certification",
    "ComplianceRecord",
    # Batch models
    "ProduceBatch",
    "BatchSplit",
    "BatchMerge",
    # Event models
    "SupplyChainEvent",
    "HarvestEvent",
    "ProcessingEvent",
    "StorageEvent",
    "TransportEvent",
    "RetailEvent",
    "ConsumerScanEvent",
    # Consumer-facing models
    "ProductJourneyStep",
    "ProductJourney",
    "QRCodeData",
    # Report models
    "BatchTraceReport",
    # QR Generator
    "QRGenerationConfig",
    "GeneratedQRCode",
    "QRCodeGenerator",
    "LabelData",
    "LabelGenerator",
    # Chain tracker
    "ChainConfig",
    "SupplyChainTracker",
    "EVENT_DISPLAY_INFO",
    # Utility functions
    "generate_batch_code",
    "decode_qr_data",
    "verify_qr_checksum",
    "calculate_carbon_footprint",
    "estimate_shelf_life",
]

__version__ = "16.0.0"
