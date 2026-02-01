# SAHOOL Admin - Coding Agent Guide
# دليل وكيل البرمجة - SAHOOL Admin

**Version:** 16.0.0
**Target App:** `apps/admin` (Next.js 16 with Turbopack)
**Last Updated:** 2026-02-01
**Primary Goal:** Replace static/mock data with dynamic API integration

---

## Table of Contents

1. [Mission Statement](#mission-statement)
2. [Architecture Overview](#architecture-overview)
3. [Current State Analysis](#current-state-analysis)
4. [Service Endpoints Reference](#service-endpoints-reference)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Code Patterns to Follow](#code-patterns-to-follow)
7. [Environment Variables](#environment-variables)
8. [Common Issues and Fixes](#common-issues-and-fixes)
9. [Testing Requirements](#testing-requirements)
10. [Appendix: Service Port Mapping](#appendix-service-port-mapping)

---

## Mission Statement

**Primary Objective:** Transform the SAHOOL Admin dashboard from a static demo application into a fully functional, production-ready admin panel that dynamically fetches and displays real-time agricultural data from 68+ microservices via Kong API Gateway.

**Key Principles:**
- All data must be fetched from backend services via Kong Gateway (port 8000)
- Implement proper error handling with graceful fallbacks
- Use React Query for data fetching and caching
- Support Arabic (RTL) and English (LTR) localization
- Maintain offline-first capabilities where possible

---

## Architecture Overview

### Request Flow

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────────┐
│   Admin App     │      │    Kong      │      │   Microservices     │
│  (Next.js 16)   │ ────▶│   Gateway    │ ────▶│   (68+ services)    │
│  localhost:3001 │      │  port:8000   │      │   ports:3000-8200   │
└─────────────────┘      └──────────────┘      └─────────────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Rate Limit  │
                         │    + ACL     │
                         │  + JWT Auth  │
                         └──────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript 5.7 |
| **State Management** | React Query (@tanstack/react-query 5.90.20) |
| **HTTP Client** | Axios with interceptors |
| **UI Components** | Tailwind CSS, Custom components |
| **Maps** | Leaflet / MapLibre |
| **WebSocket** | Native WebSocket via ws-gateway |
| **API Gateway** | Kong (port 8000) |

---

## Current State Analysis

### Static Data Locations

The admin app currently uses **mock/static data** in these key files:

| File | Issue | Priority |
|------|-------|----------|
| `src/lib/api.ts:96-115` | `fetchDashboardStats()` returns hardcoded stats | HIGH |
| `src/lib/api.ts:118-129` | `fetchFarms()` falls back to MOCK_FARMS array | HIGH |
| `src/lib/api.ts:139-200` | `fetchDiagnoses()` falls back to MOCK_DIAGNOSES | HIGH |
| `src/lib/api.ts:615-664` | MOCK_FARMS (25 items) and MOCK_DIAGNOSES (20 items) | HIGH |
| `src/app/dashboard/page.tsx` | May use local state with static values | MEDIUM |
| `src/components/dashboard/*` | Components may have hardcoded values | MEDIUM |

### Current API Client Structure

**File:** `apps/admin/src/lib/api.ts`

```typescript
// Current pattern (needs improvement):
export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    const response = await apiClient.get(`${API_URLS.indicators}/api/v1/indicators/dashboard`);
    return response.data;
  } catch (error) {
    // ❌ Returns mock data instead of showing error state
    return {
      totalFarms: 156,
      activeFarms: 142,
      // ... static mock data
    };
  }
}
```

### Required Changes Overview

1. **Remove all mock data fallbacks** - Replace with proper error handling
2. **Implement React Query hooks** - For automatic caching, refetching, and error states
3. **Add loading/error states** - Show skeletons and error messages
4. **Connect to real services** - Via Kong Gateway routes
5. **Add WebSocket support** - For real-time updates (alerts, notifications)

---

## Service Endpoints Reference

### Kong Gateway Routes

All API calls should go through Kong Gateway at `http://localhost:8000` (dev) or `NEXT_PUBLIC_API_URL` (prod).

#### Authentication (user-service:3025)

```
POST /api/v1/auth/login          # Login
POST /api/v1/auth/logout         # Logout
POST /api/v1/auth/refresh        # Refresh token
GET  /api/v1/auth/me             # Current user
GET  /api/v1/users               # List users (admin)
GET  /api/v1/users/:id           # User details
POST /api/v1/users               # Create user
PUT  /api/v1/users/:id           # Update user
```

#### Field Management (field-management-service:3000)

```
GET  /api/v1/fields              # List all fields
GET  /api/v1/fields/:id          # Field details
POST /api/v1/fields              # Create field
PUT  /api/v1/fields/:id          # Update field
GET  /api/v1/fields/:id/ndvi     # Field NDVI data
GET  /api/v1/fields/stats        # Field statistics
```

#### Weather (weather-service:8092 / weather-core:8108)

```
# Location-based (weather-service)
GET  /v1/locations               # Available locations
GET  /v1/current/:locationId     # Current weather by location
GET  /v1/forecast/:locationId    # Forecast by location
GET  /v1/alerts/:locationId      # Weather alerts

# Coordinate-based (weather-core) - POST requests
POST /weather/current            # Body: {lat, lon, field_id, tenant_id}
POST /weather/forecast           # Body: {lat, lon, field_id, tenant_id}
POST /weather/agricultural-report # Body: {lat, lon, field_id, tenant_id}
```

#### Crop Intelligence (crop-intelligence-service:8095)

```
GET  /api/v1/crop-health/diagnoses       # List diagnoses
GET  /api/v1/crop-health/diagnoses/:id   # Diagnosis details
GET  /api/v1/crop-health/diagnoses/stats # Statistics
POST /api/v1/crop-health/analyze         # Analyze image
PATCH /api/v1/crop-health/diagnoses/:id  # Update status
```

#### Indicators & Dashboard (indicators-service:8091)

```
GET  /api/v1/indicators/dashboard  # Dashboard stats
GET  /api/v1/indicators/summary    # Summary metrics
GET  /api/v1/indicators/trends     # Trend data
```

#### IoT & Sensors (virtual-sensors:8119 / iot-service:8117)

```
GET  /api/v1/iot/devices           # List devices
GET  /api/v1/iot/devices/:id       # Device details
GET  /api/v1/iot/readings/:farmId  # Sensor readings
POST /api/v1/iot/devices           # Register device
```

#### Notifications (notification-service:8110)

```
GET  /api/v1/notifications         # List notifications
GET  /api/v1/notifications/:id     # Notification details
PATCH /api/v1/notifications/:id/read # Mark as read
POST /api/v1/notifications/read-all  # Mark all as read
```

#### Tasks (task-service:8103)

```
GET  /api/v1/tasks                 # List tasks
GET  /api/v1/tasks/:id             # Task details
POST /api/v1/tasks                 # Create task
PATCH /api/v1/tasks/:id            # Update task
DELETE /api/v1/tasks/:id           # Delete task
```

#### Equipment (equipment-service:8101)

```
GET  /api/v1/equipment             # List equipment
GET  /api/v1/equipment/:id         # Equipment details
GET  /api/v1/equipment/:id/maintenance # Maintenance history
POST /api/v1/equipment             # Add equipment
PUT  /api/v1/equipment/:id         # Update equipment
```

#### Alerts (alert-service:8113)

```
GET  /api/v1/alerts                # List alerts
GET  /api/v1/alerts/stats          # Alert statistics
POST /api/v1/alerts                # Create alert
PATCH /api/v1/alerts/:id/acknowledge # Acknowledge alert
```

#### Billing (billing-core:8089)

```
GET  /api/v1/billing/invoices      # List invoices
GET  /api/v1/billing/subscriptions # Subscription status
POST /api/v1/billing/checkout      # Create checkout session
```

#### Irrigation (irrigation-smart:8094)

```
GET  /api/v1/irrigation/schedules       # Irrigation schedules
GET  /api/v1/irrigation/recommendations # Smart recommendations
GET  /api/v1/irrigation/history/:fieldId # Irrigation history
POST /api/v1/irrigation/schedules       # Create schedule
```

#### Satellite/Vegetation (vegetation-analysis-service:8090)

```
GET  /v1/timeseries/:fieldId       # NDVI time series
GET  /v1/indices/:fieldId          # Vegetation indices
GET  /v1/satellites                # Available satellites
POST /v1/analyze                   # Request analysis
```

#### AI Advisor (ai-advisor:8112)

```
POST /api/v1/advisor/query         # Ask agricultural question
GET  /api/v1/advisor/history       # Query history
GET  /api/v1/advisor/recommendations # Get recommendations
```

#### WebSocket Gateway (ws-gateway:8081)

```
ws://localhost:8081/ws             # WebSocket connection
# Events: notifications, alerts, field-updates, sensor-readings
```

---

## Implementation Roadmap

### Phase 1: Core Infrastructure (Priority: CRITICAL)

#### 1.1 Create React Query Hooks Base

**Create:** `apps/admin/src/hooks/api/use-api-query.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type { UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { AxiosError } from 'axios';

export interface ApiError {
  message: string;
  code: string;
  status: number;
}

export function useApiQuery<TData>(
  queryKey: string[],
  endpoint: string,
  options?: Omit<UseQueryOptions<TData, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery<TData, ApiError>({
    queryKey,
    queryFn: async () => {
      const response = await apiClient.get(endpoint);
      return response.data;
    },
    ...options,
  });
}

export function useApiMutation<TData, TVariables>(
  endpoint: string,
  method: 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'POST',
  options?: UseMutationOptions<TData, ApiError, TVariables>
) {
  const queryClient = useQueryClient();

  return useMutation<TData, ApiError, TVariables>({
    mutationFn: async (variables) => {
      const response = await apiClient({
        method,
        url: endpoint,
        data: variables,
      });
      return response.data;
    },
    ...options,
  });
}
```

#### 1.2 Implement Dashboard Hooks

**Create:** `apps/admin/src/hooks/api/use-dashboard.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { API_URLS } from '@/config/api';

export interface DashboardStats {
  totalFarms: number;
  activeFarms: number;
  totalArea: number;
  totalDiagnoses: number;
  pendingReviews: number;
  criticalAlerts: number;
  avgHealthScore: number;
  weeklyDiagnoses: number;
}

export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: ['dashboard', 'stats'],
    queryFn: async () => {
      const response = await apiClient.get(
        `${API_URLS.indicators}/api/v1/indicators/dashboard`
      );
      return response.data;
    },
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000,       // Consider stale after 30 seconds
  });
}

export function useDashboardMetrics() {
  return useQuery({
    queryKey: ['dashboard', 'metrics'],
    queryFn: async () => {
      // Fetch from multiple services in parallel
      const [fields, alerts, tasks, users] = await Promise.all([
        apiClient.get(`${API_URLS.fieldCore}/api/v1/fields/stats`),
        apiClient.get(`${API_URLS.alerts}/api/v1/alerts/stats`),
        apiClient.get(`${API_URLS.task}/api/v1/tasks/stats`),
        apiClient.get(`${API_URLS.users}/api/v1/users/stats`),
      ]);

      return {
        fields: fields.data,
        alerts: alerts.data,
        tasks: tasks.data,
        users: users.data,
      };
    },
    refetchInterval: 120000,
  });
}
```

#### 1.3 Update Dashboard Page

**Modify:** `apps/admin/src/app/dashboard/page.tsx`

```typescript
'use client';

import { useDashboardStats } from '@/hooks/api/use-dashboard';
import { MetricsGrid } from '@/components/dashboard/MetricsGrid';
import { AlertsPanel } from '@/components/dashboard/AlertsPanel';
import { MapOverview } from '@/components/dashboard/MapOverview';

export default function DashboardPage() {
  const { data: stats, isLoading, error } = useDashboardStats();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <h3 className="font-semibold">Error Loading Dashboard</h3>
          <p>{error.message}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 text-sm underline"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Dashboard | لوحة التحكم</h1>

      <MetricsGrid stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertsPanel />
        <MapOverview />
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="p-6 space-y-6 animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-48" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-gray-200 rounded" />
        ))}
      </div>
    </div>
  );
}
```

### Phase 2: Field Management (Priority: HIGH)

#### 2.1 Create Fields Hooks

**Create:** `apps/admin/src/hooks/api/use-fields.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { API_URLS } from '@/config/api';

export interface Field {
  id: string;
  name: string;
  nameAr: string;
  ownerId: string;
  governorate: string;
  district: string;
  area: number;
  coordinates: { lat: number; lng: number };
  crops: string[];
  status: 'active' | 'inactive' | 'fallow';
  healthScore: number;
  lastUpdated: string;
  createdAt: string;
}

export function useFields(params?: {
  governorate?: string;
  status?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery<{ fields: Field[]; total: number }>({
    queryKey: ['fields', params],
    queryFn: async () => {
      const response = await apiClient.get(`${API_URLS.fieldCore}/api/v1/fields`, {
        params,
      });
      return response.data;
    },
  });
}

export function useField(id: string) {
  return useQuery<Field>({
    queryKey: ['fields', id],
    queryFn: async () => {
      const response = await apiClient.get(`${API_URLS.fieldCore}/api/v1/fields/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useFieldNDVI(id: string) {
  return useQuery({
    queryKey: ['fields', id, 'ndvi'],
    queryFn: async () => {
      const response = await apiClient.get(`${API_URLS.fieldCore}/api/v1/fields/${id}/ndvi`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Field>) => {
      const response = await apiClient.post(`${API_URLS.fieldCore}/api/v1/fields`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });
}

export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Field> }) => {
      const response = await apiClient.put(`${API_URLS.fieldCore}/api/v1/fields/${id}`, data);
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
      queryClient.invalidateQueries({ queryKey: ['fields', id] });
    },
  });
}

export function useDeleteField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`${API_URLS.fieldCore}/api/v1/fields/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields'] });
    },
  });
}
```

### Phase 3: Weather Integration (Priority: HIGH)

#### 3.1 Create Weather Hooks

**Create:** `apps/admin/src/hooks/api/use-weather.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { API_URLS } from '@/config/api';

export interface WeatherData {
  temperature: number;
  humidity: number;
  wind_speed: number;
  wind_direction: string;
  description: string;
  description_ar: string;
  icon: string;
  pressure: number;
  visibility: number;
  uv_index: number;
  rain_probability: number;
}

// For coordinate-based weather (POST to weather-core)
export function useWeatherCurrent(lat: number, lon: number, fieldId: string = 'default') {
  return useQuery<WeatherData>({
    queryKey: ['weather', 'current', lat, lon],
    queryFn: async () => {
      const response = await apiClient.post(`${API_URLS.weatherCore}/weather/current`, {
        tenant_id: 'default',
        field_id: fieldId,
        lat,
        lon,
      });
      return response.data;
    },
    refetchInterval: 300000, // 5 minutes
    enabled: !!lat && !!lon,
  });
}

// For location-based weather (GET from weather-service)
export function useWeatherByLocation(locationId: string) {
  return useQuery<WeatherData>({
    queryKey: ['weather', 'location', locationId],
    queryFn: async () => {
      const response = await apiClient.get(`${API_URLS.weather}/v1/current/${locationId}`);
      return response.data;
    },
    refetchInterval: 300000,
    enabled: !!locationId,
  });
}

export function useWeatherForecast(lat: number, lon: number, days: number = 7) {
  return useQuery({
    queryKey: ['weather', 'forecast', lat, lon, days],
    queryFn: async () => {
      const response = await apiClient.post(`${API_URLS.weatherCore}/weather/forecast`, {
        tenant_id: 'default',
        field_id: 'default',
        lat,
        lon,
      });
      return response.data;
    },
    refetchInterval: 600000, // 10 minutes
    enabled: !!lat && !!lon,
  });
}

export function useWeatherAlerts(locationId: string) {
  return useQuery({
    queryKey: ['weather', 'alerts', locationId],
    queryFn: async () => {
      const response = await apiClient.get(`${API_URLS.weather}/v1/alerts/${locationId}`);
      return response.data?.alerts || [];
    },
    refetchInterval: 300000,
    enabled: !!locationId,
  });
}

export function useWeatherLocations() {
  return useQuery({
    queryKey: ['weather', 'locations'],
    queryFn: async () => {
      const response = await apiClient.get(`${API_URLS.weather}/v1/locations`);
      return response.data;
    },
    staleTime: 3600000, // 1 hour - locations don't change often
  });
}
```

### Phase 4: Real-time Features (Priority: MEDIUM)

#### 4.1 WebSocket Hook

**Create:** `apps/admin/src/hooks/use-realtime.ts`

```typescript
import { useEffect, useState, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface WebSocketMessage {
  type: string;
  payload: unknown;
  timestamp: string;
}

export function useRealtime(url: string = 'ws://localhost:8081/ws') {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(message);

        // Auto-invalidate relevant queries based on message type
        switch (message.type) {
          case 'notification':
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
            break;
          case 'alert':
            queryClient.invalidateQueries({ queryKey: ['alerts'] });
            queryClient.invalidateQueries({ queryKey: ['dashboard'] });
            break;
          case 'field-update':
            queryClient.invalidateQueries({ queryKey: ['fields'] });
            break;
          case 'sensor-reading':
            queryClient.invalidateQueries({ queryKey: ['sensors'] });
            break;
        }
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      // Attempt reconnect after 5 seconds
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.CLOSED) {
          wsRef.current = new WebSocket(url);
        }
      }, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, [url, queryClient]);

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { connected, lastMessage, send };
}
```

### Phase 5: Remove Mock Data

#### 5.1 Update api.ts to Remove Fallbacks

**Modify:** `apps/admin/src/lib/api.ts`

Remove the mock data constants and fallback returns. Replace with proper error throwing:

```typescript
// REMOVE these sections:
// - MOCK_FARMS array (lines 615-641)
// - MOCK_DIAGNOSES array (lines 643-664)
// - getMockFarms() function (lines 671-673)
// - getMockDiagnoses() function (lines 676-681)

// CHANGE error handling from this:
} catch (error) {
  return getMockFarms();  // ❌ Remove
}

// TO this:
} catch (error) {
  throw error;  // ✅ Let React Query handle errors
}
```

---

## Code Patterns to Follow

### Pattern 1: Query Hook Structure

```typescript
// Always follow this structure for query hooks
export function useResource(id?: string) {
  return useQuery({
    queryKey: ['resource', id],           // Unique, hierarchical key
    queryFn: async () => { ... },         // Async fetch function
    enabled: !!id,                        // Conditional fetching
    staleTime: 30000,                     // When data is considered stale
    refetchInterval: 60000,               // Auto-refresh interval
  });
}
```

### Pattern 2: Mutation Hook Structure

```typescript
export function useCreateResource() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data) => { ... },
    onSuccess: () => {
      // Always invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['resource'] });
    },
    onError: (error) => {
      // Handle errors (show toast, etc.)
      console.error('Create failed:', error);
    },
  });
}
```

### Pattern 3: Component with Loading/Error States

```typescript
export function ResourceList() {
  const { data, isLoading, error, refetch } = useResource();

  if (isLoading) return <Skeleton />;

  if (error) {
    return (
      <ErrorDisplay
        message={error.message}
        onRetry={refetch}
      />
    );
  }

  if (!data?.length) {
    return <EmptyState message="No resources found" />;
  }

  return (
    <ul>
      {data.map(item => <ResourceItem key={item.id} {...item} />)}
    </ul>
  );
}
```

### Pattern 4: Bilingual Labels

```typescript
// Always provide both Arabic and English
const labels = {
  title: 'Dashboard',
  titleAr: 'لوحة التحكم',
};

// In JSX:
<h1>{labels.title} | {labels.titleAr}</h1>
```

---

## Environment Variables

### Required Variables

**File:** `apps/admin/.env.local`

```bash
# API Gateway (Kong)
NEXT_PUBLIC_API_URL=http://localhost:8000

# WebSocket Gateway
NEXT_PUBLIC_WS_URL=ws://localhost:8081

# Feature Flags
NEXT_PUBLIC_ENABLE_REALTIME=true
NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=false  # Set to false in production!

# Optional: Direct service access (development only)
NEXT_PUBLIC_API_BASE=http://localhost
```

### Kong Gateway Required

Ensure Kong is configured with these routes. Missing routes will cause 404 errors:

| Route Pattern | Service | Port |
|---------------|---------|------|
| `/api/v1/auth/*` | user-service | 3025 |
| `/api/v1/fields/*` | field-management-service | 3000 |
| `/api/v1/users/*` | user-service | 3025 |
| `/api/v1/indicators/*` | indicators-service | 8091 |
| `/api/v1/crop-health/*` | crop-intelligence-service | 8095 |
| `/api/v1/weather/*` | weather-service | 8092 |
| `/api/v1/notifications/*` | notification-service | 8110 |
| `/api/v1/tasks/*` | task-service | 8103 |
| `/api/v1/alerts/*` | alert-service | 8113 |
| `/api/v1/equipment/*` | equipment-service | 8101 |
| `/api/v1/irrigation/*` | irrigation-smart | 8094 |
| `/api/v1/iot/*` | iot-service | 8117 |
| `/v1/timeseries/*` | vegetation-analysis-service | 8090 |
| `/weather/*` | weather-core | 8108 |

---

## Common Issues and Fixes

### Issue 1: CORS Errors

**Symptom:** `Access-Control-Allow-Origin` errors in browser console

**Solution:** Kong CORS plugin should be configured. Verify in `kong/kong.yaml`:

```yaml
plugins:
  - name: cors
    config:
      origins: ["*"]  # Development only
      methods: [GET, POST, PUT, PATCH, DELETE, OPTIONS]
      headers: [Accept, Accept-Language, Content-Type, Authorization]
      credentials: true
```

### Issue 2: 401 Unauthorized

**Symptom:** All API calls return 401

**Solution:** Check token handling in `api-client.ts`:

```typescript
// Ensure cookies are sent with requests
const apiClient = axios.create({
  withCredentials: true,  // Required for httpOnly cookies
});
```

### Issue 3: Service Unavailable (503)

**Symptom:** Kong returns 503 for specific services

**Solution:** Service is not running. Check with:

```bash
docker-compose ps | grep <service-name>
docker-compose logs <service-name>
```

### Issue 4: WebSocket Connection Failed

**Symptom:** WebSocket won't connect

**Solution:** Ensure ws-gateway is running on port 8081:

```bash
docker-compose ps ws-gateway
# If not running:
docker-compose up -d ws-gateway
```

### Issue 5: Stale Data

**Symptom:** UI shows outdated information

**Solution:** Implement proper cache invalidation:

```typescript
// After mutation, always invalidate related queries
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['fields'] });
}
```

### Issue 6: Missing Services in Kong

**Symptom:** 404 errors for valid endpoints

**Solution:** Check Kong routes configuration. Some services may not be registered:

```bash
# List all Kong routes
curl http://localhost:8001/routes | jq '.data[].paths'

# Add missing route
curl -X POST http://localhost:8001/services \
  --data "name=missing-service" \
  --data "url=http://missing-service:8xxx"
```

---

## Testing Requirements

### Unit Tests

Each hook should have unit tests:

```typescript
// apps/admin/src/hooks/api/__tests__/use-dashboard.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDashboardStats } from '../use-dashboard';

describe('useDashboardStats', () => {
  it('fetches dashboard stats successfully', async () => {
    const { result } = renderHook(() => useDashboardStats(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={new QueryClient()}>
          {children}
        </QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveProperty('totalFarms');
  });
});
```

### Integration Tests

Test against real services (with test database):

```bash
npm run test:integration
```

### E2E Tests

Full user flow testing with Playwright:

```bash
npm run test:e2e
```

---

## Appendix: Service Port Mapping

### Complete Service Inventory

| Service | Port | Type | Database | Message Queue |
|---------|------|------|----------|---------------|
| **Infrastructure** |
| Kong Gateway | 8000 | Gateway | - | - |
| PostgreSQL | 5432 | DB | - | - |
| PgBouncer | 6432 | Pooler | postgres | - |
| Redis | 6379 | Cache | - | - |
| NATS | 4222 | MQ | - | - |
| WebSocket Gateway | 8081 | Gateway | - | NATS |
| **Core Services** |
| field-management-service | 3000 | NestJS | postgres | NATS |
| user-service | 3025 | NestJS | postgres | NATS |
| marketplace-service | 3010 | NestJS | postgres | NATS |
| research-core | 3015 | NestJS | postgres | NATS |
| disaster-assessment | 3020 | NestJS | postgres | NATS |
| **Analytics & Intelligence** |
| indicators-service | 8091 | FastAPI | postgres | NATS |
| vegetation-analysis-service | 8090 | FastAPI | postgres | NATS |
| crop-intelligence-service | 8095 | FastAPI | postgres | NATS |
| field-intelligence | 8120 | FastAPI | postgres | NATS |
| ai-advisor | 8112 | FastAPI | qdrant | NATS |
| **Weather** |
| weather-service | 8092 | FastAPI | postgres | NATS |
| weather-core | 8108 | FastAPI | postgres | NATS |
| **Operations** |
| task-service | 8103 | FastAPI | postgres | NATS |
| equipment-service | 8101 | FastAPI | postgres | NATS |
| irrigation-smart | 8094 | FastAPI | postgres | NATS |
| inventory-service | 8116 | FastAPI | postgres | NATS |
| **IoT** |
| iot-service | 8117 | NestJS | postgres | NATS, MQTT |
| iot-gateway | 8106 | FastAPI | postgres | NATS, MQTT |
| virtual-sensors | 8119 | FastAPI | postgres | NATS |
| **Communication** |
| notification-service | 8110 | FastAPI | postgres | NATS |
| alert-service | 8113 | FastAPI | postgres | NATS |
| chat-service | 8114 | NestJS | postgres | NATS |
| **Billing** |
| billing-core | 8089 | FastAPI | postgres | NATS |

---

## Quick Start Checklist

- [ ] Ensure Docker services are running: `make dev`
- [ ] Verify Kong Gateway: `curl http://localhost:8000/healthz`
- [ ] Check admin app: `cd apps/admin && npm run dev`
- [ ] Create hooks in `src/hooks/api/`
- [ ] Remove mock data from `src/lib/api.ts`
- [ ] Update components to use new hooks
- [ ] Add loading/error states
- [ ] Test all pages
- [ ] Run tests: `npm test`

---

**Document Maintainer:** SAHOOL Platform Team
**Last Updated:** 2026-02-01
**Next Review:** 2026-03-01
