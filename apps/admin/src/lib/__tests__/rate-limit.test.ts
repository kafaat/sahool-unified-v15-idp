/**
 * Tests for generic rate limiting middleware
 * اختبارات وسيط تحديد معدل الطلبات
 */

import { describe, it, expect } from 'vitest';
import { NextRequest } from 'next/server';
import { checkRateLimit, rateLimitHeaders } from '../rate-limit';

function createMockRequest(path: string = '/api/test', ip: string = '127.0.0.1'): NextRequest {
  const url = `http://localhost:3001${path}`;
  const request = new NextRequest(url, {
    headers: {
      // The rate limiter resolves the client IP via `getClientIP`, which only
      // honors `X-Forwarded-For` when the direct peer is in TRUSTED_PROXIES.
      // Cloudflare's `CF-Connecting-IP` header is always trusted, so we use it
      // here to simulate a real client IP without standing up a proxy allowlist.
      'cf-connecting-ip': ip,
      'x-forwarded-for': ip,
    },
  });
  return request;
}

// Use unique paths per test to avoid state sharing
let pathCounter = 0;
function uniquePath(): string {
  return `/api/test-${++pathCounter}-${Math.random().toString(36).slice(2)}`;
}

describe('checkRateLimit', () => {
  it('allows requests under the limit', () => {
    const path = uniquePath();
    const request = createMockRequest(path);
    const result = checkRateLimit(request, { limit: 5 });
    expect(result).toBeNull();
  });

  it('blocks requests exceeding the limit', () => {
    const path = uniquePath();
    const config = { limit: 3, windowMs: 60000 };

    // Make 3 allowed requests
    for (let i = 0; i < 3; i++) {
      const result = checkRateLimit(createMockRequest(path), config);
      expect(result).toBeNull();
    }

    // 4th request should be blocked
    const blocked = checkRateLimit(createMockRequest(path), config);
    expect(blocked).not.toBeNull();
    expect(blocked!.status).toBe(429);
  });

  it('returns proper 429 response body', async () => {
    const path = uniquePath();
    const config = { limit: 1, windowMs: 60000 };

    // Exhaust limit
    checkRateLimit(createMockRequest(path), config);

    // Should be blocked
    const response = checkRateLimit(createMockRequest(path), config);
    expect(response).not.toBeNull();

    const body = await response!.json();
    expect(body.error).toBe('Too many requests');
    expect(body.errorAr).toBe('عدد الطلبات كثير جداً');
    expect(body.retryAfter).toBeGreaterThan(0);
  });

  it('includes rate limit headers on 429', () => {
    const path = uniquePath();
    const config = { limit: 1, windowMs: 60000 };

    checkRateLimit(createMockRequest(path), config);
    const response = checkRateLimit(createMockRequest(path), config);

    expect(response!.headers.get('Retry-After')).toBeTruthy();
    expect(response!.headers.get('X-RateLimit-Limit')).toBe('1');
    expect(response!.headers.get('X-RateLimit-Remaining')).toBe('0');
  });

  it('tracks different IPs separately', () => {
    const path = uniquePath();
    const config = { limit: 1, windowMs: 60000 };

    // IP 1 exhausts its limit
    checkRateLimit(createMockRequest(path, '1.1.1.1'), config);
    const blocked = checkRateLimit(createMockRequest(path, '1.1.1.1'), config);
    expect(blocked).not.toBeNull();

    // IP 2 should still be allowed
    const allowed = checkRateLimit(createMockRequest(path, '2.2.2.2'), config);
    expect(allowed).toBeNull();
  });

  it('tracks different paths separately', () => {
    const path1 = uniquePath();
    const path2 = uniquePath();
    const config = { limit: 1, windowMs: 60000 };

    // Exhaust limit on path1
    checkRateLimit(createMockRequest(path1), config);
    const blocked = checkRateLimit(createMockRequest(path1), config);
    expect(blocked).not.toBeNull();

    // Path2 should still work
    const allowed = checkRateLimit(createMockRequest(path2), config);
    expect(allowed).toBeNull();
  });

  it('uses default limits when no config provided', () => {
    const path = uniquePath();
    // Default limit is 60, so first request should always pass
    const result = checkRateLimit(createMockRequest(path));
    expect(result).toBeNull();
  });
});

describe('rateLimitHeaders', () => {
  it('returns rate limit info headers', () => {
    const path = uniquePath();
    const request = createMockRequest(path);
    const headers = rateLimitHeaders(request, { limit: 100 });

    expect(headers['X-RateLimit-Limit']).toBe('100');
    expect(headers['X-RateLimit-Remaining']).toBeTruthy();
    expect(headers['X-RateLimit-Reset']).toBeTruthy();
  });

  it('shows correct remaining count after requests', () => {
    const path = uniquePath();
    const config = { limit: 5, windowMs: 60000 };

    // Make 3 requests
    for (let i = 0; i < 3; i++) {
      checkRateLimit(createMockRequest(path), config);
    }

    const headers = rateLimitHeaders(createMockRequest(path), config);
    expect(headers['X-RateLimit-Remaining']).toBe('2');
  });
});
