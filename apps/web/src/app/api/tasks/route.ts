/**
 * Task Service API Proxy
 * وكيل API لخدمة المهام
 *
 * Proxies requests to the task backend service, extracting the
 * httpOnly JWT cookie for authentication. Supports listing, creating,
 * and updating tasks.
 *
 * GET:   list tasks (filterable by status, assignee)
 * POST:  create a new task
 * PATCH: update task status (complete, assign)
 */

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { isRateLimited } from '@/lib/rate-limiter';
import { logger } from '@/lib/logger';
import { validateCsrfRequest } from '@/lib/security/csrf-server';

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const TASK_SERVICE_URL =
  process.env.TASK_SERVICE_URL || 'http://task-service:8103';

// Allowlist the upstream host to prevent SSRF via tampered env at runtime.
// We reject anything whose parsed hostname does not match a known good value.
const ALLOWED_UPSTREAM_HOSTS = new Set(
  (process.env.TASK_SERVICE_ALLOWED_HOSTS || 'task-service,localhost,127.0.0.1')
    .split(',')
    .map((h) => h.trim())
    .filter(Boolean),
);

// Generic identifier pattern for task/field IDs.
const SAFE_ID_PATTERN = /^[a-zA-Z0-9_-]+$/;

// Strict UUID pattern for user-facing references (assignees). Matches the
// task-service backend's `_UUID_PATTERN` to avoid submitting values that
// will be rejected by the upstream validator.
const UUID_PATTERN = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;

const VALID_TASK_STATUSES = [
  'pending',
  'in_progress',
  'completed',
  'cancelled',
] as const;

const VALID_PATCH_ACTIONS = ['complete', 'assign'] as const;
type PatchAction = (typeof VALID_PATCH_ACTIONS)[number];

const REQUEST_TIMEOUT_MS = 15_000;

// Cap request body size to prevent memory abuse.
const MAX_BODY_BYTES = 128 * 1024; // 128 KB

const RATE_LIMIT_CONFIG = {
  windowMs: 60_000,
  maxRequests: 40,
  keyPrefix: 'tasks-proxy',
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

/**
 * Build the upstream URL while enforcing an allowlist on the host.
 * Returns null if TASK_SERVICE_URL is malformed or points at a disallowed host.
 * This protects against SSRF via accidental/malicious env misconfiguration.
 */
function buildUpstreamUrl(path: string): URL | null {
  let base: URL;
  try {
    base = new URL(TASK_SERVICE_URL);
  } catch {
    return null;
  }
  if (base.protocol !== 'http:' && base.protocol !== 'https:') return null;
  if (!ALLOWED_UPSTREAM_HOSTS.has(base.hostname)) return null;
  return new URL(path, base);
}

/**
 * Read and size-check the JSON request body. Prevents memory exhaustion
 * from oversize payloads and returns a bilingual 413 on overflow.
 */
async function readJsonBody(request: NextRequest): Promise<
  | { ok: true; data: Record<string, unknown> }
  | { ok: false; response: NextResponse }
> {
  const contentLength = request.headers.get('content-length');
  if (contentLength && Number(contentLength) > MAX_BODY_BYTES) {
    return {
      ok: false,
      response: bilingualError(
        'Request body too large',
        'حجم الطلب كبير جدا',
        413,
      ),
    };
  }
  let text: string;
  try {
    text = await request.text();
  } catch {
    return {
      ok: false,
      response: bilingualError('Invalid request body', 'نص الطلب غير صالح', 400),
    };
  }
  if (text.length > MAX_BODY_BYTES) {
    return {
      ok: false,
      response: bilingualError(
        'Request body too large',
        'حجم الطلب كبير جدا',
        413,
      ),
    };
  }
  try {
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return {
        ok: false,
        response: bilingualError(
          'Expected JSON object',
          'متوقع كائن JSON',
          400,
        ),
      };
    }
    return { ok: true, data: parsed as Record<string, unknown> };
  } catch {
    return {
      ok: false,
      response: bilingualError('Invalid JSON body', 'تنسيق JSON غير صالح', 400),
    };
  }
}

/**
 * Enforce CSRF double-submit cookie on state-changing methods.
 * The global middleware skips `/api/*`, so the protection must be applied
 * explicitly at the route level for write operations.
 */
function enforceCsrf(request: NextRequest): NextResponse | null {
  const result = validateCsrfRequest(request);
  if (!result.valid) {
    logger.error('[Tasks API] CSRF validation failed:', result.error);
    return bilingualError(
      'CSRF validation failed',
      'فشل التحقق من CSRF',
      403,
    );
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// GET: List Tasks
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

    // Build upstream query string with allowed filters
    const qs = new URLSearchParams();
    const allowedParams = [
      'status',
      'assignee',
      'fieldId',
      'priority',
      'page',
      'limit',
      'sort',
      'order',
    ];

    for (const key of allowedParams) {
      const val = searchParams.get(key);
      if (val) {
        // Validate status enum if provided
        if (key === 'status' && !VALID_TASK_STATUSES.includes(val as typeof VALID_TASK_STATUSES[number])) {
          return bilingualError(
            `Invalid status. Must be one of: ${VALID_TASK_STATUSES.join(', ')}`,
            `حالة غير صالحة. يجب أن تكون أحد: ${VALID_TASK_STATUSES.join(', ')}`,
            400,
          );
        }
        // Validate ID-type params
        if ((key === 'assignee' || key === 'fieldId') && !SAFE_ID_PATTERN.test(val)) {
          return bilingualError(
            `Invalid ${key} format`,
            `تنسيق ${key} غير صالح`,
            400,
          );
        }
        qs.set(key, val);
      }
    }

    const upstream = buildUpstreamUrl('/api/v1/tasks');
    if (!upstream) {
      logger.error('[Tasks API] Upstream URL blocked by SSRF allowlist');
      return bilingualError(
        'Service configuration error',
        'خطأ في تكوين الخدمة',
        500,
      );
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
      logger.error('[Tasks API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from task service',
        'استجابة غير متوقعة من خدمة المهام',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && (error.name === 'TimeoutError' || error.name === 'AbortError')) {
      logger.error('[Tasks API] Request timed out');
      return bilingualError(
        'Task service timed out',
        'انتهت مهلة خدمة المهام',
        504,
      );
    }
    logger.error('[Tasks API] GET error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// POST: Create Task
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

    // Validate required fields
    if (!body.title || typeof body.title !== 'string' || body.title.trim().length === 0) {
      return bilingualError(
        'Task title is required',
        'عنوان المهمة مطلوب',
        400,
      );
    }

    // Validate optional fieldId if provided
    if (body.fieldId) {
      const fieldError = validateId(body.fieldId, 'fieldId', 'معرف الحقل');
      if (fieldError) return fieldError;
    }

    // Validate optional assignee if provided
    if (body.assignee) {
      const assigneeError = validateId(body.assignee, 'assignee', 'المكلف');
      if (assigneeError) return assigneeError;
    }

    const upstream = new URL('/api/v1/tasks', TASK_SERVICE_URL);

    const response = await fetch(upstream.toString(), {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    if (!validateContentType(response)) {
      logger.error('[Tasks API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from task service',
        'استجابة غير متوقعة من خدمة المهام',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && (error.name === 'TimeoutError' || error.name === 'AbortError')) {
      logger.error('[Tasks API] Request timed out');
      return bilingualError(
        'Task service timed out',
        'انتهت مهلة خدمة المهام',
        504,
      );
    }
    logger.error('[Tasks API] POST error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// PATCH: Update Task Status
// ═══════════════════════════════════════════════════════════════════════════

export async function PATCH(request: NextRequest) {
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

    // Validate task ID
    const taskId = body.taskId as string | undefined;
    const taskError = validateId(taskId, 'taskId', 'معرف المهمة');
    if (taskError) return taskError;

    // Validate action
    const action = body.action as string | undefined;
    if (!action || !VALID_PATCH_ACTIONS.includes(action as PatchAction)) {
      return bilingualError(
        `Invalid action. Must be one of: ${VALID_PATCH_ACTIONS.join(', ')}`,
        `إجراء غير صالح. يجب أن يكون أحد: ${VALID_PATCH_ACTIONS.join(', ')}`,
        400,
      );
    }

    // Validate assignee for 'assign' action
    if (action === 'assign') {
      const assigneeError = validateId(body.assignee, 'assignee', 'المكلف');
      if (assigneeError) return assigneeError;
    }

    // Map action to upstream endpoint
    const actionPathMap: Record<PatchAction, string> = {
      complete: `/api/v1/tasks/${encodeURIComponent(taskId!)}/complete`,
      assign: `/api/v1/tasks/${encodeURIComponent(taskId!)}/assign`,
    };

    const upstream = new URL(
      actionPathMap[action as PatchAction],
      TASK_SERVICE_URL,
    );

    // Forward the payload (excluding proxy-level fields)
    const { taskId: _taskId, action: _action, ...payload } = body;

    const response = await fetch(upstream.toString(), {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });

    if (!validateContentType(response)) {
      logger.error('[Tasks API] Unexpected content-type from upstream');
      return bilingualError(
        'Unexpected response from task service',
        'استجابة غير متوقعة من خدمة المهام',
        502,
      );
    }

    const data = await response.json();

    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    if (error instanceof DOMException && (error.name === 'TimeoutError' || error.name === 'AbortError')) {
      logger.error('[Tasks API] Request timed out');
      return bilingualError(
        'Task service timed out',
        'انتهت مهلة خدمة المهام',
        504,
      );
    }
    logger.error('[Tasks API] PATCH error:', error);
    return bilingualError(
      'Internal server error',
      'خطأ داخلي في الخادم',
      500,
    );
  }
}
