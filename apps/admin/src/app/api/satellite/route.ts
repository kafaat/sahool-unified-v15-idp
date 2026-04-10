/**
 * Satellite/NDVI API Proxy Routes
 * وكيل واجهة برمجة تطبيقات الأقمار الصناعية
 *
 * Proxies satellite data requests to vegetation-analysis-service directly
 * (server-side only — not exposed to browser).
 *
 * Hardened (satellite audit, commit {{HASH}}):
 *   - JWT verification via `verifyToken()` (algorithm pinned HS256)
 *   - Per-IP rate limiting via shared `checkRateLimit()` helper
 *   - Trusted-proxy-gated client IP via `getClientIP()`
 *   - `X-Tenant-Id` + `Authorization` forwarded to the downstream service
 *   - Path parameters `encodeURIComponent`-wrapped (path traversal guard)
 *   - POST body size capped at 10 KB
 *   - Invalid auth is never allowed to reach the backend
 */

import { NextRequest, NextResponse } from 'next/server';
import { logger } from '@/lib/logger';
import { verifyToken } from '@/lib/auth/jwt-verify';
import { checkRateLimit } from '@/lib/rate-limit';

const VEGETATION_SERVICE_URL =
  process.env.VEGETATION_SERVICE_URL || 'http://vegetation-analysis-service:8090';

// Satellite reads are cheap server-side; this matches weather's tier.
const GET_RATE_LIMIT = { limit: 60, windowMs: 60_000 };
// Analysis triggers expensive backend work — throttle harder.
const POST_RATE_LIMIT = { limit: 15, windowMs: 60_000 };
const MAX_POST_BODY_BYTES = 10 * 1024; // 10 KB

/**
 * Extract the JWT from the Authorization header OR the admin session cookie.
 * Returns `{ token, payload }` on success, or `null` if the caller is
 * unauthenticated / the token is invalid.
 */
async function authorize(request: NextRequest): Promise<
  | { token: string; tenantId: string; userId: string }
  | { error: NextResponse }
> {
  const authHeader = request.headers.get('authorization') ?? '';
  const bearer = authHeader.toLowerCase().startsWith('bearer ')
    ? authHeader.slice(7).trim()
    : null;
  const cookieToken =
    request.cookies.get('sahool_admin_token')?.value ??
    request.cookies.get('access_token')?.value ??
    null;
  const token = bearer ?? cookieToken;

  if (!token) {
    return {
      error: NextResponse.json(
        { error: 'Unauthorized', errorAr: 'غير مصرح' },
        { status: 401 },
      ),
    };
  }

  try {
    const payload = await verifyToken(token);
    const tenantId =
      (typeof payload.tid === 'string' && payload.tid) ||
      (typeof payload.tenant_id === 'string' && payload.tenant_id) ||
      null;
    const userId =
      (typeof payload.sub === 'string' && payload.sub) ||
      (typeof payload.user_id === 'string' && payload.user_id) ||
      null;

    if (!tenantId || !userId) {
      return {
        error: NextResponse.json(
          { error: 'Token missing required claims', errorAr: 'توكن غير صالح' },
          { status: 401 },
        ),
      };
    }

    return { token, tenantId, userId };
  } catch (error) {
    logger.warn('Satellite proxy: token verification failed', {
      error: error instanceof Error ? error.message : String(error),
    });
    return {
      error: NextResponse.json(
        { error: 'Invalid or expired token', errorAr: 'توكن غير صالح أو منتهي' },
        { status: 401 },
      ),
    };
  }
}

/**
 * Build a set of forward headers that propagate the calling user's
 * identity to the vegetation-analysis-service so it can enforce tenant
 * isolation and field ownership.
 */
function buildForwardHeaders(auth: { token: string; tenantId: string; userId: string }): Headers {
  const h = new Headers();
  h.set('Content-Type', 'application/json');
  h.set('Authorization', `Bearer ${auth.token}`);
  h.set('X-Tenant-Id', auth.tenantId);
  h.set('X-User-Id', auth.userId);
  return h;
}

/**
 * GET /api/satellite?action=indices&fieldId=xxx
 * GET /api/satellite?action=timeseries&fieldId=xxx&days=90
 * GET /api/satellite?action=satellites
 * POST /api/satellite { action: 'analyze', fieldId, analysisType }
 */
export async function GET(request: NextRequest) {
  // 1. Rate limit (per-IP + per-path) — cheap, runs before auth to shed load.
  const rateLimited = checkRateLimit(request, GET_RATE_LIMIT);
  if (rateLimited) return rateLimited;

  // 2. Auth.
  const auth = await authorize(request);
  if ('error' in auth) return auth.error;

  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fieldId = searchParams.get('fieldId');
    const days = searchParams.get('days') || '90';
    const lat = searchParams.get('lat');
    const lon = searchParams.get('lon');

    // Validate fieldId against path traversal (must be UUID or alphanumeric slug)
    if (fieldId && !/^[a-zA-Z0-9_-]+$/.test(fieldId)) {
      return NextResponse.json({ error: 'Invalid fieldId format' }, { status: 400 });
    }

    // Validate days window (avoid 10-year scans)
    const daysNum = Number(days);
    if (!Number.isInteger(daysNum) || daysNum < 1 || daysNum > 365) {
      return NextResponse.json(
        { error: 'days must be an integer between 1 and 365' },
        { status: 400 },
      );
    }

    // Validate coordinates if provided
    if (lat && (isNaN(Number(lat)) || Number(lat) < -90 || Number(lat) > 90)) {
      return NextResponse.json({ error: 'lat must be between -90 and 90' }, { status: 400 });
    }
    if (lon && (isNaN(Number(lon)) || Number(lon) < -180 || Number(lon) > 180)) {
      return NextResponse.json({ error: 'lon must be between -180 and 180' }, { status: 400 });
    }

    // Path parameters are URL-encoded to guarantee no traversal even if the
    // allowlist regex above were ever weakened.
    const encodedFieldId = fieldId ? encodeURIComponent(fieldId) : '';

    let path: string;
    switch (action) {
      case 'indices': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const params = new URLSearchParams();
        if (lat) params.set('lat', lat);
        if (lon) params.set('lon', lon);
        const qs = params.toString();
        path = `/v1/indices/${encodedFieldId}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'timeseries':
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        path = `/v1/timeseries/${encodedFieldId}?days=${daysNum}`;
        break;
      case 'satellites':
        path = '/v1/satellites';
        break;
      case 'providers':
        path = '/v1/providers';
        break;
      case 'eo-status':
        path = '/v1/eo-status';
        break;
      case 'sar-timeseries': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const sarParams = new URLSearchParams();
        const startDate = searchParams.get('start_date');
        const endDate = searchParams.get('end_date');
        if (startDate) sarParams.set('start_date', startDate);
        if (endDate) sarParams.set('end_date', endDate);
        if (lat) sarParams.set('lat', lat);
        if (lon) sarParams.set('lon', lon);
        const sarQs = sarParams.toString();
        path = `/v1/sar-timeseries/${encodedFieldId}${sarQs ? `?${sarQs}` : ''}`;
        break;
      }
      case 'cloud-cover': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const ccParams = new URLSearchParams();
        if (lat) ccParams.set('lat', lat);
        if (lon) ccParams.set('lon', lon);
        const ccQs = ccParams.toString();
        path = `/v1/cloud-cover/${encodedFieldId}${ccQs ? `?${ccQs}` : ''}`;
        break;
      }
      case 'clear-observations':
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        path = `/v1/clear-observations/${encodedFieldId}`;
        break;
      default:
        return NextResponse.json(
          {
            error:
              'Invalid action. Use: indices, timeseries, satellites, providers, eo-status, sar-timeseries, cloud-cover, clear-observations',
          },
          { status: 400 },
        );
    }

    const response = await fetch(`${VEGETATION_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: buildForwardHeaders(auth),
      signal: AbortSignal.timeout(30000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Vegetation service returned non-JSON response' },
        { status: 502 },
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Satellite service timeout. Please retry.' },
        { status: 504 },
      );
    }
    logger.error('Satellite API proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch satellite data' }, { status: 502 });
  }
}

export async function POST(request: NextRequest) {
  // 1. Rate limit first (cheapest check).
  const rateLimited = checkRateLimit(request, POST_RATE_LIMIT);
  if (rateLimited) return rateLimited;

  // 2. Auth.
  const auth = await authorize(request);
  if ('error' in auth) return auth.error;

  // 3. Enforce a body-size cap before buffering, so a 1 GB body can't
  //    occupy the Node process.
  const contentLengthHeader = request.headers.get('content-length');
  if (contentLengthHeader) {
    const contentLength = Number(contentLengthHeader);
    if (Number.isFinite(contentLength) && contentLength > MAX_POST_BODY_BYTES) {
      return NextResponse.json(
        { error: 'Request body too large', maxBytes: MAX_POST_BODY_BYTES },
        { status: 413 },
      );
    }
  }

  try {
    const body = await request.json();
    const { action, fieldId, analysisType } = body;

    if (action !== 'analyze') {
      return NextResponse.json({ error: 'POST only supports analyze action' }, { status: 400 });
    }

    if (!fieldId || typeof fieldId !== 'string' || !/^[a-zA-Z0-9_-]+$/.test(fieldId)) {
      return NextResponse.json(
        { error: 'fieldId required and must be a UUID or alphanumeric slug' },
        { status: 400 },
      );
    }

    const { latitude, longitude, coordinates } = body;
    const response = await fetch(`${VEGETATION_SERVICE_URL}/v1/analyze`, {
      method: 'POST',
      headers: buildForwardHeaders(auth),
      body: JSON.stringify({
        field_id: fieldId,
        analysis_type: analysisType || 'ndvi',
        ...(latitude != null && { latitude }),
        ...(longitude != null && { longitude }),
        ...(coordinates != null && { coordinates }),
      }),
      signal: AbortSignal.timeout(60000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Vegetation service returned non-JSON response' },
        { status: 502 },
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Satellite analysis timeout. Please retry.' },
        { status: 504 },
      );
    }
    logger.error('Satellite analyze proxy error:', error);
    return NextResponse.json({ error: 'Failed to analyze satellite data' }, { status: 502 });
  }
}
