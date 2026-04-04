/**
 * Pest Detection API Proxy Routes
 * وكيل واجهة برمجة تطبيقات كشف الآفات
 *
 * Proxies pest detection requests to pest-detection-service.
 * All endpoints require authentication via httpOnly access_token cookie.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const PEST_DETECTION_URL =
  process.env.PEST_DETECTION_URL || 'http://pest-detection-service:8125';

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
// GET /api/pest-detection
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/pest-detection?action=list&region=xxx
 * GET /api/pest-detection?action=by-crop&cropType=wheat
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

    let path: string;

    switch (action) {
      case 'list': {
        const params = new URLSearchParams();
        const region = searchParams.get('region');
        const season = searchParams.get('season');
        const severity = searchParams.get('severity');
        if (region) params.set('region', region);
        if (season) params.set('season', season);
        if (severity) params.set('severity', severity);
        const qs = params.toString();
        path = `/api/v1/pests${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'by-crop': {
        const cropType = searchParams.get('cropType');
        if (!cropType || !SAFE_ID_PATTERN.test(cropType)) {
          return NextResponse.json(
            { error: 'Valid cropType is required' },
            { status: 400 }
          );
        }
        const params = new URLSearchParams();
        const region = searchParams.get('region');
        if (region) params.set('region', region);
        const qs = params.toString();
        path = `/api/v1/pests/crop/${encodeURIComponent(cropType)}${qs ? `?${qs}` : ''}`;
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: list, by-crop' },
          { status: 400 }
        );
    }

    const response = await fetch(`${PEST_DETECTION_URL}${path}`, {
      method: 'GET',
      headers: buildHeaders(token, tenantId),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Pest detection service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Pest detection service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Pest detection GET proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch pest detection data' },
      { status: 502 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST /api/pest-detection
// ═══════════════════════════════════════════════════════════════════════════

/**
 * POST /api/pest-detection
 * Body: { action: 'identify' | 'treatment', ... }
 *
 * action=identify   -> Identify pest from image (base64)
 * action=treatment  -> Recommend treatment for a detected pest
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
    const { action } = body;

    if (!action || typeof action !== 'string') {
      return NextResponse.json({ error: 'action is required' }, { status: 400 });
    }

    let path: string;
    let payload: Record<string, unknown>;

    switch (action) {
      case 'identify': {
        const { fieldId, image, image_url, crop_type, confidence_threshold } = body;

        if (fieldId && (typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId))) {
          return NextResponse.json({ error: 'Invalid fieldId format' }, { status: 400 });
        }

        if (!image && !image_url) {
          return NextResponse.json(
            { error: 'Either image (base64) or image_url is required' },
            { status: 400 }
          );
        }

        path = `/api/v1/pests/identify`;
        payload = {
          ...(fieldId != null && { field_id: fieldId }),
          ...(image != null && { image }),
          ...(image_url != null && { image_url }),
          ...(crop_type != null && { crop_type }),
          ...(confidence_threshold != null && { confidence_threshold }),
        };
        break;
      }
      case 'treatment': {
        const { pestId, fieldId, crop_type: cropType, severity: sev } = body;

        if (!pestId || typeof pestId !== 'string' || !SAFE_ID_PATTERN.test(pestId)) {
          return NextResponse.json({ error: 'Valid pestId is required' }, { status: 400 });
        }

        if (fieldId && (typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId))) {
          return NextResponse.json({ error: 'Invalid fieldId format' }, { status: 400 });
        }

        path = `/api/v1/pests/treatment`;
        payload = {
          pest_id: pestId,
          ...(fieldId != null && { field_id: fieldId }),
          ...(cropType != null && { crop_type: cropType }),
          ...(sev != null && { severity: sev }),
        };
        break;
      }
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: identify, treatment' },
          { status: 400 }
        );
    }

    const response = await fetch(`${PEST_DETECTION_URL}${path}`, {
      method: 'POST',
      headers: buildHeaders(token, tenantId),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Pest detection service returned non-JSON response' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Pest detection service timeout. Please retry.' },
        { status: 504 }
      );
    }
    logger.error('Pest detection POST proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process pest detection request' },
      { status: 502 }
    );
  }
}
