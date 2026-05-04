/**
 * Satellite API catch-all proxy
 * وكيل API الأقمار الصناعية - يضيف رمز المصادقة من الكوكيز
 *
 * Intercepts /api/v1/satellite/* before Next.js rewrites forward them to Kong.
 * Kong requires an Authorization: Bearer header that the browser client cannot
 * provide (token is in an httpOnly cookie). This route reads the cookie
 * server-side and injects the header when forwarding to vegetation-analysis-service.
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import * as jose from 'jose';

const VEGETATION_SERVICE_URL =
  process.env.VEGETATION_SERVICE_URL || 'http://vegetation-analysis-service:8090';

function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

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
    const verifyOptions: jose.JWTVerifyOptions = { algorithms: ['HS256'] };
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

async function proxy(
  request: NextRequest,
  pathSegments: string[],
  method: string,
  body?: string,
): Promise<NextResponse> {
  const auth = await getAuthContext();
  if (!auth) {
    return NextResponse.json(
      { error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
      { status: 401 },
    );
  }
  const { tenantId, token } = auth;

  // Strip /api/v1/satellite prefix — route to service root paths (/fields, /stats, …)
  const path = '/' + pathSegments.join('/');
  const qs = new URL(request.url).searchParams.toString();
  const target = `${VEGETATION_SERVICE_URL}${path}${qs ? `?${qs}` : ''}`;

  const fetchOptions: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Tenant-Id': tenantId,
    },
    signal: AbortSignal.timeout(30000),
  };
  if (body) fetchOptions.body = body;

  const response = await fetch(target, fetchOptions);
  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  try {
    const { path } = await params;
    return proxy(request, path, 'GET');
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json(
        { error: 'Satellite service timeout', error_ar: 'انتهت مهلة خدمة الأقمار الصناعية' },
        { status: 504 },
      );
    }
    return NextResponse.json(
      { error: 'Failed to fetch satellite data', error_ar: 'فشل في جلب بيانات الأقمار الصناعية' },
      { status: 502 },
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  try {
    const { path } = await params;
    const body = await request.text();
    return proxy(request, path, 'POST', body);
  } catch (error: unknown) {
    if (error instanceof Error && (error.name === 'AbortError' || error.name === 'TimeoutError')) {
      return NextResponse.json(
        { error: 'Satellite service timeout', error_ar: 'انتهت مهلة خدمة الأقمار الصناعية' },
        { status: 504 },
      );
    }
    return NextResponse.json(
      { error: 'Failed to post satellite data', error_ar: 'فشل في إرسال بيانات الأقمار الصناعية' },
      { status: 502 },
    );
  }
}
