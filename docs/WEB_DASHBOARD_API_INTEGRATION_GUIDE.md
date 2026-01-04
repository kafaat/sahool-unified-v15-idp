# SAHOOL Web & Dashboard API Integration Guide
# دليل تكامل API للويب ولوحة التحكم

**Version:** 1.0.0
**Last Updated:** January 2026
**Kong Gateway Port:** 8000
**Gateway URL:** `https://api.sahool.app` or `http://localhost:8000`

---

## Table of Contents / جدول المحتويات

1. [Overview / نظرة عامة](#overview)
2. [Architecture / البنية](#architecture)
3. [Authentication / المصادقة](#authentication)
4. [API Client Setup / إعداد عميل API](#api-client-setup)
5. [Service Endpoints / نقاط الخدمة](#service-endpoints)
6. [Rate Limiting / تحديد المعدل](#rate-limiting)
7. [Error Handling / معالجة الأخطاء](#error-handling)
8. [WebSocket Integration / تكامل WebSocket](#websocket-integration)
9. [React Query Patterns / أنماط React Query](#react-query-patterns)
10. [Admin Dashboard Specifics / خصائص لوحة التحكم](#admin-dashboard-specifics)

---

## Overview

SAHOOL Platform uses Kong API Gateway to manage all microservices. This guide covers integration for:

- **Web App** (`apps/web`): Next.js application for farmers and cooperatives
- **Admin Dashboard** (`apps/admin`): Next.js application for platform administrators

### Key Features

- JWT-based authentication with subscription tier support
- Rate limiting per subscription (Starter, Professional, Enterprise, Research)
- ACL (Access Control List) for permission management
- Real-time updates via WebSocket gateway
- Circuit breaker pattern for service resilience
- Bilingual support (Arabic/English)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Applications                          │
├────────────────────────────┬────────────────────────────────────────┤
│       Web App (Next.js)    │       Admin Dashboard (Next.js)        │
│     - Axios HTTP Client    │     - Fetch API with Retry             │
│     - js-cookie            │     - Centralized Token Management     │
│     - React Query          │     - 2FA Support                      │
└────────────────────────────┴────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Kong API Gateway (Port 8000)                     │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐  │
│  │ JWT Plugin  │ ACL Plugin  │ Rate Limit  │ CORS / Security     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  Starter Services │   │ Professional Svcs │   │ Enterprise Svcs   │
│  - field-core     │   │ - satellite       │   │ - ai-advisor      │
│  - weather-core   │   │ - ndvi-engine     │   │ - iot-gateway     │
│  - agro-advisor   │   │ - crop-health-ai  │   │ - research-core   │
│  - notifications  │   │ - irrigation      │   │ - marketplace     │
│  - calendar       │   │ - yield-engine    │   │ - billing-core    │
└───────────────────┘   └───────────────────┘   └───────────────────┘
```

---

## Authentication

### JWT Token Structure

```typescript
interface JWTPayload {
  sub: string;              // User ID
  email: string;            // User email
  role: string;             // User role (admin, supervisor, viewer, farmer)
  tenant_id?: string;       // Tenant ID for multi-tenancy
  subscription: string;     // Subscription tier: starter, professional, enterprise, research
  acl_groups: string[];     // ACL groups: starter-users, professional-users, etc.
  iat: number;              // Issued at timestamp
  exp: number;              // Expiration timestamp
}
```

### Web App Authentication (Axios + js-cookie)

```typescript
// lib/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.sahool.app';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Admin Dashboard Authentication (Fetch + 2FA)

```typescript
// lib/api-client.ts
class AdminApiClient {
  private baseUrl: string;
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  async login(email: string, password: string, totp_code?: string) {
    const body: any = { email, password };
    if (totp_code) {
      body.totp_code = totp_code;
    }

    return this.request<{
      access_token: string;
      user: User;
      requires_2fa?: boolean;
      temp_token?: string;
    }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  private async request<T>(endpoint: string, options: RequestInit = {}) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept-Language': 'ar,en',
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: { ...headers, ...options.headers },
    });

    return response.json();
  }
}

export const apiClient = new AdminApiClient();
```

---

## API Client Setup

### Environment Variables

```bash
# .env.local (Web App)
NEXT_PUBLIC_API_URL=https://api.sahool.app
NEXT_PUBLIC_WS_URL=wss://api.sahool.app/api/v1/ws

# .env.local (Admin Dashboard)
NEXT_PUBLIC_API_URL=https://admin.sahool.app/api
NEXT_PUBLIC_ADMIN_WS_URL=wss://admin.sahool.app/api/v1/ws
```

### Axios Configuration (Web App)

```typescript
// features/fields/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const fieldsApi = {
  getFields: async (filters?: FieldFilters): Promise<Field[]> => {
    const params = new URLSearchParams();
    if (filters?.search) params.set('search', filters.search);
    if (filters?.farmId) params.set('tenantId', filters.farmId);

    const response = await api.get(`/api/v1/fields?${params.toString()}`);
    return response.data.data || response.data;
  },

  createField: async (data: FieldFormData): Promise<Field> => {
    const response = await api.post('/api/v1/fields', data);
    return response.data.data || response.data;
  },
};
```

---

## Service Endpoints

### Starter Package Services
Available for all subscription tiers.

| Service | Route | Description | Description (AR) |
|---------|-------|-------------|------------------|
| Field Core | `/api/v1/fields` | Field management | إدارة الحقول |
| Weather Core | `/api/v1/weather` | Weather data | بيانات الطقس |
| Astronomical Calendar | `/api/v1/calendar` | Yemeni calendar | التقويم الفلكي |
| Agro Advisor | `/api/v1/advice` | Agricultural advice | النصائح الزراعية |
| Notifications | `/api/v1/notifications` | Push notifications | الإشعارات |

### Professional Package Services
Available for Professional, Enterprise, and Research tiers.

| Service | Route | Description | Description (AR) |
|---------|-------|-------------|------------------|
| Satellite | `/api/v1/satellite` | Satellite imagery | صور الأقمار الصناعية |
| NDVI Engine | `/api/v1/ndvi` | Vegetation indices | مؤشرات الغطاء النباتي |
| Crop Health AI | `/api/v1/crop-health` | Disease detection | كشف الأمراض |
| Smart Irrigation | `/api/v1/irrigation` | Irrigation management | إدارة الري |
| Virtual Sensors | `/api/v1/sensors/virtual` | ET0 calculations | حسابات التبخر |
| Yield Engine | `/api/v1/yield` | Yield prediction | توقع الإنتاجية |
| Fertilizer Advisor | `/api/v1/fertilizer` | Fertilizer recommendations | توصيات التسميد |
| Inventory | `/api/v1/inventory` | Inventory management | إدارة المخزون |
| Equipment | `/api/v1/equipment` | Equipment management | إدارة المعدات |

### Enterprise Package Services
Available for Enterprise and Research tiers only.

| Service | Route | Description | Description (AR) |
|---------|-------|-------------|------------------|
| AI Advisor | `/api/v1/ai-advisor` | Multi-agent AI | المستشار الذكي |
| IoT Gateway | `/api/v1/iot` | IoT device management | إدارة أجهزة IoT |
| IoT Service | `/api/v1/iot-service` | Sensor data | بيانات المستشعرات |
| Research Core | `/api/v1/research` | Research data | بيانات البحث |
| Marketplace | `/api/v1/marketplace` | Market listings | السوق |
| Billing Core | `/api/v1/billing` | Billing & payments | الفوترة |
| Disaster Assessment | `/api/v1/disaster` | Disaster analysis | تقييم الكوارث |
| Crop Growth Model | `/api/v1/crop-model` | WOFOST modeling | نماذج النمو |
| LAI Estimation | `/api/v1/lai` | Leaf area index | مؤشر المساحة الورقية |
| Yield Prediction | `/api/v1/yield-prediction` | Advanced predictions | التوقعات المتقدمة |

### Shared Services
Available based on feature requirements.

| Service | Route | Description | Description (AR) |
|---------|-------|-------------|------------------|
| Field Operations | `/api/v1/field-ops` | Field tasks | عمليات الحقل |
| WebSocket Gateway | `/api/v1/ws` | Real-time updates | التحديثات الفورية |
| Indicators | `/api/v1/indicators` | Analytics indicators | المؤشرات |
| Weather Advanced | `/api/v1/weather/advanced` | Advanced weather | الطقس المتقدم |
| Community Chat | `/api/v1/community/chat` | Community messaging | محادثة المجتمع |
| Field Chat | `/api/v1/field/chat` | Field messaging | محادثة الحقل |
| Tasks | `/api/v1/tasks` | Task management | إدارة المهام |
| Providers | `/api/v1/providers` | Provider config | تكوين المزودين |
| Alerts | `/api/v1/alerts` | Alert management | إدارة التنبيهات |
| Chat Service | `/api/v1/chat` | General chat | المحادثة |

### Authentication Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `/api/v1/auth/login` | POST | 5/min, 20/hr | User login |
| `/api/v1/auth/register` | POST | 10/min, 50/hr | User registration |
| `/api/v1/auth/refresh` | POST | 10/min, 100/hr | Token refresh |
| `/api/v1/auth/password-reset` | POST | 3/min, 10/hr | Password reset |
| `/api/v1/auth/forgot-password` | POST | 3/min, 10/hr | Forgot password |

---

## Rate Limiting

### Limits by Subscription Tier

| Tier | Requests/Minute | Requests/Hour | Notes |
|------|-----------------|---------------|-------|
| Starter | 100 | 5,000 | Basic services only |
| Professional | 1,000 | 50,000 | All professional services |
| Enterprise | 10,000 | 500,000 | All services + priority |
| Research | 10,000 | 500,000 | Full access + research APIs |

### Handling Rate Limits (TypeScript)

```typescript
// lib/rate-limit-handler.ts
import axios, { AxiosError } from 'axios';

interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
}

export function getRateLimitInfo(headers: Record<string, string>): RateLimitInfo | null {
  const limit = headers['x-ratelimit-limit'];
  const remaining = headers['x-ratelimit-remaining'];
  const reset = headers['x-ratelimit-reset'];

  if (limit && remaining && reset) {
    return {
      limit: parseInt(limit, 10),
      remaining: parseInt(remaining, 10),
      reset: parseInt(reset, 10),
    };
  }
  return null;
}

export async function handleRateLimitError(error: AxiosError): Promise<void> {
  if (error.response?.status === 429) {
    const retryAfter = error.response.headers['retry-after'];
    const waitTime = retryAfter ? parseInt(retryAfter, 10) * 1000 : 60000;

    console.warn(`Rate limited. Waiting ${waitTime / 1000} seconds...`);
    await new Promise((resolve) => setTimeout(resolve, waitTime));
  }
}
```

---

## Error Handling

### Bilingual Error Messages

```typescript
// lib/error-messages.ts
export const ERROR_MESSAGES = {
  NETWORK_ERROR: {
    en: 'Network error. Please check your connection.',
    ar: 'خطأ في الاتصال. يرجى التحقق من اتصالك.',
  },
  UNAUTHORIZED: {
    en: 'Session expired. Please log in again.',
    ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.',
  },
  FORBIDDEN: {
    en: 'You do not have permission to access this resource.',
    ar: 'ليس لديك صلاحية للوصول إلى هذا المورد.',
  },
  NOT_FOUND: {
    en: 'Resource not found.',
    ar: 'المورد غير موجود.',
  },
  RATE_LIMITED: {
    en: 'Too many requests. Please wait and try again.',
    ar: 'طلبات كثيرة جداً. يرجى الانتظار والمحاولة مرة أخرى.',
  },
  SERVER_ERROR: {
    en: 'Server error. Please try again later.',
    ar: 'خطأ في الخادم. يرجى المحاولة مرة أخرى لاحقاً.',
  },
  VALIDATION_ERROR: {
    en: 'Please check your input and try again.',
    ar: 'يرجى التحقق من المدخلات والمحاولة مرة أخرى.',
  },
  FETCH_FAILED: {
    en: 'Failed to fetch data. Using cached data.',
    ar: 'فشل في جلب البيانات. استخدام البيانات المخزنة.',
  },
};

export function getErrorMessage(
  code: keyof typeof ERROR_MESSAGES,
  locale: 'en' | 'ar' = 'ar'
): string {
  return ERROR_MESSAGES[code]?.[locale] || ERROR_MESSAGES.SERVER_ERROR[locale];
}
```

### Error Interceptor

```typescript
// lib/error-interceptor.ts
import axios, { AxiosError } from 'axios';
import { getErrorMessage } from './error-messages';

export function setupErrorInterceptor(api: typeof axios) {
  api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const locale = typeof window !== 'undefined'
        ? (localStorage.getItem('locale') as 'en' | 'ar') || 'ar'
        : 'ar';

      if (!error.response) {
        return Promise.reject({
          message: getErrorMessage('NETWORK_ERROR', locale),
          originalError: error,
        });
      }

      const status = error.response.status;

      switch (status) {
        case 401:
          return Promise.reject({
            message: getErrorMessage('UNAUTHORIZED', locale),
            originalError: error,
          });
        case 403:
          return Promise.reject({
            message: getErrorMessage('FORBIDDEN', locale),
            originalError: error,
          });
        case 404:
          return Promise.reject({
            message: getErrorMessage('NOT_FOUND', locale),
            originalError: error,
          });
        case 429:
          return Promise.reject({
            message: getErrorMessage('RATE_LIMITED', locale),
            originalError: error,
          });
        case 422:
          return Promise.reject({
            message: getErrorMessage('VALIDATION_ERROR', locale),
            originalError: error,
          });
        default:
          return Promise.reject({
            message: getErrorMessage('SERVER_ERROR', locale),
            originalError: error,
          });
      }
    }
  );
}
```

---

## WebSocket Integration

### Connecting to WebSocket Gateway

```typescript
// lib/websocket.ts
interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
}

class SahoolWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  constructor(url: string, token: string) {
    this.url = url;
    this.token = token;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const wsUrl = `${this.url}?token=${this.token}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.emit(message.type, message.payload);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.handleReconnect();
      };
    });
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay / 1000} seconds...`);
      setTimeout(() => this.connect(), delay);
    }
  }

  subscribe(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  unsubscribe(event: string, callback: (data: any) => void) {
    this.listeners.get(event)?.delete(callback);
  }

  private emit(event: string, data: any) {
    this.listeners.get(event)?.forEach((callback) => callback(data));
  }

  send(type: string, payload: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, payload }));
    }
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }
}

// Usage
const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'wss://api.sahool.app/api/v1/ws';
const token = Cookies.get('access_token') || '';
const socket = new SahoolWebSocket(wsUrl, token);

// Subscribe to events
socket.subscribe('sensor_reading', (data) => {
  console.log('New sensor reading:', data);
});

socket.subscribe('alert', (data) => {
  console.log('New alert:', data);
});

socket.connect();
```

### React Hook for WebSocket

```typescript
// hooks/useWebSocket.ts
import { useEffect, useRef, useCallback, useState } from 'react';
import Cookies from 'js-cookie';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  events?: string[];
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const token = Cookies.get('access_token');
    if (!token) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}?token=${token}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setIsConnected(true);
      // Subscribe to specific events
      if (options.events?.length) {
        wsRef.current?.send(JSON.stringify({
          type: 'subscribe',
          events: options.events,
        }));
      }
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        options.onMessage?.(data);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
    };
  }, [options]);

  const send = useCallback((type: string, payload: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { isConnected, send, disconnect };
}
```

---

## React Query Patterns

### Query Client Setup

```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes (formerly cacheTime)
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

### Custom Query Hooks

```typescript
// features/fields/hooks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fieldsApi } from './api';
import type { Field, FieldFormData, FieldFilters } from './types';

export const fieldKeys = {
  all: ['fields'] as const,
  lists: () => [...fieldKeys.all, 'list'] as const,
  list: (filters: FieldFilters) => [...fieldKeys.lists(), filters] as const,
  details: () => [...fieldKeys.all, 'detail'] as const,
  detail: (id: string) => [...fieldKeys.details(), id] as const,
  stats: () => [...fieldKeys.all, 'stats'] as const,
};

export function useFields(filters?: FieldFilters) {
  return useQuery({
    queryKey: fieldKeys.list(filters || {}),
    queryFn: () => fieldsApi.getFields(filters),
    staleTime: 2 * 60 * 1000,
  });
}

export function useField(id: string) {
  return useQuery({
    queryKey: fieldKeys.detail(id),
    queryFn: () => fieldsApi.getFieldById(id),
    enabled: !!id,
  });
}

export function useCreateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FieldFormData) => fieldsApi.createField(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
  });
}

export function useUpdateField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<FieldFormData> }) =>
      fieldsApi.updateField(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: fieldKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
    },
  });
}

export function useDeleteField() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => fieldsApi.deleteField(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fieldKeys.lists() });
      queryClient.invalidateQueries({ queryKey: fieldKeys.stats() });
    },
  });
}

export function useFieldStats(farmId?: string) {
  return useQuery({
    queryKey: [...fieldKeys.stats(), farmId],
    queryFn: () => fieldsApi.getStats(farmId),
  });
}
```

### Optimistic Updates

```typescript
// Example with optimistic update
export function useToggleAlertRule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      alertRulesApi.toggleAlertRule(id, enabled),
    onMutate: async ({ id, enabled }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['alert-rules'] });

      // Snapshot previous value
      const previousRules = queryClient.getQueryData<AlertRule[]>(['alert-rules']);

      // Optimistically update
      queryClient.setQueryData<AlertRule[]>(['alert-rules'], (old) =>
        old?.map((rule) =>
          rule.id === id ? { ...rule, enabled } : rule
        )
      );

      return { previousRules };
    },
    onError: (err, _, context) => {
      // Rollback on error
      if (context?.previousRules) {
        queryClient.setQueryData(['alert-rules'], context.previousRules);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['alert-rules'] });
    },
  });
}
```

---

## Admin Dashboard Specifics

### Circuit Breaker Pattern

The admin dashboard implements a circuit breaker pattern for service resilience:

```typescript
// lib/circuit-breaker.ts
interface CircuitBreakerState {
  failures: number;
  lastFailure: number;
  state: 'closed' | 'open' | 'half-open';
}

class CircuitBreaker {
  private state: CircuitBreakerState = {
    failures: 0,
    lastFailure: 0,
    state: 'closed',
  };

  private failureThreshold = 5;
  private recoveryTimeout = 30000; // 30 seconds

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state.state === 'open') {
      if (Date.now() - this.state.lastFailure > this.recoveryTimeout) {
        this.state.state = 'half-open';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.state = {
      failures: 0,
      lastFailure: 0,
      state: 'closed',
    };
  }

  private onFailure() {
    this.state.failures++;
    this.state.lastFailure = Date.now();

    if (this.state.failures >= this.failureThreshold) {
      this.state.state = 'open';
    }
  }
}
```

### Service Health Check

```typescript
// lib/api-gateway/index.ts
export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'degraded';
  latency?: number;
  lastCheck: string;
  error?: string;
}

export async function checkServiceHealth(serviceName: string): Promise<ServiceHealth> {
  const startTime = Date.now();

  try {
    const config = getServiceConfig(serviceName);
    const response = await fetch(`${config.baseUrl}/healthz`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });

    const latency = Date.now() - startTime;

    if (response.ok) {
      return {
        name: serviceName,
        status: latency > 2000 ? 'degraded' : 'healthy',
        latency,
        lastCheck: new Date().toISOString(),
      };
    }

    return {
      name: serviceName,
      status: 'unhealthy',
      latency,
      lastCheck: new Date().toISOString(),
      error: `HTTP ${response.status}`,
    };
  } catch (error) {
    return {
      name: serviceName,
      status: 'unhealthy',
      lastCheck: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

export async function checkAllServicesHealth(): Promise<ServiceHealth[]> {
  const services = getAllServices();
  return Promise.all(services.map(checkServiceHealth));
}
```

### Admin Role-Based Access

```typescript
// components/auth/AuthGuard.tsx
import { useAuth } from '@/stores/auth.store';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRoles?: ('admin' | 'supervisor' | 'viewer')[];
}

export function AuthGuard({ children, requiredRoles }: AuthGuardProps) {
  const { user, isAuthenticated, isLoading, checkAuth } = useAuth();
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Check role-based access
  if (requiredRoles && user && !requiredRoles.includes(user.role)) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
          <p className="text-gray-600 mt-2">
            You don't have permission to access this page.
          </p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : null;
}
```

---

## Complete Feature API Example

### IoT Feature API (Web App)

```typescript
// features/iot/api.ts
import axios from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const sensorsApi = {
  getSensors: async (filters?: SensorFilters): Promise<Sensor[]> => {
    const params = new URLSearchParams();
    if (filters?.type) params.set('type', filters.type);
    if (filters?.status) params.set('status', filters.status);
    if (filters?.fieldId) params.set('field_id', filters.fieldId);

    const response = await api.get(`/api/v1/iot/sensors?${params.toString()}`);
    return response.data.data || response.data;
  },

  getSensorById: async (id: string): Promise<Sensor> => {
    const response = await api.get(`/api/v1/iot/sensors/${id}`);
    return response.data.data || response.data;
  },

  createSensor: async (data: CreateSensorData): Promise<Sensor> => {
    const response = await api.post('/api/v1/iot/sensors', data);
    return response.data.data || response.data;
  },

  getSensorReadings: async (query: ReadingsQuery): Promise<SensorReading[]> => {
    const params = new URLSearchParams();
    params.set('sensor_id', query.sensorId);
    if (query.startDate) params.set('start_date', query.startDate);
    if (query.endDate) params.set('end_date', query.endDate);

    const response = await api.get(`/api/v1/iot/sensors/readings?${params.toString()}`);
    return response.data.data || response.data;
  },

  getStreamUrl: (sensorId?: string): string => {
    const params = sensorId ? `?sensor_id=${sensorId}` : '';
    return `${api.defaults.baseURL}/api/v1/iot/sensors/stream${params}`;
  },
};

export const actuatorsApi = {
  getActuators: async (fieldId?: string): Promise<Actuator[]> => {
    const params = fieldId ? `?field_id=${fieldId}` : '';
    const response = await api.get(`/api/v1/iot/actuators${params}`);
    return response.data.data || response.data;
  },

  controlActuator: async (data: ActuatorControlData): Promise<Actuator> => {
    const response = await api.post(`/api/v1/iot/actuators/${data.actuatorId}/control`, {
      action: data.action,
      mode: data.mode,
      duration: data.duration,
    });
    return response.data.data || response.data;
  },
};
```

---

## CORS Configuration

Kong is configured to allow requests from:

| Origin | Environment |
|--------|-------------|
| `https://sahool.app` | Production |
| `https://www.sahool.app` | Production |
| `https://admin.sahool.app` | Admin Production |
| `https://api.sahool.app` | API Production |
| `https://staging.sahool.app` | Staging |
| `http://localhost:3000` | Development |
| `http://localhost:5173` | Development (Vite) |
| `http://localhost:8080` | Development |

### Allowed Headers

- `Accept`, `Accept-Version`
- `Content-Length`, `Content-MD5`, `Content-Type`
- `Date`, `Authorization`, `X-Auth-Token`

### Exposed Headers

- `X-Request-ID`

---

## Security Headers

Kong automatically adds these security headers to all responses:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; ...
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

## Best Practices

### 1. Always Use Type-Safe API Calls

```typescript
// Good
const fields = await fieldsApi.getFields(filters);

// Bad - avoid untyped fetch
const response = await fetch('/api/v1/fields');
```

### 2. Handle Loading and Error States

```typescript
function FieldList() {
  const { data: fields, isLoading, error } = useFields();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  return <FieldGrid fields={fields} />;
}
```

### 3. Use Bilingual Error Messages

```typescript
const locale = useLocale(); // 'ar' or 'en'

try {
  await fieldsApi.createField(data);
} catch (error) {
  const msg = JSON.parse(error.message);
  showToast(locale === 'ar' ? msg.messageAr : msg.message);
}
```

### 4. Implement Offline Support with Mock Data

```typescript
export const fieldsApi = {
  getFields: async (filters?: FieldFilters): Promise<Field[]> => {
    try {
      const response = await api.get(`/api/v1/fields`);
      return response.data.data || response.data;
    } catch (error) {
      console.warn('Failed to fetch fields, using mock data');
      return MOCK_FIELDS;
    }
  },
};
```

### 5. Use Correlation IDs for Debugging

Kong adds `X-Request-ID` to all requests. Include it in error reports:

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestId = error.response?.headers?.['x-request-id'];
    console.error(`Request failed [${requestId}]:`, error);
    return Promise.reject(error);
  }
);
```

---

## Quick Reference

### API Base URLs

| Environment | URL |
|-------------|-----|
| Production | `https://api.sahool.app` |
| Admin | `https://admin.sahool.app/api` |
| Staging | `https://staging.api.sahool.app` |
| Development | `http://localhost:8000` |

### Common HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 201 | Created | Process response |
| 400 | Bad Request | Show validation errors |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show access denied |
| 404 | Not Found | Show not found message |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Show error, retry |

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/kafaat/sahool-unified/issues
- Documentation: https://docs.sahool.app
- Email: api-support@sahool.app

---

**Note:** This guide is intended for developers working on SAHOOL web applications. Keep this document updated as APIs evolve.
