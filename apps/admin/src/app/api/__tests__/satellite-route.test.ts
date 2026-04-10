/**
 * Satellite API Proxy Route Tests
 * اختبارات مسار وكيل واجهة برمجة تطبيقات الأقمار الصناعية
 *
 * Tests the satellite/NDVI proxy route handler:
 * - GET action routing (indices, timeseries, satellites, providers, eo-status)
 * - POST analyze action
 * - Input validation (action, fieldId)
 * - Error handling (upstream failures, timeouts, non-JSON responses)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

// The satellite proxy was hardened (satellite flow audit, C1) to require a
// verified JWT and forward tenant/user ids to the backend. Each test below
// therefore attaches an `Authorization: Bearer …` header, and this mock
// stands in for the real `verifyToken()` so test runs don't need a
// signing key.
vi.mock('@/lib/auth/jwt-verify', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/auth/jwt-verify')>();
  return {
    ...actual,
    verifyToken: vi.fn(async () => ({
      sub: 'user-test-123',
      tid: 'tenant-test-456',
      email: 'test@sahool.app',
      role: 'admin',
    })),
  };
});

// Disable the in-memory rate limiter for test runs. The helper returns
// `null` when a request is under the limit, which is what the hardened
// satellite route expects before auth.
vi.mock('@/lib/rate-limit', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/rate-limit')>();
  return {
    ...actual,
    checkRateLimit: vi.fn(() => null),
  };
});

// Store the original fetch
const originalFetch = globalThis.fetch;

// Every request to the hardened satellite proxy must carry an auth header.
// This is the bearer token the mocked `verifyToken` above accepts.
const AUTH_HEADERS = { Authorization: 'Bearer test-token' };

// Helper to create NextRequest
function createGetRequest(url: string): NextRequest {
  return new NextRequest(new URL(url, 'http://localhost:3002'), {
    headers: AUTH_HEADERS,
  });
}

function createPostRequest(body: Record<string, unknown>): NextRequest {
  return new NextRequest(new URL('http://localhost:3002/api/satellite'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...AUTH_HEADERS },
    body: JSON.stringify(body),
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// GET Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('GET /api/satellite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('returns proper response for action=indices with fieldId', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ ndvi: 0.72, health_status: 'healthy' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=indices&fieldId=field-001'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.ndvi).toBe(0.72);

    // Verify fetch was called with correct URL
    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/indices/field-001'),
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('returns 400 when action=indices without fieldId', async () => {
    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=indices'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBe('fieldId required');
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it('passes fieldId and days for action=timeseries', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ timeseries: [{ date: '2026-01-01', ndvi: 0.65 }] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=timeseries&fieldId=field-002&days=30'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.timeseries).toBeDefined();

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/timeseries/field-002?days=30'),
      expect.objectContaining({ method: 'GET' })
    );
  });

  it('defaults days to 90 for timeseries when not provided', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ timeseries: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=timeseries&fieldId=field-003'
    );

    await GET(request);

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/timeseries/field-003?days=90'),
      expect.any(Object)
    );
  });

  it('returns 400 when action=timeseries without fieldId', async () => {
    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=timeseries'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toBe('fieldId required');
  });

  it('handles action=satellites correctly', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ satellites: ['Sentinel-2', 'Landsat-8'] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=satellites'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.satellites).toBeDefined();

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/satellites'),
      expect.any(Object)
    );
  });

  it('handles action=providers correctly', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ providers: ['sentinel_hub'] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=providers'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.providers).toBeDefined();

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/providers'),
      expect.any(Object)
    );
  });

  it('handles action=eo-status correctly', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ status: 'operational' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=eo-status'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.status).toBe('operational');
  });

  it('returns 400 for invalid action', async () => {
    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=invalid-action'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain('Invalid action');
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it('returns 400 when no action is provided', async () => {
    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest('http://localhost:3002/api/satellite');

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain('Invalid action');
  });

  it('returns 502 when upstream service returns non-JSON response', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response('<html>502 Bad Gateway</html>', {
        status: 502,
        headers: { 'Content-Type': 'text/html' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=satellites'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toContain('non-JSON response');
  });

  it('returns 502 when upstream service connection fails', async () => {
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new Error('Connection refused')
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=satellites'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe('Failed to fetch satellite data');
  });

  it('returns 502 on timeout errors', async () => {
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new DOMException('The operation was aborted', 'AbortError')
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=indices&fieldId=field-001'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe('Failed to fetch satellite data');
  });

  it('forwards upstream status codes for JSON responses', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ error: 'Field not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { GET } = await import('@/app/api/satellite/route');
    const request = createGetRequest(
      'http://localhost:3002/api/satellite?action=indices&fieldId=nonexistent'
    );

    const response = await GET(request);
    const data = await response.json();

    expect(response.status).toBe(404);
    expect(data.error).toBe('Field not found');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// POST Route Tests
// ═══════════════════════════════════════════════════════════════════════════

describe('POST /api/satellite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('handles action=analyze with fieldId', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({ analysis_id: 'analysis-001', status: 'processing' }),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      )
    );

    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'analyze',
      fieldId: 'field-001',
      analysisType: 'ndvi',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data.analysis_id).toBe('analysis-001');

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/v1/analyze'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          field_id: 'field-001',
          analysis_type: 'ndvi',
        }),
      })
    );
  });

  it('defaults analysisType to ndvi when not provided', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ status: 'processing' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'analyze',
      fieldId: 'field-001',
    });

    await POST(request);

    expect(globalThis.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        body: JSON.stringify({
          field_id: 'field-001',
          analysis_type: 'ndvi',
        }),
      })
    );
  });

  it('returns 400 for POST with invalid action', async () => {
    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'invalid',
      fieldId: 'field-001',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    expect(data.error).toContain('POST only supports analyze action');
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it('returns 400 for POST without fieldId', async () => {
    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'analyze',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(400);
    // The hardened proxy emits the stricter message
    // "fieldId required and must be a UUID or alphanumeric slug" — match
    // the stable prefix so minor wording changes don't break the test.
    expect(data.error).toMatch(/^fieldId required/);
    expect(globalThis.fetch).not.toHaveBeenCalled();
  });

  it('returns 502 when upstream service fails on POST', async () => {
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new Error('Service unavailable')
    );

    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'analyze',
      fieldId: 'field-001',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe('Failed to analyze satellite data');
  });

  it('returns 502 when upstream returns non-JSON on POST', async () => {
    vi.mocked(globalThis.fetch).mockResolvedValueOnce(
      new Response('Internal Server Error', {
        status: 500,
        headers: { 'Content-Type': 'text/plain' },
      })
    );

    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'analyze',
      fieldId: 'field-001',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toContain('non-JSON response');
  });

  it('handles timeout errors on POST', async () => {
    vi.mocked(globalThis.fetch).mockRejectedValueOnce(
      new DOMException('The operation was aborted', 'AbortError')
    );

    const { POST } = await import('@/app/api/satellite/route');
    const request = createPostRequest({
      action: 'analyze',
      fieldId: 'field-001',
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(502);
    expect(data.error).toBe('Failed to analyze satellite data');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// Source Verification
// ═══════════════════════════════════════════════════════════════════════════

describe('satellite route source verification', () => {
  const fs = require('fs');
  const path = require('path');
  const filePath = path.resolve(__dirname, '../satellite/route.ts');

  it('route source file exists', () => {
    expect(fs.existsSync(filePath)).toBe(true);
  });

  it('exports GET and POST handlers', () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('export async function GET');
    expect(content).toContain('export async function POST');
  });

  it('uses vegetation-analysis-service as upstream', () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('vegetation-analysis-service');
    expect(content).toContain('8090');
  });

  it('supports AbortSignal timeout', () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('AbortSignal.timeout');
  });

  it('validates content-type from upstream', () => {
    const content = fs.readFileSync(filePath, 'utf-8');
    expect(content).toContain('application/json');
    expect(content).toContain('non-JSON response');
  });
});
