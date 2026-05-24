import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import * as jose from 'jose';

const VEGETATION_SERVICE_URL =
  process.env.VEGETATION_SERVICE_URL || 'http://vegetation-analysis-service:8090';

const VALID_PERIODS = new Set(['7d', '30d', '90d']);
const VALID_STATUSES = new Set(['completed', 'missed', 'skipped', 'retry_pending', 'failed']);

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
    const { payload } = await jose.jwtVerify(token, secret, { algorithms: ['HS256'] });
    const tenantId = (payload as Record<string, unknown>).tid ?? payload.tenant_id;
    if (typeof tenantId === 'string' && isValidUUID(tenantId)) {
      return { tenantId, token };
    }
    return null;
  } catch {
    return null;
  }
}

/** Empty fallback when the backend endpoint is not yet available */
function emptyLogsResponse(page: number, limit: number) {
  return { logs: [], total: 0, page, limit, hasMore: false };
}

function emptyStatsResponse(period: string) {
  return {
    totalRuns: 0,
    successfulRuns: 0,
    failedRuns: 0,
    missedRuns: 0,
    successRate: 0,
    lastRunAt: null,
    nextRunAt: null,
    totalFieldsProcessed: 0,
    averageCloudCover: 0,
    period,
  };
}

export async function POST(_request: NextRequest) {
  const auth = await getAuthContext();
  if (!auth) {
    return NextResponse.json(
      { error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
      { status: 401 }
    );
  }
  const { tenantId, token } = auth;

  try {
    const res = await fetch(`${VEGETATION_SERVICE_URL}/v1/scheduler/trigger`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-Id': tenantId,
        Authorization: `Bearer ${token}`,
      },
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json(
      { error: 'Failed to reach scheduler service', error_ar: 'تعذّر الوصول إلى خدمة المجدول' },
      { status: 502 }
    );
  }
}

export async function GET(request: NextRequest) {
  const auth = await getAuthContext();
  if (!auth) {
    return NextResponse.json(
      { error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
      { status: 401 }
    );
  }
  const { tenantId, token } = auth;

  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') ?? 'logs';
  const period = searchParams.get('period') ?? '30d';
  const status = searchParams.get('status') ?? '';
  const search = searchParams.get('search') ?? '';
  const pageRaw = parseInt(searchParams.get('page') ?? '1', 10);
  const limitRaw = parseInt(searchParams.get('limit') ?? '50', 10);

  if (!VALID_PERIODS.has(period)) {
    return NextResponse.json({ error: 'Invalid period. Use: 7d, 30d, 90d' }, { status: 400 });
  }
  if (status && !VALID_STATUSES.has(status)) {
    return NextResponse.json({ error: 'Invalid status value' }, { status: 400 });
  }
  const page = isNaN(pageRaw) || pageRaw < 1 ? 1 : pageRaw;
  const limit = isNaN(limitRaw) || limitRaw < 1 || limitRaw > 200 ? 50 : limitRaw;

  const headers = {
    'Content-Type': 'application/json',
    'X-Tenant-Id': tenantId,
    Authorization: `Bearer ${token}`,
  };

  if (action === 'stats') {
    try {
      const res = await fetch(
        `${VEGETATION_SERVICE_URL}/v1/scheduler/stats?period=${period}`,
        { method: 'GET', headers, signal: AbortSignal.timeout(15000) }
      );
      if (res.status === 404) {
        return NextResponse.json(emptyStatsResponse(period));
      }
      const data = await res.json();
      return NextResponse.json(data, { status: res.status });
    } catch {
      return NextResponse.json(emptyStatsResponse(period));
    }
  }

  // Default: fetch logs
  const params = new URLSearchParams({
    period,
    page: String(page),
    limit: String(limit),
  });
  if (status) params.set('status', status);
  if (search) params.set('search', search);

  try {
    const res = await fetch(
      `${VEGETATION_SERVICE_URL}/v1/scheduler/logs?${params.toString()}`,
      { method: 'GET', headers, signal: AbortSignal.timeout(20000) }
    );
    if (res.status === 404) {
      return NextResponse.json(emptyLogsResponse(page, limit));
    }
    const contentType = res.headers.get('content-type') ?? '';
    if (!contentType.includes('application/json')) {
      return NextResponse.json(emptyLogsResponse(page, limit));
    }
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json(emptyLogsResponse(page, limit));
  }
}
