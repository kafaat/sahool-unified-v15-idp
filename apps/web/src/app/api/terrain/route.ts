/**
 * Terrain Analysis API Proxy Routes
 * وكيل واجهة برمجة تطبيقات تحليل التضاريس
 *
 * Proxies terrain analysis requests to terrain-core-service.
 * All endpoints require authentication via httpOnly access_token cookie.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const TERRAIN_SERVICE_URL =
  process.env.TERRAIN_SERVICE_URL || 'http://terrain-core-service:8185';

const REQUEST_TIMEOUT_MS = 15_000;

/** Validate IDs to prevent path traversal */
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Extract and validate the access token from httpOnly cookie.
 * Returns the token string or null if absent/invalid.
 */
async function getAccessToken(): Promise<string | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;
  if (!token || token.length < 20 || token.length > 2048) {
    return null;
  }
  return token;
}

/**
 * Extract tenant ID from the access token JWT payload (unverified decode).
 * The backend performs full verification; this is for forwarding only.
 */
function extractTenantId(token: string): string | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) return null;
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf-8'));
    return payload.tid || payload.tenant_id || null;
  } catch {
    return null;
  }
}

/**
 * Build standard authorization headers for upstream requests.
 */
function buildHeaders(token: string, tenantId: string | null): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
  if (tenantId) {
    headers['X-Tenant-ID'] = tenantId;
  }
  return headers;
}

// ═══════════════════════════════════════════════════════════════════════════
// GET /api/terrain
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/terrain?action=dem&fieldId=xxx
 * GET /api/terrain?action=slope&fieldId=xxx
 * GET /api/terrain?action=aspect&fieldId=xxx
 */
export async function GET(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse params ---
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fieldId = searchParams.get('fieldId');

    if (fieldId && !SAFE_ID_PATTERN.test(fieldId)) {
      return NextResponse.json({ error: 'Invalid fieldId format' }, { status: 400 });
    }

    let path: string;

    switch (action) {
      case 'dem': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const params = new URLSearchParams();
        const resolution = searchParams.get('resolution');
        const format = searchParams.get('format');
        if (resolution) params.set('resolution', resolution);
        if (format) params.set('format', format);
        const qs = params.toString();
        path = `/api/v1/terrain/dem/${encodeURIComponent(fieldId)}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'slope': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const params = new URLSearchParams();
        const units = searchParams.get('units');
        if (units) params.set('units', units);
        const qs = params.toString();
        path = `/api/v1/terrain/slope/${encodeURIComponent(fieldId)}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'aspect': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        path = `/api/v1/terrain/aspect/${encodeURIComponent(fieldId)}`;
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: dem, slope, aspect' },
          { status: 400 }
        );
    }

    const response = await fetch(`${TERRAIN_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: buildHeaders(token, tenantId),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Terrain service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Terrain service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Terrain GET proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch terrain data' },
      { status: 502 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST /api/terrain
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/terrain
 * Body: { action: 'analyze', fieldId, coordinates?, analysis_types?, ... }
 *
 * action=analyze -> Full terrain analysis for a field (DEM, slope, aspect, drainage)
 */
export async function POST(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse body ---
    const body = await request.json();
    const { action, fieldId } = body;

    if (!action || typeof action !== 'string') {
      return NextResponse.json({ error: 'action is required' }, { status: 400 });
    }

    if (!fieldId || typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId)) {
      return NextResponse.json({ error: 'Valid fieldId is required' }, { status: 400 });
    }

    let path: string;
    let payload: Record<string, unknown>;

    switch (action) {
      case 'analyze': {
        path = `/api/v1/terrain/analyze`;
        const { coordinates, analysis_types, resolution, include_drainage } = body;
        payload = {
          field_id: fieldId,
          ...(coordinates != null && { coordinates }),
          ...(analysis_types != null && { analysis_types }),
          ...(resolution != null && { resolution }),
          ...(include_drainage != null && { include_drainage }),
        };
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: analyze' },
          { status: 400 }
        );
    }

    const response = await fetch(`${TERRAIN_SERVICE_URL}${path}`, {
      method: 'POST',
      headers: buildHeaders(token, tenantId),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Terrain service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Terrain analysis timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Terrain POST proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process terrain analysis request' },
      { status: 502 }
    );
  }
}
