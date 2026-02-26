# shared/traceability

Farm-to-table supply chain traceability for the SAHOOL platform. Tracks produce batches
from harvest through processing, cold storage, transport, and retail display. Generates
consumer-facing product journey pages via QR code scans, and produces compliance reports
for regulators and certifying bodies (GlobalGAP, SFDA, HACCP, Halal).

## File Structure

```
shared/traceability/
├── __init__.py       # Public API exports
├── models.py         # All data classes and enumerations
├── chain.py          # Supply chain event management and journey builder
└── qr_generator.py   # QR code generation with format and size options
```

## Key Components

### models.py

Full set of domain models for traceability.

**Event types (`EventType`):**
HARVEST, PROCESSING, STORAGE, TRANSPORT, RETAIL, CONSUMER_SCAN.

**Batch lifecycle (`BatchStatus`):**
CREATED → HARVESTED → IN_PROCESSING → IN_STORAGE → IN_TRANSIT → AT_RETAIL → SOLD → EXPIRED / RECALLED.

**Certification types (`CertificationType`):**
GLOBALGAP, ORGANIC, HALAL, SASO, SFDA, ISO_22000, HACCP, FAIR_TRADE, LOCAL_GAP.

**Quality grades (`QualityGrade`):** PREMIUM, GRADE_A, GRADE_B, GRADE_C, REJECTED.

**Storage conditions (`StorageCondition`):**
AMBIENT, CHILLED (0-4°C), FROZEN, CONTROLLED_ATMOSPHERE, HUMIDITY_CONTROLLED.

**Actor models:**

| Class | Role in supply chain |
|-------|---------------------|
| `Producer` | Farm / grower with registration number and GPS location |
| `ProcessingFacility` | Packing house or processing plant with certifications |
| `Transporter` | Carrier company with vehicle and driver details |
| `Retailer` | Store or market with address |

**Batch models:**

| Class | Purpose |
|-------|---------|
| `ProduceBatch` | Core batch record with crop, quantity, quality grade, QR code URL |
| `BatchSplit` | Records splitting one batch into multiple child batches |
| `BatchMerge` | Records merging multiple source batches into one target batch |

**Supply chain event models (all extend `SupplyChainEvent`):**

| Class | Key Fields |
|-------|-----------|
| `HarvestEvent` | field_id, harvest method, temperature and humidity at harvest |
| `ProcessingEvent` | facility_id, input/output quantity, loss %, quality check |
| `StorageEvent` | storage unit, target vs. actual temperature and humidity, duration |
| `TransportEvent` | origin/destination with GPS, transport mode, temperature excursion data |
| `RetailEvent` | retailer, received quantity, temperature at receipt, unit price |
| `ConsumerScanEvent` | anonymous session ID, device type, optional 1-5 rating and feedback |

`SupplyChainEvent` base fields: batch_id, timestamp, location, actor, description,
photo/document URLs, verification status and digital signature.

**Consumer-facing models:**

| Class | Purpose |
|-------|---------|
| `ProductJourneyStep` | Single display step: title, description, location, icon, verification badge |
| `ProductJourney` | Full consumer journey: steps, certifications, freshness score, CO2 footprint |
| `QRCodeData` | QR payload: batch code, producer, harvest date, verification URL |
| `BatchTraceReport` | Full compliance report with temperature statistics and quality checks |

`QRCodeData.to_compact_string()` generates the `SAHOOL|{batch_code}|{product}|{date}|{url}` string
encoded into the QR image.

### chain.py

Event recording and product journey construction.

`EVENT_DISPLAY_INFO` is a pre-built dict mapping each `EventType` to bilingual title,
description, and icon name for consistent UI rendering.

| Class | Description |
|-------|-------------|
| `BatchRegistry` | In-memory or DB-backed batch index; find batches by code or tenant |
| `EventStore` | Append-only event store with verification support |
| `JourneyBuilder` | Converts raw events into a consumer-friendly `ProductJourney` |
| `TraceabilityChain` | Main service: create batches, record events, build journeys |

**Key methods on `TraceabilityChain`:**

| Method | Description |
|--------|-------------|
| `create_batch(tenant_id, farm_id, product_name, quantity, ...)` | Creates `ProduceBatch` |
| `record_harvest(batch_id, producer_id, field_id, ...)` | Appends `HarvestEvent` |
| `record_processing(batch_id, facility_id, ...)` | Appends `ProcessingEvent` |
| `record_storage(batch_id, facility_id, condition, ...)` | Appends `StorageEvent` |
| `record_transport(batch_id, transporter_id, origin, destination, ...)` | Appends `TransportEvent` |
| `record_retail(batch_id, retailer_id, ...)` | Appends `RetailEvent` |
| `record_consumer_scan(batch_id, session_id, rating)` | Appends `ConsumerScanEvent` |
| `get_product_journey(batch_id)` | Returns `ProductJourney` for consumer display |
| `generate_trace_report(batch_id)` | Returns `BatchTraceReport` for compliance |

**Convenience functions:** `get_traceability_chain(tenant_id)`, `create_batch(...)`,
`record_event(batch_id, event_type, ...)`, `get_product_journey(batch_id, tenant_id)`.

### qr_generator.py

QR code generation for batch labels and packaging.

**Output formats (`QRFormat`):** PNG, SVG, BASE64_PNG, BASE64_SVG.

**Size presets (`QRSize`):**

| Preset | Pixels | Use Case |
|--------|--------|----------|
| SMALL | 128×128 | Product label sticker |
| MEDIUM | 256×256 | Box or carton |
| LARGE | 512×512 | Display poster |
| XLARGE | 1024×1024 | Print-quality export |

| Class | Description |
|-------|-------------|
| `QRGenerationConfig` | Base URL, format, size, colors, optional logo, error correction level |
| `QRGenerationResult` | Image bytes or base64 string, size, format, verification URL |
| `BatchQRGenerator` | Generates and manages QR codes for `ProduceBatch` records |

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `generate_batch_qr(batch, config)` | Returns `QRGenerationResult` for one batch |
| `generate_qr_url(batch_id, base_url)` | Returns verification URL only (no image) |
| `get_batch_qr_generator(tenant_id, base_url)` | Returns configured generator instance |

## Usage Example

```python
from shared.traceability import (
    get_traceability_chain,
    get_batch_qr_generator,
    QRGenerationConfig,
    QRSize,
    QRFormat,
    StorageCondition,
    TransportMode,
)

chain = get_traceability_chain("tenant_001")

# Create batch and record events
batch = await chain.create_batch(
    tenant_id="tenant_001",
    farm_id="FARM-001",
    field_id="FIELD-003",
    product_name_en="Wheat - Sakha 95",
    product_name_ar="قمح - سخا 95",
    variety_en="Sakha 95",
    variety_ar="سخا 95",
    quantity=8500.0,
    quantity_unit="kg",
)

await chain.record_harvest(
    batch_id=batch.id,
    producer_id="PROD-001",
    field_id="FIELD-003",
    harvest_method_en="Mechanical",
    harvest_method_ar="آلي",
    temperature_c=22.5,
    humidity_percent=45.0,
)

await chain.record_storage(
    batch_id=batch.id,
    facility_id="FAC-SILO-01",
    storage_condition=StorageCondition.AMBIENT,
    target_temperature_c=20.0,
    actual_temperature_c=21.5,
)

await chain.record_transport(
    batch_id=batch.id,
    transporter_id="TRANS-001",
    origin_en="Al-Qassim Farm",
    destination_en="Riyadh Central Market",
    transport_mode=TransportMode.TRUCK_AMBIENT,
    distance_km=350.0,
)

# Consumer journey
journey = await chain.get_product_journey(batch.id)
print(f"Freshness: {journey.freshness_score}/100")
print(f"Steps: {len(journey.steps)}")

# Compliance report
report = await chain.generate_trace_report(batch.id)
print(f"Temperature excursions: {report.temperature_excursions}")
print(f"Certifications valid: {report.all_certifications_valid}")

# QR code for packaging label
generator = get_batch_qr_generator("tenant_001", base_url="https://trace.sahool.app")
result = await generator.generate_qr(
    batch=batch,
    config=QRGenerationConfig(
        format=QRFormat.PNG,
        size=QRSize.MEDIUM,
    ),
)
# result.image_bytes -> write to file or upload to MinIO
```

## Regulatory Compliance

`BatchTraceReport` is structured to satisfy requirements for:
- SFDA (Saudi Food and Drug Authority) - traceability mandate
- GlobalGAP produce assurance
- HACCP cold chain temperature records
- Halal supply chain integrity documentation
