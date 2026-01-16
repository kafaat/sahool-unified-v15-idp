# In-Memory Storage Migration Guide

**Last Updated:** 2025-12-31
**Priority:** CRITICAL - Production Readiness
**Status:** Planning Phase

## Executive Summary

This document catalogs all in-memory storage across SAHOOL services and provides a comprehensive migration plan to PostgreSQL. In-memory storage is acceptable for development but **MUST NOT** be used in production as it leads to:

- Data loss on service restart
- Inability to scale horizontally (each pod has separate state)
- No audit trail for compliance
- No data backup/recovery
- Performance degradation with large datasets

## Services Requiring Migration

### Critical Priority (Data Loss = Business Impact)

#### 1. billing-core

**Location:** `/apps/services/billing-core/src/main.py`
**Lines:** 550-556

**In-Memory Storage:**

```python
PLANS: Dict[str, Plan] = {}
TENANTS: Dict[str, Tenant] = {}
SUBSCRIPTIONS: Dict[str, Subscription] = {}  # Partially migrated
INVOICES: Dict[str, Invoice] = {}
PAYMENTS: Dict[str, Payment] = {}
USAGE_RECORDS: List[UsageRecord] = []
INVOICE_COUNTER: int = 0
```

**Business Impact:**

- **CRITICAL:** Lost invoice/payment records = compliance violation
- **CRITICAL:** Lost tenant data = customer churn
- **HIGH:** Lost usage records = billing inaccuracies
- **MEDIUM:** Lost plans = service reconfiguration needed

**Migration Required:**

1. ✅ `subscriptions` table - PARTIALLY DONE (database.py has model)
2. ❌ `plans` table - Migrate from in-memory dict
3. ❌ `tenants` table - Customer data MUST persist
4. ❌ `invoices` table - Extend existing with line_items (JSONB)
5. ❌ `payments` table - Payment tracking for Stripe integration
6. ❌ `usage_records` table - Metered billing data

**Database Schema:**

```sql
-- plans table
CREATE TABLE plans (
    plan_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_ar VARCHAR(100) NOT NULL,
    tier VARCHAR(20) NOT NULL,
    pricing JSONB NOT NULL,
    features JSONB NOT NULL,
    limits JSONB NOT NULL,
    trial_days INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- tenants table
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    contact JSONB NOT NULL,
    settings JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_tenants_name ON tenants(name);

-- payments table
CREATE TABLE payments (
    payment_id UUID PRIMARY KEY,
    invoice_id UUID REFERENCES invoices(id),
    tenant_id VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    method VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    stripe_payment_id VARCHAR(200),
    processed_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX idx_payments_tenant ON payments(tenant_id);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);

-- usage_records table
CREATE TABLE usage_records (
    id UUID PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    metric VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);
CREATE INDEX idx_usage_tenant_metric ON usage_records(tenant_id, metric, timestamp DESC);
```

**Estimated Migration Time:** 3-4 days

---

#### 2. crop-health-ai (diagnosis_service)

**Location:** `/apps/services/crop-health-ai/src/services/diagnosis_service.py`
**Lines:** 41-90

**In-Memory Storage:**

```python
self._history: List[Dict[str, Any]] = []  # Limited to MAX_HISTORY_SIZE=1000
```

**Business Impact:**

- **CRITICAL:** Diagnosis history lost = no epidemic monitoring
- **CRITICAL:** Limited to 1000 records = data dropped in high-volume periods
- **HIGH:** No multi-instance support = cannot scale pods
- **HIGH:** No spatial queries = cannot detect disease outbreaks by region

**Migration Required:**

1. ❌ `crop_diagnoses` table - Full diagnosis history with geospatial support
2. ❌ DiagnosisRepository - Replace in-memory list operations

**Database Schema:**

```sql
CREATE TABLE crop_diagnoses (
    id UUID PRIMARY KEY,
    image_url TEXT,
    thumbnail_url TEXT,
    disease_id VARCHAR(50) NOT NULL,
    disease_name VARCHAR(200) NOT NULL,
    disease_name_ar VARCHAR(200) NOT NULL,
    confidence DECIMAL(4, 3) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    crop_type VARCHAR(50),
    field_id VARCHAR(100),
    governorate VARCHAR(50),
    location GEOGRAPHY(POINT, 4326),  -- PostGIS for spatial queries
    status VARCHAR(20) DEFAULT 'pending',
    farmer_id VARCHAR(100),
    expert_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_diagnoses_governorate ON crop_diagnoses(governorate, created_at DESC);
CREATE INDEX idx_diagnoses_field ON crop_diagnoses(field_id, created_at DESC);
CREATE INDEX idx_diagnoses_farmer ON crop_diagnoses(farmer_id, created_at DESC);
CREATE INDEX idx_diagnoses_status ON crop_diagnoses(status);
CREATE INDEX idx_diagnoses_disease ON crop_diagnoses(disease_id, created_at DESC);
CREATE INDEX idx_diagnoses_location ON crop_diagnoses USING GIST(location);  -- Spatial index

-- Time-series partitioning for large datasets
CREATE TABLE crop_diagnoses_2025_q1 PARTITION OF crop_diagnoses
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
```

**Estimated Migration Time:** 2-3 days

---

#### 3. notification-service

**Location:** `/apps/services/notification-service/src/main.py`
**Lines:** 268-295

**In-Memory Storage:**

```python
FARMER_PROFILES: Dict[str, FarmerProfile] = {}
NOTIFICATIONS: Dict[str, Notification] = {}  # LEGACY - Already using database
FARMER_NOTIFICATIONS: Dict[str, List[str]] = {}  # LEGACY
```

**Business Impact:**

- **HIGH:** Farmer profiles lost = cannot target notifications
- **LOW:** NOTIFICATIONS/FARMER_NOTIFICATIONS already migrated to database (just remove)

**Migration Required:**

1. ❌ `farmer_profiles` table - Farmer data with crops, fields, channels
2. ✅ `notifications` - ALREADY DONE via NotificationRepository
3. ✅ Remove unused NOTIFICATIONS and FARMER_NOTIFICATIONS dicts

**Database Schema:**

```sql
CREATE TABLE farmer_profiles (
    farmer_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200) NOT NULL,
    governorate VARCHAR(50) NOT NULL,
    district VARCHAR(100),
    phone VARCHAR(20),
    fcm_token VARCHAR(500),
    language VARCHAR(5) DEFAULT 'ar',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE farmer_crops (
    farmer_id VARCHAR(100) REFERENCES farmer_profiles(farmer_id) ON DELETE CASCADE,
    crop_type VARCHAR(50) NOT NULL,
    PRIMARY KEY (farmer_id, crop_type)
);

CREATE TABLE farmer_fields (
    farmer_id VARCHAR(100) REFERENCES farmer_profiles(farmer_id) ON DELETE CASCADE,
    field_id VARCHAR(100) NOT NULL,
    PRIMARY KEY (farmer_id, field_id)
);

CREATE TABLE farmer_channels (
    farmer_id VARCHAR(100) REFERENCES farmer_profiles(farmer_id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,
    PRIMARY KEY (farmer_id, channel)
);

CREATE INDEX idx_farmer_governorate ON farmer_profiles(governorate);
```

**Estimated Migration Time:** 2 days

---

### High Priority (Core Functionality)

#### 4. task-service

**Location:** `/apps/services/task-service/src/main.py`
**Lines:** 214-215

**In-Memory Storage:**

```python
tasks_db: dict[str, Task] = {}
evidence_db: dict[str, Evidence] = {}
```

**Business Impact:**

- **HIGH:** Task assignments lost = operational disruption
- **MEDIUM:** Evidence lost = no audit trail
- **MEDIUM:** No task history = cannot analyze worker performance

**Database Schema:**

```sql
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    title_ar VARCHAR(200),
    description TEXT,
    description_ar TEXT,
    task_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    field_id VARCHAR(100),
    zone_id VARCHAR(100),
    assigned_to VARCHAR(100),
    created_by VARCHAR(100) NOT NULL,
    due_date TIMESTAMP,
    scheduled_time TIME,
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    completion_notes TEXT,
    metadata JSONB
);

CREATE INDEX idx_tasks_tenant_status ON tasks(tenant_id, status);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to, status);
CREATE INDEX idx_tasks_field ON tasks(field_id, status);
CREATE INDEX idx_tasks_due ON tasks(due_date);

CREATE TABLE task_evidence (
    evidence_id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT NOW(),
    location GEOGRAPHY(POINT, 4326)
);

CREATE INDEX idx_evidence_task ON task_evidence(task_id);
```

**Estimated Migration Time:** 2 days

---

#### 5. alert-service

**Location:** `/apps/services/alert-service/src/main.py`
**Lines:** 119-120

**In-Memory Storage:**

```python
_alerts: dict[str, dict] = {}
_rules: dict[str, dict] = {}
```

**Business Impact:**

- **HIGH:** Alert history lost = cannot analyze incident patterns
- **HIGH:** Rules lost = manual reconfiguration needed
- **MEDIUM:** No compliance trail for critical alerts

**Database Schema:**

```sql
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    title_ar VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    message_ar TEXT NOT NULL,
    source VARCHAR(100),
    field_ids VARCHAR(100)[],
    governorate VARCHAR(50),
    location GEOGRAPHY(POINT, 4326),
    created_at TIMESTAMP DEFAULT NOW(),
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    resolved_at TIMESTAMP,
    expires_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_alerts_tenant_type ON alerts(tenant_id, type, created_at DESC);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity, created_at DESC);

-- Partitioning for long-term storage
CREATE TABLE alerts_2025_q1 PARTITION OF alerts
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE alert_rules (
    rule_id UUID PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    conditions JSONB NOT NULL,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rules_tenant ON alert_rules(tenant_id);
CREATE INDEX idx_rules_enabled ON alert_rules(enabled);
```

**Estimated Migration Time:** 2 days

---

#### 6. equipment-service

**Location:** `/apps/services/equipment-service/src/main.py`
**Lines:** 246-248

**In-Memory Storage:**

```python
equipment_db: dict[str, Equipment] = {}
maintenance_db: dict[str, MaintenanceRecord] = {}
alerts_db: dict[str, MaintenanceAlert] = {}
```

**Business Impact:**

- **HIGH:** Equipment inventory lost = asset management failure
- **HIGH:** Maintenance history lost = compliance issues
- **MEDIUM:** No equipment lifecycle tracking

**Database Schema:**

```sql
CREATE TABLE equipment (
    equipment_id UUID PRIMARY KEY,
    tenant_id VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    name_ar VARCHAR(200),
    equipment_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    year INTEGER,
    purchase_date DATE,
    horsepower DECIMAL(8, 2),
    fuel_capacity_liters DECIMAL(8, 2),
    current_fuel_percent DECIMAL(5, 2),
    current_hours DECIMAL(10, 2),
    field_id VARCHAR(100),
    location_name VARCHAR(200),
    current_location GEOGRAPHY(POINT, 4326),
    last_maintenance_at TIMESTAMP,
    next_maintenance_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB,
    qr_code VARCHAR(100) UNIQUE
);

CREATE INDEX idx_equipment_tenant ON equipment(tenant_id, status);
CREATE INDEX idx_equipment_type ON equipment(equipment_type);
CREATE INDEX idx_equipment_field ON equipment(field_id);
CREATE INDEX idx_equipment_location ON equipment USING GIST(current_location);

CREATE TABLE equipment_maintenance (
    record_id UUID PRIMARY KEY,
    equipment_id UUID REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50) NOT NULL,
    description TEXT,
    performed_by VARCHAR(100),
    performed_at TIMESTAMP NOT NULL,
    cost DECIMAL(10, 2),
    parts_replaced JSONB,
    next_due_at TIMESTAMP,
    photos VARCHAR(500)[]
);

CREATE INDEX idx_maintenance_equipment ON equipment_maintenance(equipment_id, performed_at DESC);

CREATE TABLE equipment_alerts (
    alert_id UUID PRIMARY KEY,
    equipment_id UUID REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    maintenance_type VARCHAR(50),
    priority VARCHAR(20) NOT NULL,
    due_at TIMESTAMP,
    is_overdue BOOLEAN DEFAULT false,
    acknowledged_at TIMESTAMP
);

CREATE INDEX idx_equipment_alerts_due ON equipment_alerts(due_at) WHERE acknowledged_at IS NULL;
```

**Estimated Migration Time:** 2-3 days

---

### Medium Priority (Can Defer but Recommended)

#### 7. inventory-service (alerts_db, settings_db)

**Location:** `/apps/services/inventory-service/src/alert_endpoints.py`
**Line:** 289

**In-Memory Storage:**

```python
settings_db = {}  # In-memory settings storage
```

**Note:** Main inventory data already uses database (inventory_db via Tortoise ORM). Only alert settings are in-memory.

**Migration Required:**

- Create `inventory_alert_settings` table
- Migrate settings_db to database

**Estimated Migration Time:** 1 day

---

#### 8. vegetation-analysis-service (VRA prescriptions)

**Location:** `/apps/services/vegetation-analysis-service/src/vra_generator.py`
**Line:** 267

**In-Memory Storage:**

```python
self._prescription_store: Dict[str, PrescriptionMap] = {}
```

**Business Impact:**

- **MEDIUM:** Lost prescription maps = farmers need to re-request
- **LOW:** Prescriptions are regenerated on-demand (acceptable loss)

**Migration Required:**

- Create `vra_prescriptions` table
- Store generated prescription maps with geometry data (PostGIS)

**Estimated Migration Time:** 2 days (due to geospatial data)

---

#### 9. satellite-service (VRA prescriptions)

**Location:** `/apps/services/satellite-service/src/vra_generator.py`
**Line:** 267

**In-Memory Storage:**

```python
self._prescription_store: Dict[str, PrescriptionMap] = {}
```

**Same as vegetation-analysis-service** - appears to be duplicated code.

**Estimated Migration Time:** 2 days

---

### Low Priority (Legacy / Already Migrated)

#### 10. field-chat

**Location:** `/apps/services/field-chat/src/main.py`
**Lines:** 27-29, 171

**Status:** ✅ Already using database (Tortoise ORM)

- Falls back to in-memory SQLite for testing only
- Connection manager is simple WebSocket state (acceptable in-memory)

**Action Required:** None - already migrated

---

#### 11. provider-config

**Location:** `/apps/services/provider-config/src/main.py`
**Line:** 621

**In-Memory Storage:** Provider configurations

**Business Impact:**

- **LOW:** Configuration lost = manual reconfiguration (rare updates)
- Configuration is typically static and can be version-controlled

**Migration Required:**

- Optional: Create `provider_configs` table for dynamic updates
- Alternative: Keep in environment variables / config files

**Estimated Migration Time:** 1 day (if needed)

---

#### 12. field-ops

**Location:** `/apps/services/field-ops/src/main.py`
**Line:** 156

**Status:** Demo/Development service
**Action Required:** Migrate if promoting to production

---

#### 13. iot-gateway (device registry)

**Location:** `/apps/services/iot-gateway/src/registry.py`
**Line:** 77

**Status:** Has optional persistence layer

- Supports both in-memory and persistent storage
- Acceptable for IoT use case (device state is ephemeral)

**Action Required:** Configure persistent storage if critical

---

## Migration Strategy

### Phase 1: Critical Services (Week 1-2)

1. **billing-core** - 4 days
   - Migrate TENANTS, INVOICES, PAYMENTS, USAGE_RECORDS
   - Load PLANS from database on startup

2. **crop-health-ai** - 3 days
   - Migrate diagnosis history with PostGIS support
   - Implement DiagnosisRepository

3. **notification-service** - 2 days
   - Migrate FARMER_PROFILES
   - Remove legacy NOTIFICATIONS dicts

**Total: 9 days (2 weeks with buffer)**

---

### Phase 2: High Priority Services (Week 3-4)

4. **task-service** - 2 days
5. **alert-service** - 2 days
6. **equipment-service** - 3 days

**Total: 7 days**

---

### Phase 3: Medium Priority Services (Week 5)

7. **inventory-service (settings)** - 1 day
8. **vegetation-analysis-service** - 2 days
9. **satellite-service** - 2 days (or deduplicate with #8)

**Total: 5 days**

---

## Implementation Checklist

For each service migration:

- [ ] 1. Create database schema (DDL scripts)
- [ ] 2. Create Tortoise ORM models
- [ ] 3. Create repository layer (separation of concerns)
- [ ] 4. Add database migrations (Aerich/Alembic)
- [ ] 5. Update service layer to use repository
- [ ] 6. Add database indexes for performance
- [ ] 7. Write migration script for existing data (if any)
- [ ] 8. Update tests to use database
- [ ] 9. Update documentation
- [ ] 10. Deploy with backward compatibility
- [ ] 11. Monitor performance and errors
- [ ] 12. Remove in-memory code after successful deployment

---

## Common PostgreSQL Patterns

### Tortoise ORM Model Example

```python
from tortoise import fields
from tortoise.models import Model

class CropDiagnosis(Model):
    id = fields.UUIDField(pk=True)
    disease_id = fields.CharField(max_length=50)
    disease_name = fields.CharField(max_length=200)
    confidence = fields.DecimalField(max_digits=4, decimal_places=3)
    governorate = fields.CharField(max_length=50, null=True, index=True)
    field_id = fields.CharField(max_length=100, null=True, index=True)
    farmer_id = fields.CharField(max_length=100, null=True, index=True)
    status = fields.CharField(max_length=20, default='pending', index=True)
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "crop_diagnoses"
        indexes = [
            ("governorate", "created_at"),
            ("disease_id", "created_at"),
        ]
```

### Repository Pattern Example

```python
class DiagnosisRepository:
    @staticmethod
    async def create(data: dict) -> CropDiagnosis:
        return await CropDiagnosis.create(**data)

    @staticmethod
    async def get_by_id(diagnosis_id: UUID) -> Optional[CropDiagnosis]:
        return await CropDiagnosis.get_or_none(id=diagnosis_id)

    @staticmethod
    async def get_history(
        governorate: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[CropDiagnosis]:
        query = CropDiagnosis.all()
        if governorate:
            query = query.filter(governorate=governorate)
        return await query.order_by('-created_at').offset(offset).limit(limit)
```

---

## Testing Strategy

### Database Testing

1. Use in-memory SQLite for unit tests (fast)
2. Use PostgreSQL container for integration tests (realistic)
3. Test migrations with production-like data volumes

### Example Test Setup

```python
import pytest
from tortoise.contrib.test import initializer, finalizer

@pytest.fixture(scope="session", autouse=True)
async def initialize_tests():
    # Use in-memory SQLite for fast tests
    await initializer(
        modules={"models": ["app.models"]},
        db_url="sqlite://:memory:",
        app_label="test"
    )
    yield
    await finalizer()
```

---

## Performance Considerations

### Indexing Strategy

1. **Single-column indexes:** For common filters (status, tenant_id, governorate)
2. **Composite indexes:** For multi-field queries (tenant_id, created_at)
3. **Geospatial indexes:** GIST indexes for PostGIS queries
4. **Partial indexes:** For filtered queries (WHERE status = 'pending')

### Partitioning

For high-volume tables (alerts, diagnoses):

```sql
-- Time-based partitioning
CREATE TABLE alerts (
    alert_id UUID,
    created_at TIMESTAMP,
    ...
) PARTITION BY RANGE (created_at);

CREATE TABLE alerts_2025_q1 PARTITION OF alerts
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
```

### Connection Pooling

```python
# In database.py
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.getenv("POSTGRES_HOST"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "user": os.getenv("POSTGRES_USER"),
                "password": os.getenv("POSTGRES_PASSWORD"),
                "database": os.getenv("POSTGRES_DB"),
                "minsize": 10,  # Minimum pool size
                "maxsize": 20,  # Maximum pool size
            }
        }
    },
    "apps": {...}
}
```

---

## Deployment Strategy

### Blue-Green Deployment

1. Deploy new version with database support (writes to both memory + DB)
2. Verify data consistency
3. Switch reads to database
4. Remove in-memory storage in next release

### Backward Compatibility

```python
# Graceful fallback example
async def get_diagnoses(limit: int = 50):
    try:
        # Try database first
        return await DiagnosisRepository.get_history(limit=limit)
    except Exception as e:
        logger.error(f"Database error, falling back to memory: {e}")
        # Fallback to in-memory (temporary)
        return diagnosis_service._history[:limit]
```

---

## Monitoring & Alerts

### Metrics to Track

- Database connection pool usage
- Query execution time (p50, p95, p99)
- Failed database operations
- Migration script duration
- Data consistency checks

### Example Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['table', 'operation']
)

db_errors = Counter(
    'db_errors_total',
    'Database errors',
    ['table', 'operation']
)
```

---

## Rollback Plan

For each service:

1. Keep in-memory storage code (commented) for 1 release cycle
2. Add feature flag: `USE_DATABASE = os.getenv("USE_DATABASE", "true") == "true"`
3. If issues detected, set `USE_DATABASE=false` and redeploy
4. Fix issues and retry migration

---

## Success Criteria

Migration is considered successful when:

- ✅ All data persists across service restarts
- ✅ Can scale to multiple pod instances
- ✅ Query performance meets SLA (p95 < 100ms)
- ✅ Zero data loss during migration
- ✅ Backward compatibility maintained
- ✅ All tests pass with database
- ✅ Documentation updated

---

## Next Steps

1. **Prioritize:** Start with billing-core (CRITICAL for revenue)
2. **Create schemas:** Write DDL scripts for each service
3. **Implement repositories:** Follow the pattern from notification-service
4. **Test thoroughly:** Both unit and integration tests
5. **Deploy incrementally:** One service at a time
6. **Monitor closely:** Track metrics and errors

---

## References

- [Tortoise ORM Documentation](https://tortoise.github.io/)
- [PostgreSQL Performance Tips](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [PostGIS for Geospatial Data](https://postgis.net/)
- SAHOOL notification-service: `/apps/services/notification-service/` (reference implementation)

---

**Document Owner:** Development Team
**Review Frequency:** Weekly during migration phase
**Questions/Issues:** Create issue in project tracker
