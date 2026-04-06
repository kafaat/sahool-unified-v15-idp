/**
 * Indicators API Proxy Route
 * وكيل واجهة برمجة تطبيقات المؤشرات
 *
 * Proxies field-indicator requests to indicators-service directly
 * (server-side only — not exposed to browser).
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import * as jose from 'jose';
import { logger } from '@/lib/logger';

const INDICATORS_SERVICE_URL =
  process.env.INDICATORS_SERVICE_URL || 'http://indicators-service:8091';

/** Validate fieldId to prevent path traversal */
const FIELD_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

/** Validate UUID format for tenant_id injection prevention */
function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

/**
 * Extract tenant_id from httpOnly JWT cookie server-side.
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
 * GET /api/indicators?fieldId=xxx
 * GET /api/indicators?action=dashboard&tenantId=xxx
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const fieldId = searchParams.get('fieldId');
    const action = searchParams.get('action') || 'field';
    const tenantId = searchParams.get('tenantId');

    // Auth enforcement
    const jwtTenantId = await getTenantId();
    if (!jwtTenantId) {
      return NextResponse.json(
        { error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
        { status: 401 }
      );
    }

    let path: string;

    if (action === 'dashboard') {
      const tid = tenantId || jwtTenantId;
      if (!isValidUUID(tid)) {
        return NextResponse.json(
          { error: 'Invalid tenantId format', error_ar: 'تنسيق معرف المستأجر غير صالح' },
          { status: 400 }
        );
      }
      path = `/v1/dashboard/${encodeURIComponent(tid)}`;
    } else {
      // Default: field indicators
      if (!fieldId) {
        return NextResponse.json(
          { error: 'fieldId required', error_ar: 'معرف الحقل مطلوب' },
          { status: 400 }
        );
      }
      if (!FIELD_ID_PATTERN.test(fieldId)) {
        return NextResponse.json(
          { error: 'Invalid fieldId format', error_ar: 'تنسيق معرف الحقل غير صالح' },
          { status: 400 }
        );
      }
      path = `/v1/field/${encodeURIComponent(fieldId)}/indicators`;
    }

    const response = await fetch(`${INDICATORS_SERVICE_URL}${path}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-Id': jwtTenantId,
      },
      signal: AbortSignal.timeout(15000),
    });

    const contentType = response.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(
        {
          error: 'Indicators service returned non-JSON response',
          error_ar: 'خدمة المؤشرات أرجعت استجابة غير JSON',
        },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json(
        {
          error: 'Indicators service timeout. Please retry.',
          error_ar: 'انتهت مهلة خدمة المؤشرات. يرجى المحاولة مرة أخرى.',
        },
        { status: 504 }
      );
    }
    logger.error('Indicators API proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch indicators data', error_ar: 'فشل في جلب بيانات المؤشرات' },
      { status: 502 }
    );
  }
}
