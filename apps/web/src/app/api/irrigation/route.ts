/**
 * Irrigation API Proxy Route
 * مسار وكيل API للري
 *
 * Server-side proxy that forwards irrigation requests to the irrigation-smart
 * backend service. Reads the httpOnly access_token cookie to extract tenant_id
 * from the JWT and forwards it to the backend service.
 *
 * GET  /api/irrigation        - Get irrigation data (methods, crops, water balance)
 * POST /api/irrigation        - Calculate irrigation amount for a field
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const IRRIGATION_SERVICE_URL =
  process.env.IRRIGATION_SERVICE_URL || 'http://irrigation-smart:8094';

const VALID_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

const VALID_RESOURCES = ['methods', 'crops', 'water-balance'] as const;
type IrrigationResource = (typeof VALID_RESOURCES)[number];

/**
 * Map the UI-facing resource to the actual backend path on the
 * irrigation-smart service. The backend exposes routes at `/v1/...`
 * (no `/api` prefix), and `water-balance` takes the field id as a
 * path parameter rather than a query string.
 */
function buildBackendPath(resource: IrrigationResource, fieldId: string | null): string {
  switch (resource) {
    case 'methods':
      return '/v1/methods';
    case 'crops':
      return '/v1/crops';
    case 'water-balance':
      // fieldId is required & already validated against VALID_ID_PATTERN by the caller
      return `/v1/water-balance/${encodeURIComponent(fieldId ?? '')}`;
  }
}

const RATE_LIMIT_CONFIG = {
  windowMs: 60000,
  maxRequests: 60,
  keyPrefix: 'irrigation-proxy',
};

const REQUEST_TIMEOUT_MS = 15000;

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get client IP address for rate limiting
 */
function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIp = request.headers.get('x-real-ip');

  if (forwarded) {
    const firstIp = forwarded.split(',')[0];
    return firstIp ? firstIp.trim() : 'unknown';
  }

  if (realIp) {
    return realIp;
  }

  return 'unknown';
}

/**
 * Extract tenant_id from the httpOnly access_token JWT cookie.
 * Decodes the JWT payload (base64url) without signature verification
 * since the middleware already validates the token on protected routes.
 */
function extractTenantId(token: string): string | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) {
      return null;
    }

    // Decode base64url payload
    const payload = JSON.parse(
      Buffer.from(parts[1], 'base64url').toString('utf-8')
    );

    // Backend uses 'tid' claim; accept both for compatibility
    const tenantId = payload.tid ?? payload.tenant_id;
    if (typeof tenantId === 'string' && tenantId.length > 0) {
      return tenantId;
    }

    return null;
  } catch {
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// GET: Irrigation Data (methods, crops, water balance)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Retrieve irrigation data for the authenticated tenant.
 *
 * Query parameters:
 *   resource: "methods" | "crops" | "water-balance" (required)
 *   fieldId:  field identifier (required for water-balance)
 *   season:   season filter (optional)
 */
export async function GET(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    // Extract access token from httpOnly cookie
    const cookieStore = await cookies();
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
      return NextResponse.json(
        { success: false, error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Extract tenant_id from JWT payload
    const tenantId = extractTenantId(accessToken);
    if (!tenantId) {
      return NextResponse.json(
        { success: false, error: 'Invalid token: missing tenant_id' },
        { status: 401 }
      );
    }

    // Parse and validate query parameters
    const { searchParams } = request.nextUrl;
    const resource = searchParams.get('resource') as IrrigationResource | null;

    if (!resource || !VALID_RESOURCES.includes(resource)) {
      return NextResponse.json(
        {
          success: false,
          error: `Missing or invalid resource. Must be one of: ${VALID_RESOURCES.join(', ')}`,
        },
        { status: 400 }
      );
    }

    // Validate fieldId if provided
    const fieldId = searchParams.get('fieldId');
    if (fieldId && !VALID_ID_PATTERN.test(fieldId)) {
      return NextResponse.json(
        { success: false, error: 'Invalid fieldId format' },
        { status: 400 }
      );
    }

    // water-balance requires fieldId
    if (resource === 'water-balance' && !fieldId) {
      return NextResponse.json(
        { success: false, error: 'fieldId is required for water-balance resource' },
        { status: 400 }
      );
    }

    // Build query parameters for the backend. The irrigation-smart service
    // reads tenant_id from the JWT `tid` claim, so it is not strictly
    // required as a query parameter, but we forward it for any downstream
    // logging/compat. field_id is passed as a path param for water-balance.
    const backendParams = new URLSearchParams();
    backendParams.set('tenant_id', tenantId);

    // Forward optional query params that the backend actually accepts.
    // Only known-safe params are allow-listed to avoid SSRF / param injection.
    const allowedParams = ['season', 'crop', 'crop_type', 'days', 'page', 'limit'];
    for (const param of allowedParams) {
      const value = searchParams.get(param);
      if (value !== null && value.length <= 100) {
        backendParams.set(param, value);
      }
    }

    const backendPath = buildBackendPath(resource, fieldId);
    const query = backendParams.toString();
    const backendUrl = `${IRRIGATION_SERVICE_URL}${backendPath}${query ? `?${query}` : ''}`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { success: false, error: 'Irrigation service returned non-JSON response', error_ar: 'خدمة الري أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || data.message || `Failed to fetch ${resource}`,
        },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true, data });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      logger.error('[Irrigation API] Request to irrigation-smart timed out');
      return NextResponse.json(
        { success: false, error: 'Request timed out' },
        { status: 504 }
      );
    }

    logger.error('[Irrigation API] Error fetching irrigation data:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST: Calculate Irrigation Amount
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Calculate irrigation amount for a given field.
 *
 * Request body (matches irrigation-smart IrrigationRequest):
 * {
 *   fieldId: string,                 // required — will be forwarded as field_id
 *   crop: string,                    // required — crop type (wheat, tomato, ...)
 *   growth_stage: string,            // required — seedling/vegetative/...
 *   area_hectares: number,           // required — > 0
 *   soil_type?: string,              // optional — defaults to loamy on backend
 *   irrigation_method?: string,      // optional — defaults to drip on backend
 *   current_soil_moisture?: number,  // optional — 0..100
 *   last_irrigation_date?: string,   // optional — ISO date string
 *   weather_forecast?: Record<string, unknown>
 * }
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, {
      ...RATE_LIMIT_CONFIG,
      maxRequests: 30,
      keyPrefix: 'irrigation-calculate',
    });

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: 'Too many requests. Please try again later.' },
        { status: 429 }
      );
    }

    // Extract access token from httpOnly cookie
    const cookieStore = await cookies();
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
      return NextResponse.json(
        { success: false, error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Extract tenant_id from JWT payload
    const tenantId = extractTenantId(accessToken);
    if (!tenantId) {
      return NextResponse.json(
        { success: false, error: 'Invalid token: missing tenant_id' },
        { status: 401 }
      );
    }

    // Parse and validate request body
    let body: Record<string, unknown>;
    try {
      body = (await request.json()) as Record<string, unknown>;
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON body' },
        { status: 400 }
      );
    }

    const {
      fieldId,
      crop,
      crop_type,
      growth_stage,
      area_hectares,
      soil_type,
      soil_moisture,
      current_soil_moisture,
      weather_data,
      weather_forecast,
      irrigation_method,
      last_irrigation_date,
    } = body as {
      fieldId?: string;
      crop?: string;
      crop_type?: string;
      growth_stage?: string;
      area_hectares?: number;
      soil_type?: string;
      soil_moisture?: number;
      current_soil_moisture?: number;
      weather_data?: Record<string, unknown>;
      weather_forecast?: Record<string, unknown>;
      irrigation_method?: string;
      last_irrigation_date?: string;
    };

    // Validate fieldId (required)
    if (!fieldId || typeof fieldId !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Missing required field: fieldId' },
        { status: 400 }
      );
    }

    if (!VALID_ID_PATTERN.test(fieldId)) {
      return NextResponse.json(
        { success: false, error: 'Invalid fieldId format' },
        { status: 400 }
      );
    }

    // Validate required backend fields to fail fast instead of round-tripping
    // to irrigation-smart for a 422.
    const resolvedCrop = crop ?? crop_type;
    if (!resolvedCrop || typeof resolvedCrop !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Missing required field: crop' },
        { status: 400 }
      );
    }
    if (!growth_stage || typeof growth_stage !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Missing required field: growth_stage' },
        { status: 400 }
      );
    }
    if (typeof area_hectares !== 'number' || !Number.isFinite(area_hectares) || area_hectares <= 0) {
      return NextResponse.json(
        { success: false, error: 'Invalid or missing field: area_hectares (must be > 0)' },
        { status: 400 }
      );
    }

    // Backend exposes /v1/calculate — NOT /api/v1/irrigation/calculate.
    const backendUrl = `${IRRIGATION_SERVICE_URL}/v1/calculate`;

    // Map to the backend IrrigationRequest schema (snake_case field names).
    // Accept both soil_moisture and current_soil_moisture for compatibility.
    const resolvedMoisture = current_soil_moisture ?? soil_moisture;
    const resolvedWeather = weather_forecast ?? weather_data;

    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        field_id: fieldId,
        crop: resolvedCrop,
        growth_stage,
        area_hectares,
        ...(soil_type ? { soil_type } : {}),
        ...(irrigation_method ? { irrigation_method } : {}),
        ...(resolvedMoisture !== undefined ? { current_soil_moisture: resolvedMoisture } : {}),
        ...(last_irrigation_date ? { last_irrigation_date } : {}),
        ...(resolvedWeather ? { weather_forecast: resolvedWeather } : {}),
      }),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { success: false, error: 'Irrigation service returned non-JSON response', error_ar: 'خدمة الري أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || data.message || 'Failed to calculate irrigation',
        },
        { status: response.status }
      );
    }

    return NextResponse.json({
      success: true,
      data,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      logger.error('[Irrigation API] Request to irrigation-smart timed out');
      return NextResponse.json(
        { success: false, error: 'Request timed out' },
        { status: 504 }
      );
    }

    logger.error('[Irrigation API] Error calculating irrigation:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    );
  }
}
