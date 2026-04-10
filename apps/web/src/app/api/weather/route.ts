/**
 * Weather API Proxy Routes
 * وكيل واجهة برمجة تطبيقات الطقس
 *
 * Server-side proxy that extracts tenant_id from the httpOnly JWT cookie
 * and forwards weather requests to the backend weather-service.
 * This solves the issue where client-side code cannot read httpOnly cookies.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import * as jose from 'jose';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

// Weather service URL from environment, fallback to docker service name
const WEATHER_SERVICE_URL = process.env.WEATHER_SERVICE_URL || 'http://weather-service:8092';

const RATE_LIMIT_CONFIG = {
  windowMs: 60000, // 1 minute
  maxRequests: 60, // Weather queries per minute
  keyPrefix: 'weather-api',
};

/**
 * Validate UUID format for tenant_id injection prevention
 */
function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

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
 * Extract tenant_id and raw JWT from httpOnly cookie server-side.
 * Returns both so the Bearer token can be forwarded to backend services.
 */
async function getAuthContext(): Promise<{ tenantId: string; token: string } | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;
    if (!token) return null;

    const secretKey = process.env.JWT_SECRET_KEY;
    if (!secretKey) {
      if (process.env.NODE_ENV === 'development') {
        try {
          const payload = jose.decodeJwt(token);
          const tenantId = (payload as Record<string, unknown>).tid ?? payload.tenant_id;
          if (typeof tenantId === 'string' && isValidUUID(tenantId)) {
            return { tenantId, token };
          }
        } catch {
          return null;
        }
      }
      return null;
    }

    const secret = new TextEncoder().encode(secretKey);
    const verifyOptions: jose.JWTVerifyOptions = {};
    if (process.env.JWT_ISSUER) verifyOptions.issuer = process.env.JWT_ISSUER;
    if (process.env.JWT_AUDIENCE) verifyOptions.audience = process.env.JWT_AUDIENCE;

    const { payload } = await jose.jwtVerify(token, secret, verifyOptions);
    const tenantId = (payload as Record<string, unknown>).tid ?? payload.tenant_id;
    if (typeof tenantId === 'string' && isValidUUID(tenantId)) {
      return { tenantId, token };
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * POST /api/weather
 *
 * Proxies weather requests to the backend weather-service.
 * Expects JSON body with: { action, lat, lon, field_id?, days? }
 * where action is one of: "current", "forecast", "agricultural"
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);
    if (rateLimited) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.', error_ar: 'طلبات كثيرة جداً. يرجى المحاولة لاحقاً.' },
        { status: 429 }
      );
    }

    const body = await request.json();
    const { action, lat, lon, field_id, days } = body;

    if (!action || !['current', 'forecast', 'agricultural'].includes(action)) {
      return NextResponse.json(
        { error: 'Invalid action. Must be: current, forecast, or agricultural', error_ar: 'إجراء غير صالح. يجب أن يكون: current أو forecast أو agricultural' },
        { status: 400 }
      );
    }

    if (
      typeof lat !== 'number' ||
      typeof lon !== 'number' ||
      !Number.isFinite(lat) ||
      !Number.isFinite(lon) ||
      lat < -90 ||
      lat > 90 ||
      lon < -180 ||
      lon > 180
    ) {
      return NextResponse.json(
        { error: 'lat must be between -90 and 90, lon between -180 and 180', error_ar: 'يجب أن يكون خط العرض بين -90 و 90 وخط الطول بين -180 و 180' },
        { status: 400 }
      );
    }

    const auth = await getAuthContext();
    if (!auth) {
      return NextResponse.json({ error: 'Authentication required', error_ar: 'المصادقة مطلوبة' }, { status: 401 });
    }
    const { tenantId, token } = auth;

    // Build path based on action
    const pathMap: Record<string, string> = {
      current: '/weather/current',
      forecast: '/weather/forecast',
      agricultural: '/weather/agricultural-report',
    };

    // Validate field_id if provided -- must be UUID to prevent injection
    if (field_id !== undefined && field_id !== null && field_id !== 'default') {
      if (typeof field_id !== 'string' || !isValidUUID(field_id)) {
        return NextResponse.json({ error: 'field_id must be a valid UUID', error_ar: 'يجب أن يكون معرف الحقل UUID صالح' }, { status: 400 });
      }
    }

    const payload: Record<string, unknown> = {
      tenant_id: tenantId,
      field_id: field_id && isValidUUID(field_id) ? field_id : 'default',
      lat,
      lon,
    };

    if (action === 'forecast' && typeof days === 'number' && Number.isFinite(days)) {
      payload.days = Math.max(1, Math.min(30, Math.floor(days)));
    }

    const response = await fetch(`${WEATHER_SERVICE_URL}${pathMap[action]}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`, 'X-Tenant-Id': tenantId },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(15000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      const text = await response.text();
      logger.error('Weather service returned non-JSON response:', {
        status: response.status,
        contentType,
        body: text.slice(0, 200),
      });
      return NextResponse.json(
        { error: 'Weather service returned an unexpected response', error_ar: 'خدمة الطقس أعادت استجابة غير متوقعة' },
        { status: 502 }
      );
    }

    let data: unknown;
    try {
      data = await response.json();
    } catch {
      logger.error('Failed to parse weather service JSON response');
      return NextResponse.json({ error: 'Weather service returned invalid JSON', error_ar: 'خدمة الطقس أعادت JSON غير صالح' }, { status: 502 });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    logger.error('Weather API proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch weather data', error_ar: 'فشل في جلب بيانات الطقس' }, { status: 502 });
  }
}

/**
 * GET /api/weather?action=providers|locations|current|forecast&locationId=xxx&days=7
 *
 * Proxy for GET-based weather endpoints (providers list, location queries).
 * Extracts tenant_id from httpOnly JWT cookie and forwards as header.
 */
export async function GET(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);
    if (rateLimited) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.', error_ar: 'طلبات كثيرة جداً. يرجى المحاولة لاحقاً.' },
        { status: 429 }
      );
    }

    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const locationId = searchParams.get('locationId');
    const days = searchParams.get('days');

    // Extract tenant context
    const auth = await getAuthContext();
    if (!auth) {
      return NextResponse.json({ error: 'Authentication required', error_ar: 'المصادقة مطلوبة' }, { status: 401 });
    }
    const { tenantId, token } = auth;

    // Validate locationId against path traversal (must be UUID or slug)
    if (locationId && !/^[a-zA-Z0-9_-]+$/.test(locationId)) {
      return NextResponse.json({ error: 'Invalid locationId format', error_ar: 'صيغة معرف الموقع غير صالحة' }, { status: 400 });
    }

    let path: string;
    switch (action) {
      case 'providers':
        path = '/weather/providers';
        break;
      case 'locations':
        path = '/weather/locations';
        break;
      case 'current':
        if (!locationId) return NextResponse.json({ error: 'locationId required', error_ar: 'معرف الموقع مطلوب' }, { status: 400 });
        path = `/weather/current/${encodeURIComponent(locationId)}`;
        break;
      case 'forecast': {
        if (!locationId) return NextResponse.json({ error: 'locationId required', error_ar: 'معرف الموقع مطلوب' }, { status: 400 });
        const forecastParams = new URLSearchParams();
        if (days) {
          const parsedDays = parseInt(days, 10);
          if (isNaN(parsedDays) || parsedDays < 1 || parsedDays > 30) {
            return NextResponse.json({ error: 'days must be an integer between 1 and 30', error_ar: 'يجب أن يكون عدد الأيام بين 1 و 30' }, { status: 400 });
          }
          forecastParams.set('days', String(Math.max(1, Math.min(30, parsedDays))));
        }
        const forecastQs = forecastParams.toString();
        path = `/weather/forecast/${encodeURIComponent(locationId)}${forecastQs ? `?${forecastQs}` : ''}`;
        break;
      }
      default:
        return NextResponse.json({ error: 'Invalid action', error_ar: 'إجراء غير صالح' }, { status: 400 });
    }

    // Build headers with tenant context and Bearer token
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Tenant-Id': tenantId,
    };

    const response = await fetch(`${WEATHER_SERVICE_URL}${path}`, {
      method: 'GET',
      headers,
      signal: AbortSignal.timeout(15000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json({ error: 'Weather service returned non-JSON', error_ar: 'خدمة الطقس أعادت استجابة غير صالحة' }, { status: 502 });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    logger.error('Weather GET proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch weather data', error_ar: 'فشل في جلب بيانات الطقس' }, { status: 502 });
  }
}
