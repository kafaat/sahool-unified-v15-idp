/**
 * Alerts API Proxy Route
 * مسار وكيل API للتنبيهات
 *
 * Server-side proxy that forwards alert requests to the alert-service backend.
 * Reads the httpOnly access_token cookie to extract tenant_id from the JWT
 * and forwards it to the backend service.
 *
 * GET  /api/alerts           - List alerts for the tenant
 * POST /api/alerts           - Perform alert actions (acknowledge, resolve, dismiss)
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const ALERT_SERVICE_URL =
  process.env.ALERT_SERVICE_URL || 'http://alert-service:8113';

const VALID_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

const VALID_ACTIONS = ['acknowledge', 'resolve', 'dismiss'] as const;
type AlertAction = (typeof VALID_ACTIONS)[number];

// Allow-listed enum values for query param forwarding (must match shared contracts).
const VALID_SEVERITIES = new Set(['info', 'warning', 'critical', 'emergency']);
const VALID_STATUSES = new Set(['active', 'acknowledged', 'resolved', 'dismissed']);
const VALID_SORT_FIELDS = new Set(['createdAt', 'severity', 'status']);

const RATE_LIMIT_CONFIG = {
  windowMs: 60000,
  maxRequests: 60,
  keyPrefix: 'alerts-proxy',
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
// GET: List Alerts
// ═══════════════════════════════════════════════════════════════════════════

/**
 * List alerts for the authenticated tenant.
 * Forwards query parameters (status, severity, page, limit) to the backend.
 */
export async function GET(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, RATE_LIMIT_CONFIG);

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: 'Too many requests. Please try again later.', error_ar: 'طلبات كثيرة جداً. يرجى المحاولة لاحقاً.' },
        { status: 429 }
      );
    }

    // Extract access token from httpOnly cookie
    const cookieStore = await cookies();
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
      return NextResponse.json(
        { success: false, error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
        { status: 401 }
      );
    }

    // Extract tenant_id from JWT payload
    const tenantId = extractTenantId(accessToken);
    if (!tenantId) {
      return NextResponse.json(
        { success: false, error: 'Invalid token: missing tenant_id', error_ar: 'رمز غير صالح: معرف المستأجر مفقود' },
        { status: 401 }
      );
    }

    // Build query parameters for the backend
    const { searchParams } = request.nextUrl;
    const backendParams = new URLSearchParams();
    backendParams.set('tenant_id', tenantId);

    // Validate & forward supported query params (enum allow-listing + numeric bounds)
    const severityParam = searchParams.get('severity');
    if (severityParam !== null) {
      if (!VALID_SEVERITIES.has(severityParam)) {
        return NextResponse.json(
          { success: false, error: 'Invalid severity value', error_ar: 'قيمة الشدة غير صالحة' },
          { status: 400 }
        );
      }
      backendParams.set('severity', severityParam);
    }

    const statusParam = searchParams.get('status');
    if (statusParam !== null) {
      if (!VALID_STATUSES.has(statusParam)) {
        return NextResponse.json(
          { success: false, error: 'Invalid status value', error_ar: 'قيمة الحالة غير صالحة' },
          { status: 400 }
        );
      }
      backendParams.set('status', statusParam);
    }

    const pageParam = searchParams.get('page');
    if (pageParam !== null) {
      const parsedPage = parseInt(pageParam, 10);
      if (!Number.isFinite(parsedPage) || parsedPage < 1 || parsedPage > 10000) {
        return NextResponse.json(
          { success: false, error: 'page must be an integer between 1 and 10000', error_ar: 'يجب أن يكون رقم الصفحة بين 1 و 10000' },
          { status: 400 }
        );
      }
      backendParams.set('page', String(parsedPage));
    }

    const limitParam = searchParams.get('limit');
    if (limitParam !== null) {
      const parsedLimit = parseInt(limitParam, 10);
      if (!Number.isFinite(parsedLimit) || parsedLimit < 1 || parsedLimit > 200) {
        return NextResponse.json(
          { success: false, error: 'limit must be an integer between 1 and 200', error_ar: 'يجب أن يكون الحد بين 1 و 200' },
          { status: 400 }
        );
      }
      backendParams.set('limit', String(parsedLimit));
    }

    const sortParam = searchParams.get('sort');
    if (sortParam !== null) {
      if (!VALID_SORT_FIELDS.has(sortParam)) {
        return NextResponse.json(
          { success: false, error: 'Invalid sort field', error_ar: 'حقل الفرز غير صالح' },
          { status: 400 }
        );
      }
      backendParams.set('sort', sortParam);
    }

    const fieldIdParam = searchParams.get('field_id');
    if (fieldIdParam !== null) {
      if (!VALID_ID_PATTERN.test(fieldIdParam)) {
        return NextResponse.json(
          { success: false, error: 'Invalid field_id format', error_ar: 'تنسيق معرف الحقل غير صالح' },
          { status: 400 }
        );
      }
      backendParams.set('field_id', fieldIdParam);
    }

    const backendUrl = `${ALERT_SERVICE_URL}/api/v1/alerts?${backendParams.toString()}`;

    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const respContentType = response.headers.get('content-type') || '';
    if (!respContentType.includes('application/json')) {
      return NextResponse.json(
        { success: false, error: 'Alert service returned non-JSON response', error_ar: 'خدمة التنبيهات أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || data.message || 'Failed to fetch alerts',
          error_ar: 'فشل في جلب التنبيهات',
        },
        { status: response.status }
      );
    }

    return NextResponse.json({ success: true, data });
  } catch (error) {
    if (error instanceof Error && (error.name === 'TimeoutError' || error.name === 'AbortError')) {
      logger.error('[Alerts API] Request to alert-service timed out');
      return NextResponse.json(
        { success: false, error: 'Request timed out', error_ar: 'انتهت مهلة الطلب' },
        { status: 504 }
      );
    }

    logger.error('[Alerts API] Error fetching alerts:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error', error_ar: 'خطأ داخلي في الخادم' },
      { status: 500 }
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST: Alert Actions (acknowledge, resolve, dismiss)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Perform an action on an alert (acknowledge, resolve, dismiss).
 *
 * Request body:
 * {
 *   alert_id: string,
 *   action: "acknowledge" | "resolve" | "dismiss",
 *   comment?: string
 * }
 */
export async function POST(request: NextRequest) {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimited = await isRateLimited(clientIP, {
      ...RATE_LIMIT_CONFIG,
      maxRequests: 30,
      keyPrefix: 'alerts-action',
    });

    if (rateLimited) {
      return NextResponse.json(
        { success: false, error: 'Too many requests. Please try again later.', error_ar: 'طلبات كثيرة جداً. يرجى المحاولة لاحقاً.' },
        { status: 429 }
      );
    }

    // Extract access token from httpOnly cookie
    const cookieStore = await cookies();
    const accessToken = cookieStore.get('access_token')?.value;

    if (!accessToken) {
      return NextResponse.json(
        { success: false, error: 'Authentication required', error_ar: 'المصادقة مطلوبة' },
        { status: 401 }
      );
    }

    // Extract tenant_id from JWT payload
    const tenantId = extractTenantId(accessToken);
    if (!tenantId) {
      return NextResponse.json(
        { success: false, error: 'Invalid token: missing tenant_id', error_ar: 'رمز غير صالح: معرف المستأجر مفقود' },
        { status: 401 }
      );
    }

    // Validate Content-Type before parsing
    const requestContentType = request.headers.get('content-type') || '';
    if (!requestContentType.includes('application/json')) {
      return NextResponse.json(
        { success: false, error: 'Content-Type must be application/json', error_ar: 'نوع المحتوى يجب أن يكون application/json' },
        { status: 415 }
      );
    }

    // Parse and validate request body
    let body: Record<string, unknown>;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { success: false, error: 'Invalid JSON body', error_ar: 'نص الطلب غير صالح' },
        { status: 400 }
      );
    }

    const { alert_id, action, comment } = body as {
      alert_id?: string;
      action?: string;
      comment?: string;
    };

    // Validate alert_id
    if (!alert_id || typeof alert_id !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Missing required field: alert_id', error_ar: 'حقل مطلوب مفقود: معرف التنبيه' },
        { status: 400 }
      );
    }

    if (!VALID_ID_PATTERN.test(alert_id)) {
      return NextResponse.json(
        { success: false, error: 'Invalid alert_id format', error_ar: 'تنسيق معرف التنبيه غير صالح' },
        { status: 400 }
      );
    }

    // Validate action
    if (!action || !VALID_ACTIONS.includes(action as AlertAction)) {
      return NextResponse.json(
        {
          success: false,
          error: `Invalid action. Must be one of: ${VALID_ACTIONS.join(', ')}`,
          error_ar: 'إجراء غير صالح',
        },
        { status: 400 }
      );
    }

    // Validate optional comment (bound length to prevent large payload forwarding)
    if (comment !== undefined) {
      if (typeof comment !== 'string' || comment.length > 2000) {
        return NextResponse.json(
          { success: false, error: 'comment must be a string up to 2000 characters', error_ar: 'يجب أن يكون التعليق نصاً بحد أقصى 2000 حرف' },
          { status: 400 }
        );
      }
    }

    const backendUrl = `${ALERT_SERVICE_URL}/api/v1/alerts/${encodeURIComponent(alert_id)}/${encodeURIComponent(action)}`;

    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        tenant_id: tenantId,
        ...(comment ? { comment } : {}),
      }),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    const respContentType = response.headers.get('content-type') || '';
    if (!respContentType.includes('application/json')) {
      return NextResponse.json(
        { success: false, error: 'Alert service returned non-JSON response', error_ar: 'خدمة التنبيهات أرجعت استجابة غير JSON' },
        { status: 502 }
      );
    }

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || data.message || `Failed to ${action} alert`,
          error_ar: 'فشل في تنفيذ إجراء التنبيه',
        },
        { status: response.status }
      );
    }

    const messageMap: Record<string, string> = { acknowledge: 'Alert acknowledged successfully', resolve: 'Alert resolved successfully', dismiss: 'Alert dismissed successfully' };
    const messageMapAr: Record<string, string> = { acknowledge: 'تم الإقرار بالتنبيه بنجاح', resolve: 'تم حل التنبيه بنجاح', dismiss: 'تم تجاهل التنبيه بنجاح' };

    return NextResponse.json({
      success: true,
      message: messageMap[action] ?? `Alert ${action} completed`,
      message_ar: messageMapAr[action] ?? 'تم تنفيذ إجراء التنبيه',
      data,
    });
  } catch (error) {
    if (error instanceof Error && (error.name === 'TimeoutError' || error.name === 'AbortError')) {
      logger.error('[Alerts API] Request to alert-service timed out');
      return NextResponse.json(
        { success: false, error: 'Request timed out', error_ar: 'انتهت مهلة الطلب' },
        { status: 504 }
      );
    }

    logger.error('[Alerts API] Error performing alert action:', error);
    return NextResponse.json(
      { success: false, error: 'Internal server error', error_ar: 'خطأ داخلي في الخادم' },
      { status: 500 }
    );
  }
}
