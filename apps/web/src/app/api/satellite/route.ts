/**
 * Satellite/NDVI API Proxy Routes
 * وكيل واجهة برمجة تطبيقات الأقمار الصناعية
 *
 * Proxies satellite data requests to vegetation-analysis-service directly
 * (server-side only -- not exposed to browser).
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import * as jose from 'jose';
import { logger } from '@/lib/logger';

const VEGETATION_SERVICE_URL =
  process.env.VEGETATION_SERVICE_URL || 'http://vegetation-analysis-service:8090';

/** Validate fieldId to prevent path traversal */
const FIELD_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

/** Validate UUID format for tenant_id injection prevention */
function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

/**
 * Extract tenant_id from httpOnly cookie server-side.
 * Uses jose library to decode the JWT from the web app's access_token cookie.
 */
async function getTenantId(): Promise<string | null> {
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
            return tenantId;
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
      return tenantId;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * GET /api/satellite?action=indices&fieldId=xxx
 * GET /api/satellite?action=timeseries&fieldId=xxx&days=90
 * GET /api/satellite?action=satellites
 * GET /api/satellite?action=providers
 * GET /api/satellite?action=eo-status
 * GET /api/satellite?action=sar-timeseries&fieldId=xxx&start_date=...&end_date=...
 * GET /api/satellite?action=cloud-cover&fieldId=xxx
 * GET /api/satellite?action=clear-observations&fieldId=xxx
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fieldId = searchParams.get('fieldId');
    const days = searchParams.get('days') || '90';
    const lat = searchParams.get('lat');
    const lon = searchParams.get('lon');

    // Auth enforcement
    const tenantId = await getTenantId();
    if (!tenantId) {
      return NextResponse.json({ error: 'Authentication required', error_ar: 'المصادقة مطلوبة' }, { status: 401 });
    }

    // Validate fieldId format if provided
    if (fieldId && !FIELD_ID_PATTERN.test(fieldId)) {
      return NextResponse.json({ error: 'Invalid fieldId format', error_ar: 'تنسيق معرف الحقل غير صالح' }, { status: 400 });
    }

    // Validate days as integer 1-365
    const parsedDays = parseInt(days, 10);
    if (isNaN(parsedDays) || parsedDays < 1 || parsedDays > 365) {
      return NextResponse.json({ error: 'days must be an integer between 1 and 365', error_ar: 'يجب أن يكون عدد الأيام بين 1 و 365' }, { status: 400 });
    }

    // Validate coordinates if provided
    if (lat && (isNaN(Number(lat)) || Number(lat) < -90 || Number(lat) > 90)) {
      return NextResponse.json({ error: 'lat must be between -90 and 90', error_ar: 'يجب أن يكون خط العرض بين -90 و 90' }, { status: 400 });
    }
    if (lon && (isNaN(Number(lon)) || Number(lon) < -180 || Number(lon) > 180)) {
      return NextResponse.json({ error: 'lon must be between -180 and 180', error_ar: 'يجب أن يكون خط الطول بين -180 و 180' }, { status: 400 });
    }

    let path: string;
    switch (action) {
      case 'indices': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        const params = new URLSearchParams();
        if (lat) params.set('lat', lat);
        if (lon) params.set('lon', lon);
        const qs = params.toString();
        path = `/v1/indices/${encodeURIComponent(fieldId)}${qs ? `?${qs}` : ''}`;
        break;
      }
      case 'timeseries': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        const tsParams = new URLSearchParams();
        tsParams.set('days', String(parsedDays));
        path = `/v1/timeseries/${encodeURIComponent(fieldId)}?${tsParams.toString()}`;
        break;
      }
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
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        const sarParams = new URLSearchParams();
        const startDate = searchParams.get('start_date');
        const endDate = searchParams.get('end_date');
        if (startDate) sarParams.set('start_date', startDate);
        if (endDate) sarParams.set('end_date', endDate);
        if (lat) sarParams.set('lat', lat);
        if (lon) sarParams.set('lon', lon);
        const sarQs = sarParams.toString();
        path = `/v1/sar-timeseries/${encodeURIComponent(fieldId)}${sarQs ? `?${sarQs}` : ''}`;
        break;
      }
      case 'cloud-cover': {
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        const ccParams = new URLSearchParams();
        if (lat) ccParams.set('lat', lat);
        if (lon) ccParams.set('lon', lon);
        const ccQs = ccParams.toString();
        path = `/v1/cloud-cover/${encodeURIComponent(fieldId)}${ccQs ? `?${ccQs}` : ''}`;
        break;
      }
      case 'clear-observations':
        if (!fieldId) {
          return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
        }
        path = `/v1/clear-observations/${encodeURIComponent(fieldId)}`;
        break;
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use: indices, timeseries, satellites, providers, eo-status, sar-timeseries, cloud-cover, clear-observations', error_ar: 'إجراء غير صالح' },
          { status: 400 }
        );
    }

    const response = await fetch(`${VEGETATION_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-Id': tenantId,
      },
      signal: AbortSignal.timeout(30000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        { error: 'Vegetation service returned non-JSON response', error_ar: 'خدمة الغطاء النباتي أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json({ error: 'Satellite service timeout. Please retry.', error_ar: 'انتهت مهلة خدمة الأقمار الصناعية. يرجى المحاولة مرة أخرى.' }, { status: 504 });
    }
    logger.error('Satellite API proxy error:', error);
    return NextResponse.json({ error: 'Failed to fetch satellite data', error_ar: 'فشل في جلب بيانات الأقمار الصناعية' }, { status: 502 });
  }
}

/**
 * POST /api/satellite
 * Body: { action: 'analyze', fieldId, analysisType, latitude?, longitude?, coordinates? }
 */
export async function POST(request: NextRequest) {
  try {
    // Auth enforcement (same as GET handler)
    const tenantId = await getTenantId();
    if (!tenantId) {
      return NextResponse.json({ error: 'Authentication required', error_ar: 'المصادقة مطلوبة' }, { status: 401 });
    }

    const body = await request.json();
    const { action, fieldId, analysisType } = body;

    if (action !== 'analyze') {
      return NextResponse.json({ error: 'POST only supports analyze action', error_ar: 'POST يدعم فقط إجراء التحليل' }, { status: 400 });
    }

    if (!fieldId) {
      return NextResponse.json({ error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' }, { status: 400 });
    }

    // Validate fieldId format
    if (typeof fieldId !== 'string' || !FIELD_ID_PATTERN.test(fieldId)) {
      return NextResponse.json({ error: 'Invalid fieldId format', error_ar: 'تنسيق معرف الحقل غير صالح' }, { status: 400 });
    }

    const { latitude, longitude, coordinates } = body;
    const response = await fetch(`${VEGETATION_SERVICE_URL}/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Tenant-Id': tenantId },
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
        { error: 'Vegetation service returned non-JSON response', error_ar: 'خدمة الغطاء النباتي أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json({ error: 'Satellite analysis timeout. Please retry.', error_ar: 'انتهت مهلة تحليل الأقمار الصناعية. يرجى المحاولة مرة أخرى.' }, { status: 504 });
    }
    logger.error('Satellite analyze proxy error:', error);
    return NextResponse.json({ error: 'Failed to analyze satellite data', error_ar: 'فشل في تحليل بيانات الأقمار الصناعية' }, { status: 502 });
  }
}
