import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth, useCan, useCanAny, useHasRole } from './useAuth';
import type { ReactNode } from 'react';

// Mock user data
const mockUser = {
  id: 'user-123',
  email: 'farmer@sahool.sa',
  name: 'أحمد المزارع',
  roles: ['farmer'],
  permissions: ['field:view', 'field:create', 'ndvi:view', 'alert:view'],
  tenantId: 'tenant-456',
};

const mockAdminUser = {
  id: 'admin-123',
  email: 'admin@sahool.sa',
  name: 'مدير النظام',
  roles: ['admin'],
  permissions: ['field:view', 'field:create', 'field:edit', 'field:delete', 'admin:users', 'admin:settings'],
  tenantId: 'tenant-456',
};

// Create wrapper with providers
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <AuthProvider>{children}</AuthProvider>
      </QueryClientProvider>
    );
  };
}

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.getItem.mockReturnValue(null);
  });

  it('should return unauthenticated state initially', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(result.current.isLoading).toBe(true);
  });

  it('should load user from token on mount', async () => {
    localStorage.getItem.mockReturnValue('valid-token');
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
  });

  it('should handle login successfully', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ token: 'new-token', user: mockUser }),
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.login('farmer@sahool.sa', 'password123');
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
  });

  it('should handle login failure', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ message: 'Invalid credentials' }),
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    await expect(
      act(async () => {
        await result.current.login('wrong@email.com', 'wrongpass');
      })
    ).rejects.toThrow();

    expect(result.current.isAuthenticated).toBe(false);
  });

  it('should handle logout', async () => {
    localStorage.getItem.mockReturnValue('valid-token');
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
    });

    act(() => {
      result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});

describe('useCan', () => {
  beforeEach(() => {
    localStorage.getItem.mockReturnValue('valid-token');
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });
  });

  it('should return true when user has permission', async () => {
    const { result } = renderHook(() => useCan('field:view'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(true);
    });
  });

  it('should return false when user lacks permission', async () => {
    const { result } = renderHook(() => useCan('admin:users'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(false);
    });
  });
});

describe('useCanAny', () => {
  beforeEach(() => {
    localStorage.getItem.mockReturnValue('valid-token');
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });
  });

  it('should return true when user has any permission', async () => {
    const { result } = renderHook(() => useCanAny(['field:view', 'admin:users']), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(true);
    });
  });

  it('should return false when user has none of the permissions', async () => {
    const { result } = renderHook(() => useCanAny(['admin:users', 'admin:settings']), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(false);
    });
  });
});

describe('useHasRole', () => {
  beforeEach(() => {
    localStorage.getItem.mockReturnValue('valid-token');
  });

  it('should return true when user has the role', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    const { result } = renderHook(() => useHasRole('farmer'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(true);
    });
  });

  it('should return false when user lacks the role', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    });

    const { result } = renderHook(() => useHasRole('admin'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(false);
    });
  });

  it('should return true for admin user with admin role', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockAdminUser),
    });

    const { result } = renderHook(() => useHasRole('admin'), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current).toBe(true);
    });
  });
});
