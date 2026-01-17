# Event Catalog

> Auto-generated from `shared/contracts/events/registry.json`
> Generated: 2025-12-17 19:55:49

## Overview

Total registered events: **5**

## Event Registry

| Ref                                | Topic                    | Version | Owner       | Breaking Policy |
| ---------------------------------- | ------------------------ | ------: | ----------- | --------------- |
| `events.field.created:v1`          | `field.created`          |       1 | field_suite | new_version     |
| `events.field.updated:v1`          | `field.updated`          |       1 | field_suite | new_version     |
| `events.farm.created:v1`           | `farm.created`           |       1 | field_suite | new_version     |
| `events.crop.planted:v1`           | `crop.planted`           |       1 | field_suite | new_version     |
| `events.advisor.recommendation:v1` | `advisor.recommendation` |       1 | advisor     | new_version     |

## Event Details

### advisor

#### `advisor.recommendation`

- **Schema Ref:** `events.advisor.recommendation:v1`
- **Version:** 1
- **File:** `advisor.recommendation.v1.json`

**AdvisorRecommendationV1**

Event emitted when AI advisor generates a recommendation

**Required Fields:**

- `recommendation_id`
- `tenant_id`
- `recommendation_type`
- `summary`
- `created_at`

**Fields:**

| Field                   | Type               | Description                                   |
| ----------------------- | ------------------ | --------------------------------------------- |
| `recommendation_id` ✓   | string (uuid)      | Unique identifier of the recommendation       |
| `tenant_id` ✓           | string (uuid)      | Tenant that received the recommendation       |
| `field_id`              | string (uuid)      | Optional field the recommendation applies to  |
| `recommendation_type` ✓ | string             | Type of recommendation                        |
| `summary` ✓             | string             | Summary of the recommendation                 |
| `summary_ar`            | string             | Summary in Arabic                             |
| `confidence`            | string             | Confidence level of the recommendation        |
| `actions_count`         | integer            | Number of recommended actions                 |
| `created_at` ✓          | string (date-time) | Timestamp when the recommendation was created |

### field_suite

#### `field.created`

- **Schema Ref:** `events.field.created:v1`
- **Version:** 1
- **File:** `field.created.v1.json`

**FieldCreatedV1**

Event emitted when a new field is created

**Required Fields:**

- `field_id`
- `farm_id`
- `name`
- `geometry_wkt`
- `created_at`

**Fields:**

| Field             | Type               | Description                          |
| ----------------- | ------------------ | ------------------------------------ |
| `field_id` ✓      | string (uuid)      | Unique identifier of the field       |
| `farm_id` ✓       | string (uuid)      | Parent farm identifier               |
| `name` ✓          | string             | Field name                           |
| `name_ar`         | string             | Field name in Arabic                 |
| `geometry_wkt` ✓  | string             | Field boundary in WKT format         |
| `area_hectares`   | number             | Field area in hectares               |
| `soil_type`       | string             | Soil classification                  |
| `irrigation_type` | string             | Irrigation method                    |
| `created_at` ✓    | string (date-time) | Timestamp when the field was created |

#### `field.updated`

- **Schema Ref:** `events.field.updated:v1`
- **Version:** 1
- **File:** `field.updated.v1.json`

**FieldUpdatedV1**

Event emitted when a field is updated

**Required Fields:**

- `field_id`
- `updated_at`
- `changes`

**Fields:**

| Field          | Type               | Description                          |
| -------------- | ------------------ | ------------------------------------ |
| `field_id` ✓   | string (uuid)      | Unique identifier of the field       |
| `updated_at` ✓ | string (date-time) | Timestamp when the field was updated |
| `changes` ✓    | object             | Changed fields                       |

#### `farm.created`

- **Schema Ref:** `events.farm.created:v1`
- **Version:** 1
- **File:** `farm.created.v1.json`

**FarmCreatedV1**

Event emitted when a new farm is created

**Required Fields:**

- `farm_id`
- `tenant_id`
- `name`
- `location`
- `created_at`

**Fields:**

| Field                 | Type               | Description                         |
| --------------------- | ------------------ | ----------------------------------- |
| `farm_id` ✓           | string (uuid)      | Unique identifier of the farm       |
| `tenant_id` ✓         | string (uuid)      | Tenant that owns the farm           |
| `name` ✓              | string             | Farm name                           |
| `name_ar`             | string             | Farm name in Arabic                 |
| `location` ✓          | object             |                                     |
| `total_area_hectares` | number             | Total farm area in hectares         |
| `owner_id`            | string (uuid)      | User ID of the farm owner           |
| `created_at` ✓        | string (date-time) | Timestamp when the farm was created |

#### `crop.planted`

- **Schema Ref:** `events.crop.planted:v1`
- **Version:** 1
- **File:** `crop.planted.v1.json`

**CropPlantedV1**

Event emitted when a crop is planted in a field

**Required Fields:**

- `crop_id`
- `field_id`
- `crop_type`
- `planting_date`
- `created_at`

**Fields:**

| Field                   | Type               | Description                                |
| ----------------------- | ------------------ | ------------------------------------------ |
| `crop_id` ✓             | string (uuid)      | Unique identifier of the crop              |
| `field_id` ✓            | string (uuid)      | Field where the crop is planted            |
| `crop_type` ✓           | string             | Type of crop (wheat, barley, coffee, etc.) |
| `variety`               | string             | Crop variety                               |
| `variety_ar`            | string             | Crop variety in Arabic                     |
| `planting_date` ✓       | string (date)      | Date when the crop was planted             |
| `expected_harvest_date` | string (date)      | Expected harvest date                      |
| `created_at` ✓          | string (date-time) | Timestamp when the event was created       |

---

## Usage

### Producing Events

```python
from shared.libs.events.producer import enqueue_event

enqueue_event(
    db=session,
    event_type='field.created',
    schema_ref='events.field.created:v1',
    tenant_id=tenant_id,
    correlation_id=correlation_id,
    producer='field_suite',
    payload={
        'field_id': str(field.id),
        'farm_id': str(field.farm_id),
        'name': field.name,
        'geometry_wkt': field.boundary_wkt,
        'created_at': field.created_at.isoformat(),
    },
)
```

### Validating Payloads

```python
from shared.libs.events.schema_registry import SchemaRegistry

registry = SchemaRegistry.load()
registry.validate('events.field.created:v1', payload)
```
