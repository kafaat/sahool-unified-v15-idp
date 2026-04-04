/**
 * Advisory Service API Proxy
 * وكيل API لخدمة الاستشارات الزراعية
 *
 * Proxies requests to the advisory backend service, extracting the
 * httpOnly JWT cookie for authentication. Supports disease assessment,
 * fertilizer planning, and crop advice actions.
 *
 * POST actions: disease-assess, fertilizer-plan, crop-advice
 * GET: list recommendations for a field
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const ADVISORY_SERVICE_URL =
  process.env.ADVISORY_SERVICE_URL || 'http://advisory-service:8093';

const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

const VALID_ACTIONS = ['disease-assess', 'fertilizer-plan', 'crop-advice'] as const;
type AdvisoryAction = (typeof VALID_ACTIONS)[number];

const REQUEST_TIMEOUT_MS = 15_000;

const RATE_LIMIT_CONFIG = {
  windowMs: 60_000,
  maxRequests: 30,
  keyPrefix: 'advisory-proxy',
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
// GET: List Recommendations for a Field
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
    const fieldId = searchParams.get('fieldId');

    const fieldError = validateId(fieldId, 'fieldId', 'معرف الحقل');
    if (fieldError) return fieldError;

    // Build upstream URL with query params
    const upstream = new URL(
      `/api/v1/advisory/recommendations/${encodeURIComponent(fieldId!)}`,
      ADVISORY_SERVICE_URL,
    );

    // Forward optional filters
    const allowedParams = ['page', 'limit', 'type', 'status'];
    const qs = new URLSearchParams();
    for (const key of allowedParams) {
      const val = searchParams.get(key);
      if (val) qs.set(key, val);
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
      logger.error('[Advisory API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from advisory service',
        'استجابة غير متوقعة من خدمة الاستشارات',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      logger.error('[Advisory API] Request timed out');
      return bilingualError(
        'Advisory service timed out',
        'انتهت مهلة خدمة الاستشارات',
        504,
      );
    }
    logger.error('[Advisory API] GET error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST: Execute Advisory Action
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
    if (!action || !VALID_ACTIONS.includes(action as AdvisoryAction)) {
      return bilingualError(
        `Invalid action. Must be one of: ${VALID_ACTIONS.join(', ')}`,
        `إجراء غير صالح. يجب أن يكون أحد: ${VALID_ACTIONS.join(', ')}`,
        400,
      );
    }

    // Validate fieldId
    const fieldId = body.fieldId as string | undefined;
    const fieldError = validateId(fieldId, 'fieldId', 'معرف الحقل');
    if (fieldError) return fieldError;

    // Map action to upstream endpoint
    const actionPathMap: Record<AdvisoryAction, string> = {
      'disease-assess': `/api/v1/advisory/disease-assess/${encodeURIComponent(fieldId!)}`,
      'fertilizer-plan': `/api/v1/advisory/fertilizer-plan/${encodeURIComponent(fieldId!)}`,
      'crop-advice': `/api/v1/advisory/crop-advice/${encodeURIComponent(fieldId!)}`,
    };

    const upstream = new URL(
      actionPathMap[action as AdvisoryAction],
      ADVISORY_SERVICE_URL,
    );

    // Forward the payload (excluding proxy-level fields)
    const { action: _action, fieldId: _fieldId, ...payload } = body;

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
      logger.error('[Advisory API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from advisory service',
        'استجابة غير متوقعة من خدمة الاستشارات',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && error.name === 'TimeoutError') {
      logger.error('[Advisory API] Request timed out');
      return bilingualError(
        'Advisory service timed out',
        'انتهت مهلة خدمة الاستشارات',
        504,
      );
    }
    logger.error('[Advisory API] POST error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}
