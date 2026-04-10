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

// Safe identifier pattern: alphanumerics, underscores, dashes only.
// Length is capped separately via MAX_ID_LENGTH to prevent abuse.
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;
const MAX_ID_LENGTH = 128;

const VALID_ACTIONS = ['disease-assess', 'fertilizer-plan', 'crop-advice'] as const;
type AdvisoryAction = (typeof VALID_ACTIONS)[number];

const REQUEST_TIMEOUT_MS = 15_000;

// Hard cap on inbound POST body size to mitigate DoS / memory abuse and
// to limit prompt-injection payload length before it reaches the LLM.
const MAX_BODY_BYTES = 32 * 1024; // 32 KiB

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
  if (typeof value !== 'string' || value.length === 0) {
    return bilingualError(
      `${label} is required`,
      `${labelAr} مطلوب`,
      400,
    );
  }
  if (value.length > MAX_ID_LENGTH) {
    return bilingualError(
      `${label} exceeds maximum length`,
      `${labelAr} يتجاوز الحد الأقصى للطول`,
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

/**
 * Parse a JSON body with a hard byte cap. Returns either a plain object
 * (never an array, primitive, or null) or an error NextResponse.
 * تحليل طلب JSON مع حد أقصى لحجم البيانات.
 */
async function parseJsonBody(
  request: NextRequest,
): Promise<Record<string, unknown> | NextResponse> {
  // Reject obviously wrong content-type early
  const ct = request.headers.get('content-type') || '';
  if (!ct.toLowerCase().includes('application/json')) {
    return bilingualError(
      'Content-Type must be application/json',
      'يجب أن يكون نوع المحتوى application/json',
      415,
    );
  }

  // Enforce content-length when provided
  const contentLength = request.headers.get('content-length');
  if (contentLength) {
    const parsed = Number.parseInt(contentLength, 10);
    if (Number.isFinite(parsed) && parsed > MAX_BODY_BYTES) {
      return bilingualError(
        'Request body too large',
        'حجم الطلب كبير جدا',
        413,
      );
    }
  }

  let text: string;
  try {
    text = await request.text();
  } catch {
    return bilingualError(
      'Failed to read request body',
      'فشل في قراءة محتوى الطلب',
      400,
    );
  }

  if (text.length > MAX_BODY_BYTES) {
    return bilingualError(
      'Request body too large',
      'حجم الطلب كبير جدا',
      413,
    );
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    return bilingualError(
      'Invalid JSON body',
      'محتوى JSON غير صالح',
      400,
    );
  }

  if (
    parsed === null ||
    typeof parsed !== 'object' ||
    Array.isArray(parsed)
  ) {
    return bilingualError(
      'Request body must be a JSON object',
      'يجب أن يكون محتوى الطلب كائن JSON',
      400,
    );
  }

  return parsed as Record<string, unknown>;
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

    let data: unknown;
    try {
      data = await response.json();
    } catch (parseErr) {
      logger.error('[Advisory API] Failed to parse upstream JSON (GET):', parseErr);
      return bilingualError(
        'Invalid response from advisory service',
        'استجابة غير صالحة من خدمة الاستشارات',
        502,
      );
    }

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
    // AbortSignal.timeout may surface on some runtimes as a plain Error
    if (error instanceof Error && error.name === 'TimeoutError') {
      logger.error('[Advisory API] Request timed out (Error)');
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

    const parsed = await parseJsonBody(request);
    if (parsed instanceof NextResponse) return parsed;
    const body = parsed;

    // Validate action
    const rawAction = body.action;
    const action = typeof rawAction === 'string' ? rawAction : undefined;
    if (!action || !VALID_ACTIONS.includes(action as AdvisoryAction)) {
      return bilingualError(
        `Invalid action. Must be one of: ${VALID_ACTIONS.join(', ')}`,
        `إجراء غير صالح. يجب أن يكون أحد: ${VALID_ACTIONS.join(', ')}`,
        400,
      );
    }

    // Validate fieldId
    const rawFieldId = body.fieldId;
    const fieldId = typeof rawFieldId === 'string' ? rawFieldId : undefined;
    const fieldError = validateId(fieldId, 'fieldId', 'معرف الحقل');
    if (fieldError) return fieldError;

    // Map action to upstream endpoint. Paths are hardcoded constants — never
    // interpolated from user input — so URL construction is SSRF-safe.
    const actionPathMap: Record<AdvisoryAction, string> = {
      'disease-assess': `/api/v1/advisory/disease-assess/${encodeURIComponent(fieldId!)}`,
      'fertilizer-plan': `/api/v1/advisory/fertilizer-plan/${encodeURIComponent(fieldId!)}`,
      'crop-advice': `/api/v1/advisory/crop-advice/${encodeURIComponent(fieldId!)}`,
    };

    const upstream = new URL(
      actionPathMap[action as AdvisoryAction],
      ADVISORY_SERVICE_URL,
    );

    // Forward the payload (excluding proxy-level fields).
    // Strip any client-supplied auth header fields that might override the
    // JWT-derived identity downstream.
    const {
      action: _action,
      fieldId: _fieldId,
      authorization: _authHdr,
      Authorization: _authHdr2,
      ...payload
    } = body;
    void _action;
    void _fieldId;
    void _authHdr;
    void _authHdr2;

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

    let data: unknown;
    try {
      data = await response.json();
    } catch (parseErr) {
      logger.error('[Advisory API] Failed to parse upstream JSON (POST):', parseErr);
      return bilingualError(
        'Invalid response from advisory service',
        'استجابة غير صالحة من خدمة الاستشارات',
        502,
      );
    }

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
    if (error instanceof Error && error.name === 'TimeoutError') {
      logger.error('[Advisory API] Request timed out (Error)');
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
