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

    // Build query parameters for the backend
    const backendParams = new URLSearchParams();
    backendParams.set('tenant_id', tenantId);

    if (fieldId) {
      backendParams.set('field_id', fieldId);
    }

    // Forward optional query params
    const allowedParams = ['season', 'crop_type', 'page', 'limit'];
    for (const param of allowedParams) {
      const value = searchParams.get(param);
      if (value !== null) {
        backendParams.set(param, value);
      }
    }

    const backendUrl = `${IRRIGATION_SERVICE_URL}/api/v1/irrigation/${resource}?${backendParams.toString()}`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

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
 * Request body:
 * {
 *   fieldId: string,
 *   crop_type?: string,
 *   soil_moisture?: number,
 *   weather_data?: { temperature: number, humidity: number, rain_forecast: number },
 *   irrigation_method?: string
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
    const body = await request.json();

    const { fieldId, crop_type, soil_moisture, weather_data, irrigation_method } = body as {
      fieldId?: string;
      crop_type?: string;
      soil_moisture?: number;
      weather_data?: { temperature: number; humidity: number; rain_forecast: number };
      irrigation_method?: string;
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

    const backendUrl = `${IRRIGATION_SERVICE_URL}/api/v1/irrigation/calculate`;

    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        tenant_id: tenantId,
        field_id: fieldId,
        ...(crop_type ? { crop_type } : {}),
        ...(soil_moisture !== undefined ? { soil_moisture } : {}),
        ...(weather_data ? { weather_data } : {}),
        ...(irrigation_method ? { irrigation_method } : {}),
      }),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

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
