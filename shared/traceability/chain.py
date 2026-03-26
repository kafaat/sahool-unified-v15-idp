"""
Supply Chain Event Tracking - تتبع أحداث سلسلة التوريد

Manages the tracking of produce batches through the supply chain,
from harvest to consumer, with full event history and verification.

يدير تتبع دفعات المنتجات عبر سلسلة التوريد،
من الحصاد إلى المستهلك، مع سجل الأحداث الكامل والتحقق.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from .models import (
    BatchStatus,
    BatchTraceReport,
    Certification,
    ConsumerScanEvent,
    EventType,
    GeoLocation,
    HarvestEvent,
    ProcessingEvent,
    ProduceBatch,
    Producer,
    ProductJourney,
    ProductJourneyStep,
    QualityGrade,
    RetailEvent,
    StorageCondition,
    StorageEvent,
    SupplyChainEvent,
    TransportEvent,
    TransportMode,
)

# ─────────────────────────────────────────────────────────────────────────────
# Event Type Metadata - بيانات أنواع الأحداث الوصفية
# ─────────────────────────────────────────────────────────────────────────────


EVENT_DISPLAY_INFO = {
    EventType.HARVEST: {
        "title_en": "Harvested",
        "title_ar": "الحصاد",
        "icon": "harvest",
        "description_en": "Produce harvested from the field",
        "description_ar": "تم حصاد المنتج من الحقل",
    },
    EventType.PROCESSING: {
        "title_en": "Processed & Packed",
        "title_ar": "المعالجة والتعبئة",
        "icon": "processing",
        "description_en": "Cleaned, sorted, and packed",
        "description_ar": "تم التنظيف والفرز والتعبئة",
    },
    EventType.STORAGE: {
        "title_en": "In Storage",
        "title_ar": "التخزين",
        "icon": "storage",
        "description_en": "Stored under controlled conditions",
        "description_ar": "تم التخزين في ظروف متحكم بها",
    },
    EventType.TRANSPORT: {
        "title_en": "In Transit",
        "title_ar": "النقل",
        "icon": "transport",
        "description_en": "Transported to destination",
        "description_ar": "تم النقل إلى الوجهة",
    },
    EventType.RETAIL: {
        "title_en": "At Store",
        "title_ar": "في المتجر",
        "icon": "retail",
        "description_en": "Available for purchase",
        "description_ar": "متاح للشراء",
    },
    EventType.CONSUMER_SCAN: {
        "title_en": "Verified by Consumer",
        "title_ar": "تحقق المستهلك",
        "icon": "scan",
        "description_en": "Product authenticity verified",
        "description_ar": "تم التحقق من أصالة المنتج",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Supply Chain Manager - مدير سلسلة التوريد
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ChainConfig:
    """Configuration for supply chain tracking - إعدادات تتبع سلسلة التوريد"""

    # Temperature thresholds for alerts
    min_temp_threshold_c: float = 0.0
    max_temp_threshold_c: float = 8.0

    # Time thresholds
    max_transport_hours: int = 24
    max_storage_days: int = 30

    # Quality settings
    require_quality_check: bool = True
    auto_update_batch_status: bool = True

    # Event verification
    require_event_verification: bool = False
    require_photo_evidence: bool = False


class SupplyChainTracker:
    """
    Supply Chain Event Tracker
    متتبع أحداث سلسلة التوريد

    Manages the complete lifecycle of produce batches through
    the supply chain with event logging and verification.

    يدير دورة الحياة الكاملة لدفعات المنتجات عبر
    سلسلة التوريد مع تسجيل الأحداث والتحقق.
    """

    def __init__(self, config: ChainConfig | None = None):
        """
        Initialize the supply chain tracker.

        Args:
            config: Chain tracking configuration
        """
        self.config = config or ChainConfig()

        # In-memory storage (replace with actual DB in production)
        self._batches: dict[str, ProduceBatch] = {}
        self._events: dict[str, list[SupplyChainEvent]] = {}  # batch_id -> events
        self._certifications: dict[str, Certification] = {}
        self._producers: dict[str, Producer] = {}

        # Event listeners
        self._event_listeners: list[Callable[[SupplyChainEvent], None]] = []

    # ─────────────────────────────────────────────────────────────────────────
    # Batch Management - إدارة الدفعات
    # ─────────────────────────────────────────────────────────────────────────

    def create_batch(
        self,
        tenant_id: str,
        farm_id: str,
        field_id: str,
        product_name_en: str,
        product_name_ar: str,
        batch_code: str,
        quantity: float,
        quantity_unit: str = "kg",
        variety_en: str = "",
        variety_ar: str = "",
        producer_id: str | None = None,
    ) -> ProduceBatch:
        """
        Create a new produce batch.
        إنشاء دفعة منتج جديدة.

        Args:
            tenant_id: Tenant ID
            farm_id: Farm ID
            field_id: Field ID
            product_name_en: Product name in English
            product_name_ar: Product name in Arabic
            batch_code: Unique batch code
            quantity: Initial quantity
            quantity_unit: Unit of measurement
            variety_en: Variety in English
            variety_ar: Variety in Arabic
            producer_id: Optional producer ID

        Returns:
            Created batch
        """
        batch = ProduceBatch(
            id=str(uuid4()),
            batch_code=batch_code,
            tenant_id=tenant_id,
            farm_id=farm_id,
            field_id=field_id,
            product_name_en=product_name_en,
            product_name_ar=product_name_ar,
            variety_en=variety_en,
            variety_ar=variety_ar,
            quantity=quantity,
            quantity_unit=quantity_unit,
            status=BatchStatus.CREATED,
            producer_id=producer_id,
        )

        self._batches[batch.id] = batch
        self._events[batch.id] = []

        return batch

    def get_batch(self, batch_id: str) -> ProduceBatch | None:
        """Get a batch by ID"""
        return self._batches.get(batch_id)

    def get_batch_by_code(self, batch_code: str) -> ProduceBatch | None:
        """Get a batch by batch code"""
        for batch in self._batches.values():
            if batch.batch_code == batch_code:
                return batch
        return None

    def update_batch_status(
        self,
        batch_id: str,
        status: BatchStatus,
    ) -> ProduceBatch | None:
        """Update batch status"""
        batch = self._batches.get(batch_id)
        if batch:
            batch.status = status
            batch.updated_at = datetime.now(UTC)
        return batch

    # ─────────────────────────────────────────────────────────────────────────
    # Event Recording - تسجيل الأحداث
    # ─────────────────────────────────────────────────────────────────────────

    def record_harvest(
        self,
        batch_id: str,
        field_name_en: str,
        field_name_ar: str,
        crop_type: str,
        harvest_method_en: str,
        harvest_method_ar: str,
        location: GeoLocation | None = None,
        actor_id: str = "",
        actor_name_en: str = "",
        actor_name_ar: str = "",
        temperature_c: float | None = None,
        humidity_percent: float | None = None,
        quality_notes_en: str = "",
        quality_notes_ar: str = "",
        photos: list[str] | None = None,
    ) -> HarvestEvent | None:
        """
        Record a harvest event.
        تسجيل حدث الحصاد.

        Args:
            batch_id: Batch ID
            field_name_en: Field name in English
            field_name_ar: Field name in Arabic
            crop_type: Type of crop harvested
            harvest_method_en: Harvest method in English
            harvest_method_ar: Harvest method in Arabic
            location: GPS location
            actor_id: ID of person/entity performing harvest
            actor_name_en: Actor name in English
            actor_name_ar: Actor name in Arabic
            temperature_c: Temperature at harvest
            humidity_percent: Humidity at harvest
            quality_notes_en: Quality notes in English
            quality_notes_ar: Quality notes in Arabic
            photos: Photo evidence URLs

        Returns:
            Created harvest event
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        event = HarvestEvent(
            id=str(uuid4()),
            batch_id=batch_id,
            field_id=batch.field_id,
            field_name_en=field_name_en,
            field_name_ar=field_name_ar,
            crop_type=crop_type,
            harvest_method_en=harvest_method_en,
            harvest_method_ar=harvest_method_ar,
            location=location,
            location_name_en=field_name_en,
            location_name_ar=field_name_ar,
            actor_id=actor_id,
            actor_type="producer",
            actor_name_en=actor_name_en,
            actor_name_ar=actor_name_ar,
            description_en=f"Harvested {batch.product_name_en} from {field_name_en}",
            description_ar=f"تم حصاد {batch.product_name_ar} من {field_name_ar}",
            temperature_c=temperature_c,
            humidity_percent=humidity_percent,
            quality_notes_en=quality_notes_en,
            quality_notes_ar=quality_notes_ar,
            photos=photos or [],
        )

        self._add_event(event)

        # Update batch
        if self.config.auto_update_batch_status:
            batch.status = BatchStatus.HARVESTED
            batch.harvest_date = event.timestamp
            batch.updated_at = datetime.now(UTC)

        return event

    def record_processing(
        self,
        batch_id: str,
        facility_id: str,
        facility_name_en: str,
        facility_name_ar: str,
        processing_type_en: str,
        processing_type_ar: str,
        input_quantity: float,
        output_quantity: float,
        quantity_unit: str = "kg",
        quality_grade: QualityGrade | None = None,
        quality_notes_en: str = "",
        quality_notes_ar: str = "",
        location: GeoLocation | None = None,
        photos: list[str] | None = None,
    ) -> ProcessingEvent | None:
        """
        Record a processing/packing event.
        تسجيل حدث المعالجة/التعبئة.
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        loss_percentage = 0.0
        if input_quantity > 0:
            loss_percentage = ((input_quantity - output_quantity) / input_quantity) * 100

        event = ProcessingEvent(
            id=str(uuid4()),
            batch_id=batch_id,
            facility_id=facility_id,
            facility_name_en=facility_name_en,
            facility_name_ar=facility_name_ar,
            processing_type_en=processing_type_en,
            processing_type_ar=processing_type_ar,
            input_quantity=input_quantity,
            output_quantity=output_quantity,
            quantity_unit=quantity_unit,
            loss_percentage=loss_percentage,
            quality_grade=quality_grade,
            quality_notes_en=quality_notes_en,
            quality_notes_ar=quality_notes_ar,
            location=location,
            location_name_en=facility_name_en,
            location_name_ar=facility_name_ar,
            actor_id=facility_id,
            actor_type="facility",
            actor_name_en=facility_name_en,
            actor_name_ar=facility_name_ar,
            description_en=f"{processing_type_en} at {facility_name_en}",
            description_ar=f"{processing_type_ar} في {facility_name_ar}",
            photos=photos or [],
        )

        self._add_event(event)

        # Update batch
        if self.config.auto_update_batch_status:
            batch.status = BatchStatus.IN_PROCESSING
            batch.quantity = output_quantity
            if quality_grade:
                batch.quality_grade = quality_grade
            batch.pack_date = event.timestamp
            batch.updated_at = datetime.now(UTC)

        return event

    def record_storage(
        self,
        batch_id: str,
        facility_id: str,
        facility_name_en: str,
        facility_name_ar: str,
        storage_unit_id: str,
        storage_condition: StorageCondition,
        target_temperature_c: float | None = None,
        actual_temperature_c: float | None = None,
        target_humidity_percent: float | None = None,
        actual_humidity_percent: float | None = None,
        condition_notes_en: str = "",
        condition_notes_ar: str = "",
        location: GeoLocation | None = None,
    ) -> StorageEvent | None:
        """
        Record a storage event.
        تسجيل حدث التخزين.
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        event = StorageEvent(
            id=str(uuid4()),
            batch_id=batch_id,
            facility_id=facility_id,
            facility_name_en=facility_name_en,
            facility_name_ar=facility_name_ar,
            storage_unit_id=storage_unit_id,
            storage_condition=storage_condition,
            target_temperature_c=target_temperature_c,
            actual_temperature_c=actual_temperature_c,
            target_humidity_percent=target_humidity_percent,
            actual_humidity_percent=actual_humidity_percent,
            condition_notes_en=condition_notes_en,
            condition_notes_ar=condition_notes_ar,
            location=location,
            location_name_en=facility_name_en,
            location_name_ar=facility_name_ar,
            actor_id=facility_id,
            actor_type="facility",
            actor_name_en=facility_name_en,
            actor_name_ar=facility_name_ar,
            description_en=f"Stored in {storage_condition.value} conditions",
            description_ar=f"تم التخزين في ظروف {storage_condition.value}",
        )

        self._add_event(event)

        # Update batch
        if self.config.auto_update_batch_status:
            batch.status = BatchStatus.IN_STORAGE
            batch.updated_at = datetime.now(UTC)

        # Check temperature compliance
        if actual_temperature_c is not None:
            self._check_temperature_compliance(batch, actual_temperature_c)

        return event

    def record_transport(
        self,
        batch_id: str,
        transporter_id: str,
        transporter_name_en: str,
        transporter_name_ar: str,
        vehicle_id: str,
        origin_en: str,
        origin_ar: str,
        destination_en: str,
        destination_ar: str,
        transport_mode: TransportMode,
        origin_location: GeoLocation | None = None,
        destination_location: GeoLocation | None = None,
        target_temperature_c: float | None = None,
        departure_time: datetime | None = None,
        distance_km: float | None = None,
    ) -> TransportEvent | None:
        """
        Record a transport event.
        تسجيل حدث النقل.
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        event = TransportEvent(
            id=str(uuid4()),
            batch_id=batch_id,
            transporter_id=transporter_id,
            transporter_name_en=transporter_name_en,
            transporter_name_ar=transporter_name_ar,
            vehicle_id=vehicle_id,
            origin_en=origin_en,
            origin_ar=origin_ar,
            origin_location=origin_location,
            destination_en=destination_en,
            destination_ar=destination_ar,
            destination_location=destination_location,
            transport_mode=transport_mode,
            target_temperature_c=target_temperature_c,
            departure_time=departure_time or datetime.now(UTC),
            distance_km=distance_km,
            location_name_en=f"{origin_en} to {destination_en}",
            location_name_ar=f"{origin_ar} إلى {destination_ar}",
            actor_id=transporter_id,
            actor_type="transporter",
            actor_name_en=transporter_name_en,
            actor_name_ar=transporter_name_ar,
            description_en=f"Transport from {origin_en} to {destination_en}",
            description_ar=f"نقل من {origin_ar} إلى {destination_ar}",
        )

        self._add_event(event)

        # Update batch
        if self.config.auto_update_batch_status:
            batch.status = BatchStatus.IN_TRANSIT
            batch.updated_at = datetime.now(UTC)

        return event

    def complete_transport(
        self,
        transport_event_id: str,
        arrival_time: datetime | None = None,
        min_temperature_c: float | None = None,
        max_temperature_c: float | None = None,
    ) -> TransportEvent | None:
        """
        Complete a transport event with arrival info.
        إكمال حدث النقل بمعلومات الوصول.
        """
        for events in self._events.values():
            for event in events:
                if event.id == transport_event_id and isinstance(event, TransportEvent):
                    event.arrival_time = arrival_time or datetime.now(UTC)
                    event.min_recorded_temperature_c = min_temperature_c
                    event.max_recorded_temperature_c = max_temperature_c
                    return event
        return None

    def record_retail(
        self,
        batch_id: str,
        retailer_id: str,
        retailer_name_en: str,
        retailer_name_ar: str,
        store_location_en: str,
        store_location_ar: str,
        received_quantity: float,
        quantity_unit: str = "kg",
        temperature_at_receipt_c: float | None = None,
        quality_check_passed: bool = True,
        display_location_en: str = "",
        display_location_ar: str = "",
        unit_price: float | None = None,
        currency: str = "SAR",
        location: GeoLocation | None = None,
    ) -> RetailEvent | None:
        """
        Record a retail arrival event.
        تسجيل حدث الوصول إلى التجزئة.
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        event = RetailEvent(
            id=str(uuid4()),
            batch_id=batch_id,
            retailer_id=retailer_id,
            retailer_name_en=retailer_name_en,
            retailer_name_ar=retailer_name_ar,
            store_location_en=store_location_en,
            store_location_ar=store_location_ar,
            received_quantity=received_quantity,
            quantity_unit=quantity_unit,
            temperature_at_receipt_c=temperature_at_receipt_c,
            quality_check_passed=quality_check_passed,
            display_location_en=display_location_en,
            display_location_ar=display_location_ar,
            unit_price=unit_price,
            currency=currency,
            location=location,
            location_name_en=store_location_en,
            location_name_ar=store_location_ar,
            actor_id=retailer_id,
            actor_type="retailer",
            actor_name_en=retailer_name_en,
            actor_name_ar=retailer_name_ar,
            description_en=f"Received at {retailer_name_en}",
            description_ar=f"تم الاستلام في {retailer_name_ar}",
        )

        self._add_event(event)

        # Update batch
        if self.config.auto_update_batch_status:
            batch.status = BatchStatus.AT_RETAIL
            batch.updated_at = datetime.now(UTC)

        return event

    def record_consumer_scan(
        self,
        batch_id: str,
        session_id: str,
        device_type: str = "mobile",
        scan_location: GeoLocation | None = None,
        rating: int | None = None,
        feedback_en: str | None = None,
        feedback_ar: str | None = None,
    ) -> ConsumerScanEvent | None:
        """
        Record a consumer QR scan event.
        تسجيل حدث مسح المستهلك لرمز QR.
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        event = ConsumerScanEvent(
            id=str(uuid4()),
            batch_id=batch_id,
            session_id=session_id,
            device_type=device_type,
            scan_location=scan_location,
            rating=rating,
            feedback_en=feedback_en,
            feedback_ar=feedback_ar,
            location=scan_location,
            description_en="Product verified by consumer",
            description_ar="تم التحقق من المنتج بواسطة المستهلك",
            actor_type="consumer",
        )

        self._add_event(event)

        return event

    # ─────────────────────────────────────────────────────────────────────────
    # Event Retrieval - استرجاع الأحداث
    # ─────────────────────────────────────────────────────────────────────────

    def get_events(
        self,
        batch_id: str,
        event_type: EventType | None = None,
    ) -> list[SupplyChainEvent]:
        """
        Get events for a batch.
        الحصول على أحداث دفعة.

        Args:
            batch_id: Batch ID
            event_type: Optional filter by event type

        Returns:
            List of events
        """
        events = self._events.get(batch_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return sorted(events, key=lambda e: e.timestamp)

    def get_latest_event(
        self,
        batch_id: str,
        event_type: EventType | None = None,
    ) -> SupplyChainEvent | None:
        """Get the most recent event for a batch"""
        events = self.get_events(batch_id, event_type)
        return events[-1] if events else None

    # ─────────────────────────────────────────────────────────────────────────
    # Product Journey - رحلة المنتج
    # ─────────────────────────────────────────────────────────────────────────

    def build_product_journey(
        self,
        batch_id: str,
    ) -> ProductJourney | None:
        """
        Build a consumer-friendly product journey.
        بناء رحلة منتج سهلة للمستهلك.

        Args:
            batch_id: Batch ID

        Returns:
            Product journey for display
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        events = self.get_events(batch_id)
        if not events:
            return None

        # Get producer info
        producer = self._producers.get(batch.producer_id or "")
        producer_name_en = producer.name_en if producer else ""
        producer_name_ar = producer.name_ar if producer else ""
        farm_name_en = producer.farm_name_en if producer else ""
        farm_name_ar = producer.farm_name_ar if producer else ""
        farm_location_en = ""
        farm_location_ar = ""
        if producer and producer.address:
            farm_location_en = f"{producer.address.city_en}, {producer.address.region_en}"
            farm_location_ar = f"{producer.address.city_ar}, {producer.address.region_ar}"

        # Build journey steps
        steps = []
        total_distance = 0.0
        for i, event in enumerate(events):
            display_info = EVENT_DISPLAY_INFO.get(event.event_type, {})

            step = ProductJourneyStep(
                step_number=i + 1,
                event_type=event.event_type,
                title_en=display_info.get("title_en", event.event_type.value),
                title_ar=display_info.get("title_ar", event.event_type.value),
                description_en=event.description_en or display_info.get("description_en", ""),
                description_ar=event.description_ar or display_info.get("description_ar", ""),
                location_en=event.location_name_en,
                location_ar=event.location_name_ar,
                date=event.timestamp,
                icon=display_info.get("icon", ""),
                verified=event.verified,
            )
            steps.append(step)

            # Accumulate distance from transport events
            if isinstance(event, TransportEvent) and event.distance_km:
                total_distance += event.distance_km

        # Calculate freshness
        days_since_harvest = 0
        if batch.harvest_date:
            days_since_harvest = (datetime.now(UTC) - batch.harvest_date).days

        # Calculate freshness score (100 = just harvested, decreases over time)
        freshness_score = max(0, 100 - (days_since_harvest * 5))

        # Calculate journey duration
        journey_duration = 0.0
        if events:
            first_event = events[0]
            last_event = events[-1]
            journey_duration = (last_event.timestamp - first_event.timestamp).total_seconds() / 3600

        # Get certifications
        certifications = [
            self._certifications[cert_id] for cert_id in batch.certification_ids if cert_id in self._certifications
        ]

        return ProductJourney(
            batch_id=batch.id,
            batch_code=batch.batch_code,
            product_name_en=batch.product_name_en,
            product_name_ar=batch.product_name_ar,
            variety_en=batch.variety_en,
            variety_ar=batch.variety_ar,
            producer_name_en=producer_name_en,
            producer_name_ar=producer_name_ar,
            farm_name_en=farm_name_en,
            farm_name_ar=farm_name_ar,
            farm_location_en=farm_location_en,
            farm_location_ar=farm_location_ar,
            quality_grade=batch.quality_grade,
            harvest_date=batch.harvest_date or events[0].timestamp,
            pack_date=batch.pack_date,
            expiry_date=batch.expiry_date,
            steps=steps,
            certifications=certifications,
            days_since_harvest=days_since_harvest,
            freshness_score=freshness_score,
            transport_distance_km=total_distance,
            journey_duration_hours=journey_duration,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Trace Report - تقرير التتبع
    # ─────────────────────────────────────────────────────────────────────────

    def generate_trace_report(
        self,
        batch_id: str,
        generated_by: str = "system",
    ) -> BatchTraceReport | None:
        """
        Generate a comprehensive trace report for a batch.
        إنشاء تقرير تتبع شامل لدفعة.

        Args:
            batch_id: Batch ID
            generated_by: User/system generating the report

        Returns:
            Complete batch trace report
        """
        batch = self._batches.get(batch_id)
        if not batch:
            return None

        events = self.get_events(batch_id)
        producer = self._producers.get(batch.producer_id or "")
        certifications = [
            self._certifications[cert_id] for cert_id in batch.certification_ids if cert_id in self._certifications
        ]

        # Calculate stats
        total_distance = 0.0
        min_temp: float | None = None
        max_temp: float | None = None
        temp_excursions = 0
        quality_passed = 0
        quality_failed = 0
        handlers: set[str] = set()

        for event in events:
            handlers.add(event.actor_id)

            if isinstance(event, TransportEvent):
                if event.distance_km:
                    total_distance += event.distance_km
                if event.min_recorded_temperature_c is not None:
                    if min_temp is None or event.min_recorded_temperature_c < min_temp:
                        min_temp = event.min_recorded_temperature_c
                if event.max_recorded_temperature_c is not None:
                    if max_temp is None or event.max_recorded_temperature_c > max_temp:
                        max_temp = event.max_recorded_temperature_c
                    # Check for excursion
                    if event.max_recorded_temperature_c > self.config.max_temp_threshold_c:
                        temp_excursions += 1

            if isinstance(event, StorageEvent):
                if event.actual_temperature_c is not None:
                    if min_temp is None or event.actual_temperature_c < min_temp:
                        min_temp = event.actual_temperature_c
                    if max_temp is None or event.actual_temperature_c > max_temp:
                        max_temp = event.actual_temperature_c
                    if event.actual_temperature_c > self.config.max_temp_threshold_c:
                        temp_excursions += 1

            if isinstance(event, (ProcessingEvent, RetailEvent)):
                if hasattr(event, "quality_check_passed"):
                    if event.quality_check_passed:
                        quality_passed += 1
                    else:
                        quality_failed += 1

        # Calculate journey time
        journey_hours = 0.0
        if events:
            first = events[0]
            last = events[-1]
            journey_hours = (last.timestamp - first.timestamp).total_seconds() / 3600

        # Check certification validity
        all_certs_valid = all(c.is_currently_valid() for c in certifications)

        # Compliance issues
        compliance_issues = []
        if temp_excursions > 0:
            compliance_issues.append(f"Temperature excursion detected {temp_excursions} time(s)")
        if quality_failed > 0:
            compliance_issues.append(f"Quality check failed {quality_failed} time(s)")
        if not all_certs_valid:
            compliance_issues.append("One or more certifications are expired")

        return BatchTraceReport(
            batch=batch,
            producer=producer,
            events=events,
            certifications=certifications,
            total_journey_hours=journey_hours,
            total_distance_km=total_distance,
            number_of_handlers=len(handlers),
            min_temperature_c=min_temp,
            max_temperature_c=max_temp,
            temperature_excursions=temp_excursions,
            quality_checks_passed=quality_passed,
            quality_checks_failed=quality_failed,
            all_certifications_valid=all_certs_valid,
            compliance_issues=compliance_issues,
            generated_by=generated_by,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Certification Management - إدارة الشهادات
    # ─────────────────────────────────────────────────────────────────────────

    def add_certification(self, certification: Certification) -> None:
        """Add a certification to the registry"""
        self._certifications[certification.id] = certification

    def link_certification_to_batch(
        self,
        batch_id: str,
        certification_id: str,
    ) -> bool:
        """Link a certification to a batch"""
        batch = self._batches.get(batch_id)
        if batch and certification_id in self._certifications:
            if certification_id not in batch.certification_ids:
                batch.certification_ids.append(certification_id)
            return True
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # Producer Management - إدارة المنتجين
    # ─────────────────────────────────────────────────────────────────────────

    def add_producer(self, producer: Producer) -> None:
        """Add a producer to the registry"""
        self._producers[producer.id] = producer

    # ─────────────────────────────────────────────────────────────────────────
    # Event Listeners - مستمعو الأحداث
    # ─────────────────────────────────────────────────────────────────────────

    def add_event_listener(
        self,
        listener: Callable[[SupplyChainEvent], None],
    ) -> None:
        """Add an event listener for supply chain events"""
        self._event_listeners.append(listener)

    def remove_event_listener(
        self,
        listener: Callable[[SupplyChainEvent], None],
    ) -> None:
        """Remove an event listener"""
        if listener in self._event_listeners:
            self._event_listeners.remove(listener)

    # ─────────────────────────────────────────────────────────────────────────
    # Private Methods - الدوال الخاصة
    # ─────────────────────────────────────────────────────────────────────────

    def _add_event(self, event: SupplyChainEvent) -> None:
        """Add an event and notify listeners"""
        if event.batch_id not in self._events:
            self._events[event.batch_id] = []
        self._events[event.batch_id].append(event)

        # Notify listeners
        for listener in self._event_listeners:
            try:
                listener(event)
            except Exception:
                pass  # Don't let listener errors break the chain

    def _check_temperature_compliance(
        self,
        batch: ProduceBatch,
        temperature_c: float,
    ) -> bool:
        """Check if temperature is within acceptable range"""
        if temperature_c < self.config.min_temp_threshold_c:
            return False
        if temperature_c > self.config.max_temp_threshold_c:
            return False
        return True


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions - دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────


def calculate_carbon_footprint(
    distance_km: float,
    transport_mode: TransportMode,
    weight_kg: float,
) -> float:
    """
    Estimate carbon footprint for transport.
    تقدير البصمة الكربونية للنقل.

    Args:
        distance_km: Distance in kilometers
        transport_mode: Mode of transport
        weight_kg: Weight of produce in kg

    Returns:
        Estimated CO2 in kg
    """
    # Emission factors (kg CO2 per ton-km)
    emission_factors = {
        TransportMode.TRUCK_REFRIGERATED: 0.15,  # Higher due to cooling
        TransportMode.TRUCK_AMBIENT: 0.10,
        TransportMode.AIR_FREIGHT: 0.60,
        TransportMode.SEA_FREIGHT: 0.015,
        TransportMode.RAIL: 0.03,
        TransportMode.LOCAL_DELIVERY: 0.20,
    }

    factor = emission_factors.get(transport_mode, 0.10)
    weight_tons = weight_kg / 1000

    return distance_km * weight_tons * factor


def estimate_shelf_life(
    product_type: str,
    storage_condition: StorageCondition,
    quality_grade: QualityGrade,
) -> int:
    """
    Estimate shelf life in days.
    تقدير مدة الصلاحية بالأيام.

    Args:
        product_type: Type of produce
        storage_condition: Storage condition
        quality_grade: Quality grade

    Returns:
        Estimated shelf life in days
    """
    # Base shelf life by product type (days at chilled storage)
    base_shelf_life = {
        "tomato": 14,
        "cucumber": 10,
        "lettuce": 7,
        "apple": 60,
        "date": 180,
        "wheat": 365,
        "default": 14,
    }

    # Condition multipliers
    condition_multipliers = {
        StorageCondition.FROZEN: 4.0,
        StorageCondition.CHILLED: 1.0,
        StorageCondition.CONTROLLED_ATMOSPHERE: 1.5,
        StorageCondition.HUMIDITY_CONTROLLED: 1.2,
        StorageCondition.AMBIENT: 0.3,
    }

    # Quality grade multipliers
    grade_multipliers = {
        QualityGrade.PREMIUM: 1.1,
        QualityGrade.GRADE_A: 1.0,
        QualityGrade.GRADE_B: 0.8,
        QualityGrade.GRADE_C: 0.6,
        QualityGrade.REJECTED: 0.0,
    }

    base = base_shelf_life.get(product_type.lower(), base_shelf_life["default"])
    condition_mult = condition_multipliers.get(storage_condition, 1.0)
    grade_mult = grade_multipliers.get(quality_grade, 1.0)

    return int(base * condition_mult * grade_mult)
