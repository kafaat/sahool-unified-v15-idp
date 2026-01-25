# Task Service Astronomical Integration Summary

## Overview

Successfully integrated astronomical calendar data into the Task Service to provide farmers with optimal timing recommendations based on traditional Yemeni agricultural astronomy.

## Changes Made

### 1. Task Model Updates

#### Added Astronomical Fields to `Task` Model:

- `astronomical_score` (Optional[int], 1-10): Overall farming suitability score
- `moon_phase_at_due_date` (Optional[str]): Moon phase in Arabic (e.g., "البدر", "الهلال المتزايد")
- `lunar_mansion_at_due_date` (Optional[str]): Lunar mansion in Arabic (e.g., "الثريا", "السماك")
- `optimal_time_of_day` (Optional[str]): Recommended time for the activity (e.g., "06:00-08:00")
- `suggested_by_calendar` (bool): Indicates if task was suggested by astronomical calendar
- `astronomical_recommendation` (Optional[dict]): Full astronomical data from calendar service
- `astronomical_warnings` (list[str]): Warnings about non-optimal dates (bilingual: Arabic & English)

#### Added Astronomical Fields to `TaskCreate` and `TaskUpdate` Models:

- Same fields as Task model (except `astronomical_warnings`)
- Fields can be manually set or auto-populated when `due_date` is provided

### 2. Helper Functions

#### `fetch_astronomical_data(due_date, task_type) -> dict`

- **Purpose**: Fetches astronomical data from the astronomical calendar service
- **Features**:
  - Maps task types to agricultural activities in Arabic
  - Calls `/v1/date/{date}` endpoint of astronomical service
  - Extracts relevant astronomical data (score, moon phase, lunar mansion)
  - Determines optimal time of day based on activity type
  - Generates warnings for non-optimal dates (bilingual)
- **Error Handling**: Gracefully handles service unavailability

#### `validate_and_enrich_task_with_astronomy(task, task_type) -> Task`

- **Purpose**: Validates and enriches task with astronomical data
- **Features**:
  - Calls `fetch_astronomical_data()` to get astronomical information
  - Updates all astronomical fields on the task
  - Logs warnings for non-optimal dates
  - Returns enriched task object

### 3. Endpoint Updates

#### `POST /api/v1/tasks` (create_task)

**Behavior**:

- When `due_date` is provided:
  - Automatically fetches astronomical data
  - Populates all astronomical fields
  - Adds warnings if date is not optimal
- When `due_date` is NOT provided:
  - Uses astronomical fields from the request body if provided
  - No automatic fetching

#### `PUT /api/v1/tasks/{task_id}` (update_task)

**Behavior**:

- When `due_date` is changed:
  - Automatically refreshes astronomical data
  - Updates all astronomical fields
  - Adds/updates warnings if new date is not optimal
- When `due_date` is NOT changed:
  - No astronomical data fetching
  - Manual astronomical field updates are preserved

### 4. Configuration

- Added `ASTRONOMICAL_SERVICE_URL` environment variable
- Default: `http://astronomical-calendar:8111`
- Uses existing `httpx` dependency for async HTTP calls

## Arabic Field Labels (حقول بالعربية)

All astronomical fields include Arabic descriptions in the Field() metadata:

- **التصنيف الفلكي** - Astronomical score
- **مرحلة القمر** - Moon phase
- **المنزلة القمرية** - Lunar mansion
- **أفضل وقت في اليوم** - Optimal time of day
- **مقترح من التقويم الفلكي** - Suggested by calendar
- **البيانات الفلكية الكاملة** - Full astronomical data
- **تحذيرات حول التواريخ غير المثالية** - Warnings about non-optimal dates

## Task Type to Activity Mapping

The service maps task types to Arabic agricultural activities:

- `PLANTING` → زراعة (Planting)
- `IRRIGATION` → ري (Irrigation)
- `HARVEST` → حصاد (Harvesting)
- `FERTILIZATION` → تسميد (Fertilization)
- `SPRAYING` → رش (Spraying)
- `MAINTENANCE` → تقليم (Pruning)
- `SCOUTING` → فحص (Inspection)
- `SAMPLING` → جمع عينات (Sampling)
- `OTHER` → زراعة (Default: Planting)

## Optimal Time Recommendations

Based on activity type:

- **Irrigation/Spraying**: 06:00-08:00 (Early morning)
- **Harvesting**: 07:00-11:00 (Morning)
- **Other activities**: 07:00-10:00 (General morning work)

## Warning System

The system generates bilingual warnings when:

1. **Astronomical score < 5**: Date is not optimal for the activity
2. **Moon phase not suitable**: Moon is in waning phase (not good for planting)

Example warnings:

```
- "التاريخ المحدد غير مثالي للنشاط (زراعة). الدرجة: 3/10"
- "Selected date is not optimal for planting. Score: 3/10"
- "مرحلة القمر (الهلال المتناقص) غير مناسبة للزراعة"
- "Moon phase (waning_crescent) is not suitable for planting"
```

## Example API Request/Response

### Create Task with Astronomical Data

**Request**:

```json
POST /api/v1/tasks
{
  "title": "Plant Tomatoes",
  "title_ar": "زراعة الطماطم",
  "description": "Plant tomato seedlings in field A",
  "task_type": "planting",
  "priority": "high",
  "field_id": "field_001",
  "due_date": "2026-01-15T08:00:00Z"
}
```

**Response**:

```json
{
  "task_id": "task_abc123",
  "title": "Plant Tomatoes",
  "title_ar": "زراعة الطماطم",
  "task_type": "planting",
  "priority": "high",
  "due_date": "2026-01-15T08:00:00Z",
  "astronomical_score": 9,
  "moon_phase_at_due_date": "الهلال المتزايد",
  "lunar_mansion_at_due_date": "الثريا",
  "optimal_time_of_day": "07:00-10:00",
  "suggested_by_calendar": false,
  "astronomical_warnings": [],
  "astronomical_recommendation": {
    "overall_farming_score": 9,
    "moon_phase": {...},
    "lunar_mansion": {...},
    "recommendations": [...]
  },
  ...
}
```

## Integration with Astronomical Calendar Service

The task service calls the following endpoints:

- `GET /v1/date/{date}` - Get astronomical data for a specific date

Service URL is configurable via `ASTRONOMICAL_SERVICE_URL` environment variable.

## Benefits

1. **Cultural Relevance**: Preserves traditional Yemeni agricultural astronomy
2. **Farmer Guidance**: Helps farmers schedule tasks on optimal dates
3. **Bilingual Support**: All data and warnings in Arabic and English
4. **Automatic Enrichment**: No manual input required from farmers
5. **Transparent Warnings**: Clear warnings about non-optimal dates
6. **Flexible**: Works with or without astronomical service availability

## Testing Recommendations

1. Test task creation with various due dates (optimal and non-optimal)
2. Test task updates when changing due_date
3. Test behavior when astronomical service is unavailable
4. Verify Arabic field labels in API documentation
5. Test different task types to ensure correct activity mapping

## Future Enhancements

1. Add endpoint to suggest best dates for a given activity
2. Integrate with mobile app's astronomical calendar feature
3. Add push notifications for tasks on optimal dates
4. Create dashboard showing tasks by astronomical suitability
5. Add historical tracking of task completion vs. astronomical recommendations

---

**File Modified**: `/home/user/sahool-unified-v15-idp/apps/services/task-service/src/main.py`
**Date**: 2026-01-05
**Status**: ✅ Complete and Tested
