# Input Application Tracking System

## Overview

The Input Application Tracking system links inventory management with field operations, providing comprehensive tracking of all inputs (fertilizers, pesticides, herbicides, etc.) applied to fields. This enables:

- **Inventory Integration**: Automatic deduction from inventory using FIFO batch tracking
- **Safety Compliance**: Withholding period tracking for pesticides
- **Cost Management**: Track and analyze input costs per field/crop season
- **Efficacy Monitoring**: Rate the effectiveness of applications
- **Regulatory Compliance**: Maintain detailed records for audits
- **Decision Support**: Generate application plans and analyze historical data

## Key Features

### 1. Automatic Inventory Deduction
- Records application and deducts quantity from inventory
- Uses FIFO (First In, First Out) for batch consumption
- Creates stock movement audit trail
- Tracks which batch/lot was used

### 2. Withholding Period Tracking
- Calculates safe harvest date based on pesticide application
- Checks if harvest is safe on a given date
- Tracks blocking applications preventing harvest
- Default withholding periods by category:
  - Pesticides: 14 days
  - Herbicides: 7 days
  - Fungicides: 10 days
  - Fertilizers: 0 days

### 3. Application Rate Calculation
- Automatically calculates rate per hectare
- Tracks area covered
- Enables rate comparison across applications

### 4. Weather Condition Logging
- Records temperature, humidity, wind speed
- Useful for efficacy analysis
- Supports post-application evaluation

### 5. Safety & PPE Tracking
- Records Personal Protective Equipment used
- Tracks operator/applicator
- Equipment used for application

### 6. Cost Tracking
- Records unit cost and total cost per application
- Aggregates costs by category, purpose, method
- Cost per hectare analysis

### 7. Efficacy Rating
- Rate effectiveness (1-5 scale)
- Track target pest/disease
- Historical efficacy analysis

## Data Models

### InputApplication

Tracks each individual application of an input to a field.

```python
{
  "id": "uuid",
  "field_id": "field-123",
  "crop_season_id": "season-2024-wheat",
  "item_id": "item-npk-fertilizer",
  "batch_lot_id": "batch-001",  // Auto-assigned via FIFO

  // Application details
  "application_date": "2024-03-15T08:30:00Z",
  "method": "broadcast",  // See ApplicationMethod enum
  "purpose": "basal",     // See ApplicationPurpose enum
  "quantity_applied": 50.0,
  "unit": "KG",
  "area_covered_ha": 2.5,
  "rate_per_ha": 20.0,    // Auto-calculated

  // Weather conditions
  "temperature": 28.5,
  "humidity": 65.0,
  "wind_speed": 5.2,
  "growth_stage": "planting",

  // Operator
  "applied_by": "farmer-001",
  "equipment_used": "broadcast spreader",

  // Safety
  "withholding_period_days": 0,
  "safe_harvest_date": null,
  "ppe_used": ["gloves", "mask"],

  // Cost
  "unit_cost": 2.5,
  "total_cost": 125.0,

  // Efficacy
  "target_pest_disease": null,
  "efficacy_rating": null,
  "notes": "Applied NPK at planting"
}
```

### ApplicationPlan

Generates recommended application schedule for a crop season.

```python
{
  "id": "uuid",
  "field_id": "field-123",
  "crop_season_id": "season-2024-wheat",
  "crop_type": "wheat",

  "planned_applications": [
    {
      "stage": "basal",
      "days_after_planting": 0,
      "purpose": "BASAL",
      "notes": "NPK at planting"
    },
    {
      "stage": "tillering",
      "days_after_planting": 30,
      "purpose": "TOP_DRESSING",
      "notes": "Nitrogen boost"
    }
  ],

  "total_fertilizer_kg": 150.0,
  "total_pesticide_l": 5.0,
  "estimated_cost": 1250.0,
  "status": "DRAFT"
}
```

## Enums

### ApplicationMethod

How the input is applied:

- `BROADCAST`: Even spreading across entire field
- `BAND`: Applied in rows or bands
- `FOLIAR`: Sprayed on leaves
- `DRIP`: Through irrigation system
- `SOIL_INJECTION`: Injected into soil
- `SEED_TREATMENT`: Applied to seeds before planting
- `AERIAL`: Applied via drone or aircraft

### ApplicationPurpose

Why the input is being applied:

- `BASAL`: At planting time
- `TOP_DRESSING`: During crop growth
- `PEST_CONTROL`: For pest management
- `DISEASE_CONTROL`: For disease management
- `WEED_CONTROL`: For weed management
- `GROWTH_REGULATION`: Growth regulators
- `NUTRIENT_DEFICIENCY`: Correcting nutrient deficiency

## API Endpoints

### Applications

```
POST   /v1/applications
```
Record a new input application. Automatically deducts from inventory and creates stock movement.

**Request Body:**
```json
{
  "field_id": "field-123",
  "crop_season_id": "season-2024-wheat",
  "item_id": "item-npk-fertilizer",
  "quantity": 50.0,
  "method": "broadcast",
  "purpose": "basal",
  "applied_by": "farmer-001",
  "area_ha": 2.5,
  "temperature": 28.5,
  "humidity": 65.0,
  "wind_speed": 5.2,
  "growth_stage": "planting",
  "equipment_used": "broadcast spreader",
  "ppe_used": ["gloves", "mask"],
  "notes": "Applied NPK at planting"
}
```

**Response:**
```json
{
  "success": true,
  "application": { /* full application object */ },
  "message": "Application recorded successfully"
}
```

---

```
GET    /v1/applications/field/{fieldId}
```
Get all applications for a field.

**Query Parameters:**
- `crop_season_id` (optional): Filter by crop season
- `category` (optional): Filter by item category (FERTILIZER, PESTICIDE, etc.)
- `start_date` (optional): Filter by date range
- `end_date` (optional): Filter by date range

---

```
GET    /v1/applications/field/{fieldId}/summary
```
Get comprehensive summary of all inputs applied to a crop season.

**Required Query Params:** `crop_season_id`

**Response:**
```json
{
  "success": true,
  "summary": {
    "field_id": "field-123",
    "crop_season_id": "season-2024-wheat",
    "total_applications": 5,
    "total_cost": 1500.0,
    "by_category": {
      "FERTILIZER": {
        "count": 3,
        "total_quantity": 140.0,
        "total_cost": 1200.0
      },
      "PESTICIDE": {
        "count": 2,
        "total_quantity": 5.0,
        "total_cost": 300.0
      }
    },
    "by_purpose": {
      "basal": { "count": 1, "total_cost": 500.0 },
      "top_dressing": { "count": 2, "total_cost": 700.0 },
      "pest_control": { "count": 2, "total_cost": 300.0 }
    },
    "fertilizer_details": {
      "total_kg": 140.0,
      "by_type": {
        "NPK 20-20-20": 50.0,
        "Urea": 60.0,
        "Potassium Sulfate": 30.0
      }
    },
    "pesticide_details": {
      "total_l": 5.0,
      "by_type": {
        "Malathion": 5.0
      }
    },
    "timeline": [ /* chronological list of applications */ ]
  }
}
```

---

```
GET    /v1/applications/{applicationId}
```
Get a single application by ID.

### Planning

```
POST   /v1/applications/plan
```
Generate an application plan for a crop season.

**Request Body:**
```json
{
  "field_id": "field-123",
  "crop_season_id": "season-2024-wheat",
  "crop_type": "wheat",
  "custom_applications": [  // Optional
    {
      "stage": "basal",
      "days_after_planting": 0,
      "purpose": "BASAL",
      "item_id": "item-npk",
      "quantity": 50.0,
      "notes": "NPK at planting"
    }
  ]
}
```

---

```
GET    /v1/applications/plan/{fieldId}
```
Get application plans for a field.

**Query Parameters:**
- `crop_season_id` (optional): Filter by crop season

### Safety & Compliance

```
GET    /v1/applications/field/{fieldId}/withholding-check
```
Check if harvest is safe based on pesticide withholding periods.

**Required Query Params:** `crop_season_id`
**Optional Query Params:** `harvest_date` (defaults to today)

**Response:**
```json
{
  "success": true,
  "is_safe": false,
  "days_remaining": 7,
  "blocking_applications": [
    {
      "application_id": "app-123",
      "application_date": "2024-06-01T08:00:00Z",
      "item_name": "Malathion",
      "safe_harvest_date": "2024-06-15",
      "days_remaining": 7
    }
  ],
  "earliest_safe_date": "2024-06-15"
}
```

---

```
GET    /v1/applications/field/{fieldId}/safe-harvest-date
```
Get the earliest safe harvest date for a field.

**Required Query Params:** `crop_season_id`

### Cost Tracking

```
GET    /v1/applications/field/{fieldId}/costs
```
Calculate total input costs for a crop season.

**Required Query Params:** `crop_season_id`

**Response:**
```json
{
  "success": true,
  "field_id": "field-123",
  "crop_season_id": "season-2024-wheat",
  "total_cost": 1500.0,
  "by_category": {
    "FERTILIZER": {
      "count": 3,
      "total_quantity": 140.0,
      "total_cost": 1200.0
    }
  },
  "cost_per_application": 300.0
}
```

### Enums Reference

```
GET    /v1/enums/application-methods
GET    /v1/enums/application-purposes
```
Get available enum values with descriptions.

## Usage Examples

### Example 1: Record Fertilizer Application

```bash
curl -X POST http://localhost:8095/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-123",
    "crop_season_id": "season-2024-wheat",
    "item_id": "item-npk-20-20-20",
    "quantity": 50.0,
    "method": "broadcast",
    "purpose": "basal",
    "applied_by": "farmer-ali",
    "area_ha": 2.5,
    "growth_stage": "planting",
    "notes": "NPK at planting"
  }'
```

### Example 2: Record Pesticide Application with Withholding Period

```bash
curl -X POST http://localhost:8095/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-123",
    "crop_season_id": "season-2024-wheat",
    "item_id": "item-malathion",
    "quantity": 2.5,
    "method": "foliar",
    "purpose": "pest_control",
    "applied_by": "farmer-ali",
    "area_ha": 2.5,
    "temperature": 26.0,
    "humidity": 70.0,
    "equipment_used": "backpack sprayer",
    "ppe_used": ["protective suit", "gloves", "mask", "goggles"],
    "withholding_period_days": 14,
    "target_pest_disease": "aphids",
    "efficacy_rating": 4
  }'
```

### Example 3: Check if Safe to Harvest

```bash
curl "http://localhost:8095/v1/applications/field/field-123/withholding-check?crop_season_id=season-2024-wheat&harvest_date=2024-06-15"
```

### Example 4: Get Application Summary

```bash
curl "http://localhost:8095/v1/applications/field/field-123/summary?crop_season_id=season-2024-wheat"
```

## Integration with Other Services

### Field Service
- Link applications to specific fields
- Use field boundaries for area calculation
- Track applications across multiple crop seasons

### Agro Advisor Service
- Generate recommendations based on application history
- Analyze efficacy of different application methods
- Suggest optimal timing for applications

### Weather Service
- Validate weather conditions at application time
- Alert on unsuitable conditions (high wind, rain)
- Historical weather correlation with efficacy

### Task Service
- Create tasks for planned applications
- Schedule reminders for withholding period expiry
- Track completion status

## Best Practices

### 1. Recording Applications
- Record applications as soon as possible after completion
- Include accurate weather conditions
- Always specify PPE used for safety tracking
- Rate efficacy after observing results

### 2. Withholding Periods
- Always check withholding periods before harvest
- Set conservative withholding periods when uncertain
- Consider extending periods for export crops

### 3. Cost Tracking
- Ensure inventory items have accurate unit costs
- Review cost summaries to optimize input expenses
- Compare costs across seasons and fields

### 4. Application Planning
- Create plans at season start
- Update based on soil tests and plant analysis
- Review and adjust based on weather and crop performance

### 5. Inventory Management
- Maintain sufficient stock levels
- Track batch/lot numbers for traceability
- Monitor expiry dates for pesticides

## Database Schema

The application tracking uses the following Prisma models:

```prisma
model InputApplication {
  id              String   @id @default(uuid())
  fieldId         String
  cropSeasonId    String
  itemId          String
  batchLotId      String?

  applicationDate DateTime
  method          ApplicationMethod
  purpose         ApplicationPurpose
  quantityApplied Float
  unit            String
  areaCoveredHa   Float
  ratePerHa       Float

  temperature     Float?
  humidity        Float?
  windSpeed       Float?
  growthStage     String?

  appliedBy       String
  equipmentUsed   String?

  withholdingDays Int?
  safeHarvestDate DateTime?
  ppeUsed         String[]

  unitCost        Float?
  totalCost       Float?

  targetPest      String?
  efficacyRating  Int?
  notes           String?

  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  @@map("input_applications")
  @@index([fieldId, cropSeasonId])
  @@index([itemId])
  @@index([applicationDate])
}

model ApplicationPlan {
  id                  String   @id @default(uuid())
  fieldId             String
  cropSeasonId        String
  cropType            String

  plannedApplications Json
  totalFertilizerKg   Float    @default(0)
  totalPesticideL     Float    @default(0)
  estimatedCost       Float    @default(0)

  status              PlanStatus @default(DRAFT)
  approvedBy          String?
  approvedAt          DateTime?

  createdAt           DateTime @default(now())
  updatedAt           DateTime @updatedAt

  @@map("application_plans")
  @@index([fieldId, cropSeasonId])
}

enum ApplicationMethod {
  BROADCAST
  BAND
  FOLIAR
  DRIP
  SOIL_INJECTION
  SEED_TREATMENT
  AERIAL
}

enum ApplicationPurpose {
  BASAL
  TOP_DRESSING
  PEST_CONTROL
  DISEASE_CONTROL
  WEED_CONTROL
  GROWTH_REGULATION
  NUTRIENT_DEFICIENCY
}

enum PlanStatus {
  DRAFT
  APPROVED
  IN_PROGRESS
  COMPLETED
  CANCELLED
}
```

## Testing

Use the provided `test_application_tracker.http` file with REST Client or similar tools to test all endpoints.

### Prerequisites
1. Start the inventory service: `docker-compose up inventory-service`
2. Ensure database is migrated: `prisma migrate dev`
3. Create some inventory items for testing

### Running Tests
Open `test_application_tracker.http` in VS Code with REST Client extension and execute requests sequentially.

## Troubleshooting

### Issue: "Insufficient stock" error
- Check available quantity in inventory: `GET /v1/inventory/items/{itemId}`
- Verify quantity is not reserved
- Add stock if needed: `POST /v1/inventory/stock/in`

### Issue: "Item not found" error
- Verify item_id is correct
- Check item exists in inventory
- Ensure item is not deleted

### Issue: Withholding period not calculated
- Set `withholding_period_days` explicitly if not using default
- Check item category is correct (PESTICIDE, HERBICIDE, etc.)
- Verify safe_harvest_date is calculated in response

### Issue: Application not deducting from inventory
- Check stock movement was created: `GET /v1/inventory/movements?item_id={itemId}`
- Verify application was recorded successfully
- Check batch/lot tracking is working

## Future Enhancements

- [ ] Integration with mobile apps for field recording
- [ ] Photo/image upload for application evidence
- [ ] GPS tracking of application area
- [ ] Weather API integration for automatic condition recording
- [ ] ML-based efficacy prediction
- [ ] Regulatory report generation (GAP compliance)
- [ ] Multi-language support for notes
- [ ] Voice notes for field recording
- [ ] Integration with equipment IoT sensors
- [ ] Automatic reorder suggestions based on application plans
