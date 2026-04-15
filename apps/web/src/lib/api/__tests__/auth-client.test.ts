/**
 * AuthApiClient Tests
 * اختبارات عميل API المصادقة
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock js-cookie before importing the module
vi.mock('js-cookie', () => ({
  default: {
    get: vi.fn(),
    set: vi.fn(),
    remove: vi.fn(),
  },
}));

// Mock logger
vi.mock('../../logger', () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

import Cookies from 'js-cookie';

// We need to test the class directly, so we'll import and re-create
// Since authApiClient is a singleton, we test via the exported instance
describe('AuthApiClient', () => {
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    originalFetch = global.fetch;
    vi.clearAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // LOGIN
  // ═══════════════════════════════════════════════════════════════════════════

  describe('login', () => {
    it('should reject malformed email (contains @ but invalid shape)', async () => {
      // Dynamically import to get fresh instance after mocks.
      // Note: login() now accepts email OR phone. A string containing "@"
      // is treated as an email candidate and validated; strings without "@"
      // are forwarded as phone numbers.
      const { authApiClient } = await import('../auth-client');

      const result = await authApiClient.login('not-an-email@', 'password123');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid email format');
    });

    it('should reject empty identifier', async () => {
      const { authApiClient } = await import('../auth-client');

      const result = await authApiClient.login('', 'password123');

      expect(result.success).toBe(false);
      // Message changed when login was extended to accept phone numbers.
      expect(result.error).toBe('Email or phone is required');
    });

    it('should reject whitespace-only identifier', async () => {
      const { authApiClient } = await import('../auth-client');

      const result = await authApiClient.login('   ', 'password123');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Email or phone is required');
    });

    it('should trim and lowercase email before sending', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () =>
          Promise.resolve({
            success: true,
            data: {
              access_token: 'token123',
              user: { id: '1', email: 'test@sahool.com', name: 'Test', role: 'farmer' },
            },
          }),
      });

      await authApiClient.login('  Test@Sahool.COM  ', 'password123');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"email":"test@sahool.com"'),
        })
      );
    });

    it('should return success with user data on valid login', async () => {
      const { authApiClient } = await import('../auth-client');

      // The /api/v1/auth/login route returns the token/user payload directly
      // (not wrapped in { success, data }). `request()` then returns
      // `{ success: true, data: <parsedJson> }`, so the shape the test
      // mocks here must be the raw backend payload.
      const mockResponse = {
        access_token: 'jwt-token',
        refresh_token: 'refresh-token',
        user: {
          id: 'user-1',
          email: 'farmer@sahool.com',
          name: 'Ahmed',
          role: 'farmer',
        },
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve(mockResponse),
      });

      const result = await authApiClient.login('farmer@sahool.com', 'SecurePass123');

      expect(result.success).toBe(true);
      expect(result.data?.access_token).toBe('jwt-token');
      expect(result.data?.user.email).toBe('farmer@sahool.com');
    });

    it('should return error on server failure', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ error: 'Invalid credentials' }),
      });

      const result = await authApiClient.login('user@sahool.com', 'wrong-pass');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid credentials');
    });

    it('should handle network errors', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockRejectedValue(new Error('Network failure'));

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Network failure');
    });

    it('should handle timeout (AbortError)', async () => {
      const { authApiClient } = await import('../auth-client');

      // DOMException with AbortError name may not be available in jsdom
      const abortError = new Error('Aborted');
      abortError.name = 'AbortError';
      global.fetch = vi.fn().mockRejectedValue(abortError);

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Request timeout');
    });

    it('should handle non-JSON responses', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'text/plain' }),
        text: () => Promise.resolve('OK'),
      });

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(true);
    });

    it('should handle invalid JSON response', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.reject(new Error('Invalid JSON')),
      });

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid JSON response from server');
    });

    it('should handle error response with message field', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ message: 'Account locked' }),
      });

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Account locked');
    });

    it('should handle error response without message or error field', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({}),
      });

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Request failed with status 500');
    });

    it('should handle non-Error thrown objects', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockRejectedValue('string error');

      const result = await authApiClient.login('user@sahool.com', 'password');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Network error - please check your connection');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // TOKEN MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════════

  describe('token management', () => {
    // Note: `getCurrentUser()` was migrated off the bearer-token path. It
    // now calls the Next.js proxy route `/api/auth/me` which reads the
    // httpOnly cookie server-side, so these tests verify the cookie-flow
    // contract instead of the (removed) `Authorization: Bearer …` header.

    it('setToken/clearToken are accepted without throwing', async () => {
      const { authApiClient } = await import('../auth-client');

      expect(() => authApiClient.setToken('my-token')).not.toThrow();
      expect(() => authApiClient.clearToken()).not.toThrow();
    });

    it('getCurrentUser calls the Next proxy with credentials: include (no Authorization header)', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ success: true, data: {} }),
      });

      await authApiClient.getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/me',
        expect.objectContaining({ credentials: 'include' })
      );
      const fetchCall = (global.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
      const init = fetchCall[1] as RequestInit | undefined;
      // Intentionally bearer-less — the httpOnly cookie is the authoritative
      // token store.
      expect((init?.headers as Record<string, string> | undefined)?.Authorization).toBeUndefined();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GET CURRENT USER
  // ═══════════════════════════════════════════════════════════════════════════

  describe('getCurrentUser', () => {
    it('should make GET request to /api/v1/auth/me', async () => {
      const { authApiClient } = await import('../auth-client');

      const mockUser = {
        id: 'user-1',
        email: 'user@sahool.com',
        name: 'Test User',
        role: 'farmer',
      };

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ success: true, data: mockUser }),
      });

      const result = await authApiClient.getCurrentUser();

      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockUser);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // REFRESH TOKEN
  // ═══════════════════════════════════════════════════════════════════════════

  describe('refreshToken', () => {
    it('should call /api/auth/refresh server proxy (httpOnly cookie flow)', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            access_token: 'new-token',
          }),
      });

      const result = await authApiClient.refreshToken();

      expect(result.success).toBe(true);
      expect(result.access_token).toBe('new-token');
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/refresh',
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
        })
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ATTEMPT TOKEN REFRESH
  // ═══════════════════════════════════════════════════════════════════════════

  describe('attemptTokenRefresh', () => {
    it('should return false when running server-side', async () => {
      const { authApiClient } = await import('../auth-client');

      // Simulate server-side (no window)
      vi.stubGlobal('window', undefined);

      const result = await authApiClient.attemptTokenRefresh();
      expect(result).toBe(false);

      vi.unstubAllGlobals();
    });

    it('should refresh and set new token via proxy route', async () => {
      const { authApiClient } = await import('../auth-client');

      // Mock the proxy-based refreshToken() call
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            success: true,
            access_token: 'new-access-token',
          }),
      });

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/refresh',
        expect.objectContaining({ method: 'POST', credentials: 'include' })
      );
    });

    it('should clear tokens when refresh fails', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ success: false, error: 'Token expired' }),
      });

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(false);
      // Root-scoped removal
      expect(Cookies.remove).toHaveBeenCalledWith('access_token', { path: '/' });
      expect(Cookies.remove).toHaveBeenCalledWith('refresh_token', { path: '/' });
      // Legacy path-scoped removal
      expect(Cookies.remove).toHaveBeenCalledWith('access_token');
      expect(Cookies.remove).toHaveBeenCalledWith('refresh_token');
    });

    it('should handle errors during refresh gracefully', async () => {
      const { authApiClient } = await import('../auth-client');

      vi.mocked(Cookies.get).mockReturnValue('token');

      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      const result = await authApiClient.attemptTokenRefresh();

      expect(result).toBe(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // REQUEST CREDENTIALS
  // ═══════════════════════════════════════════════════════════════════════════

  describe('request credentials', () => {
    it('should include credentials: include in all requests', async () => {
      const { authApiClient } = await import('../auth-client');

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ success: true, data: {} }),
      });

      await authApiClient.getCurrentUser();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          credentials: 'include',
        })
      );
    });
  });
});
