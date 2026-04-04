/**
 * Soil Analysis API Proxy Routes
 * وكيل واجهة برمجة تطبيقات تحليل التربة
 *
 * Proxies soil analysis requests to soil-analysis-service.
 * All endpoints require authentication via httpOnly access_token cookie.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const SOIL_ANALYSIS_URL =
  process.env.SOIL_ANALYSIS_URL || 'http://soil-analysis-service:8134';

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
    if (parts.length !== 3) return null;
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
// GET /api/soil-analysis
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/soil-analysis?action=soil-data&fieldId=xxx
 * GET /api/soil-analysis?action=soil-types
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
      case 'soil-data': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required' }, { status: 400 });
        }
        const params = new URLSearchParams();
        const depth = searchParams.get('depth');
        const date = searchParams.get('date');
        if (depth) params.set('depth', depth);
        if (date) params.set('date', date);
        const qs = params.toString();
        path = `/api/v1/soil/${encodeURIComponent(fieldId)}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'soil-types': {
        const region = searchParams.get('region');
        const params = new URLSearchParams();
        if (region) params.set('region', region);
        const qs = params.toString();
        path = `/api/v1/soil/types${qs ? `?${qs}` : ''}`;
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: soil-data, soil-types' },
          { status: 400 }
        );
    }

    const response = await fetch(`${SOIL_ANALYSIS_URL}${path}`, {
      method: 'GET',
      headers: buildHeaders(token, tenantId),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Soil analysis service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Soil analysis service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Soil analysis GET proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch soil analysis data' },
      { status: 502 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST /api/soil-analysis
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/soil-analysis
 * Body: { action: 'interpret' | 'amendment-plan', fieldId, ... }
 *
 * action=interpret  -> Interpret a soil test result
 * action=amendment-plan -> Generate a soil amendment plan
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
      case 'interpret': {
        path = `/api/v1/soil/interpret`;
        const { ph, nitrogen, phosphorus, potassium, organic_matter, texture, ec } = body;
        payload = {
          field_id: fieldId,
          ...(ph != null && { ph }),
          ...(nitrogen != null && { nitrogen }),
          ...(phosphorus != null && { phosphorus }),
          ...(potassium != null && { potassium }),
          ...(organic_matter != null && { organic_matter }),
          ...(texture != null && { texture }),
          ...(ec != null && { ec }),
        };
        break;
      }
      case 'amendment-plan': {
        path = `/api/v1/soil/amendment-plan`;
        const { crop_type, target_yield, soil_test_id } = body;
        payload = {
          field_id: fieldId,
          ...(crop_type != null && { crop_type }),
          ...(target_yield != null && { target_yield }),
          ...(soil_test_id != null && { soil_test_id }),
        };
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: interpret, amendment-plan' },
          { status: 400 }
        );
    }

    const response = await fetch(`${SOIL_ANALYSIS_URL}${path}`, {
      method: 'POST',
      headers: buildHeaders(token, tenantId),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Soil analysis service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Soil analysis service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Soil analysis POST proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process soil analysis request' },
      { status: 502 }
    );
  }
}
