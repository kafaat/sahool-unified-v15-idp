/**
 * useAuth Hook Contract Test
 * اختبار عقد خطاف useAuth
 *
 * Verifies that useAuth throws with a specific error message
 * when called outside of AuthProvider.
 *
 * This test lives in its own file to avoid vi.resetModules() calls
 * in auth.store.test.ts corrupting the React.act reference that
 * renderHook depends on.
 */
import { describe, it, expect, vi } from 'vitest';

vi.mock('js-cookie', () => ({
  default: { get: vi.fn(), set: vi.fn(), remove: vi.fn() },
}));

vi.mock('@/lib/logger', () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn() },
}));

vi.mock('@/lib/api/auth-client', () => ({
  authApiClient: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn(),
    attemptTokenRefresh: vi.fn(),
    setToken: vi.fn(),
    clearToken: vi.fn(),
  },
}));

describe('useAuth contract', () => {
  it('should throw when used outside AuthProvider', async () => {
    const { renderHook } = await import('@testing-library/react');
    const { useAuth } = await import('../../stores/auth.store');

    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within AuthProvider');
  });
});
