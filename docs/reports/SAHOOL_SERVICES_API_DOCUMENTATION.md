# SAHOOL Platform - Complete Services API Documentation

**Version:** 15.5.0  
**Last Updated:** December 2025  
**Platform:** SAHOOL Unified Agricultural Platform

---

## Table of Contents

1. [Infrastructure Services](#infrastructure-services)
2. [Core Services](#core-services)
3. [Application Services](#application-services)
4. [AI & Analysis Services](#ai--analysis-services)
5. [Business Services](#business-services)
6. [Observability Services](#observability-services)

---

## Infrastructure Services

### 1. PostgreSQL with PostGIS
**Container:** `sahool-postgres`  
**Port:** 5432  
**Image:** `postgis/postgis:16-3.4`

#### Functions
- Primary geospatial database for all agricultural data
- PostGIS extension for spatial queries
- Multi-tenant data isolation
- ACID compliance

#### Input/Output
- **Input:** SQL queries via connection string
- **Output:** Query results with geospatial data (PostGIS geometry types)
- **Connection:** `postgresql://USER:PASSWORD@postgres:5432/DB_NAME`

#### Configuration
```yaml
POSTGRES_USER: Required
POSTGRES_PASSWORD: Required
POSTGRES_DB: sahool (default)
```

#### Error Reports & Recommendations

**Error: Connection refused**
- **Cause:** Service not ready or network issues
- **Fix:** Check healthcheck, verify network connectivity
- **Recommendation:** Use healthcheck endpoint before connecting

**Error: PostGIS extension not found**
- **Cause:** Extension not initialized
- **Fix:** Run `CREATE EXTENSION postgis;` in init script
- **Recommendation:** Include in `/docker-entrypoint-initdb.d/` scripts

**Error: Authentication failed**
- **Cause:** Wrong credentials
- **Fix:** Verify POSTGRES_PASSWORD in .env file
- **Recommendation:** Use strong passwords, rotate regularly

---

### 2. Kong API Gateway
**Container:** `sahool-kong`  
**Port:** 8000 (proxy), 127.0.0.1:8001 (admin)  
**Image:** `kong:3.9`

#### Functions
- API routing and load balancing
- Rate limiting and authentication
- Request/response transformation
- Declarative configuration

#### Input/Output
- **Input:** HTTP requests from clients
- **Output:** Routed requests to backend services
- **Config:** `/infra/kong/kong.yml`

#### Error Reports & Recommendations

**Error: Service unavailable (503)**
- **Cause:** Backend service not responding
- **Fix:** Check backend service health
- **Recommendation:** Implement circuit breakers

**Error: Rate limit exceeded (429)**
- **Cause:** Too many requests
- **Fix:** Adjust rate limit configuration
- **Recommendation:** Implement client-side retry with exponential backoff

---

### 3. NATS Message Broker
**Container:** `sahool-nats`  
**Port:** 4222 (client), 8222 (monitoring)  
**Image:** `nats:2.10.24-alpine`

#### Functions
- Pub/sub messaging between services
- JetStream for event persistence
- Real-time event streaming

#### Input/Output
- **Input:** Events from services (JSON)
- **Output:** Published events to subscribers
- **Topics:** `sahool.fields.*`, `sahool.operations.*`, etc.

#### Error Reports & Recommendations

**Error: Connection timeout**
- **Cause:** NATS not ready or network issues
- **Fix:** Wait for healthcheck, verify NATS_URL
- **Recommendation:** Implement reconnection logic

---

### 4. Redis Cache
**Container:** `sahool-redis`  
**Port:** 127.0.0.1:6379  
**Image:** `redis:7.4-alpine`

#### Functions
- Session storage
- Cache layer for frequently accessed data
- Rate limiting counters

#### Input/Output
- **Input:** Key-value pairs (strings, hashes, sets)
- **Output:** Cached data or cache operations
- **Connection:** `redis://:PASSWORD@redis:6379/0`

#### Error Reports & Recommendations

**Error: Authentication required**
- **Cause:** Missing or wrong password
- **Fix:** Set REDIS_PASSWORD in .env
- **Recommendation:** Use strong passwords

---

### 5. MQTT Broker
**Container:** `sahool-mqtt`  
**Port:** 1883 (MQTT), 9001 (WebSocket)  
**Image:** `eclipse-mosquitto:2`

#### Functions
- IoT device connectivity
- Sensor data ingestion
- Real-time telemetry

#### Input/Output
- **Input:** MQTT messages from sensors
- **Output:** Published data to subscribers
- **Topics:** `sahool/sensors/#`

#### Error Reports & Recommendations

**Error: Connection refused**
- **Cause:** Broker not ready or config error
- **Fix:** Check mosquitto.conf, verify port mapping
- **Recommendation:** Use authentication for production

---

## Core Services

### 6. Field Core Service
**Container:** `sahool-field-core`  
**Port:** 3000  
**Stack:** Node.js + TypeScript + Express + TypeORM + PostGIS

#### Functions
- Geospatial field boundary management
- Field CRUD operations with optimistic locking (ETags)
- Field boundary history tracking
- Area calculations
- Multi-tenant field isolation

#### API Endpoints

**GET `/api/v1/fields`**
- **Description:** List all fields with filtering
- **Query Parameters:**
  - `tenantId` (string, optional): Filter by tenant
  - `status` (string, optional): Filter by status
  - `cropType` (string, optional): Filter by crop type
  - `limit` (number, default: 100): Pagination limit
  - `offset` (number, default: 0): Pagination offset
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "field_001",
      "name": "North Field",
      "tenantId": "tenant_001",
      "cropType": "wheat",
      "areaHectares": 5.2,
      "boundary": {
        "type": "Polygon",
        "coordinates": [[[lat, lon], ...]]
      },
      "status": "active",
      "createdAt": "2025-01-01T00:00:00Z",
      "version": 1
    }
  ],
  "pagination": {
    "total": 50,
    "limit": 100,
    "offset": 0
  }
}
```

**GET `/api/v1/fields/:id`**
- **Description:** Get single field by ID
- **Response:** Field object with ETag header
- **Headers:**
  - `ETag`: "field-id:version" (for optimistic locking)

**POST `/api/v1/fields`**
- **Description:** Create new field
- **Request Body:**
```json
{
  "name": "South Field",
  "tenantId": "tenant_001",
  "cropType": "tomato",
  "coordinates": [[[lat, lon], ...]],
  "ownerId": "user_001",
  "irrigationType": "drip",
  "soilType": "loamy",
  "plantingDate": "2025-01-15",
  "expectedHarvest": "2025-05-15"
}
```
- **Response:** Created field with ID and ETag

**PUT `/api/v1/fields/:id`**
- **Description:** Update field (requires If-Match header)
- **Headers:**
  - `If-Match`: ETag value from GET request
- **Response:** Updated field with new ETag

**DELETE `/api/v1/fields/:id`**
- **Description:** Delete field
- **Response:** 204 No Content

#### Input/Output Data Types

**Field Model:**
```typescript
{
  id: string (UUID)
  tenantId: string
  name: string
  cropType: string (enum)
  boundary: GeoJSON Polygon
  areaHectares: number
  status: "active" | "inactive" | "archived"
  version: number (for optimistic locking)
  createdAt: ISO 8601 datetime
  updatedAt: ISO 8601 datetime
}
```

#### Error Reports & Recommendations

**Error: 409 Conflict**
- **Cause:** ETag mismatch (optimistic locking conflict)
- **Fix:** Fetch latest version, reapply changes
- **Recommendation:** Implement conflict resolution UI

**Error: 400 Invalid GeoJSON**
- **Cause:** Invalid polygon coordinates
- **Fix:** Validate coordinates before sending
- **Recommendation:** Use map UI for boundary drawing

**Error: 404 Field not found**
- **Cause:** Field ID doesn't exist
- **Fix:** Verify field ID
- **Recommendation:** Refresh field list

---

### 7. Field Operations Service
**Container:** `sahool-field-ops`  
**Port:** 8080  
**Stack:** Python + FastAPI

#### Functions
- Field operation tracking
- Task scheduling and assignment
- Activity logging
- NATS event publishing

#### API Endpoints

**GET `/fields`**
- **Query Parameters:**
  - `tenant_id` (required): Filter by tenant
  - `skip` (default: 0): Pagination
  - `limit` (default: 50, max: 100): Page size
- **Response:**
```json
{
  "items": [
    {
      "id": "field_001",
      "tenant_id": "tenant_001",
      "name": "North Field",
      "area_hectares": 5.2,
      "crop_type": "wheat",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 50
}
```

**POST `/fields`**
- **Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "name": "New Field",
  "name_ar": "حقل جديد",
  "area_hectares": 3.5,
  "crop_type": "tomato",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[lat, lon], ...]]
  }
}
```
- **Response:** Created field object

**GET `/operations`**
- **Query Parameters:**
  - `field_id` (required)
  - `status` (optional): Filter by status
  - `skip`, `limit`: Pagination
- **Response:** List of operations

**POST `/operations`**
- **Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "field_id": "field_001",
  "operation_type": "irrigation",
  "scheduled_date": "2025-01-15T08:00:00Z",
  "notes": "Sector C needs water"
}
```

**POST `/operations/{operation_id}/complete`**
- **Description:** Mark operation as completed
- **Response:** Updated operation with completion date

#### Input/Output Data Types

**FieldCreate:**
```python
{
  "tenant_id": str,
  "name": str,
  "name_ar": Optional[str],
  "area_hectares": float (must be > 0),
  "crop_type": Optional[str],
  "geometry": Optional[dict],
  "metadata": Optional[dict]
}
```

**OperationCreate:**
```python
{
  "tenant_id": str,
  "field_id": str,
  "operation_type": str,  # planting, irrigation, fertilizing, etc.
  "scheduled_date": Optional[ISO datetime],
  "notes": Optional[str],
  "metadata": Optional[dict]
}
```

#### Error Reports & Recommendations

**Error: 422 Validation Error**
- **Cause:** Invalid input data
- **Fix:** Validate area_hectares > 0, required fields present
- **Recommendation:** Client-side validation before API call

**Error: 404 Field not found**
- **Cause:** Field ID doesn't exist
- **Fix:** Verify field_id before creating operation
- **Recommendation:** Use field list endpoint to verify IDs

**Error: NATS connection failed**
- **Cause:** NATS service unavailable
- **Fix:** Check NATS health, verify NATS_URL
- **Recommendation:** Make event publishing optional (graceful degradation)

---

### 8. Task Service
**Container:** `sahool-task-service`  
**Port:** 8103  
**Stack:** Python + FastAPI

#### Functions
- Agricultural task management
- Task assignment and tracking
- Evidence attachment (photos, notes)
- Task filtering and search

#### API Endpoints

**GET `/api/v1/tasks`**
- **Query Parameters:**
  - `field_id` (optional): Filter by field
  - `status` (optional): pending, in_progress, completed, cancelled, overdue
  - `task_type` (optional): irrigation, fertilization, spraying, scouting, etc.
  - `priority` (optional): low, medium, high, urgent
  - `assigned_to` (optional): User ID
  - `due_before`, `due_after` (optional): Date filters
  - `limit` (default: 50, max: 100)
  - `offset` (default: 0)
- **Response:**
```json
{
  "tasks": [
    {
      "task_id": "task_001",
      "tenant_id": "tenant_001",
      "title": "Irrigate North Field",
      "title_ar": "ري الحقل الشمالي",
      "task_type": "irrigation",
      "priority": "high",
      "status": "pending",
      "field_id": "field_001",
      "assigned_to": "user_ahmed",
      "due_date": "2025-01-15T08:00:00Z",
      "scheduled_time": "08:00",
      "estimated_duration_minutes": 120,
      "created_at": "2025-01-14T10:00:00Z",
      "metadata": {"pump_id": "pump_2", "water_volume_m3": 500}
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

**POST `/api/v1/tasks`**
- **Request Body:**
```json
{
  "title": "Pest Inspection",
  "title_ar": "فحص الحشرات",
  "description": "Weekly inspection",
  "task_type": "scouting",
  "priority": "medium",
  "field_id": "field_001",
  "assigned_to": "user_ahmed",
  "due_date": "2025-01-16T10:30:00Z",
  "scheduled_time": "10:30",
  "estimated_duration_minutes": 60
}
```
- **Response:** Created task with task_id

**POST `/api/v1/tasks/{task_id}/complete`**
- **Request Body:**
```json
{
  "notes": "No pests found",
  "notes_ar": "لم يتم العثور على حشرات",
  "photo_urls": ["https://cdn.sahool.io/photos/task_001_1.jpg"],
  "actual_duration_minutes": 45
}
```

**POST `/api/v1/tasks/{task_id}/start`**
- **Description:** Mark task as in progress

**GET `/api/v1/tasks/today`**
- **Description:** Get tasks due today

**GET `/api/v1/tasks/stats`**
- **Response:**
```json
{
  "total": 100,
  "pending": 25,
  "in_progress": 10,
  "completed": 60,
  "overdue": 5,
  "week_progress": {
    "completed": 15,
    "total": 20,
    "percentage": 75
  }
}
```

#### Input/Output Data Types

**TaskType Enum:**
- irrigation, fertilization, spraying, scouting, maintenance, sampling, harvest, planting, other

**TaskPriority Enum:**
- low, medium, high, urgent

**TaskStatus Enum:**
- pending, in_progress, completed, cancelled, overdue

#### Error Reports & Recommendations

**Error: 400 Task is not pending**
- **Cause:** Trying to start non-pending task
- **Fix:** Check task status before starting
- **Recommendation:** Disable start button for non-pending tasks

**Error: 422 Validation Error**
- **Cause:** Invalid due_date format or missing required fields
- **Fix:** Validate datetime format (ISO 8601)
- **Recommendation:** Use date/time picker components

---

### 9. Equipment Service
**Container:** `sahool-equipment-service`  
**Port:** 8101  
**Stack:** Python + FastAPI

#### Functions
- Equipment/asset management (tractors, pumps, drones)
- Maintenance tracking and alerts
- Real-time status (fuel, hours, location)
- QR code registration

#### API Endpoints

**GET `/api/v1/equipment`**
- **Query Parameters:**
  - `equipment_type` (optional): tractor, pump, drone, harvester, etc.
  - `status` (optional): operational, maintenance, inactive, repair
  - `field_id` (optional): Filter by field
  - `limit` (default: 50), `offset` (default: 0)
- **Response:** List of equipment

**POST `/api/v1/equipment`**
- **Request Body:**
```json
{
  "name": "John Deere 8R 410",
  "name_ar": "جون ديري 8R 410",
  "equipment_type": "tractor",
  "brand": "John Deere",
  "model": "8R 410",
  "serial_number": "JD8R410-2023-001",
  "year": 2023,
  "horsepower": 410,
  "fuel_capacity_liters": 800,
  "field_id": "field_001"
}
```

**GET `/api/v1/equipment/alerts`**
- **Response:** List of maintenance alerts
```json
{
  "alerts": [
    {
      "alert_id": "alert_001",
      "equipment_id": "eq_001",
      "equipment_name": "John Deere 8R",
      "maintenance_type": "oil_change",
      "description": "Engine oil change required",
      "priority": "medium",
      "due_hours": 1300,
      "is_overdue": false
    }
  ],
  "count": 5,
  "overdue_count": 2
}
```

**POST `/api/v1/equipment/{equipment_id}/telemetry`**
- **Request Body:**
```json
{
  "fuel_percent": 75.0,
  "hours": 1250.5,
  "lat": 15.3694,
  "lon": 44.1910
}
```

**GET `/api/v1/equipment/qr/{qr_code}`**
- **Description:** Get equipment by QR code

**POST `/api/v1/equipment/{equipment_id}/maintenance`**
- **Request Body:**
```json
{
  "maintenance_type": "oil_change",
  "description": "Changed engine oil",
  "performed_by": "user_tech",
  "cost": 150.0,
  "parts_replaced": ["Oil filter", "Engine oil 5W-30"]
}
```

#### Input/Output Data Types

**EquipmentType Enum:**
- tractor, pump, drone, harvester, sprayer, pivot, sensor, vehicle, other

**EquipmentStatus Enum:**
- operational, maintenance, inactive, repair

**MaintenanceType Enum:**
- oil_change, filter_change, tire_check, battery_check, calibration, general_service, repair, other

#### Error Reports & Recommendations

**Error: 404 Equipment not found**
- **Cause:** Invalid equipment_id or QR code
- **Fix:** Verify equipment ID or scan QR code again
- **Recommendation:** Implement QR scanner with error handling

**Error: 422 Invalid telemetry data**
- **Cause:** Fuel percent out of range (0-100) or invalid coordinates
- **Fix:** Validate ranges before sending
- **Recommendation:** Client-side validation for telemetry input

---

## Application Services

### 10. Satellite Service
**Container:** `sahool-satellite-service`  
**Port:** 8090  
**Stack:** Python + FastAPI + eo-learn

#### Functions
- Multi-satellite imagery analysis (Sentinel-2, Landsat-8/9, MODIS)
- NDVI, NDWI, EVI, SAVI, LAI calculations
- Vegetation health scoring
- Anomaly detection
- Time series analysis

#### API Endpoints

**POST `/v1/analyze`**
- **Description:** Analyze field using satellite imagery
- **Request Body:**
```json
{
  "field_id": "field_001",
  "latitude": 15.3694,
  "longitude": 44.1910,
  "satellite": "sentinel-2",
  "start_date": "2025-01-01",
  "end_date": "2025-01-15",
  "cloud_cover_max": 20.0
}
```
- **Response:**
```json
{
  "field_id": "field_001",
  "analysis_date": "2025-01-15T10:00:00Z",
  "satellite": "sentinel-2",
  "imagery": {
    "imagery_id": "img_001",
    "acquisition_date": "2025-01-12T10:30:00Z",
    "cloud_cover_percent": 5.2,
    "scene_id": "S2A_MSIL2A_20250112T103000"
  },
  "indices": {
    "ndvi": 0.72,
    "ndwi": 0.45,
    "evi": 0.68,
    "savi": 0.70,
    "lai": 2.5,
    "ndmi": 0.38
  },
  "health_score": 85.5,
  "health_status": "excellent",
  "anomalies": [],
  "recommendations_ar": ["المحصول في حالة ممتازة"],
  "recommendations_en": ["Crop health is excellent"]
}
```

**GET `/v1/timeseries/{field_id}`**
- **Query Parameters:**
  - `start_date` (optional)
  - `end_date` (optional)
  - `satellite` (optional): sentinel-2, landsat-8, landsat-9, modis
- **Response:** Time series data with NDVI trends

**GET `/v1/satellites`**
- **Response:** List of available satellites with configurations

**POST `/v1/imagery/request`**
- **Description:** Request satellite imagery for specific location
- **Response:** Imagery request ID and status

#### Input/Output Data Types

**SatelliteSource Enum:**
- sentinel-2, landsat-8, landsat-9, modis

**VegetationIndices:**
```python
{
  "ndvi": float (0-1),
  "ndwi": float (0-1),
  "evi": float (0-1),
  "savi": float (0-1),
  "lai": float (Leaf Area Index),
  "ndmi": float (0-1)
}
```

#### Error Reports & Recommendations

**Error: 400 Invalid coordinates**
- **Cause:** Latitude or longitude out of range
- **Fix:** Validate coordinates: lat [-90, 90], lon [-180, 180]
- **Recommendation:** Use map picker or GPS for coordinates

**Error: 503 Service unavailable (EO-learn not configured)**
- **Cause:** Sentinel Hub credentials missing
- **Fix:** Set PLANET_API_KEY and PLANET_CLIENT_ID
- **Recommendation:** Graceful degradation - return mock data if credentials missing

**Error: 504 Gateway timeout**
- **Cause:** Satellite data processing takes too long
- **Fix:** Use background task processing, return analysis_id
- **Recommendation:** Implement async pattern with status polling

---

### 11. Weather Advanced Service
**Container:** `sahool-weather-advanced`  
**Port:** 8092  
**Stack:** Python + FastAPI + Open-Meteo/OpenWeatherMap

#### Functions
- 7-day weather forecasting
- Agricultural weather alerts
- Evapotranspiration calculation
- Spray window identification
- Crop-specific calendar

#### API Endpoints

**GET `/v1/current/{location_id}`**
- **Description:** Get current weather for Yemen location
- **Response:**
```json
{
  "location_id": "sanaa",
  "location_name_ar": "صنعاء",
  "latitude": 15.3694,
  "longitude": 44.1910,
  "timestamp": "2025-01-15T12:00:00Z",
  "temperature_c": 22.5,
  "feels_like_c": 21.8,
  "humidity_percent": 45.0,
  "pressure_hpa": 1013.25,
  "wind_speed_kmh": 15.2,
  "wind_direction": "NW",
  "condition": "clear",
  "condition_ar": "صافي"
}
```

**GET `/v1/forecast/{location_id}`**
- **Query Parameters:**
  - `days` (default: 7, max: 14): Forecast days
- **Response:**
```json
{
  "location_id": "sanaa",
  "generated_at": "2025-01-15T12:00:00Z",
  "current": { /* CurrentWeather object */ },
  "hourly_forecast": [
    {
      "datetime": "2025-01-15T13:00:00Z",
      "temperature_c": 23.0,
      "precipitation_mm": 0.0,
      "humidity_percent": 44.0,
      "wind_speed_kmh": 14.5,
      "condition": "clear"
    }
  ],
  "daily_forecast": [
    {
      "date": "2025-01-15",
      "temp_max_c": 25.0,
      "temp_min_c": 18.0,
      "precipitation_total_mm": 0.0,
      "condition": "clear",
      "agricultural_summary_ar": "طقس مناسب للري"
    }
  ],
  "alerts": [],
  "growing_degree_days": 15.5,
  "evapotranspiration_mm": 4.2,
  "spray_window_hours": ["06:00-08:00", "18:00-20:00"],
  "irrigation_recommendation_ar": "يمكن الري خلال ساعات الصباح"
}
```

**GET `/v1/alerts/{location_id}`**
- **Response:** List of weather alerts (heat waves, frost, storms, etc.)

**GET `/v1/locations`**
- **Response:** List of all 22 Yemen governorates with coordinates

#### Input/Output Data Types

**Yemen Locations:**
- sanaa, aden, taiz, hodeidah, ibb, dhamar, hadramaut, marib, hajjah, saadah, lahj, abyan, and 10 more

**AlertType Enum:**
- heat_wave, frost, heavy_rain, drought, high_wind, high_humidity, low_humidity, dust_storm

#### Error Reports & Recommendations

**Error: 404 Location not found**
- **Cause:** Invalid location_id
- **Fix:** Use `/v1/locations` to get valid location IDs
- **Recommendation:** Auto-detect location from GPS or use location picker

**Error: 503 Weather API unavailable**
- **Cause:** External weather API (Open-Meteo/OpenWeatherMap) down
- **Fix:** Check API keys, implement fallback
- **Recommendation:** Cache weather data, use last known values

---

### 12. Crop Health AI Service (Sahool Vision)
**Container:** `sahool-crop-health-ai`  
**Port:** 8095  
**Stack:** Python + FastAPI + TensorFlow Lite

#### Functions
- AI-powered plant disease diagnosis from images
- Batch image processing
- Disease treatment recommendations
- Crop-specific disease database

#### API Endpoints

**POST `/v1/diagnose`**
- **Description:** Diagnose plant disease from image
- **Content-Type:** `multipart/form-data`
- **Form Data:**
  - `image` (file, required): Plant image (max 10MB)
  - `field_id` (string, optional)
  - `crop_type` (enum, optional): tomato, wheat, coffee, etc.
  - `symptoms` (string, optional): Description of symptoms
  - `governorate` (string, optional): Yemen governorate
  - `lat`, `lng` (float, optional): GPS coordinates
- **Response:**
```json
{
  "diagnosis_id": "diag_001",
  "field_id": "field_001",
  "crop_type": "tomato",
  "disease_detected": {
    "disease_id": "early_blight",
    "disease_name": "Early Blight",
    "disease_name_ar": "اللفحة المبكرة",
    "confidence": 0.92,
    "severity": "moderate"
  },
  "treatment": {
    "treatment_id": "treat_001",
    "recommendations_ar": [
      "رش مبيد فطري مانكوزيب",
      "إزالة الأوراق المصابة",
      "تحسين التهوية"
    ],
    "recommendations_en": [
      "Spray mancozeb fungicide",
      "Remove infected leaves",
      "Improve ventilation"
    ],
    "chemicals": [
      {
        "name": "Mancozeb",
        "name_ar": "مانكوزيب",
        "rate_ml_ha": 2500,
        "frequency": "Every 7-10 days"
      }
    ]
  },
  "prevention_ar": ["استخدام بذور مقاومة", "تجنب الري العلوي"],
  "image_url": "https://cdn.sahool.io/diagnosis/diag_001.jpg",
  "diagnosed_at": "2025-01-15T10:30:00Z"
}
```

**POST `/v1/diagnose/batch`**
- **Description:** Diagnose multiple images (max 20)
- **Form Data:**
  - `images` (files[]): Multiple image files
  - `field_id` (optional)
- **Response:** Array of diagnosis results

**GET `/v1/crops`**
- **Response:** List of supported crop types

**GET `/v1/diseases`**
- **Query Parameters:**
  - `crop_type` (optional): Filter by crop
- **Response:** List of diseases with details

**GET `/v1/treatment/{treatment_id}`**
- **Response:** Detailed treatment information

#### Input/Output Data Types

**CropType Enum:**
- tomato, wheat, coffee, qat, banana, cucumber, pepper, potato, corn, grapes, date_palm, mango, onion, garlic

**Image Requirements:**
- Format: JPEG, PNG
- Max size: 10MB
- Recommended: Clear, well-lit photos of affected leaves/plants

#### Error Reports & Recommendations

**Error: 400 Invalid image format**
- **Cause:** File is not an image or unsupported format
- **Fix:** Validate image format client-side before upload
- **Recommendation:** Use image picker with format validation

**Error: 400 Image too large**
- **Cause:** File size > 10MB
- **Fix:** Compress/resize image before upload
- **Recommendation:** Implement client-side image compression

**Error: 503 Model not loaded**
- **Cause:** TensorFlow model failed to load
- **Fix:** Check MODEL_PATH, verify model file exists
- **Recommendation:** Health check should verify model loaded

---

### 13. Virtual Sensors Service
**Container:** `sahool-virtual-sensors`  
**Port:** 8096  
**Stack:** Python + FastAPI

#### Functions
- FAO-56 Penman-Monteith ET0 calculations (without physical sensors)
- Crop evapotranspiration (ETc) calculations
- Soil moisture estimation
- Irrigation recommendations

#### API Endpoints

**POST `/v1/et0/calculate`**
- **Description:** Calculate reference evapotranspiration
- **Request Body:**
```json
{
  "latitude": 15.3694,
  "longitude": 44.1910,
  "date": "2025-01-15",
  "temperature_max_c": 28.0,
  "temperature_min_c": 18.0,
  "humidity_percent": 50.0,
  "wind_speed_kmh": 15.0,
  "solar_radiation_mj_m2": 22.5
}
```
- **Response:**
```json
{
  "et0_mm": 4.2,
  "calculated_at": "2025-01-15T12:00:00Z",
  "method": "FAO-56 Penman-Monteith",
  "inputs_used": {
    "temperature_avg_c": 23.0,
    "humidity_percent": 50.0,
    "wind_speed_kmh": 15.0
  }
}
```

**POST `/v1/etc/calculate`**
- **Description:** Calculate crop evapotranspiration
- **Request Body:**
```json
{
  "crop": "tomato",
  "growth_stage": "mid_season",
  "et0_mm": 4.2,
  "area_hectares": 5.0
}
```
- **Response:**
```json
{
  "etc_mm": 4.83,
  "kc": 1.15,
  "crop_name_ar": "الطماطم",
  "growth_stage_ar": "منتصف الموسم"
}
```

**POST `/v1/irrigation/recommend`**
- **Description:** Get irrigation recommendation
- **Request Body:**
```json
{
  "field_id": "field_001",
  "crop": "tomato",
  "growth_stage": "mid_season",
  "soil_type": "loam",
  "area_hectares": 5.0,
  "last_irrigation_date": "2025-01-10",
  "current_soil_moisture_percent": 45.0,
  "weather_data": { /* optional */ }
}
```
- **Response:**
```json
{
  "recommendation_id": "rec_001",
  "irrigation_needed": true,
  "urgency": "medium",
  "urgency_ar": "متوسط",
  "recommended_date": "2025-01-16",
  "water_amount_mm": 25.0,
  "water_amount_m3": 1250.0,
  "reasoning_ar": "رطوبة التربة منخفضة، المحصول في مرحلة حساسة",
  "recommendations_ar": [
    "الري خلال ساعات الصباح الباكر",
    "استخدام نظام التنقيط لتوفير المياه"
  ]
}
```

**GET `/v1/crops`**
- **Response:** List of crops with Kc coefficients

#### Input/Output Data Types

**Crop Coefficients (Kc):**
```python
{
  "crop": str,  # wheat, tomato, coffee, etc.
  "kc_initial": float,  # 0.3-0.9
  "kc_mid": float,  # 0.9-1.2
  "kc_end": float,  # 0.25-0.9
  "root_depth_max": float  # meters
}
```

#### Error Reports & Recommendations

**Error: 422 Invalid growth stage**
- **Cause:** Growth stage not valid for crop
- **Fix:** Use `/v1/crops` to get valid growth stages
- **Recommendation:** Dropdown menu with valid stages

**Error: 400 Invalid soil moisture**
- **Cause:** Soil moisture out of range (0-100%)
- **Fix:** Validate input range
- **Recommendation:** Use slider component (0-100%)

---

### 14. Irrigation Smart Service
**Container:** `sahool-irrigation-smart`  
**Port:** 8094  
**Stack:** Python + FastAPI

#### Functions
- AI-powered irrigation scheduling
- Water conservation optimization
- Multi-method irrigation support
- Water balance tracking

#### API Endpoints

**POST `/v1/calculate`**
- **Description:** Calculate irrigation needs
- **Request Body:**
```json
{
  "field_id": "field_001",
  "crop": "tomato",
  "growth_stage": "mid_season",
  "area_hectares": 5.0,
  "soil_type": "loamy",
  "irrigation_method": "drip",
  "current_soil_moisture": 45.0,
  "last_irrigation_date": "2025-01-10"
}
```
- **Response:**
```json
{
  "schedule_id": "sched_001",
  "field_id": "field_001",
  "irrigation_date": "2025-01-16",
  "start_time": "06:00",
  "duration_minutes": 120,
  "water_amount_liters": 1250000.0,
  "water_amount_m3": 1250.0,
  "urgency": "medium",
  "urgency_ar": "متوسط",
  "method": "drip",
  "method_ar": "ري بالتنقيط",
  "reasoning_ar": "رطوبة التربة 45% أقل من المثالية 60%",
  "weather_adjusted": true,
  "savings_percent": 15.5
}
```

**GET `/v1/water-balance/{field_id}`**
- **Description:** Get water balance for field
- **Response:**
```json
{
  "field_id": "field_001",
  "date": "2025-01-15",
  "et_mm": 4.2,
  "rainfall_mm": 0.0,
  "irrigation_mm": 0.0,
  "soil_moisture_change_mm": -4.2,
  "water_deficit_mm": 4.2,
  "cumulative_deficit_mm": 12.5
}
```

#### Input/Output Data Types

**IrrigationMethod Enum:**
- flood, drip, sprinkler, furrow, traditional

**UrgencyLevel Enum:**
- low, medium, high, critical

#### Error Reports & Recommendations

**Error: 422 Invalid crop type**
- **Cause:** Crop not supported
- **Fix:** Use supported crop types from enum
- **Recommendation:** Crop selection dropdown

---

## Business Services

### 15. Billing Core Service
**Container:** `sahool-billing-core`  
**Port:** 8089  
**Stack:** Python + FastAPI + Stripe

#### Functions
- Subscription plan management
- Tenant/subscription lifecycle
- Usage-based billing
- Invoice generation
- Payment processing (Stripe, bank transfer, mobile money)

#### API Endpoints

**GET `/v1/plans`**
- **Query Parameters:**
  - `active_only` (default: true)
- **Response:**
```json
{
  "plans": [
    {
      "plan_id": "free",
      "name": "Free",
      "name_ar": "مجاني",
      "tier": "free",
      "pricing": {
        "monthly_usd": 0.0,
        "monthly_yer": 0.0,
        "yearly_usd": 0.0,
        "yearly_yer": 0.0
      },
      "limits": {
        "fields": 3,
        "satellite_analyses_per_month": 10,
        "storage_gb": 1
      },
      "trial_days": 0
    },
    {
      "plan_id": "starter",
      "name": "Starter",
      "name_ar": "المبتدئ",
      "tier": "starter",
      "pricing": {
        "monthly_usd": 29.0,
        "monthly_yer": 7250.0,
        "yearly_usd": 290.0,
        "yearly_yer": 72500.0
      },
      "limits": {
        "fields": 10,
        "satellite_analyses_per_month": 50,
        "ai_diagnoses_per_month": 20
      },
      "trial_days": 14
    }
  ]
}
```

**POST `/v1/tenants`**
- **Description:** Create new tenant with subscription
- **Request Body:**
```json
{
  "name": "Ahmed Farm",
  "name_ar": "مزرعة أحمد",
  "email": "ahmed@example.com",
  "phone": "+967712345678",
  "plan_id": "starter",
  "billing_cycle": "monthly"
}
```
- **Response:**
```json
{
  "success": true,
  "tenant_id": "tenant_001",
  "subscription_id": "sub_001",
  "status": "trial",
  "trial_ends": "2025-01-29",
  "message_ar": "مرحباً مزرعة أحمد! تم إنشاء حسابك بنجاح."
}
```

**GET `/v1/tenants/{tenant_id}/quota`**
- **Response:**
```json
{
  "tenant_id": "tenant_001",
  "plan": "Starter",
  "plan_ar": "المبتدئ",
  "subscription_status": "active",
  "usage": {
    "fields": {
      "limit": 10,
      "used": 5,
      "remaining": 5,
      "percentage": 50.0
    },
    "satellite_analyses_per_month": {
      "limit": 50,
      "used": 15,
      "remaining": 35,
      "percentage": 30.0
    }
  },
  "billing_cycle_ends": "2025-02-15"
}
```

**GET `/v1/tenants/{tenant_id}/invoices`**
- **Response:** List of invoices

**POST `/v1/payments`**
- **Description:** Process payment
- **Request Body:**
```json
{
  "invoice_id": "inv_001",
  "amount": 29.0,
  "method": "credit_card",
  "stripe_token": "tok_visa"  // Optional for Stripe
}
```

#### Input/Output Data Types

**PlanTier Enum:**
- free, starter, professional, enterprise

**BillingCycle Enum:**
- monthly, quarterly, yearly

**Currency Enum:**
- USD, YER (1 USD = 250 YER default)

**PaymentMethod Enum:**
- credit_card, bank_transfer, mobile_money, cash

#### Error Reports & Recommendations

**Error: 429 Quota exceeded**
- **Cause:** Usage limit reached
- **Fix:** Upgrade plan or wait for next billing cycle
- **Recommendation:** Show upgrade prompt when limit reached

**Error: 404 Tenant not found**
- **Cause:** Invalid tenant_id
- **Fix:** Verify tenant_id from authentication token
- **Recommendation:** Extract tenant_id from JWT token automatically

**Error: 400 Payment failed**
- **Cause:** Stripe payment declined or insufficient funds
- **Fix:** Verify payment method, check card details
- **Recommendation:** Show user-friendly error messages

---

### 16. Notification Service
**Container:** `sahool-notification-service`  
**Port:** 8110  
**Stack:** Python + FastAPI + Firebase FCM

#### Functions
- Multi-channel notifications (Push, SMS, In-App)
- Personalized alerts based on farmer profile
- Weather warnings
- Pest outbreak alerts
- Irrigation reminders

#### API Endpoints

**GET `/v1/notifications`**
- **Query Parameters:**
  - `page` (default: 1)
  - `limit` (default: 20)
  - `unread_only` (default: false)
- **Response:** List of notifications

**POST `/v1/notifications`**
- **Description:** Create custom notification
- **Request Body:**
```json
{
  "tenant_id": "tenant_001",
  "user_ids": ["user_001"],
  "title": "تنبيه الري",
  "body": "حان وقت ري الحقل رقم 1",
  "category": "irrigation",
  "priority": "high",
  "channels": ["push", "in_app"]
}
```

**GET `/v1/notifications/unread/count`**
- **Response:**
```json
{
  "count": 5
}
```

**POST `/v1/notifications/{notification_id}/read`**
- **Description:** Mark notification as read

**POST `/push/register`**
- **Description:** Register FCM token for push notifications
- **Request Body:**
```json
{
  "token": "fcm_token_here",
  "platform": "android",
  "device_id": "device-001"
}
```

#### Input/Output Data Types

**NotificationType Enum:**
- weather_alert, pest_outbreak, irrigation_reminder, crop_health, market_price, system, task_reminder

**NotificationPriority Enum:**
- low, medium, high, critical

#### Error Reports & Recommendations

**Error: 400 Invalid FCM token**
- **Cause:** FCM token expired or invalid
- **Fix:** Re-register token
- **Recommendation:** Auto-refresh FCM token on app start

---

## AI & Analysis Services

### 17. Yield Engine Service
**Container:** `sahool-yield-engine`  
**Port:** 8098  
**Stack:** Python + FastAPI + ML Models

#### Functions
- ML-based crop yield prediction
- Historical yield analysis
- Yield forecasting

#### API Endpoints

**POST `/v1/predict`**
- **Description:** Predict crop yield
- **Request Body:**
```json
{
  "field_id": "field_001",
  "crop": "wheat",
  "area_hectares": 5.0,
  "planting_date": "2024-11-01",
  "soil_data": {
    "ph": 6.5,
    "nitrogen_ppm": 120.0
  },
  "weather_data": { /* historical/forecast */ }
}
```
- **Response:**
```json
{
  "prediction_id": "pred_001",
  "predicted_yield_kg_ha": 3200.0,
  "predicted_yield_total_kg": 16000.0,
  "confidence": 0.85,
  "factors": {
    "weather_impact": "favorable",
    "soil_quality": "good"
  }
}
```

---

### 18. Fertilizer Advisor Service
**Container:** `sahool-fertilizer-advisor`  
**Port:** 8093  
**Stack:** Python + FastAPI

#### Functions
- NPK fertilizer recommendations
- Soil analysis interpretation
- Fertilization scheduling
- Cost estimation

#### API Endpoints

**POST `/v1/recommend`**
- **Description:** Get fertilizer recommendation
- **Request Body:**
```json
{
  "field_id": "field_001",
  "crop": "tomato",
  "growth_stage": "vegetative",
  "area_hectares": 5.0,
  "soil_analysis": {
    "ph": 6.5,
    "nitrogen_ppm": 80.0,
    "phosphorus_ppm": 15.0,
    "potassium_ppm": 120.0,
    "organic_matter_percent": 2.5,
    "soil_type": "loamy"
  },
  "target_yield_kg_ha": 50000.0
}
```
- **Response:**
```json
{
  "plan_id": "plan_001",
  "recommendations": [
    {
      "fertilizer_type": "npk_20_20_20",
      "fertilizer_name_ar": "سماد NPK 20-20-20",
      "quantity_kg_per_hectare": 200.0,
      "quantity_kg_per_donum": 20.0,
      "application_method": "side_dressing",
      "application_method_ar": "تسميد جانبي",
      "timing_ar": "بعد 3 أسابيع من الزراعة",
      "npk_content": {"N": 20, "P": 20, "K": 20},
      "cost_estimate_yer": 150000.0
    }
  ],
  "total_nitrogen_kg": 100.0,
  "total_phosphorus_kg": 100.0,
  "total_potassium_kg": 100.0,
  "total_cost_yer": 150000.0
}
```

---

## Observability Services

### 19. Prometheus
**Container:** `sahool-prometheus`  
**Port:** 9090  
**Image:** `prom/prometheus:v2.48.0`

#### Functions
- Metrics collection and storage
- Alerting
- Time-series data storage

---

### 20. Grafana
**Container:** `sahool-grafana`  
**Port:** 3002  
**Image:** `grafana/grafana:10.2.0`

#### Functions
- Metrics visualization
- Custom dashboards
- Alert management

---

## Common Error Patterns & Solutions

### Authentication Errors
**Error: 401 Unauthorized**
- **Cause:** Missing or invalid JWT token
- **Fix:** Include `Authorization: Bearer <token>` header
- **Recommendation:** Auto-refresh tokens before expiration

### Rate Limiting
**Error: 429 Too Many Requests**
- **Cause:** API rate limit exceeded
- **Fix:** Implement exponential backoff retry
- **Recommendation:** Cache responses, batch requests

### Network Errors
**Error: Connection timeout**
- **Cause:** Service unavailable or network issues
- **Fix:** Check service health, implement retry logic
- **Recommendation:** Circuit breaker pattern for resilience

### Validation Errors
**Error: 422 Unprocessable Entity**
- **Cause:** Invalid request data
- **Fix:** Validate input client-side before sending
- **Recommendation:** Use Pydantic models for validation

---

## API Best Practices

1. **Always include headers:**
   - `Authorization: Bearer <token>`
   - `X-Tenant-Id: <tenant_id>`
   - `Content-Type: application/json`

2. **Handle errors gracefully:**
   - Check status codes
   - Parse error messages
   - Show user-friendly messages

3. **Implement pagination:**
   - Use `limit` and `offset` for large datasets
   - Default limit: 50, max: 100

4. **Cache when possible:**
   - Cache static data (crops, diseases, locations)
   - Use ETags for optimistic locking

5. **Use health checks:**
   - Check `/healthz` before critical operations
   - Implement service discovery

---

**End of Documentation**

