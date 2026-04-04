/**
 * Comprehensive Tests for Admin API Hooks
 * اختبارات شاملة لخطافات API الإدارية
 *
 * Tests: use-alerts, use-notifications, use-realtime, use-tasks
 * Uses fs.readFileSync source analysis pattern.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import * as fs from 'fs';
import * as path from 'path';
import { invalidateQueries } from '../use-api-query';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

vi.mock('@/lib/api', () => ({
  fetchAlerts: vi.fn().mockResolvedValue([
    { id: 'a1', severity: 'high', type: 'pest', message: 'Red Palm Weevil detected', acknowledged: false },
    { id: 'a2', severity: 'medium', type: 'weather', message: 'Frost warning', acknowledged: true },
  ]),
  apiClient: {
    patch: vi.fn().mockResolvedValue({ data: { id: 'a1', acknowledged: true } }),
    post: vi.fn().mockResolvedValue({
      data: { id: 't1', title: 'New Task', status: 'pending' },
    }),
    get: vi.fn().mockResolvedValue({ data: [] }),
  },
  API_URLS: {
    alerts: 'http://localhost:8113',
    taskEndpoints: {
      create: 'http://localhost:8103/api/v1/tasks',
    },
  },
  fetchNotifications: vi.fn().mockResolvedValue([
    { id: 'n1', type: 'alert', priority: 'high', read: false },
    { id: 'n2', type: 'info', priority: 'low', read: true },
  ]),
  markNotificationRead: vi.fn().mockResolvedValue(undefined),
  fetchTasks: vi.fn().mockResolvedValue([
    { id: 't1', status: 'pending', type: 'irrigation', title: 'Check valves' },
    { id: 't2', status: 'completed', type: 'inspection', title: 'Field visit' },
  ]),
  updateTaskStatus: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('@/hooks/useWebSocket', () => ({
  useWebSocket: vi.fn().mockReturnValue({
    isConnected: true,
    subscribe: vi.fn((_event: string, _callback: () => void) => {
      return vi.fn(); // unsubscribe function
    }),
  }),
}));

// ═══════════════════════════════════════════════════════════════════════════
// Helper: read source file
// ═══════════════════════════════════════════════════════════════════════════

const HOOKS_DIR = path.resolve(__dirname, '..');

function readHookSource(filename: string): string {
  return fs.readFileSync(path.join(HOOKS_DIR, filename), 'utf-8');
}

// ═══════════════════════════════════════════════════════════════════════════
// 1. use-alerts.ts — خطافات التنبيهات
// ═══════════════════════════════════════════════════════════════════════════

describe('use-alerts source analysis', () => {
  const source = readHookSource('use-alerts.ts');

  it('file exists and is non-empty', () => {
    expect(source.length).toBeGreaterThan(0);
  });

  it('exports useAlerts named export', () => {
    expect(source).toContain('export function useAlerts');
  });

  it('exports useAcknowledgeAlert named export', () => {
    expect(source).toContain('export function useAcknowledgeAlert');
  });

  it('imports useApiQuery and useApiMutation from use-api-query', () => {
    expect(source).toContain("import { useApiQuery, useApiMutation } from './use-api-query'");
  });

  it('imports fetchAlerts from @/lib/api', () => {
    expect(source).toContain('fetchAlerts');
  });

  it('imports apiClient from @/lib/api', () => {
    expect(source).toContain('apiClient');
  });

  it('imports API_URLS from @/config/api', () => {
    expect(source).toContain("import { API_URLS } from '@/config/api'");
  });

  it('has use client directive', () => {
    expect(source).toContain("'use client'");
  });

  it('useAlerts accepts optional severity parameter', () => {
    expect(source).toContain('severity?: string');
  });

  it('useAlerts accepts optional type parameter', () => {
    expect(source).toContain('type?: string');
  });

  it('useAlerts accepts optional acknowledged parameter', () => {
    expect(source).toContain('acknowledged?: boolean');
  });

  it('useAlerts accepts optional limit parameter', () => {
    expect(source).toContain('limit?: number');
  });

  it('useAlerts sets refetchInterval to 30000ms', () => {
    expect(source).toContain('refetchInterval: 30000');
  });

  it('useAlerts sets staleTime to 15000ms', () => {
    expect(source).toContain('staleTime: 15000');
  });

  it('useAcknowledgeAlert uses post method on alerts endpoint', () => {
    expect(source).toContain('apiClient.post');
    expect(source).toContain('/acknowledge');
  });

  it('useAcknowledgeAlert invalidates alerts cache key', () => {
    expect(source).toContain("invalidateKeys: ['alerts']");
  });

  it('uses alerts query key', () => {
    expect(source).toContain("['alerts'");
  });
});

describe('useAlerts hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns alert data on success', async () => {
    const { useAlerts } = await import('../use-alerts');
    const { result } = renderHook(() => useAlerts());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0]).toHaveProperty('id', 'a1');
    expect(result.current.data?.[0]).toHaveProperty('severity', 'high');
  });

  it('accepts filter parameters', async () => {
    const { fetchAlerts } = await import('@/lib/api');
    const { useAlerts } = await import('../use-alerts');

    renderHook(() => useAlerts({ severity: 'high', type: 'pest' }));

    await waitFor(() => {
      expect(fetchAlerts).toHaveBeenCalledWith({ severity: 'high', type: 'pest' });
    });
  });

  it('uses useApiQuery for data fetching', () => {
    const content = fs.readFileSync(path.resolve(__dirname, '../use-alerts.ts'), 'utf-8');
    expect(content).toContain('useApiQuery');
    expect(content).toMatch(/return.*data|response\.data/);
  });
});

describe('useAcknowledgeAlert hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns mutate function', async () => {
    const { useAcknowledgeAlert } = await import('../use-alerts');
    const { result } = renderHook(() => useAcknowledgeAlert());

    expect(result.current).toHaveProperty('mutate');
    expect(typeof result.current.mutate).toBe('function');
  });

  it('returns mutation state properties', async () => {
    const { useAcknowledgeAlert } = await import('../use-alerts');
    const { result } = renderHook(() => useAcknowledgeAlert());

    expect(result.current).toHaveProperty('isLoading');
    expect(result.current).toHaveProperty('isError');
    expect(result.current).toHaveProperty('isSuccess');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 2. use-notifications.ts — خطافات الإشعارات
// ═══════════════════════════════════════════════════════════════════════════

describe('use-notifications source analysis', () => {
  const source = readHookSource('use-notifications.ts');

  it('file exists and is non-empty', () => {
    expect(source.length).toBeGreaterThan(0);
  });

  it('exports useNotifications named export', () => {
    expect(source).toContain('export function useNotifications');
  });

  it('exports useMarkNotificationRead named export', () => {
    expect(source).toContain('export function useMarkNotificationRead');
  });

  it('imports useApiQuery, useApiMutation, and invalidateQueries', () => {
    expect(source).toContain('useApiQuery');
    expect(source).toContain('useApiMutation');
    expect(source).toContain('invalidateQueries');
  });

  it('imports fetchNotifications from @/lib/api', () => {
    expect(source).toContain('fetchNotifications');
  });

  it('imports markNotificationRead from @/lib/api', () => {
    expect(source).toContain('markNotificationRead');
  });

  it('has use client directive', () => {
    expect(source).toContain("'use client'");
  });

  it('useNotifications accepts optional type parameter', () => {
    expect(source).toContain('type?: string');
  });

  it('useNotifications accepts optional priority parameter', () => {
    expect(source).toContain('priority?: string');
  });

  it('useNotifications accepts optional limit parameter', () => {
    expect(source).toContain('limit?: number');
  });

  it('sets refetchInterval to 30000ms', () => {
    expect(source).toContain('refetchInterval: 30000');
  });

  it('sets staleTime to 15000ms', () => {
    expect(source).toContain('staleTime: 15000');
  });

  it('useMarkNotificationRead invalidates notifications cache', () => {
    expect(source).toContain("invalidateKeys: ['notifications']");
  });

  it('useMarkNotificationRead also invalidates dashboard cache on success', () => {
    expect(source).toContain("invalidateQueries('dashboard')");
  });

  it('uses notifications query key', () => {
    expect(source).toContain("['notifications'");
  });
});

describe('useNotifications hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns notification data on success', async () => {
    const { useNotifications } = await import('../use-notifications');
    const { result } = renderHook(() => useNotifications());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0]).toHaveProperty('id', 'n1');
  });

  it('passes filter params to fetch function', async () => {
    const { fetchNotifications } = await import('@/lib/api');
    const { useNotifications } = await import('../use-notifications');

    renderHook(() => useNotifications({ type: 'alert', priority: 'high' }));

    await waitFor(() => {
      expect(fetchNotifications).toHaveBeenCalledWith({ type: 'alert', priority: 'high' });
    });
  });
});

describe('useMarkNotificationRead hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns mutate function', async () => {
    const { useMarkNotificationRead } = await import('../use-notifications');
    const { result } = renderHook(() => useMarkNotificationRead());

    expect(result.current).toHaveProperty('mutate');
    expect(typeof result.current.mutate).toBe('function');
  });

  it('returns standard mutation state', async () => {
    const { useMarkNotificationRead } = await import('../use-notifications');
    const { result } = renderHook(() => useMarkNotificationRead());

    expect(result.current).toHaveProperty('isLoading');
    expect(result.current).toHaveProperty('isError');
    expect(result.current).toHaveProperty('isSuccess');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 3. use-realtime.ts — خطاف البيانات اللحظية
// ═══════════════════════════════════════════════════════════════════════════

describe('use-realtime source analysis', () => {
  const source = readHookSource('use-realtime.ts');

  it('file exists and is non-empty', () => {
    expect(source.length).toBeGreaterThan(0);
  });

  it('exports useRealtimeSync named export', () => {
    expect(source).toContain('export function useRealtimeSync');
  });

  it('imports useEffect and useRef from react', () => {
    expect(source).toContain('useEffect');
    expect(source).toContain('useRef');
  });

  it('imports useWebSocket hook', () => {
    expect(source).toContain("import { useWebSocket } from '@/hooks/useWebSocket'");
  });

  it('imports invalidateQueries from use-api-query', () => {
    expect(source).toContain("import { invalidateQueries } from './use-api-query'");
  });

  it('has use client directive', () => {
    expect(source).toContain("'use client'");
  });

  it('defines RealtimeEvent type with all expected event types', () => {
    expect(source).toContain("'alert'");
    expect(source).toContain("'sensor'");
    expect(source).toContain("'irrigation'");
    expect(source).toContain("'diagnosis'");
    expect(source).toContain("'farm_update'");
    expect(source).toContain("'weather'");
    expect(source).toContain("'task'");
  });

  it('defines EVENT_TO_CACHE_KEYS mapping', () => {
    expect(source).toContain('EVENT_TO_CACHE_KEYS');
  });

  it('maps alert events to alerts and dashboard cache keys', () => {
    expect(source).toContain("alert: ['alerts', 'dashboard']");
  });

  it('maps sensor events to sensors and fields cache keys', () => {
    expect(source).toContain("sensor: ['sensors', 'fields']");
  });

  it('maps irrigation events to irrigation and fields cache keys', () => {
    expect(source).toContain("irrigation: ['irrigation', 'fields']");
  });

  it('maps weather events to weather cache key', () => {
    expect(source).toContain("weather: ['weather']");
  });

  it('maps task events to tasks cache key', () => {
    expect(source).toContain("task: ['tasks']");
  });

  it('returns isConnected property', () => {
    expect(source).toContain('return { isConnected }');
  });

  it('uses autoConnect: true for WebSocket', () => {
    expect(source).toContain('autoConnect: true');
  });

  it('cleans up subscriptions on unmount', () => {
    expect(source).toContain('return () => {');
    expect(source).toContain('unsubscribers.forEach');
  });

  it('uses ref to avoid re-subscriptions', () => {
    expect(source).toContain('useRef(events)');
  });
});

describe('useRealtimeSync hook behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns isConnected state', async () => {
    const { useRealtimeSync } = await import('../use-realtime');
    const { result } = renderHook(() => useRealtimeSync(['alert', 'task']));

    expect(result.current).toHaveProperty('isConnected');
    expect(result.current.isConnected).toBe(true);
  });

  it('subscribes to specified events when connected', async () => {
    const { useWebSocket } = await import('@/hooks/useWebSocket');
    const subscribeFn = vi.fn(() => vi.fn());
    (useWebSocket as ReturnType<typeof vi.fn>).mockReturnValue({
      isConnected: true,
      subscribe: subscribeFn,
    });

    const { useRealtimeSync } = await import('../use-realtime');
    renderHook(() => useRealtimeSync(['alert', 'weather']));

    await waitFor(() => {
      expect(subscribeFn).toHaveBeenCalledWith('alert', expect.any(Function));
      expect(subscribeFn).toHaveBeenCalledWith('weather', expect.any(Function));
    });
  });

  it('does not subscribe when disconnected', async () => {
    const { useWebSocket } = await import('@/hooks/useWebSocket');
    const subscribeFn = vi.fn(() => vi.fn());
    (useWebSocket as ReturnType<typeof vi.fn>).mockReturnValue({
      isConnected: false,
      subscribe: subscribeFn,
    });

    const { useRealtimeSync } = await import('../use-realtime');
    renderHook(() => useRealtimeSync(['alert']));

    expect(subscribeFn).not.toHaveBeenCalled();
  });

  it('subscribes to all events when empty array passed', async () => {
    const { useWebSocket } = await import('@/hooks/useWebSocket');
    const subscribeFn = vi.fn(() => vi.fn());
    (useWebSocket as ReturnType<typeof vi.fn>).mockReturnValue({
      isConnected: true,
      subscribe: subscribeFn,
    });

    const { useRealtimeSync } = await import('../use-realtime');
    renderHook(() => useRealtimeSync([]));

    await waitFor(() => {
      // Should subscribe to all 7 event types
      expect(subscribeFn).toHaveBeenCalledTimes(7);
    });
  });

  it('cleans up subscriptions on unmount', async () => {
    const unsubFn = vi.fn();
    const { useWebSocket } = await import('@/hooks/useWebSocket');
    (useWebSocket as ReturnType<typeof vi.fn>).mockReturnValue({
      isConnected: true,
      subscribe: vi.fn(() => unsubFn),
    });

    const { useRealtimeSync } = await import('../use-realtime');
    const { unmount } = renderHook(() => useRealtimeSync(['alert']));

    unmount();

    expect(unsubFn).toHaveBeenCalled();
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 4. use-tasks.ts — خطافات إدارة المهام
// ═══════════════════════════════════════════════════════════════════════════

describe('use-tasks source analysis', () => {
  const source = readHookSource('use-tasks.ts');

  it('file exists and is non-empty', () => {
    expect(source.length).toBeGreaterThan(0);
  });

  it('exports useTasks named export', () => {
    expect(source).toContain('export function useTasks');
  });

  it('exports useUpdateTaskStatus named export', () => {
    expect(source).toContain('export function useUpdateTaskStatus');
  });

  it('exports useCreateTask named export', () => {
    expect(source).toContain('export function useCreateTask');
  });

  it('imports useApiQuery and useApiMutation from use-api-query', () => {
    expect(source).toContain("import { useApiQuery, useApiMutation } from './use-api-query'");
  });

  it('imports fetchTasks and updateTaskStatus from @/lib/api', () => {
    expect(source).toContain('fetchTasks');
    expect(source).toContain('updateTaskStatus');
  });

  it('imports apiClient from @/lib/api', () => {
    expect(source).toContain('apiClient');
  });

  it('imports API_URLS from @/config/api', () => {
    expect(source).toContain("import { API_URLS } from '@/config/api'");
  });

  it('has use client directive', () => {
    expect(source).toContain("'use client'");
  });

  it('useTasks accepts optional status parameter', () => {
    expect(source).toContain('status?: string');
  });

  it('useTasks accepts optional type parameter', () => {
    expect(source).toContain('type?: string');
  });

  it('useTasks accepts optional assignedTo parameter', () => {
    expect(source).toContain('assignedTo?: string');
  });

  it('useTasks accepts optional limit parameter', () => {
    expect(source).toContain('limit?: number');
  });

  it('useTasks sets staleTime to 30000ms', () => {
    expect(source).toContain('staleTime: 30000');
  });

  it('useUpdateTaskStatus invalidates tasks cache', () => {
    expect(source).toContain("invalidateKeys: ['tasks']");
  });

  it('useCreateTask accepts title, type, and priority as required fields', () => {
    expect(source).toContain('title: string');
    expect(source).toContain('type: string');
    expect(source).toContain('priority: string');
  });

  it('useCreateTask accepts optional description, assignedTo, fieldId, dueDate', () => {
    expect(source).toContain('description?: string');
    expect(source).toContain('assignedTo?: string');
    expect(source).toContain('fieldId?: string');
    expect(source).toContain('dueDate?: string');
  });

  it('useCreateTask uses apiClient.post to taskEndpoints.create', () => {
    expect(source).toContain('apiClient.post');
    expect(source).toContain('API_URLS.taskEndpoints.create');
  });

  it('uses tasks query key', () => {
    expect(source).toContain("['tasks'");
  });

  it('useUpdateTaskStatus accepts id and status parameters', () => {
    expect(source).toContain('id: string; status: string');
  });
});

describe('useTasks hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns task data on success', async () => {
    const { useTasks } = await import('../use-tasks');
    const { result } = renderHook(() => useTasks());

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toHaveLength(2);
    expect(result.current.data?.[0]).toHaveProperty('id', 't1');
    expect(result.current.data?.[0]).toHaveProperty('status', 'pending');
  });

  it('passes filter params to fetchTasks', async () => {
    const { fetchTasks } = await import('@/lib/api');
    const { useTasks } = await import('../use-tasks');

    renderHook(() => useTasks({ status: 'pending', assignedTo: 'user-1' }));

    await waitFor(() => {
      expect(fetchTasks).toHaveBeenCalledWith({ status: 'pending', assignedTo: 'user-1' });
    });
  });

  it('returns standard query result shape', async () => {
    const { useTasks } = await import('../use-tasks');
    const { result } = renderHook(() => useTasks());

    expect(result.current).toHaveProperty('data');
    expect(result.current).toHaveProperty('error');
    expect(result.current).toHaveProperty('isLoading');
    expect(result.current).toHaveProperty('isError');
    expect(result.current).toHaveProperty('isSuccess');
    expect(result.current).toHaveProperty('refetch');
  });
});

describe('useUpdateTaskStatus hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns mutate function', async () => {
    const { useUpdateTaskStatus } = await import('../use-tasks');
    const { result } = renderHook(() => useUpdateTaskStatus());

    expect(result.current).toHaveProperty('mutate');
    expect(typeof result.current.mutate).toBe('function');
  });
});

describe('useCreateTask hook behavior', () => {
  beforeEach(() => {
    invalidateQueries('');
    vi.clearAllMocks();
  });

  it('returns mutate function', async () => {
    const { useCreateTask } = await import('../use-tasks');
    const { result } = renderHook(() => useCreateTask());

    expect(result.current).toHaveProperty('mutate');
    expect(typeof result.current.mutate).toBe('function');
  });

  it('returns mutation state properties', async () => {
    const { useCreateTask } = await import('../use-tasks');
    const { result } = renderHook(() => useCreateTask());

    expect(result.current).toHaveProperty('isLoading');
    expect(result.current).toHaveProperty('isError');
    expect(result.current).toHaveProperty('isSuccess');
    expect(result.current).toHaveProperty('data');
    expect(result.current).toHaveProperty('error');
  });
});
