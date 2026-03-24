/**
 * API Middleware Tests
 * اختبارات وسيط API
 *
 * Tests api-middleware.ts: withAuth, withRole, withAdmin, withSupervisor,
 * checkUserRole, errorResponse
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NextRequest, NextResponse } from 'next/server';
import type { User } from '../jwt-verify';

// Mock next/headers cookies
const mockCookieStore = {
  get: vi.fn(),
  set: vi.fn(),
  delete: vi.fn(),
};

vi.mock('next/headers', () => ({
  cookies: vi.fn(() => Promise.resolve(mockCookieStore)),
}));

// Mock jwt-verify
vi.mock('../jwt-verify', async () => {
  const actual = await vi.importActual('../jwt-verify');
  return {
    ...actual,
    getUserFromToken: vi.fn(),
    hasAnyRole: (actual as Record<string, unknown>).hasAnyRole,
  };
});

import { getUserFromToken } from '../jwt-verify';
import {
  withAuth,
  withRole,
  withAdmin,
  withSupervisor,
  checkUserRole,
  errorResponse,
} from '../api-middleware';

const mockUser: User = {
  id: 'user-1',
  email: 'admin@sahool.app',
  name: 'Admin',
  role: 'admin',
  tenant_id: 'tenant-1',
};

function createRequest(url = 'http://localhost:3002/api/test'): NextRequest {
  return new NextRequest(new URL(url));
}

describe('withAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns 401 when no token cookie', async () => {
    mockCookieStore.get.mockReturnValue(undefined);

    const handler = vi.fn();
    const wrapped = withAuth(handler);
    const response = await wrapped(createRequest());
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.error).toBe('Unauthorized');
    expect(handler).not.toHaveBeenCalled();
  });

  it('returns 401 when getUserFromToken returns null', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'bad-token' });
    vi.mocked(getUserFromToken).mockResolvedValue(null);

    const handler = vi.fn();
    const wrapped = withAuth(handler);
    const response = await wrapped(createRequest());
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.message).toBe('Invalid token');
    expect(handler).not.toHaveBeenCalled();
  });

  it('calls handler with user context when authenticated', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });
    vi.mocked(getUserFromToken).mockResolvedValue(mockUser);

    const handler = vi.fn(async (_req, ctx) => NextResponse.json({ user: ctx.user }));
    const wrapped = withAuth(handler);
    const request = createRequest();
    const response = await wrapped(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.user.email).toBe('admin@sahool.app');
    expect(handler).toHaveBeenCalledWith(
      request,
      expect.objectContaining({
        user: mockUser,
        token: 'valid-token',
      })
    );
  });

  it('returns 401 when getUserFromToken throws', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'expired-token' });
    vi.mocked(getUserFromToken).mockRejectedValue(new Error('Token expired'));

    const handler = vi.fn();
    const wrapped = withAuth(handler);
    const response = await wrapped(createRequest());
    const data = await response.json();

    expect(response.status).toBe(401);
    expect(data.message).toBe('Token verification failed');
  });
});

describe('withRole', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('allows access when user has required role', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });
    vi.mocked(getUserFromToken).mockResolvedValue(mockUser);

    const handler = vi.fn(async () => NextResponse.json({ ok: true }));
    const wrapped = withRole(['admin'], handler);
    const response = await wrapped(createRequest());

    expect(response.status).toBe(200);
    expect(handler).toHaveBeenCalled();
  });

  it('returns 403 when user lacks required role', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });
    vi.mocked(getUserFromToken).mockResolvedValue({
      ...mockUser,
      role: 'viewer',
    });

    const handler = vi.fn();
    const wrapped = withRole(['admin'], handler);
    const response = await wrapped(createRequest());
    const data = await response.json();

    expect(response.status).toBe(403);
    expect(data.error).toBe('Forbidden');
    expect(data.required_roles).toEqual(['admin']);
    expect(data.your_role).toBe('viewer');
    expect(handler).not.toHaveBeenCalled();
  });
});

describe('withAdmin', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('allows admin access', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });
    vi.mocked(getUserFromToken).mockResolvedValue(mockUser);

    const handler = vi.fn(async () => NextResponse.json({ admin: true }));
    const wrapped = withAdmin(handler);
    const response = await wrapped(createRequest());

    expect(response.status).toBe(200);
  });

  it('blocks non-admin users', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });
    vi.mocked(getUserFromToken).mockResolvedValue({
      ...mockUser,
      role: 'supervisor',
    });

    const wrapped = withAdmin(vi.fn());
    const response = await wrapped(createRequest());

    expect(response.status).toBe(403);
  });
});

describe('withSupervisor', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('allows admin and supervisor', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });

    // Admin
    vi.mocked(getUserFromToken).mockResolvedValue(mockUser);
    const handler = vi.fn(async () => NextResponse.json({ ok: true }));
    let response = await withSupervisor(handler)(createRequest());
    expect(response.status).toBe(200);

    // Supervisor
    vi.mocked(getUserFromToken).mockResolvedValue({
      ...mockUser,
      role: 'supervisor',
    });
    response = await withSupervisor(handler)(createRequest());
    expect(response.status).toBe(200);
  });

  it('blocks viewer', async () => {
    mockCookieStore.get.mockReturnValue({ value: 'valid-token' });
    vi.mocked(getUserFromToken).mockResolvedValue({
      ...mockUser,
      role: 'viewer',
    });

    const response = await withSupervisor(vi.fn())(createRequest());
    expect(response.status).toBe(403);
  });
});

describe('checkUserRole', () => {
  it('returns true for matching role', () => {
    expect(checkUserRole(mockUser, ['admin'])).toBe(true);
    expect(checkUserRole(mockUser, ['admin', 'supervisor'])).toBe(true);
  });

  it('returns false for insufficient role', () => {
    const viewer = { ...mockUser, role: 'viewer' as const };
    expect(checkUserRole(viewer, ['admin'])).toBe(false);
  });
});

describe('errorResponse', () => {
  it('creates error response with default 400', async () => {
    const response = errorResponse('Bad input');
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBe('Bad Request');
    expect(data.message).toBe('Bad input');
  });

  it('creates error response with custom status', async () => {
    const response = errorResponse('Not found', 404);
    const data = await response.json();

    expect(response.status).toBe(404);
    expect(data.error).toBe('Not Found');
  });

  it('includes additional data', async () => {
    const response = errorResponse('Rate limited', 429, {
      retryAfter: 60,
    });
    const data = await response.json();

    expect(response.status).toBe(429);
    expect(data.error).toBe('Too Many Requests');
    expect(data.retryAfter).toBe(60);
  });

  it('maps common status codes correctly', async () => {
    const codes = [
      [401, 'Unauthorized'],
      [403, 'Forbidden'],
      [409, 'Conflict'],
      [422, 'Validation Error'],
      [500, 'Internal Server Error'],
      [418, 'Error'],
    ] as const;

    for (const [status, expected] of codes) {
      const response = errorResponse('test', status);
      const data = await response.json();
      expect(data.error).toBe(expected);
    }
  });
});
