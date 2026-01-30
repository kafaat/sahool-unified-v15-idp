# Admin App Migration Guide - SAHOOL v16.0.0

**Target App:** `apps/admin` (Next.js 16 with Turbopack)  
**Last Updated:** 2026-01-30  
**Migration Goal:** Replace static data with dynamic API integration

---

## 🎯 Migration Overview

The admin app currently uses **static/mock data** for all displays. This guide provides step-by-step instructions for the Antigravity coding agent to make the admin app fully dynamic by integrating with backend services via Kong Gateway.

---

## 📋 Current Static Data Issues

### 1. User Management
- **Current:** Hardcoded user list in component state
- **Target:** Dynamic user data from `user-service:3025`
- **Impact:** HIGH - Core functionality

### 2. Dashboard Metrics
- **Current:** Static numbers (e.g., "1,234 fields", "567 users")
- **Target:** Real-time metrics from multiple services
- **Impact:** HIGH - Executive visibility

### 3. Field Management
- **Current:** Mock field data with fake coordinates
- **Target:** Real field data from `field-management-service:3000`
- **Impact:** HIGH - Core functionality

### 4. Weather Display
- **Current:** Static weather widget
- **Target:** Live weather from `weather-service:8092`
- **Impact:** MEDIUM - User experience

### 5. Crop Information
- **Current:** Hardcoded crop types and health status
- **Target:** Dynamic crop data from `crop-intelligence-service:8095`
- **Impact:** MEDIUM - Operational data

### 6. Notifications
- **Current:** Mock notification list
- **Target:** Real notifications from `notification-service:8110`
- **Impact:** MEDIUM - User engagement

---

## 🚀 Migration Strategy

### Phase 1: Authentication Integration (Week 1)

#### 1.1 Setup API Client

**File:** `apps/admin/src/lib/api-client.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });
        
        const { access_token } = response.data;
        localStorage.setItem('accessToken', access_token);
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

#### 1.2 Create Auth Hook

**File:** `apps/admin/src/hooks/use-auth.ts`

```typescript
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await apiClient.get('/api/v1/auth/me');
      setUser(response.data);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/api/v1/auth/login', {
      email,
      password,
    });
    
    const { access_token, refresh_token, user } = response.data;
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    setUser(user);
    
    return user;
  };

  const logout = async () => {
    try {
      await apiClient.post('/api/v1/auth/logout');
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      window.location.href = '/login';
    }
  };

  return { user, loading, login, logout };
}
```

#### 1.3 Update Login Page

**File:** `apps/admin/src/app/login/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">SAHOOL Admin</h2>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

### Phase 2: Dynamic Data Integration (Week 2-3)

#### 2.1 User Management

**File:** `apps/admin/src/hooks/use-users.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  created_at: string;
  is_active: boolean;
}

export function useUsers(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['users', page, limit],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/users', {
        params: { page, limit },
      });
      return response.data;
    },
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: Partial<User>) => {
      const response = await apiClient.post('/api/v1/users', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<User> }) => {
      const response = await apiClient.put(`/api/v1/users/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/users/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

**File:** `apps/admin/src/app/users/page.tsx`

```typescript
'use client';

import { useUsers, useDeleteUser } from '@/hooks/use-users';

export default function UsersPage() {
  const { data, isLoading, error } = useUsers();
  const deleteUser = useDeleteUser();

  if (isLoading) return <div>Loading users...</div>;
  if (error) return <div>Error loading users</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">User Management</h1>
      
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Email
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Role
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data?.users?.map((user: any) => (
            <tr key={user.id}>
              <td className="px-6 py-4 whitespace-nowrap">{user.name}</td>
              <td className="px-6 py-4 whitespace-nowrap">{user.email}</td>
              <td className="px-6 py-4 whitespace-nowrap">{user.role}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  onClick={() => deleteUser.mutate(user.id)}
                  className="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

#### 2.2 Dashboard Metrics

**File:** `apps/admin/src/hooks/use-dashboard.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useDashboardMetrics() {
  return useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      // Fetch metrics from multiple services in parallel
      const [users, fields, tasks, alerts] = await Promise.all([
        apiClient.get('/api/v1/users/stats'),
        apiClient.get('/api/v1/fields/stats'),
        apiClient.get('/api/v1/tasks/stats'),
        apiClient.get('/api/v1/alerts/stats'),
      ]);

      return {
        users: users.data,
        fields: fields.data,
        tasks: tasks.data,
        alerts: alerts.data,
      };
    },
    refetchInterval: 60000, // Refresh every minute
  });
}
```

#### 2.3 Field Management

**File:** `apps/admin/src/hooks/use-fields.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function useFields(filters = {}) {
  return useQuery({
    queryKey: ['fields', filters],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/fields', {
        params: filters,
      });
      return response.data;
    },
  });
}

export function useFieldDetails(id: string) {
  return useQuery({
    queryKey: ['field', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/fields/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useFieldNDVI(id: string) {
  return useQuery({
    queryKey: ['field-ndvi', id],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v1/fields/${id}/ndvi`);
      return response.data;
    },
    enabled: !!id,
  });
}
```

#### 2.4 Weather Widget

**File:** `apps/admin/src/components/weather-widget.tsx`

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function WeatherWidget({ lat, lon }: { lat: number; lon: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['weather', lat, lon],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/weather/current', {
        params: { lat, lon },
      });
      return response.data;
    },
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  if (isLoading) return <div>Loading weather...</div>;

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-2">Current Weather</h3>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-3xl font-bold">{data?.temperature}°C</p>
          <p className="text-gray-600">{data?.description}</p>
        </div>
        <div className="text-right">
          <p className="text-sm">Humidity: {data?.humidity}%</p>
          <p className="text-sm">Wind: {data?.wind_speed} m/s</p>
        </div>
      </div>
    </div>
  );
}
```

---

### Phase 3: Real-time Features (Week 4)

#### 3.1 WebSocket Integration

**File:** `apps/admin/src/lib/websocket.ts`

```typescript
import { useEffect, useState } from 'react';

export function useWebSocket(url: string) {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket(url);

    websocket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [...prev, data]);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [url]);

  const send = (data: any) => {
    if (ws && connected) {
      ws.send(JSON.stringify(data));
    }
  };

  return { messages, connected, send };
}
```

#### 3.2 Real-time Notifications

**File:** `apps/admin/src/components/notification-bell.tsx`

```typescript
'use client';

import { useWebSocket } from '@/lib/websocket';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

export function NotificationBell() {
  const { messages } = useWebSocket('ws://localhost:8081/ws');
  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/notifications');
      return response.data;
    },
  });

  const unreadCount = notifications?.filter((n: any) => !n.read).length || 0;

  return (
    <div className="relative">
      <button className="p-2 rounded-full hover:bg-gray-100">
        <BellIcon className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>
    </div>
  );
}
```

---

## 🔧 Environment Configuration

**File:** `apps/admin/.env.local`

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8081

# Feature Flags
NEXT_PUBLIC_ENABLE_REALTIME=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# Sentry (Optional)
NEXT_PUBLIC_SENTRY_DSN=

# Google Maps (Optional)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=
```

---

## ✅ Migration Checklist

### Phase 1: Authentication
- [ ] Create API client with interceptors
- [ ] Implement auth hook
- [ ] Update login page
- [ ] Add protected route wrapper
- [ ] Test login/logout flow

### Phase 2: Dynamic Data
- [ ] User management (CRUD)
- [ ] Dashboard metrics
- [ ] Field management
- [ ] Weather widget
- [ ] Crop intelligence
- [ ] Notification list
- [ ] Task management
- [ ] Inventory management
- [ ] IoT dashboard
- [ ] Billing dashboard

### Phase 3: Real-time
- [ ] WebSocket connection
- [ ] Real-time notifications
- [ ] Live field updates
- [ ] Real-time alerts

### Phase 4: Testing
- [ ] Test all API integrations
- [ ] Test error handling
- [ ] Test token refresh
- [ ] Test WebSocket reconnection
- [ ] Performance testing

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Errors
**Solution:** Kong CORS plugin is configured for `*` in development. Ensure `NEXT_PUBLIC_API_URL` is correct.

### Issue 2: 401 Unauthorized
**Solution:** Check token refresh logic in API client interceptor.

### Issue 3: WebSocket Connection Failed
**Solution:** Ensure `ws-gateway` is running and accessible on port 8081.

### Issue 4: Slow API Responses
**Solution:** Implement loading states and consider caching with React Query.

---

**Last Updated:** 2026-01-30  
**Maintainer:** SAHOOL Platform Team
