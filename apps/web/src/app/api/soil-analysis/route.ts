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

/**
 * Upstream soil-analysis-service URL.
 * Validated at module load to prevent SSRF via misconfigured env vars:
 * must be http(s) and resolve to a hostname (no IP literals to internal
 * link-local ranges, no file://, etc.).
 */
function resolveUpstreamUrl(): string {
  const raw = process.env.SOIL_ANALYSIS_URL || 'http://soil-analysis-service:8134';
  try {
    const parsed = new URL(raw);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      logger.warn('Invalid SOIL_ANALYSIS_URL protocol, falling back to default', {
        protocol: parsed.protocol,
      });
      return 'http://soil-analysis-service:8134';
    }
    // Strip trailing slash for consistent path joining
    return `${parsed.protocol}//${parsed.host}`;
  } catch {
    logger.warn('Invalid SOIL_ANALYSIS_URL, falling back to default');
    return 'http://soil-analysis-service:8134';
  }
}

const SOIL_ANALYSIS_URL = resolveUpstreamUrl();

/** Default timeout for quick reads (soil data, type lookups). */
const REQUEST_TIMEOUT_MS = 15_000;

/** Extended timeout for long analyses (interpret, amendment plans). */
const LONG_ANALYSIS_TIMEOUT_MS = 45_000;

/**
 * Validate IDs to prevent path traversal and header injection.
 * Accepts alphanumerics, underscore, hyphen; capped at 128 chars to avoid
 * unbounded inputs being forwarded upstream.
 */
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]{1,128}$/;

/** Validate tenant IDs forwarded in headers to prevent CRLF/header injection. */
const SAFE_TENANT_ID_PATTERN = /^[a-zA-Z0-9_-]{1,128}$/;

/**
 * Bilingual error helper. Ensures every proxy error response carries
 * both English and Arabic messages for UX consistency.
 */
function errorResponse(
  en: string,
  ar: string,
  status: number
): NextResponse {
  return NextResponse.json({ error: en, error_ar: ar }, { status });
}

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
 *
 * The returned value is validated against SAFE_TENANT_ID_PATTERN so we never
 * forward untrusted characters (e.g. CRLF) in an HTTP header.
 */
function extractTenantId(token: string): string | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) return null;
    // Cap payload size to avoid parsing pathological JWTs.
    if (parts[1].length > 8192) return null;
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf-8'));
    const raw =
      (typeof payload.tid === 'string' && payload.tid) ||
      (typeof payload.tenant_id === 'string' && payload.tenant_id) ||
      null;
    if (!raw) return null;
    return SAFE_TENANT_ID_PATTERN.test(raw) ? raw : null;
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
    // Backend expects X-Tenant-Id (see soil_tests.py get_tenant_id()).
    headers['X-Tenant-Id'] = tenantId;
  }
  return headers;
}

/**
 * Detect timeout/abort errors from fetch + AbortSignal.timeout().
 * Node uses TimeoutError (DOMException) while some polyfills raise AbortError.
 */
function isTimeoutError(error: unknown): boolean {
  if (!(error instanceof Error)) return false;
  return error.name === 'TimeoutError' || error.name === 'AbortError';
}

// ═══════════════════════════════════════════════════════════════════════════
// GET /api/soil-analysis
// ═══════════════════════════════════════════════════════════════════════════

/**
 * GET /api/soil-analysis?action=soil-data&fieldId=xxx
 *   → upstream: GET /api/v1/soil/tests/field/{fieldId}
 * GET /api/soil-analysis?action=soil-test&testId=xxx
 *   → upstream: GET /api/v1/soil/tests/{testId}
 * GET /api/soil-analysis?action=products
 *   → upstream: GET /api/v1/soil/products
 * GET /api/soil-analysis?action=crop-requirements&crop=wheat
 *   → upstream: GET /api/v1/soil/crops/{crop}/requirements
 */
export async function GET(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return errorResponse(
        'Authentication required',
        'مطلوب تسجيل الدخول',
        401
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse params ---
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fieldId = searchParams.get('fieldId');
    const testId = searchParams.get('testId');

    if (fieldId && !SAFE_ID_PATTERN.test(fieldId)) {
      return errorResponse(
        'Invalid fieldId format',
        'صيغة معرف الحقل غير صالحة',
        400
      );
    }
    if (testId && !SAFE_ID_PATTERN.test(testId)) {
      return errorResponse(
        'Invalid testId format',
        'صيغة معرف التحليل غير صالحة',
        400
      );
    }

    let path: string;

    switch (action) {
      case 'soil-data': {
        if (!fieldId) {
          return errorResponse(
            'fieldId required',
            'معرف الحقل مطلوب',
            400
          );
        }
        // Backend: GET /api/v1/soil/tests/field/{field_id}
        path = `/api/v1/soil/tests/field/${encodeURIComponent(fieldId)}`;
        break;
      }
      case 'soil-test': {
        if (!testId) {
          return errorResponse(
            'testId required',
            'معرف التحليل مطلوب',
            400
          );
        }
        path = `/api/v1/soil/tests/${encodeURIComponent(testId)}`;
        break;
      }
      case 'products': {
        path = `/api/v1/soil/products`;
        break;
      }
      case 'crop-requirements': {
        const crop = searchParams.get('crop');
        if (!crop || !SAFE_ID_PATTERN.test(crop)) {
          return errorResponse(
            'Valid crop parameter required',
            'مطلوب معرف محصول صالح',
            400
          );
        }
        path = `/api/v1/soil/crops/${encodeURIComponent(crop)}/requirements`;
        break;
      }
      default:
        return errorResponse(
          'Invalid action. Use: soil-data, soil-test, products, crop-requirements',
          'إجراء غير صالح. استخدم: soil-data, soil-test, products, crop-requirements',
          400
        );
    }

    const response = await fetch(`${SOIL_ANALYSIS_URL}${path}`, {
      method: 'GET',
      headers: buildHeaders(token, tenantId),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return errorResponse(
        'Soil analysis service returned non-JSON response',
        'خدمة تحليل التربة أرجعت استجابة غير صالحة',
        502
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (isTimeoutError(error)) {
      return errorResponse(
        'Soil analysis service timeout. Please retry.',
        'انتهت مهلة خدمة تحليل التربة. يرجى المحاولة لاحقاً.',
        504
      );
    }
    logger.error('Soil analysis GET proxy error:', error);
    return errorResponse(
      'Failed to fetch soil analysis data',
      'فشل جلب بيانات تحليل التربة',
      502
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST /api/soil-analysis
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validate that a value is a finite number within an allowed range.
 * Returns the number or null if invalid.
 */
function validNumber(value: unknown, min: number, max: number): number | null {
  if (typeof value !== 'number' || !Number.isFinite(value)) return null;
  if (value < min || value > max) return null;
  return value;
}

/**
 * POST /api/soil-analysis
 * Body shapes (discriminated by `action`):
 *
 *   { action: 'interpret', testId, crop? }
 *     → upstream: POST /api/v1/soil/interpret { test_id, crop }
 *
 *   { action: 'amendment-plan', testId, crop?, target_yield_t_ha?, area_ha? }
 *     → upstream: POST /api/v1/soil/recommendations/amendment-plan
 *
 *   { action: 'create-test', fieldId, sample_date?, sample_depth_cm?,
 *     macronutrients: { nitrogen_nitrate_ppm, phosphorus_ppm, potassium_ppm },
 *     soil_properties: { ph, ec_ds_m, organic_matter_percent } }
 *     → upstream: POST /api/v1/soil/tests
 *
 *   { action: 'ph-status', ph }
 *     → upstream: POST /api/v1/soil/interpretation/ph-status
 *
 *   { action: 'ec-status', ec_ds_m }
 *     → upstream: POST /api/v1/soil/interpretation/ec-status
 */
export async function POST(request: NextRequest) {
  try {
    // --- Auth ---
    const token = await getAccessToken();
    if (!token) {
      return errorResponse(
        'Authentication required',
        'مطلوب تسجيل الدخول',
        401
      );
    }
    const tenantId = extractTenantId(token);

    // --- Parse body ---
    let body: Record<string, unknown>;
    try {
      body = await request.json();
    } catch {
      return errorResponse(
        'Invalid JSON body',
        'محتوى الطلب غير صالح',
        400
      );
    }
    if (!body || typeof body !== 'object') {
      return errorResponse(
        'Invalid request body',
        'جسم الطلب غير صالح',
        400
      );
    }

    const action = body.action;
    if (!action || typeof action !== 'string') {
      return errorResponse(
        'action is required',
        'حقل الإجراء مطلوب',
        400
      );
    }

    let path: string;
    let payload: Record<string, unknown>;
    let timeoutMs: number = REQUEST_TIMEOUT_MS;

    switch (action) {
      case 'interpret': {
        const testId = body.testId;
        if (typeof testId !== 'string' || !SAFE_ID_PATTERN.test(testId)) {
          return errorResponse(
            'Valid testId is required',
            'مطلوب معرف تحليل صالح',
            400
          );
        }
        const crop = typeof body.crop === 'string' && SAFE_ID_PATTERN.test(body.crop)
          ? body.crop
          : 'wheat';
        path = `/api/v1/soil/interpret`;
        payload = { test_id: testId, crop };
        timeoutMs = LONG_ANALYSIS_TIMEOUT_MS;
        break;
      }
      case 'amendment-plan': {
        const testId = body.testId;
        if (typeof testId !== 'string' || !SAFE_ID_PATTERN.test(testId)) {
          return errorResponse(
            'Valid testId is required',
            'مطلوب معرف تحليل صالح',
            400
          );
        }
        const crop = typeof body.crop === 'string' && SAFE_ID_PATTERN.test(body.crop)
          ? body.crop
          : 'wheat';
        const targetYield = validNumber(body.target_yield_t_ha, 0, 50) ?? 5.0;
        const areaHa = validNumber(body.area_ha, 0, 100_000) ?? 1.0;
        path = `/api/v1/soil/recommendations/amendment-plan`;
        payload = {
          test_id: testId,
          crop,
          target_yield_t_ha: targetYield,
          area_ha: areaHa,
        };
        timeoutMs = LONG_ANALYSIS_TIMEOUT_MS;
        break;
      }
      case 'create-test': {
        const fieldId = body.fieldId;
        if (typeof fieldId !== 'string' || !SAFE_ID_PATTERN.test(fieldId)) {
          return errorResponse(
            'Valid fieldId is required',
            'مطلوب معرف حقل صالح',
            400
          );
        }
        const macronutrients = body.macronutrients as
          | Record<string, unknown>
          | undefined;
        const soilProperties = body.soil_properties as
          | Record<string, unknown>
          | undefined;
        if (!macronutrients || !soilProperties) {
          return errorResponse(
            'macronutrients and soil_properties are required',
            'العناصر الغذائية وخصائص التربة مطلوبة',
            400
          );
        }

        // Parse & validate required nutrient values (ppm, must be non-negative).
        const n = validNumber(macronutrients.nitrogen_nitrate_ppm, 0, 10_000);
        const p = validNumber(macronutrients.phosphorus_ppm, 0, 10_000);
        const k = validNumber(macronutrients.potassium_ppm, 0, 10_000);
        if (n === null || p === null || k === null) {
          return errorResponse(
            'Invalid NPK values (must be 0-10000 ppm)',
            'قيم العناصر الغذائية غير صالحة (يجب أن تكون 0-10000 جزء في المليون)',
            400
          );
        }

        // pH must be 0-14, EC non-negative, OM 0-100%.
        const ph = validNumber(soilProperties.ph, 0, 14);
        const ec = validNumber(soilProperties.ec_ds_m, 0, 100);
        const om = validNumber(soilProperties.organic_matter_percent, 0, 100);
        if (ph === null || ec === null || om === null) {
          return errorResponse(
            'Invalid soil properties (pH 0-14, EC 0-100 dS/m, OM 0-100%)',
            'خصائص تربة غير صالحة',
            400
          );
        }

        path = `/api/v1/soil/tests`;
        payload = {
          field_id: fieldId,
          sample_depth_cm: validNumber(body.sample_depth_cm, 0, 500) ?? 30.0,
          macronutrients: {
            nitrogen_nitrate_ppm: n,
            phosphorus_ppm: p,
            potassium_ppm: k,
          },
          soil_properties: {
            ph,
            ec_ds_m: ec,
            organic_matter_percent: om,
          },
        };
        break;
      }
      case 'ph-status': {
        const ph = validNumber(body.ph, 0, 14);
        if (ph === null) {
          return errorResponse(
            'Valid pH (0-14) is required',
            'مطلوب قيمة pH صالحة (0-14)',
            400
          );
        }
        path = `/api/v1/soil/interpretation/ph-status`;
        payload = { ph };
        break;
      }
      case 'ec-status': {
        const ec = validNumber(body.ec_ds_m, 0, 100);
        if (ec === null) {
          return errorResponse(
            'Valid ec_ds_m (0-100) is required',
            'مطلوب قيمة ملوحة صالحة (0-100 ديسيسيمنز/م)',
            400
          );
        }
        path = `/api/v1/soil/interpretation/ec-status`;
        payload = { ec_ds_m: ec };
        break;
      }
      default:
        return errorResponse(
          'Invalid action. Use: interpret, amendment-plan, create-test, ph-status, ec-status',
          'إجراء غير صالح',
          400
        );
    }

    const response = await fetch(`${SOIL_ANALYSIS_URL}${path}`, {
      method: 'POST',
      headers: buildHeaders(token, tenantId),
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(timeoutMs),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return errorResponse(
        'Soil analysis service returned non-JSON response',
        'خدمة تحليل التربة أرجعت استجابة غير صالحة',
        502
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (isTimeoutError(error)) {
      return errorResponse(
        'Soil analysis service timeout. Please retry.',
        'انتهت مهلة خدمة تحليل التربة. يرجى المحاولة لاحقاً.',
        504
      );
    }
    logger.error('Soil analysis POST proxy error:', error);
    return errorResponse(
      'Failed to process soil analysis request',
      'فشل معالجة طلب تحليل التربة',
      502
    );
  }
}
