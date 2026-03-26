/**
 * Auth Utilities Tests
 * اختبارات أدوات المصادقة
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock submodules to avoid importing server-only code
vi.mock('../auth/jwt-verify', () => ({
  verifyJWT: vi.fn(),
}));
vi.mock('../auth/route-protection', () => ({
  protectRoute: vi.fn(),
}));
vi.mock('../auth/api-middleware', () => ({
  withAuth: vi.fn(),
}));

import { getUser, setUser, getToken, hasRole, isAuthenticated } from '../auth';

describe('Auth Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReset();
    (window.localStorage.setItem as ReturnType<typeof vi.fn>).mockReset();
    (window.localStorage.removeItem as ReturnType<typeof vi.fn>).mockReset();
  });

  describe('getUser', () => {
    it('returns parsed user from localStorage', () => {
      const user = { id: '1', email: 'a@b.com', name: 'A', role: 'admin' };
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(
        JSON.stringify(user)
      );

      const result = getUser();
      expect(result).toEqual(user);
    });

    it('returns null when no user stored', () => {
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(null);
      expect(getUser()).toBeNull();
    });

    it('returns null for invalid JSON', () => {
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue('not-json');
      expect(getUser()).toBeNull();
    });
  });

  describe('setUser', () => {
    it('stores user in localStorage', () => {
      const user = { id: '1', email: 'a@b.com', name: 'A', role: 'admin' as const };
      setUser(user);

      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        'sahool_admin_user',
        JSON.stringify(user)
      );
    });
  });

  describe('getToken', () => {
    it('returns undefined (tokens now in httpOnly cookies)', () => {
      expect(getToken()).toBeUndefined();
    });
  });

  describe('isAuthenticated', () => {
    it('returns false (token is always undefined now)', () => {
      expect(isAuthenticated()).toBe(false);
    });
  });

  describe('hasRole', () => {
    it('returns true for admin accessing viewer route', () => {
      const user = { id: '1', email: 'a@b.com', name: 'A', role: 'admin' };
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(
        JSON.stringify(user)
      );
      expect(hasRole('viewer')).toBe(true);
    });

    it('returns true for admin accessing admin route', () => {
      const user = { id: '1', email: 'a@b.com', name: 'A', role: 'admin' };
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(
        JSON.stringify(user)
      );
      expect(hasRole('admin')).toBe(true);
    });

    it('returns false for viewer accessing admin route', () => {
      const user = { id: '1', email: 'a@b.com', name: 'V', role: 'viewer' };
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(
        JSON.stringify(user)
      );
      expect(hasRole('admin')).toBe(false);
    });

    it('returns false when no user stored', () => {
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(null);
      expect(hasRole('viewer')).toBe(false);
    });
  });
});
