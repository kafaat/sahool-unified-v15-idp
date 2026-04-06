/**
 * Code Fix Agent API Proxy
 * وكيل واجهة برمجة تطبيقات إصلاح الكود
 *
 * Server-side proxy to code-fix-agent (port 8162).
 * Admin-only: protected by route-protection.ts
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { getUserFromToken } from '@/lib/auth/jwt-verify';
import { logger } from '@/lib/logger';

const CODE_FIX_SERVICE_URL =
  process.env.CODE_FIX_SERVICE_URL || 'http://code-fix-agent:8162';

const MAX_CODE_SIZE = 512_000;

async function getAuthHeaders(): Promise<Record<string, string> | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get('sahool_admin_token')?.value;
    if (!token) return null;

    const user = await getUserFromToken(token);
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    };
    if (user?.tenant_id) {
      headers['X-Tenant-ID'] = user.tenant_id;
    }
    return headers;
  } catch {
    return null;
  }
}

/**
 * GET /api/code-fix?action=health|info
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
  const headers = await getAuthHeaders();
  if (!headers) {
    return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action') || 'health';

  const pathMap: Record<string, string> = {
    health: '/healthz',
    info: '/api/v1/agent/info',
  };

  const path = pathMap[action] || '/healthz';

  try {
    const response = await fetch(`${CODE_FIX_SERVICE_URL}${path}`, {
      headers,
      signal: AbortSignal.timeout(10000),
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (err) {
    logger.error('Code fix agent proxy GET error', { error: String(err) });
    return NextResponse.json(
      { error: 'خدمة إصلاح الكود غير متاحة | Code fix agent unavailable' },
      { status: 502 }
    );
  }
}

/**
 * POST /api/code-fix — { action: "analyze"|"fix"|"review"|"generate-tests", ...body }
 */
export async function POST(request: NextRequest): Promise<NextResponse> {
  const headers = await getAuthHeaders();
  if (!headers) {
    return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const action: string = body.action || 'analyze';

    // Validate code size
    const code = body.code || body.diff || '';
    if (typeof code === 'string' && code.length > MAX_CODE_SIZE) {
      return NextResponse.json(
        { error: `الكود أكبر من الحد المسموح (${MAX_CODE_SIZE} حرف) | Code exceeds size limit` },
        { status: 400 }
      );
    }

    const endpointMap: Record<string, string> = {
      analyze: '/api/v1/analyze',
      fix: '/api/v1/fix',
      review: '/api/v1/review',
      'generate-tests': '/api/v1/generate-tests',
    };

    const endpoint = endpointMap[action];
    if (!endpoint) {
      return NextResponse.json(
        { error: `إجراء غير معروف: ${action} | Unknown action` },
        { status: 400 }
      );
    }

    // Remove the 'action' field before forwarding
    const { action: _, ...forwardBody } = body;

    const response = await fetch(`${CODE_FIX_SERVICE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(forwardBody),
      signal: AbortSignal.timeout(60000), // Longer timeout for AI processing
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (err) {
    logger.error('Code fix agent proxy POST error', { error: String(err) });
    return NextResponse.json(
      { error: 'فشل معالجة الطلب | Processing failed' },
      { status: 502 }
    );
  }
}
