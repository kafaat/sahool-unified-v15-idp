# Prisma Model Ownership & Schema Management
# إدارة ملكية نماذج Prisma والمخططات

**Generated**: 2026-02-04  
**Version**: 1.0  
**Status**: Documentation

## Overview | نظرة عامة

This document defines the ownership and responsibility for Prisma data models across the SAHOOL microservices architecture. It addresses the issue of duplicate model definitions and establishes clear boundaries for each service.

توثق هذه الوثيقة ملكية والمسؤولية عن نماذج بيانات Prisma عبر بنية الخدمات المصغرة لمنصة سهول. تعالج مشكلة تعريفات النماذج المكررة وتحدد حدودًا واضحة لكل خدمة.

---

## Prisma Services (10 Total)

1. **iot-service** - IoT Device Management
2. **disaster-assessment** - Disaster Risk Assessment  
3. **research-core** - Agricultural Research Trials
4. **chat-service** - Messaging & Chat
5. **inventory-service** - Equipment & Product Inventory
6. **user-service** - User Management & Authentication
7. **community-chat** - Community Discussions
8. **field-management-service** - Field & Farm Management
9. **weather-service** - Weather Data & Forecasts
10. **marketplace-service** - Agricultural Marketplace

---

## Model Ownership Matrix | مصفوفة ملكية النماذج

### Core Principles | المبادئ الأساسية

1. **Single Source of Truth**: Each model has ONE authoritative service
2. **Bounded Contexts**: Services own their domain models
3. **Table Mapping**: Use `@@map()` to ensure unique table names
4. **Cross-Service References**: Use IDs, not foreign keys
5. **Data Duplication**: Acceptable for microservices autonomy

---

### Service-Specific Models

#### 1. iot-service (6 models)
**Domain**: IoT devices, sensors, actuators

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Device | `iot_devices` | IoT device registry | ✅ Owner |
| Sensor | `iot_sensors` | Sensor configurations | ✅ Owner |
| SensorReading | `iot_sensor_readings` | Sensor data points | ✅ Owner |
| Actuator | `iot_actuators` | Actuator configurations | ✅ Owner |
| ActuatorCommand | `iot_actuator_commands` | Actuator control commands | ✅ Owner |
| DeviceAlert | `iot_device_alerts` | Device-specific alerts | ✅ Owner |

**Recommendation**: 
```prisma
model Device {
  // ...
  @@map("iot_devices")
}
```

---

#### 2. disaster-assessment (4 models)
**Domain**: Natural disaster risk assessment

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Assessment | `disaster_assessments` | Risk assessments | ✅ Owner |
| RiskFactor | `disaster_risk_factors` | Risk factor definitions | ✅ Owner |
| Mitigation | `disaster_mitigations` | Mitigation strategies | ✅ Owner |
| HistoricalEvent | `disaster_historical_events` | Past disaster records | ✅ Owner |

---

#### 3. research-core (12 models)
**Domain**: Agricultural research & experimentation

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Experiment | `research_experiments` | Research experiments | ✅ Owner |
| ResearchPlot | `research_plots` | Experimental field plots | ✅ Owner |
| Treatment | `research_treatments` | Experimental treatments | ✅ Owner |
| Planting | `research_plantings` | Planting records | ✅ Owner |
| ResearchProtocol | `research_protocols` | Research protocols | ✅ Owner |
| Germplasm | `research_germplasm` | Seed/genetic material | ✅ Owner |
| SeedLot | `research_seed_lots` | Seed lot tracking | ✅ Owner |
| LabSample | `research_lab_samples` | Laboratory samples | ✅ Owner |
| ResearchDailyLog | `research_daily_logs` | Daily observations | ✅ Owner |
| ExperimentCollaborator | `research_collaborators` | Research team members | ✅ Owner |
| ExperimentAuditLog | `research_audit_logs` | Experiment audit trail | ✅ Owner |
| NdviReading | `research_ndvi_readings` | NDVI measurements | ⚠️ Shared with field-management |

**Note**: `NdviReading` appears in both research-core and field-management. Consider:
- Research: `research_ndvi_readings` (experimental plots)
- Field Management: `field_ndvi_readings` (production fields)

---

#### 4. chat-service (3 models)
**Domain**: Real-time messaging

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Conversation | `chat_conversations` | Chat conversations | ✅ Owner |
| Message | `chat_messages` | Chat messages | ✅ Owner |
| Participant | `chat_participants` | Conversation participants | ✅ Owner |

---

#### 5. inventory-service (8 models)
**Domain**: Equipment & product inventory management

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| InventoryItem | `inventory_items` | Inventory items | ✅ Owner |
| StorageLocation | `inventory_storage_locations` | Warehouse locations | ✅ Owner |
| Warehouse | `inventory_warehouses` | Warehouse facilities | ✅ Owner |
| InventoryMovement | `inventory_movements` | Stock movements | ✅ Owner |
| StockTransfer | `inventory_stock_transfers` | Inter-warehouse transfers | ✅ Owner |
| InventoryAlert | `inventory_alerts` | Stock alerts (low stock, etc.) | ✅ Owner |
| Product | `inventory_products` | Product catalog | ⚠️ Shared with marketplace |
| SyncStatus | `inventory_sync_status` | Offline sync tracking | ✅ Owner |

**Note**: `Product` conflict with marketplace-service. Recommendation:
- Inventory: `inventory_products` (warehouse stock)
- Marketplace: `marketplace_products` (customer-facing catalog)

---

#### 6. user-service (5 models)
**Domain**: User authentication & management

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| User | `users` | User accounts | ✅ Owner |
| Role | `user_roles` | User roles | ✅ Owner |
| Permission | `user_permissions` | Permissions | ✅ Owner |
| Session | `user_sessions` | Active sessions | ✅ Owner |
| TwoFactorAuth | `user_2fa` | 2FA settings | ✅ Owner |

---

#### 7. community-chat (3 models)
**Domain**: Community forums & discussions

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Topic | `community_topics` | Discussion topics | ✅ Owner |
| Post | `community_posts` | Forum posts | ✅ Owner |
| Comment | `community_comments` | Post comments | ✅ Owner |

---

#### 8. field-management-service (6 models)
**Domain**: Farm & field operations management

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Field | `fields` | Agricultural fields | ✅ Owner |
| Zone | `field_zones` | Field sub-zones | ✅ Owner |
| FieldBoundaryHistory | `field_boundary_history` | Boundary change tracking | ✅ Owner |
| Task | `field_tasks` | Field operations tasks | ⚠️ Shared with research-core |
| LocationConfig | `field_location_configs` | GPS/location settings | ✅ Owner |
| AlertSettings | `field_alert_settings` | Field-specific alert rules | ✅ Owner |

**Note**: `Task` conflict. Recommendation:
- Field Management: `field_tasks` (operational tasks)
- Research: `research_tasks` (research activities)

---

#### 9. weather-service (4 models)
**Domain**: Weather data & forecasting

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| WeatherObservation | `weather_observations` | Historical weather data | ✅ Owner |
| WeatherForecast | `weather_forecasts` | Weather predictions | ✅ Owner |
| WeatherAlert | `weather_alerts` | Weather warnings | ✅ Owner |
| WeatherStation | `weather_stations` | Weather station registry | ✅ Owner |

---

#### 10. marketplace-service (14 models)
**Domain**: Agricultural e-commerce marketplace

| Model | Table Name | Description | Status |
|-------|------------|-------------|--------|
| Product | `marketplace_products` | Product listings | ⚠️ Shared with inventory |
| Order | `marketplace_orders` | Customer orders | ✅ Owner |
| OrderItem | `marketplace_order_items` | Order line items | ✅ Owner |
| Transaction | `marketplace_transactions` | Payment transactions | ⚠️ Shared with inventory |
| BuyerProfile | `marketplace_buyer_profiles` | Buyer accounts | ✅ Owner |
| SellerProfile | `marketplace_seller_profiles` | Seller accounts | ✅ Owner |
| ProductReview | `marketplace_product_reviews` | Product reviews | ✅ Owner |
| ReviewResponse | `marketplace_review_responses` | Seller responses | ✅ Owner |
| Escrow | `marketplace_escrow` | Escrow payments | ✅ Owner |
| Wallet | `marketplace_wallets` | User wallet balances | ⚠️ Shared with billing |
| WalletAuditLog | `marketplace_wallet_audit_logs` | Wallet transaction logs | ✅ Owner |
| CreditEvent | `marketplace_credit_events` | Credit/debit events | ✅ Owner |
| Loan | `marketplace_loans` | Agricultural loans | ✅ Owner |
| ScheduledPayment | `marketplace_scheduled_payments` | Payment schedules | ✅ Owner |
| DigitalSignature | `marketplace_digital_signatures` | Contract signatures | ✅ Owner |

---

## Duplicate Model Resolution Strategy

### High-Priority Conflicts (Require Immediate Action)

| Model Name | Services | Recommendation |
|------------|----------|----------------|
| Device | iot-service, field-management, inventory | `iot_devices`, `field_devices`, `inventory_devices` |
| Field | field-management, research-core, disaster | `fields` (field-mgmt owner), others use field_id reference |
| Product | marketplace, inventory | `marketplace_products`, `inventory_products` |
| Transaction | marketplace, inventory, disaster | `marketplace_transactions`, `inventory_transactions` |
| Order | marketplace, inventory | `marketplace_orders`, `inventory_orders` |
| Task | field-management, research-core | `field_tasks`, `research_tasks` |
| Sensor | iot-service, field-management | `iot_sensors` (iot owner), field-mgmt references |
| Wallet | marketplace, billing-core | `marketplace_wallets`, `billing_wallets` |
| NdviReading | research-core, field-management | `research_ndvi_readings`, `field_ndvi_readings` |
| Zone | field-management, disaster-assessment | `field_zones`, `disaster_zones` |

### Medium-Priority Conflicts (Document & Monitor)

| Model Name | Services | Status |
|------------|----------|--------|
| Conversation | chat-service, community-chat | Different contexts, acceptable |
| Message | chat-service, community-chat | Different contexts, acceptable |
| Participant | chat-service, community-chat | Different contexts, acceptable |
| AlertSettings | field-management, iot-service | Different contexts, acceptable |

---

## Implementation Guidelines

### 1. Use @@map() Directive

**Before** (causes conflict):
```prisma
model Device {
  id String @id @default(uuid())
  name String
  // ...
}
```

**After** (prevents conflict):
```prisma
model Device {
  id String @id @default(uuid())
  name String
  // ...
  
  @@map("iot_devices")  // Unique table name
}
```

### 2. Schema Namespacing

Use service prefixes for all tables:

```prisma
// iot-service
model Device {
  @@map("iot_devices")
}

// field-management-service
model Device {
  @@map("field_devices")
}
```

### 3. Cross-Service References

Use foreign key IDs, not actual foreign keys:

```prisma
// marketplace-service
model Order {
  id String @id
  fieldId String  // Reference to field-management.Field
  // NO foreign key constraint across services
}
```

### 4. Migration Script Template

```bash
# For each service with conflicts
cd apps/services/[service-name]

# Update schema.prisma with @@map() directives
# Then create migration

npx prisma migrate dev --name add_table_mapping
npx prisma generate
```

---

## Validation Checklist

- [ ] All Prisma services have unique table names via `@@map()`
- [ ] No foreign keys across service boundaries
- [ ] Service ownership documented for each model
- [ ] Migration plan created for conflicting models
- [ ] Integration tests verify data isolation
- [ ] API documentation reflects service boundaries

---

## Monitoring & Compliance

### Automated Checks

```bash
# Check for duplicate table names
for schema in $(find apps/services -name "schema.prisma"); do
  service=$(echo $schema | cut -d'/' -f3)
  grep "@@map(" $schema || echo "⚠️ $service: No table mapping found"
done

# Validate unique table names across all services
find apps/services -name "schema.prisma" -exec grep "@@map(" {} \; | sort | uniq -d
```

### Pre-Deployment Validation

```yaml
# .github/workflows/prisma-validation.yml
name: Prisma Schema Validation
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for duplicate table names
        run: |
          ./scripts/validate-prisma-schemas.sh
```

---

## Migration Timeline

### Phase 1: Documentation (Week 1)
- [x] Document all Prisma models and ownership
- [x] Identify all conflicts
- [ ] Create migration plan per service

### Phase 2: Schema Updates (Week 2-3)
- [ ] Add `@@map()` directives to all schemas
- [ ] Test migrations in development
- [ ] Update service tests

### Phase 3: Deployment (Week 4)
- [ ] Deploy schema updates service-by-service
- [ ] Monitor for issues
- [ ] Update API documentation

### Phase 4: Validation (Week 5)
- [ ] Run integration tests
- [ ] Verify data isolation
- [ ] Performance testing

---

## References

- [Prisma Schema Reference](https://www.prisma.io/docs/reference/api-reference/prisma-schema-reference)
- [Microservices Data Patterns](https://microservices.io/patterns/data/database-per-service.html)
- [Bounded Context (DDD)](https://martinfowler.com/bliki/BoundedContext.html)
- [SAHOOL Governance Registry](./governance/services.yaml)

---

**Document Maintainers**:
- Database Team
- Service Owners
- Architecture Team

**Review Frequency**: Monthly

**Last Updated**: 2026-02-04
