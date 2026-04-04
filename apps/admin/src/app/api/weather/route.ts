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
import { getUserFromToken } from '@/lib/auth/jwt-verify';
import { logger } from '@/lib/logger';

// Weather service URL from environment, fallback to docker service name
const WEATHER_SERVICE_URL = process.env.WEATHER_SERVICE_URL || 'http://weather-service:8092';

/**
 * Validate UUID format for tenant_id injection prevention
 */
function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

/**
 * Extract tenant_id from httpOnly cookie server-side.
 * Returns the tenant_id string on success, or null if auth is missing/invalid.
 */
async function getTenantId(): Promise<string | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;
    if (!token) return null;

    const user = await getUserFromToken(token);
    if (user?.tenant_id && isValidUUID(user.tenant_id)) {
      return user.tenant_id;
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
    const body = await request.json();
    const { action, lat, lon, field_id, days } = body;

    if (!action || !['current', 'forecast', 'agricultural'].includes(action)) {
      return NextResponse.json(
        { error: 'Invalid action. Must be: current, forecast, or agricultural' },
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
        { error: 'lat must be between -90 and 90, lon between -180 and 180' },
        { status: 400 }
      );
    }

    const tenantId = await getTenantId();
    if (!tenantId) {
      return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
    }

    // Build path based on action
    const pathMap: Record<string, string> = {
      current: '/weather/current',
      forecast: '/weather/forecast',
      agricultural: '/weather/agricultural-report',
    };

    // Validate field_id if provided — must be UUID to prevent injection
    if (field_id !== undefined && field_id !== null && field_id !== 'default') {
      if (typeof field_id !== 'string' || !isValidUUID(field_id)) {
        return NextResponse.json({ error: 'field_id must be a valid UUID' }, { status: 400 });
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
      headers: { 'Content-Type': 'application/json' },
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
        { error: 'Weather service returned an unexpected response' },
        { status: 502 }
      );
    }

    let data: unknown;
    try {
      data = await response.json();
    } catch {
      logger.error('Failed to parse weather service JSON response');
      return NextResponse.json({ error: 'Weather service returned invalid JSON' }, { status: 502 });
    }

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    logger.error('Weather API proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch weather data' }, { status: 502 });
  }
}

/**
 * GET /api/weather?action=providers|locations|current|forecast&locationId=xxx&days=7
 *
 * Proxy for GET-based weather endpoints (providers list, location queries).
 * Forwards the request to the weather service without injecting tenant context.
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const locationId = searchParams.get('locationId');
    const days = searchParams.get('days');

    let path: string;
    switch (action) {
      case 'providers':
        path = '/weather/providers';
        break;
      case 'locations':
        path = '/weather/locations';
        break;
      case 'current':
        if (!locationId) return NextResponse.json({ error: 'locationId required' }, { status: 400 });
        path = `/weather/current/${locationId}`;
        break;
      case 'forecast': {
        if (!locationId) return NextResponse.json({ error: 'locationId required' }, { status: 400 });
        const forecastParams = new URLSearchParams();
        if (days) forecastParams.set('days', days);
        const forecastQs = forecastParams.toString();
        path = `/weather/forecast/${locationId}${forecastQs ? `?${forecastQs}` : ''}`;
        break;
      }
      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

    const response = await fetch(`${WEATHER_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      signal: AbortSignal.timeout(15000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json({ error: 'Weather service returned non-JSON' }, { status: 502 });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    logger.error('Weather GET proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch weather data' }, { status: 502 });
  }
}
