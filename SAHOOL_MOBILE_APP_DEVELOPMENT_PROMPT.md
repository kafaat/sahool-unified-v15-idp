# SAHOOL Mobile App Development - Complete API Integration Prompt

## Project Overview

Build a comprehensive agricultural mobile application (Android/iOS) that integrates with the SAHOOL Unified Agricultural Platform APIs. The app should provide farmers with field management, crop monitoring, irrigation scheduling, disease diagnosis, weather forecasts, and marketplace access.

**Platform:** SAHOOL Unified v15.5  
**Base URL:** `http://your-api-gateway:8000` (or direct service URLs)  
**Authentication:** JWT Bearer Tokens  
**Primary Language:** Arabic (with English fallback)  
**Target Users:** Yemeni farmers and agricultural workers

---

## Architecture Requirements

### Technology Stack Recommendations
- **Framework:** React Native, Flutter, or native (Swift/Kotlin)
- **State Management:** Redux/MobX (React Native) or Provider/Bloc (Flutter)
- **HTTP Client:** Axios/Fetch or Dio (Flutter)
- **Local Storage:** AsyncStorage or SharedPreferences
- **Maps:** React Native Maps or Google Maps SDK
- **Image Picker:** react-native-image-picker or image_picker (Flutter)
- **Push Notifications:** Firebase Cloud Messaging (FCM)

### Core Architecture Patterns
1. **Repository Pattern:** Separate API calls from UI logic
2. **MVVM/MVP:** Clear separation of concerns
3. **Offline-First:** Cache data locally for offline access
4. **Token Management:** Secure storage and auto-refresh
5. **Error Handling:** Centralized error handling with user-friendly messages

---

## Authentication & Authorization

### Screen 1: Login Screen
**Purpose:** User authentication

**API Endpoint:** (Note: Authentication service not in docker-compose, but typically)
```
POST /api/v1/auth/login
```

**Request:**
```json
{
  "email": "farmer@example.com",
  "password": "password123",
  "device_id": "device-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_token_here",
  "user": {
    "id": "user_001",
    "tenant_id": "tenant_001",
    "name": "Ahmed Ali",
    "name_ar": "أحمد علي",
    "email": "farmer@example.com",
    "role": "farmer"
  },
  "expires_in": 3600
}
```

**UI Components:**
- Email/Phone input field (Arabic RTL support)
- Password input (show/hide toggle)
- Login button
- "Forgot Password?" link
- Language switcher (Arabic/English)

**Error Handling:**
- **401 Unauthorized:** Show "البريد الإلكتروني أو كلمة المرور غير صحيحة"
- **Network Error:** Show "تحقق من اتصال الإنترنت"
- **Validation:** Show inline errors for empty fields

**Store Token:**
- Save JWT token securely (Keychain/Keystore)
- Store tenant_id for API calls
- Save refresh_token for auto-login

---

### Screen 2: Registration Screen
**Purpose:** New user registration

**API Integration:**
1. **Get Available Plans:**
   ```
   GET /v1/plans
   ```
   Display plan cards (Free, Starter, Professional)

2. **Create Tenant:**
   ```
   POST /v1/tenants
   ```
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

**UI Flow:**
1. Personal info form (name, email, phone)
2. Farm info form (farm name, governorate selection)
3. Plan selection (show pricing in USD and YER)
4. Terms acceptance checkbox
5. Submit button

---

## Main Dashboard Screen

### Screen 3: Home/Dashboard
**Purpose:** Overview of farm operations

**Data to Display:**
1. **Weather Widget** (from Weather Advanced Service)
   - Current temperature and condition
   - Today's forecast
   - Weather alerts

2. **Task Summary** (from Task Service)
   - Pending tasks count
   - Overdue tasks count
   - Today's tasks list

3. **Field Status** (from Field Operations Service)
   - Total fields count
   - Fields needing attention

4. **Notifications Badge** (from Notification Service)
   - Unread notifications count

**API Calls:**
```javascript
// Parallel API calls for dashboard
const [
  weatherData,
  taskStats,
  fieldStats,
  notificationsCount
] = await Promise.all([
  fetch('/v1/current/sanaa'),
  fetch('/api/v1/tasks/stats'),
  fetch('/stats/tenant/{tenant_id}'),
  fetch('/v1/notifications/unread/count')
]);
```

**UI Layout:**
- Header with user name and profile picture
- Weather card (top section)
- Quick stats grid (Tasks, Fields, Alerts)
- Recent activities list
- Bottom navigation (Home, Fields, Tasks, Market, Profile)

---

## Field Management Screens

### Screen 4: Fields List Screen
**Purpose:** Display all fields

**API Endpoint:**
```
GET /api/v1/fields?tenantId={tenant_id}&limit=50&offset=0
```

**Request Headers:**
```
Authorization: Bearer {token}
X-Tenant-Id: {tenant_id}
```

**Response Parsing:**
```json
{
  "success": true,
  "data": [
    {
      "id": "field_001",
      "name": "North Field",
      "name_ar": "الحقل الشمالي",
      "cropType": "wheat",
      "areaHectares": 5.2,
      "status": "active",
      "boundary": {
        "type": "Polygon",
        "coordinates": [[[15.3694, 44.1910], ...]]
      },
      "etag": "field_001:1"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 50,
    "offset": 0
  }
}
```

**UI Components:**
- Search bar (filter by name or crop type)
- Filter buttons (All, Active, Inactive)
- Field cards showing:
  - Field name (Arabic/English)
  - Crop type icon and name
  - Area in hectares
  - Status badge
  - Thumbnail map preview
- Pull-to-refresh
- Infinite scroll pagination
- FAB button to add new field

**Display Format:**
```
┌─────────────────────────────┐
│ 🗺️  الحقل الشمالي          │
│    North Field              │
│    🌾 قمح  •  5.2 هكتار    │
│    📍 Active                │
│    [Map Preview]            │
└─────────────────────────────┘
```

---

### Screen 5: Field Detail Screen
**Purpose:** Detailed field information

**API Endpoints:**
1. **Get Field:**
   ```
   GET /api/v1/fields/{field_id}
   ```
   Save ETag from response header for updates

2. **Get Field Operations:**
   ```
   GET /operations?field_id={field_id}
   ```

3. **Get Field Analysis (Satellite):**
   ```
   GET /v1/timeseries/{field_id}
   ```

**UI Tabs/Sections:**
1. **Overview Tab:**
   - Field name and crop type
   - Area and location (map view)
   - Planting date and expected harvest
   - Status and last updated

2. **Analytics Tab:**
   - NDVI trend chart (from satellite service)
   - Health score gauge
   - Recent analysis results

3. **Operations Tab:**
   - List of recent operations
   - Add operation button
   - Filter by operation type

4. **Tasks Tab:**
   - Field-specific tasks
   - Create task button

**Actions:**
- Edit field (requires ETag)
- Delete field
- Request satellite analysis
- View on map (full screen)

---

### Screen 6: Create/Edit Field Screen
**Purpose:** Add or modify field

**API Endpoint (Create):**
```
POST /api/v1/fields
```

**API Endpoint (Update):**
```
PUT /api/v1/fields/{field_id}
Headers: If-Match: {etag}
```

**Form Fields:**
1. **Basic Info:**
   - Field name (Arabic and English)
   - Crop type (dropdown)
   - Area in hectares (number input)
   - Soil type (dropdown)

2. **Location:**
   - Map view for boundary drawing
   - GPS button to auto-center
   - Draw polygon on map
   - Coordinates display

3. **Crop Details:**
   - Planting date (date picker)
   - Expected harvest date (date picker)
   - Irrigation type (dropdown)

**Request Body:**
```json
{
  "name": "South Field",
  "tenantId": "tenant_001",
  "cropType": "tomato",
  "coordinates": [
    [
      [15.3694, 44.1910],
      [15.3700, 44.1910],
      [15.3700, 44.1920],
      [15.3694, 44.1920],
      [15.3694, 44.1910]
    ]
  ],
  "ownerId": "user_001",
  "irrigationType": "drip",
  "soilType": "loamy",
  "plantingDate": "2025-01-15",
  "expectedHarvest": "2025-05-15"
}
```

**Validation:**
- Field name required
- Crop type required
- Area must be > 0
- Polygon must have at least 3 points
- Polygon must be closed (first point = last point)

**Error Handling:**
- **409 Conflict (ETag mismatch):** Show "تم تحديث الحقل بواسطة مستخدم آخر. يرجى تحديث الصفحة."
- **422 Validation Error:** Show field-specific errors

---

## Task Management Screens

### Screen 7: Tasks List Screen
**Purpose:** Display all tasks

**API Endpoint:**
```
GET /api/v1/tasks?tenant_id={tenant_id}&status=pending&limit=50&offset=0
```

**Query Parameters:**
- `field_id` (optional): Filter by field
- `status` (optional): pending, in_progress, completed, overdue
- `task_type` (optional): irrigation, fertilization, spraying, etc.
- `priority` (optional): low, medium, high, urgent
- `assigned_to` (optional): User ID
- `due_before`, `due_after` (optional): Date filters

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "task_001",
      "title": "Irrigate North Field",
      "title_ar": "ري الحقل الشمالي",
      "task_type": "irrigation",
      "priority": "high",
      "status": "pending",
      "field_id": "field_001",
      "due_date": "2025-01-15T08:00:00Z",
      "scheduled_time": "08:00",
      "estimated_duration_minutes": 120
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

**UI Layout:**
- Filter chips (Today, This Week, All, Overdue)
- Task type filter (dropdown)
- Priority filter (dropdown)
- Task cards grouped by date:
  ```
  ┌─────────────────────────────┐
  │ 📅 اليوم - 15 يناير         │
  │                             │
  │ 🔴 URGENT                   │
  │ 💧 ري الحقل الشمالي        │
  │   08:00 • 2 hours           │
  │   [Start] [Details]         │
  └─────────────────────────────┘
  ```
- Swipe actions:
  - Swipe right: Mark complete
  - Swipe left: Delete/Cancel
- FAB button to create task

---

### Screen 8: Task Detail Screen
**Purpose:** View and manage task

**API Endpoints:**
1. **Get Task:**
   ```
   GET /api/v1/tasks/{task_id}
   ```

2. **Start Task:**
   ```
   POST /api/v1/tasks/{task_id}/start
   ```

3. **Complete Task:**
   ```
   POST /api/v1/tasks/{task_id}/complete
   ```

**UI Sections:**
1. **Header:**
   - Task title (Arabic/English)
   - Priority badge (color-coded)
   - Status badge

2. **Details:**
   - Task type icon and name
   - Field name (clickable to field detail)
   - Due date and time
   - Estimated duration
   - Assigned to (if applicable)
   - Description

3. **Actions:**
   - Start Task button (if pending)
   - Complete Task button (if in progress)
   - Edit Task button
   - Delete Task button

4. **Evidence (if completed):**
   - Photos grid
   - Completion notes
   - Actual duration

---

### Screen 9: Create Task Screen
**Purpose:** Create new task

**API Endpoint:**
```
POST /api/v1/tasks
```

**Form Fields:**
1. **Basic Info:**
   - Title (Arabic and English)
   - Description (optional)
   - Task type (picker: irrigation, fertilization, spraying, scouting, maintenance, sampling, harvest, planting, other)
   - Priority (picker: low, medium, high, urgent)

2. **Assignment:**
   - Field selection (dropdown)
   - Assign to (user picker, optional)

3. **Schedule:**
   - Due date (date picker)
   - Scheduled time (time picker)
   - Estimated duration (minutes)

**Request Body:**
```json
{
  "title": "Pest Inspection",
  "title_ar": "فحص الحشرات",
  "description": "Weekly pest inspection for tomato greenhouse",
  "task_type": "scouting",
  "priority": "medium",
  "field_id": "field_001",
  "assigned_to": "user_ahmed",
  "due_date": "2025-01-16T10:30:00Z",
  "scheduled_time": "10:30",
  "estimated_duration_minutes": 60
}
```

**Validation:**
- Title required
- Task type required
- Field ID required
- Due date must be in future

---

## Crop Health & Diagnosis Screens

### Screen 10: Disease Diagnosis Screen
**Purpose:** AI-powered plant disease diagnosis

**API Endpoint:**
```
POST /v1/diagnose
Content-Type: multipart/form-data
```

**Request Form Data:**
```
image: (file, required, max 10MB)
field_id: (string, optional)
crop_type: (enum, optional)
symptoms: (string, optional)
governorate: (string, optional)
lat: (float, optional)
lng: (float, optional)
```

**UI Flow:**
1. **Camera/Gallery Selection:**
   - Button: "Take Photo" (opens camera)
   - Button: "Choose from Gallery" (opens image picker)
   - Image preview

2. **Crop Information Form:**
   - Crop type selector (dropdown)
   - Field selector (optional)
   - Symptoms description (text area)
   - Location (auto from GPS or manual)

3. **Analyze Button:**
   - Show loading spinner
   - Display progress: "جاري التحليل..."

4. **Results Display:**
   ```json
   {
     "disease_detected": {
       "disease_name_ar": "اللفحة المبكرة",
       "confidence": 0.92,
       "severity": "moderate"
     },
     "treatment": {
       "recommendations_ar": [
         "رش مبيد فطري مانكوزيب",
         "إزالة الأوراق المصابة"
       ],
       "chemicals": [
         {
           "name_ar": "مانكوزيب",
           "rate_ml_ha": 2500
         }
       ]
     }
   }
   ```

**UI Components:**
- Disease name and confidence percentage
- Severity indicator (color-coded: green/yellow/red)
- Treatment recommendations list
- Chemical details card
- Prevention tips
- Share results button

**Error Handling:**
- **400 Invalid image:** Show "يرجى اختيار صورة صحيحة"
- **400 Image too large:** Show "حجم الصورة كبير جداً. الحد الأقصى 10 ميجابايت"
- **Network Error:** Show retry button

---

### Screen 11: Batch Diagnosis Screen
**Purpose:** Diagnose multiple images at once

**API Endpoint:**
```
POST /v1/diagnose/batch
Content-Type: multipart/form-data
```

**Form Data:**
```
images: (files[], max 20 images)
field_id: (optional)
```

**UI:**
- Image grid (selected images)
- Add more button (up to 20)
- Remove image (X button on each)
- Analyze all button
- Progress indicator: "Processing 3/10..."
- Results list (collapsible cards)

---

## Weather & Forecast Screens

### Screen 12: Weather Dashboard
**Purpose:** Weather information and forecasts

**API Endpoints:**
1. **Current Weather:**
   ```
   GET /v1/current/{location_id}
   ```

2. **Forecast:**
   ```
   GET /v1/forecast/{location_id}?days=7
   ```

3. **Alerts:**
   ```
   GET /v1/alerts/{location_id}
   ```

**UI Layout:**
1. **Current Weather Card:**
   - Location name (Arabic)
   - Current temperature (large display)
   - Condition icon and description
   - Humidity, wind speed, pressure
   - "Feels like" temperature

2. **Hourly Forecast:**
   - Horizontal scrollable list
   - Time, icon, temperature, precipitation probability

3. **7-Day Forecast:**
   - List view:
     ```
     ┌─────────────────────────────┐
     │ 📅 اليوم                    │
     │ ☀️  25° / 18°               │
     │ صافي • 0% أمطار            │
     └─────────────────────────────┘
     ```

4. **Alerts Section:**
   - Alert cards (if any):
     ```
     ┌─────────────────────────────┐
     │ ⚠️  تحذير موجات حارة       │
     │ درجات حرارة عالية متوقعة   │
     │ 15-18 يناير                 │
     └─────────────────────────────┘
     ```

5. **Agricultural Info:**
   - Growing degree days
   - Evapotranspiration (ET0)
   - Spray window hours
   - Irrigation recommendation

**Location Selection:**
- Dropdown with all 22 Yemen governorates
- Auto-detect from GPS (optional)

---

## Irrigation Management Screens

### Screen 13: Irrigation Dashboard
**Purpose:** Irrigation scheduling and recommendations

**API Endpoints:**
1. **Calculate Irrigation:**
   ```
   POST /v1/calculate
   ```

2. **Get Water Balance:**
   ```
   GET /v1/water-balance/{field_id}
   ```

**UI Sections:**
1. **Upcoming Irrigation:**
   - List of scheduled irrigation:
     ```
     ┌─────────────────────────────┐
     │ 💧 ري الحقل الشمالي        │
     │ 16 يناير 2025 • 06:00      │
     │ 1250 م³ • ⚠️ متوسط        │
     │ [View Details] [Start]      │
     └─────────────────────────────┘
     ```

2. **Recommendations:**
   - Card showing:
     - Field name
     - Recommended date and time
     - Water amount (m³ and liters)
     - Urgency level (color-coded)
     - Reasoning in Arabic

3. **Water Balance:**
   - Chart showing:
     - ET (evapotranspiration)
     - Rainfall
     - Irrigation
     - Deficit

**Request Body for Calculation:**
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

---

### Screen 14: Virtual Sensors Screen
**Purpose:** ET0 and soil moisture calculations (without physical sensors)

**API Endpoints:**
1. **Calculate ET0:**
   ```
   POST /v1/et0/calculate
   ```

2. **Calculate ETc:**
   ```
   POST /v1/etc/calculate
   ```

3. **Irrigation Recommendation:**
   ```
   POST /v1/irrigation/recommend
   ```

**UI Form:**
- Location (GPS or manual)
- Date selector
- Weather inputs (if not auto-filled):
  - Max temperature
  - Min temperature
  - Humidity
  - Wind speed
- Crop selection
- Growth stage selector
- Calculate button

**Results Display:**
- ET0 value (mm/day)
- ETc value (mm/day)
- Kc coefficient
- Irrigation recommendation
- Water amount needed

---

## Equipment Management Screens

### Screen 15: Equipment List
**Purpose:** View all equipment

**API Endpoint:**
```
GET /api/v1/equipment?tenant_id={tenant_id}&equipment_type=tractor
```

**Query Parameters:**
- `equipment_type` (optional): tractor, pump, drone, harvester, etc.
- `status` (optional): operational, maintenance, inactive
- `field_id` (optional)

**UI:**
- Filter chips (All, Tractors, Pumps, Drones)
- Equipment cards:
  ```
  ┌─────────────────────────────┐
  │ 🚜 John Deere 8R 410        │
  │    Operational              │
  │    ⛽ 75% • 1250 hours      │
  │    📍 الحقل الشمالي        │
  │    [View] [QR]              │
  └─────────────────────────────┘
  ```
- FAB button to add equipment

---

### Screen 16: Equipment Detail
**Purpose:** Equipment information and maintenance

**API Endpoints:**
1. **Get Equipment:**
   ```
   GET /api/v1/equipment/{equipment_id}
   ```

2. **Get Maintenance Alerts:**
   ```
   GET /api/v1/equipment/alerts?overdue_only=true
   ```

3. **Get Maintenance History:**
   ```
   GET /api/v1/equipment/{equipment_id}/maintenance
   ```

**UI Tabs:**
1. **Overview:**
   - Equipment name and photo
   - Brand, model, serial number
   - Status badge
   - Current location (map)
   - Fuel percentage (gauge)
   - Operating hours

2. **Maintenance:**
   - Alerts list (if any):
     ```
     ⚠️  تغيير زيت المحرك مطلوب
     Due: 1300 hours (50 hours remaining)
     Priority: Medium
     ```
   - Maintenance history
   - Add maintenance record button

3. **Telemetry:**
   - Real-time data (if available):
     - Fuel level
     - Hours
     - GPS location
   - Update telemetry button

**Actions:**
- Scan QR code (if available)
- Update status
- Update location
- Add maintenance record

---

### Screen 17: Add Maintenance Record
**Purpose:** Log maintenance activity

**API Endpoint:**
```
POST /api/v1/equipment/{equipment_id}/maintenance
```

**Form Fields:**
- Maintenance type (picker):
  - Oil change
  - Filter change
  - Tire check
  - Battery check
  - General service
  - Repair
  - Other
- Description (text area)
- Performed by (user picker)
- Cost (number input)
- Parts replaced (multi-select or tags)
- Date/time (default: now)

**Request Body:**
```json
{
  "maintenance_type": "oil_change",
  "description": "Changed engine oil and filter",
  "description_ar": "تغيير زيت المحرك والفلاتر",
  "performed_by": "user_tech",
  "cost": 150.0,
  "parts_replaced": ["Oil filter", "Engine oil 5W-30"]
}
```

---

## Satellite Analysis Screens

### Screen 18: Satellite Analysis Screen
**Purpose:** View NDVI and vegetation health analysis

**API Endpoints:**
1. **Request Analysis:**
   ```
   POST /v1/analyze
   ```

2. **Get Time Series:**
   ```
   GET /v1/timeseries/{field_id}
   ```

**UI Flow:**
1. **Field Selection:**
   - Dropdown to select field
   - Or select from map

2. **Analysis Request:**
   - Satellite selection (Sentinel-2, Landsat-8, MODIS)
   - Date range picker
   - Cloud cover slider (0-100%)
   - Request button

3. **Results Display:**
   - NDVI map (color-coded overlay)
   - Health score (gauge: 0-100)
   - Vegetation indices:
     - NDVI: 0.72
     - NDWI: 0.45
     - EVI: 0.68
     - LAI: 2.5
   - Anomalies list (if any)
   - Recommendations in Arabic

4. **Time Series Chart:**
   - Line chart showing NDVI over time
   - X-axis: Dates
   - Y-axis: NDVI values (0-1)

**Request Body:**
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

---

## Billing & Subscription Screens

### Screen 19: Subscription Screen
**Purpose:** View and manage subscription

**API Endpoints:**
1. **Get Subscription:**
   ```
   GET /v1/tenants/{tenant_id}/subscription
   ```

2. **Get Quota:**
   ```
   GET /v1/tenants/{tenant_id}/quota
   ```

**UI Sections:**
1. **Current Plan:**
   - Plan name and tier badge
   - Billing cycle
   - Renewal date
   - Status (Active, Trial, Expired)

2. **Usage Quota:**
   - Progress bars for each metric:
     ```
     Fields: ████████░░ 8/10 (80%)
     Satellite Analyses: █████░░░░░ 15/50 (30%)
     AI Diagnoses: ████░░░░░░ 8/20 (40%)
     ```
   - Upgrade button (if limit reached)

3. **Billing History:**
   - List of invoices (clickable)
   - Payment history

4. **Upgrade Options:**
   - Plan comparison table
   - Upgrade button for each plan

---

### Screen 20: Invoice Detail Screen
**Purpose:** View invoice and payment

**API Endpoint:**
```
GET /v1/invoices/{invoice_id}
```

**UI:**
- Invoice number and date
- Line items table
- Subtotal, tax, total
- Amount in USD and YER
- Status badge
- Pay button (if unpaid)
- Download PDF button

**Payment Flow:**
1. Select payment method:
   - Credit card (Stripe)
   - Bank transfer
   - Mobile money
   - Cash
2. Enter payment details
3. Confirm payment
4. Show receipt

---

## Notifications Screen

### Screen 21: Notifications List
**Purpose:** View all notifications

**API Endpoint:**
```
GET /v1/notifications?page=1&limit=20&unread_only=false
```

**UI:**
- Filter tabs: All, Unread, Alerts, Tasks
- Notification cards:
  ```
  ┌─────────────────────────────┐
  │ 🔔 تنبيه ري                 │
  │ حان وقت ري الحقل رقم 1     │
  │ 2 hours ago                 │
  │ [View] [Mark Read]          │
  └─────────────────────────────┘
  ```
- Pull-to-refresh
- Infinite scroll
- Mark all as read button

**Notification Types:**
- Weather alerts (🌤️)
- Irrigation reminders (💧)
- Task reminders (📋)
- Crop health alerts (🌱)
- Market prices (💰)
- System notifications (⚙️)

---

## Marketplace Screens (Future)

### Screen 22: Marketplace Screen
**Note:** Marketplace service exists but not detailed in current APIs

**Features:**
- Browse products
- Sell crops
- View prices
- Contact sellers

---

## Settings Screen

### Screen 23: Settings
**Purpose:** App configuration

**Sections:**
1. **Profile:**
   - Edit name, email, phone
   - Change password
   - Profile picture

2. **Preferences:**
   - Language (Arabic/English)
   - Notifications settings
   - Default location
   - Units (metric/imperial)

3. **Notifications:**
   - Push notifications toggle
   - Category preferences
   - Quiet hours

4. **About:**
   - App version
   - Terms of service
   - Privacy policy
   - Contact support

---

## API Integration Implementation Guide

### 1. HTTP Client Setup

**React Native Example (Axios):**
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://your-api-gateway:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept-Language': 'ar,en',
  },
});

// Request interceptor - Add token
apiClient.interceptors.request.use((config) => {
  const token = await getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  const tenantId = await getStoredTenantId();
  if (tenantId) {
    config.headers['X-Tenant-Id'] = tenantId;
  }
  return config;
});

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired - refresh or logout
      await refreshToken();
    }
    return Promise.reject(error);
  }
);
```

### 2. State Management

**Redux Example:**
```javascript
// Actions
export const fetchFields = () => async (dispatch) => {
  dispatch({ type: 'FIELDS_LOADING' });
  try {
    const response = await apiClient.get('/api/v1/fields');
    dispatch({ type: 'FIELDS_SUCCESS', payload: response.data.data });
  } catch (error) {
    dispatch({ type: 'FIELDS_ERROR', payload: error.message });
  }
};

// Reducer
const fieldsReducer = (state = { items: [], loading: false }, action) => {
  switch (action.type) {
    case 'FIELDS_LOADING':
      return { ...state, loading: true };
    case 'FIELDS_SUCCESS':
      return { items: action.payload, loading: false };
    default:
      return state;
  }
};
```

### 3. Error Handling

```javascript
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    const status = error.response.status;
    const message = error.response.data?.detail || error.response.data?.error;
    
    switch (status) {
      case 400:
        return 'بيانات غير صحيحة. يرجى التحقق من المدخلات.';
      case 401:
        return 'انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى.';
      case 404:
        return 'البيانات المطلوبة غير موجودة.';
      case 422:
        return message || 'بيانات غير صحيحة.';
      case 429:
        return 'تم تجاوز عدد الطلبات المسموح. يرجى المحاولة لاحقاً.';
      case 500:
        return 'خطأ في الخادم. يرجى المحاولة لاحقاً.';
      default:
        return message || 'حدث خطأ غير متوقع.';
    }
  } else if (error.request) {
    // Request made but no response
    return 'تحقق من اتصال الإنترنت.';
  } else {
    return 'حدث خطأ أثناء إعداد الطلب.';
  }
};
```

### 4. Image Upload

**React Native Example:**
```javascript
import ImagePicker from 'react-native-image-picker';
import FormData from 'form-data';

const uploadDiagnosisImage = async (imageUri, cropType, fieldId) => {
  const formData = new FormData();
  formData.append('image', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'diagnosis.jpg',
  });
  if (cropType) formData.append('crop_type', cropType);
  if (fieldId) formData.append('field_id', fieldId);

  const response = await apiClient.post('/v1/diagnose', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};
```

### 5. Offline Support

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

// Cache API responses
const cacheResponse = async (key, data) => {
  await AsyncStorage.setItem(key, JSON.stringify({
    data,
    timestamp: Date.now(),
  }));
};

// Get cached data
const getCachedData = async (key, maxAge = 3600000) => {
  const cached = await AsyncStorage.getItem(key);
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp < maxAge) {
      return data;
    }
  }
  return null;
};

// Check network and use cache if offline
const fetchWithCache = async (endpoint, cacheKey) => {
  const netInfo = await NetInfo.fetch();
  
  if (!netInfo.isConnected) {
    // Return cached data if offline
    const cached = await getCachedData(cacheKey);
    if (cached) return cached;
    throw new Error('No internet connection and no cached data');
  }
  
  try {
    const response = await apiClient.get(endpoint);
    await cacheResponse(cacheKey, response.data);
    return response.data;
  } catch (error) {
    // Try cache as fallback
    const cached = await getCachedData(cacheKey);
    if (cached) return cached;
    throw error;
  }
};
```

### 6. Push Notifications

**Firebase Cloud Messaging Setup:**
```javascript
import messaging from '@react-native-firebase/messaging';

// Register FCM token
const registerFCMToken = async () => {
  const token = await messaging().getToken();
  await apiClient.post('/push/register', {
    token,
    platform: Platform.OS,
    device_id: DeviceInfo.getUniqueId(),
  });
};

// Handle notifications
messaging().onMessage(async (remoteMessage) => {
  // Show local notification
  Alert.alert(
    remoteMessage.notification.title,
    remoteMessage.notification.body,
  );
});

// Handle notification tap
messaging().onNotificationOpenedApp((remoteMessage) => {
  // Navigate to relevant screen
  if (remoteMessage.data.field_id) {
    navigation.navigate('FieldDetail', { 
      fieldId: remoteMessage.data.field_id 
    });
  }
});
```

---

## UI/UX Guidelines

### Arabic (RTL) Support
- All text should support RTL layout
- Use `flexDirection: 'row-reverse'` for RTL
- Mirror icons and images for RTL
- Use Arabic numerals (٠-٩) optionally

### Color Scheme
- Primary: Green (#2E7D32) - Agriculture theme
- Secondary: Orange (#F57C00) - Alerts
- Success: Green (#4CAF50)
- Warning: Orange (#FF9800)
- Error: Red (#F44336)
- Info: Blue (#2196F3)

### Typography
- Arabic font: Tajawal, Cairo, or Noto Sans Arabic
- English font: Roboto or Inter
- Font sizes: 12px (small), 14px (body), 16px (title), 20px (heading), 24px (large heading)

### Icons
- Use Material Icons or FontAwesome
- Common icons:
  - 🌾 Fields
  - 📋 Tasks
  - 💧 Irrigation
  - 🌤️ Weather
  - 🔬 Diagnosis
  - 🚜 Equipment
  - 📊 Analytics
  - 🔔 Notifications

---

## Testing Checklist

1. **Authentication:**
   - [ ] Login with valid credentials
   - [ ] Login with invalid credentials (error handling)
   - [ ] Token refresh on expiration
   - [ ] Logout clears token

2. **Fields:**
   - [ ] List fields (with pagination)
   - [ ] Create field (with map boundary)
   - [ ] Update field (ETag handling)
   - [ ] Delete field
   - [ ] Search and filter fields

3. **Tasks:**
   - [ ] List tasks (all filters)
   - [ ] Create task
   - [ ] Start task
   - [ ] Complete task with evidence
   - [ ] Delete task

4. **Diagnosis:**
   - [ ] Upload image from camera
   - [ ] Upload image from gallery
   - [ ] Process diagnosis
   - [ ] Display results
   - [ ] Batch diagnosis

5. **Weather:**
   - [ ] Fetch current weather
   - [ ] Fetch 7-day forecast
   - [ ] Display alerts
   - [ ] Change location

6. **Offline Mode:**
   - [ ] App works with cached data
   - [ ] Queue actions when offline
   - [ ] Sync when back online

---

## Performance Optimization

1. **Image Optimization:**
   - Compress images before upload
   - Use thumbnails for lists
   - Lazy load images

2. **API Optimization:**
   - Batch requests when possible
   - Use pagination for large lists
   - Cache static data (crops, diseases)

3. **UI Optimization:**
   - Use FlatList for long lists
   - Implement pull-to-refresh
   - Show loading states
   - Optimize re-renders (React.memo)

---

## Security Best Practices

1. **Token Storage:**
   - Use secure storage (Keychain/Keystore)
   - Never log tokens
   - Auto-refresh before expiration

2. **API Security:**
   - Always use HTTPS in production
   - Validate SSL certificates
   - Don't expose API keys in code

3. **Data Validation:**
   - Validate input client-side
   - Sanitize user input
   - Handle errors gracefully

---

## Deployment Checklist

- [ ] Replace base URL with production API
- [ ] Configure Firebase for push notifications
- [ ] Set up error tracking (Sentry, Crashlytics)
- [ ] Configure app icons and splash screens
- [ ] Test on both Android and iOS
- [ ] Localize all strings (Arabic/English)
- [ ] Optimize app bundle size
- [ ] Set up app signing certificates
- [ ] Configure deep linking
- [ ] Set up analytics (Firebase Analytics)

---

**End of Mobile App Development Prompt**

