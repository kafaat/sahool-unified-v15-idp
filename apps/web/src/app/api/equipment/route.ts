/**
 * Equipment Service API Proxy
 * وكيل API لخدمة المعدات
 *
 * Proxies requests to the equipment backend service, extracting the
 * httpOnly JWT cookie for authentication. Supports listing equipment,
 * maintenance schedules, logging maintenance, and reporting issues.
 *
 * GET:  list equipment, maintenance schedule
 * POST: log maintenance, report issue
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const EQUIPMENT_SERVICE_URL =
  process.env.EQUIPMENT_SERVICE_URL || 'http://equipment-service:8101';

const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

const VALID_POST_ACTIONS = ['log-maintenance', 'report-issue'] as const;
type EquipmentPostAction = (typeof VALID_POST_ACTIONS)[number];

const VALID_GET_VIEWS = ['list', 'maintenance-schedule'] as const;
type EquipmentGetView = (typeof VALID_GET_VIEWS)[number];

const REQUEST_TIMEOUT_MS = 15_000;

const RATE_LIMIT_CONFIG = {
  windowMs: 60_000,
  maxRequests: 40,
  keyPrefix: 'equipment-proxy',
};

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  if (forwarded) {
    const first = forwarded.split(',')[0];
    return first ? first.trim() : 'unknown';
  }
  return request.headers.get('x-real-ip') || 'unknown';
}

function bilingualError(en: string, ar: string, status: number) {
  return NextResponse.json(
    { success: false, error: en, error_ar: ar },
    { status },
  );
}

function validateId(value: string | null | undefined, label: string, labelAr: string) {
  if (!value) {
    return bilingualError(
      `${label} is required`,
      `${labelAr} مطلوب`,
      400,
    );
  }
  if (!SAFE_ID_PATTERN.test(value)) {
    return bilingualError(
      `Invalid ${label} format`,
      `تنسيق ${labelAr} غير صالح`,
      400,
    );
  }
  return null;
}

async function extractToken(): Promise<string | null> {
  const cookieStore = await cookies();
  return cookieStore.get('access_token')?.value ?? null;
}

function validateContentType(response: Response): boolean {
  const ct = response.headers.get('content-type') || '';
  return ct.includes('application/json');
}

// ═══════════════════════════════════════════════════════════════════════════
// GET: List Equipment / Maintenance Schedule
// ═══════════════════════════════════════════════════════════════════════════

export async function GET(request: NextRequest) {
  try {
    const clientIP = getClientIP(request);
    if (await isRateLimited(clientIP, RATE_LIMIT_CONFIG)) {
      return bilingualError(
        'Too many requests. Please try again later.',
        'طلبات كثيرة جدا. يرجى المحاولة لاحقا.',
        429,
      );
    }

    const token = await extractToken();
    if (!token) {
      return bilingualError(
        'Authentication required',
        'المصادقة مطلوبة',
        401,
      );
    }

    const { searchParams } = new URL(request.url);

    // Determine view: 'list' (default) or 'maintenance-schedule'
    const view = (searchParams.get('view') || 'list') as string;
    if (!VALID_GET_VIEWS.includes(view as EquipmentGetView)) {
      return bilingualError(
        `Invalid view. Must be one of: ${VALID_GET_VIEWS.join(', ')}`,
        `عرض غير صالح. يجب أن يكون أحد: ${VALID_GET_VIEWS.join(', ')}`,
        400,
      );
    }

    // Validate optional equipmentId if provided
    const equipmentId = searchParams.get('equipmentId');
    if (equipmentId) {
      const eqError = validateId(equipmentId, 'equipmentId', 'معرف المعدات');
      if (eqError) return eqError;
    }

    // Build upstream URL based on view
    let upstreamPath: string;
    if (view === 'maintenance-schedule') {
      upstreamPath = equipmentId
        ? `/api/v1/equipment/${encodeURIComponent(equipmentId)}/maintenance-schedule`
        : '/api/v1/equipment/maintenance-schedule';
    } else {
      upstreamPath = equipmentId
        ? `/api/v1/equipment/${encodeURIComponent(equipmentId)}`
        : '/api/v1/equipment';
    }

    const upstream = new URL(upstreamPath, EQUIPMENT_SERVICE_URL);

    // Forward allowed query params
    const qs = new URLSearchParams();
    const allowedParams = ['page', 'limit', 'type', 'status', 'fieldId', 'sort', 'order'];
    for (const key of allowedParams) {
      const val = searchParams.get(key);
      if (val) {
        // Validate ID-type params
        if (key === 'fieldId' && !SAFE_ID_PATTERN.test(val)) {
          return bilingualError(
            'Invalid fieldId format',
            'تنسيق معرف الحقل غير صالح',
            400,
          );
        }
        qs.set(key, val);
      }
    }
    const qsStr = qs.toString();
    if (qsStr) upstream.search = qsStr;

    const response = await fetch(upstream.toString(), {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: 'application/json',
      },
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    if (!validateContentType(response)) {
      logger.error('[Equipment API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from equipment service',
        'استجابة غير متوقعة من خدمة المعدات',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      logger.error('[Equipment API] Request timed out');
      return bilingualError(
        'Equipment service timed out',
        'انتهت مهلة خدمة المعدات',
        504,
      );
    }
    logger.error('[Equipment API] GET error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST: Log Maintenance / Report Issue
// ═══════════════════════════════════════════════════════════════════════════

export async function POST(request: NextRequest) {
  try {
    const clientIP = getClientIP(request);
    if (await isRateLimited(clientIP, RATE_LIMIT_CONFIG)) {
      return bilingualError(
        'Too many requests. Please try again later.',
        'طلبات كثيرة جدا. يرجى المحاولة لاحقا.',
        429,
      );
    }

    const token = await extractToken();
    if (!token) {
      return bilingualError(
        'Authentication required',
        'المصادقة مطلوبة',
        401,
      );
    }

    const body = await request.json();

    // Validate action
    const action = body.action as string | undefined;
    if (!action || !VALID_POST_ACTIONS.includes(action as EquipmentPostAction)) {
      return bilingualError(
        `Invalid action. Must be one of: ${VALID_POST_ACTIONS.join(', ')}`,
        `إجراء غير صالح. يجب أن يكون أحد: ${VALID_POST_ACTIONS.join(', ')}`,
        400,
      );
    }

    // Validate equipment ID
    const equipmentId = body.equipmentId as string | undefined;
    const eqError = validateId(equipmentId, 'equipmentId', 'معرف المعدات');
    if (eqError) return eqError;

    // Map action to upstream endpoint
    const actionPathMap: Record<EquipmentPostAction, string> = {
      'log-maintenance': `/api/v1/equipment/${encodeURIComponent(equipmentId!)}/maintenance`,
      'report-issue': `/api/v1/equipment/${encodeURIComponent(equipmentId!)}/issues`,
    };

    const upstream = new URL(
      actionPathMap[action as EquipmentPostAction],
      EQUIPMENT_SERVICE_URL,
    );

    // Forward the payload (excluding proxy-level fields)
    const { action: _action, equipmentId: _equipmentId, ...payload } = body;

    const response = await fetch(upstream.toString(), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    if (!validateContentType(response)) {
      logger.error('[Equipment API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from equipment service',
        'استجابة غير متوقعة من خدمة المعدات',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      logger.error('[Equipment API] Request timed out');
      return bilingualError(
        'Equipment service timed out',
        'انتهت مهلة خدمة المعدات',
        504,
      );
    }
    logger.error('[Equipment API] POST error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}
