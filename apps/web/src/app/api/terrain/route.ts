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

/**
 * Upstream terrain service base URL. Validated at module load to prevent
 * accidental SSRF via mis-configured env vars. Must be an http(s):// URL.
 */
function resolveTerrainServiceUrl(): string {
  const raw = process.env.TERRAIN_SERVICE_URL || 'http://terrain-core-service:8185';
  try {
    const u = new URL(raw);
    if (u.protocol !== 'http:' && u.protocol !== 'https:') {
      throw new Error('unsupported protocol');
    }
    // Strip trailing slash so we can safely concatenate paths.
    return raw.replace(/\/+$/, '');
  } catch {
    // Fall back to a safe default rather than exposing the malformed value.
    return 'http://terrain-core-service:8185';
  }
}

const TERRAIN_SERVICE_URL = resolveTerrainServiceUrl();

// Terrain analysis (DEM acquisition + slope/aspect/flow) can take 30-60s for
// large fields. GET lookups are faster. Differentiate so slow analyses do not
// time out prematurely while still bounding GETs to keep the event loop healthy.
const GET_TIMEOUT_MS = 20_000;
const ANALYZE_TIMEOUT_MS = 90_000;

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

/** Allowed DEM source identifiers (mirrors backend DEMSourceType enum). */
const ALLOWED_DEM_SOURCES = new Set(['copernicus', 'srtm', 'aster', 'alos', 'local']);

/** Allowed slope unit identifiers (mirrors backend SlopeUnit enum). */
const ALLOWED_SLOPE_UNITS = new Set(['degrees', 'percent', 'radians']);

/**
 * GET /api/terrain?action=dem&fieldId=xxx
 * GET /api/terrain?action=slope&fieldId=xxx
 * GET /api/terrain?action=flow&fieldId=xxx
 * GET /api/terrain?action=twi&fieldId=xxx
 * GET /api/terrain?action=contours&fieldId=xxx
 *
 * Note: `aspect` is NOT a standalone backend endpoint — aspect data is
 * returned as part of the POST /analyze response. Callers should POST
 * `action=analyze` to obtain aspect.
 */
export async function GET(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
        { status: 401 }
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse params ---
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fieldId = searchParams.get('fieldId');

    if (fieldId && !SAFE_ID_PATTERN.test(fieldId)) {
      return NextResponse.json({ error: 'Invalid fieldId format', error_ar: 'تنسيق معرف الحقل غير صالح' }, { status: 400 });
    }

    let path: string;

    switch (action) {
      case 'dem': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        const params = new URLSearchParams();
        const demSource = searchParams.get('dem_source');
        const resolution = searchParams.get('resolution_m') || searchParams.get('resolution');
        if (demSource && ALLOWED_DEM_SOURCES.has(demSource.toLowerCase())) {
          params.set('dem_source', demSource.toLowerCase());
        }
        if (resolution) {
          const n = Number(resolution);
          if (Number.isFinite(n) && n >= 1 && n <= 1000) {
            params.set('resolution_m', String(n));
          }
        }
        const qs = params.toString();
        path = `/api/v1/terrain/dem/${encodeURIComponent(fieldId)}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'slope': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        const params = new URLSearchParams();
        const units = (searchParams.get('slope_unit') || searchParams.get('units') || '').toLowerCase();
        if (units && ALLOWED_SLOPE_UNITS.has(units)) {
          params.set('slope_unit', units);
        }
        const qs = params.toString();
        path = `/api/v1/terrain/slope/${encodeURIComponent(fieldId)}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'flow': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        path = `/api/v1/terrain/flow/${encodeURIComponent(fieldId)}`;
        break;
      }
      case 'twi': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        path = `/api/v1/terrain/twi/${encodeURIComponent(fieldId)}`;
        break;
      }
      case 'contours': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        path = `/api/v1/terrain/contours/${encodeURIComponent(fieldId)}`;
        break;
      }
      case 'aspect': {
        // Backend has no standalone /aspect endpoint; aspect is only produced
        // by POST /analyze. Return 400 to surface the misuse clearly.
        return NextResponse.json(
          {
            error: 'aspect is only available via POST /api/terrain with action=analyze',
            error_ar: 'الاتجاه متاح فقط عبر POST /api/terrain مع action=analyze',
          },
          { status: 400 }
        );
      }
      default:
        return NextResponse.json(
          {
            error: 'Invalid action. Use: dem, slope, flow, twi, contours',
            error_ar: 'إجراء غير صالح. استخدم: dem, slope, flow, twi, contours',
          },
          { status: 400 }
        );
    }

    const response = await fetch(`${TERRAIN_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: buildHeaders(token, tenantId),
      signal: AbortSignal.timeout(GET_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Terrain service returned non-JSON response', error_ar: 'خدمة التضاريس أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json(
        { error: 'Terrain service timeout. Please retry.', error_ar: 'انتهت مهلة خدمة التضاريس. يرجى المحاولة مرة أخرى.' },
        { status: 504 }
      );
    }
    logger.error('Terrain GET proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch terrain data', error_ar: 'فشل في جلب بيانات التضاريس' },
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
        { error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
        { status: 401 }
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse body ---
    const body = await request.json();
    const { action, fieldId } = body;

    if (!action || typeof action !== 'string') {
      return NextResponse.json({ error: 'action is required', error_ar: 'الإجراء مطلوب' }, { status: 400 });
    }

    if (!fieldId || typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId)) {
      return NextResponse.json({ error: 'Valid fieldId is required', error_ar: 'معرف حقل صالح مطلوب' }, { status: 400 });
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
          { error: 'Invalid action. Use: analyze', error_ar: 'إجراء غير صالح. استخدم: analyze' },
          { status: 400 }
        );
    }

    const response = await fetch(`${TERRAIN_SERVICE_URL}${path}`, {
      method: 'POST',
      headers: buildHeaders(token, tenantId),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(ANALYZE_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Terrain service returned non-JSON response', error_ar: 'خدمة التضاريس أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json(
        { error: 'Terrain analysis timeout. Please retry.', error_ar: 'انتهت مهلة تحليل التضاريس. يرجى المحاولة مرة أخرى.' },
        { status: 504 }
      );
    }
    logger.error('Terrain POST proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process terrain analysis request', error_ar: 'فشل في معالجة طلب تحليل التضاريس' },
      { status: 502 }
    );
  }
}
