/**
 * Audit Service API Proxy
 * وكيل واجهة برمجة تطبيقات خدمة التدقيق
 *
 * Server-side proxy to audit-service (port 8114).
 * Extracts tenant_id from httpOnly JWT cookie.
 * Admin-only: protected by route-protection.ts
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { getUserFromToken } from '@/lib/auth/jwt-verify';
import { logger } from '@/lib/logger';

const AUDIT_SERVICE_URL =
  process.env.AUDIT_SERVICE_URL || 'http://audit-service:8114';

async function getAuthContext(): Promise<{
  headers: Record<string, string>;
  tenantId: string;
} | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;
    if (!token) return null;

    const user = await getUserFromToken(token);
    if (!user) return null;

    const tenantId = user.tenant_id || 'default';
    return {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        'X-Tenant-Id': tenantId,
      },
      tenantId,
    };
  } catch {
    return null;
  }
}

/**
 * GET /api/audit?action=logs|stats|security-events|export
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  const auth = await getAuthContext();
  if (!auth) {
    return NextResponse.json(
      { error: 'المصادقة مطلوبة | Authentication required' },
      { status: 401 }
    );
  }

  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'logs';

  // Build backend URL based on action
  let backendPath: string;
  const params = new URLSearchParams();

  switch (action) {
    case 'stats': {
      const period = searchParams.get('period') || '30d';
      backendPath = `/api/v1/audit/stats?period=${encodeURIComponent(period)}`;
      break;
    }
    case 'security-events': {
      const skip = searchParams.get('skip') || '0';
      const limit = searchParams.get('limit') || '100';
      backendPath = `/api/v1/audit/security-events?skip=${skip}&limit=${limit}`;
      break;
    }
    case 'compliance': {
      const startDate = searchParams.get('start_date');
      const endDate = searchParams.get('end_date');
      const framework = searchParams.get('framework') || 'general';
      if (!startDate || !endDate) {
        return NextResponse.json(
          { error: 'start_date and end_date required' },
          { status: 400 }
        );
      }
      backendPath = `/api/v1/audit/compliance/report?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}&framework=${framework}`;
      break;
    }
    case 'chain-validate': {
      backendPath = '/api/v1/audit/chain/validate';
      break;
    }
    case 'chain-summary': {
      backendPath = '/api/v1/audit/chain/summary';
      break;
    }
    case 'export': {
      const startDate = searchParams.get('start_date');
      const endDate = searchParams.get('end_date');
      const format = searchParams.get('format') || 'json';
      if (!startDate || !endDate) {
        return NextResponse.json(
          { error: 'start_date and end_date required' },
          { status: 400 }
        );
      }
      backendPath = `/api/v1/audit/export?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}&format=${format}`;
      break;
    }
    default: {
      // logs - with filters
      for (const key of [
        'user_id', 'action', 'category', 'resource_type',
        'resource_id', 'success', 'start_date', 'end_date',
        'skip', 'limit',
      ]) {
        const val = searchParams.get(key);
        if (val) params.set(key, val);
      }
      if (!params.has('skip')) params.set('skip', '0');
      if (!params.has('limit')) params.set('limit', '50');
      backendPath = `/api/v1/audit/logs?${params.toString()}`;
      break;
    }
  }

  try {
    const response = await fetch(`${AUDIT_SERVICE_URL}${backendPath}`, {
      headers: auth.headers,
      signal: AbortSignal.timeout(15000),
    });

    // Passthrough non-JSON responses (e.g. CSV export)
    const contentType = response.headers.get('content-type') || '';
    if (!contentType.toLowerCase().includes('application/json')) {
      const body = await response.arrayBuffer();
      const headers = new Headers();
      if (contentType) headers.set('Content-Type', contentType);
      const disposition = response.headers.get('content-disposition');
      if (disposition) headers.set('Content-Disposition', disposition);
      return new NextResponse(body, { status: response.status, headers });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (err) {
    logger.error('Audit service proxy error', { error: String(err) });
    return NextResponse.json(
      { error: 'فشل الاتصال بخدمة التدقيق | Audit service unavailable' },
      { status: 502 }
    );
  }
}

/**
 * POST /api/audit — create audit log entry
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  const auth = await getAuthContext();
  if (!auth) {
    return NextResponse.json(
      { error: 'المصادقة مطلوبة | Authentication required' },
      { status: 401 }
    );
  }

  try {
    const body = await request.json();
    const response = await fetch(`${AUDIT_SERVICE_URL}/api/v1/audit/logs`, {
      method: 'POST',
      headers: auth.headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10000),
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (err) {
    logger.error('Audit service POST error', { error: String(err) });
    return NextResponse.json(
      { error: 'فشل إنشاء سجل التدقيق | Failed to create audit log' },
      { status: 502 }
    );
  }
}
