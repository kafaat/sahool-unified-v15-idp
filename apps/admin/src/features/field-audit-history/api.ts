/**
 * Field Audit History — API Client
 * عميل API لسجل تدقيق الحقل
 *
 * Targets audit-service's general
 *   GET /api/v1/audit/logs?resource_type=field&resource_id=<id>&...
 *
 * The per-resource endpoint `/audit/resources/{type}/{id}/trail` exists
 * and is surfaced in our contracts as AUDIT_ENDPOINTS.RESOURCE_TRAIL,
 * but its handler only accepts skip + limit (see
 * apps/services/audit-service/src/main.py::get_resource_audit_trail).
 * The Field History page needs category / user / date-range filtering,
 * so we use the LOGS endpoint — which accepts the full filter set — and
 * pin the scope via resource_type/resource_id query params.
 *
 * Why a separate module instead of extending advanced-services.ts:
 * The existing `auditService.getAll()` targets the same endpoint but
 * returns a different response shape (snake_case, PaginatedResponse<T>
 * with `data`/`meta` rather than `items`/`total`/`has_more`). Reusing
 * it would require forking its response handling inline; a dedicated
 * module keeps the Field History page's contract obvious and lets us
 * evolve the per-field surface independently.
 */

import { logger } from '@/lib/logger';
import { API_URLS } from '@/config/api';
import type {
  FieldAuditEvent,
  FieldAuditFilters,
  FieldAuditTrailPage,
  PaginationState,
} from './types';

/** Resource type constant — matches the literal audit-service expects. */
export const RESOURCE_TYPE_FIELD = 'field';

/** Cookie-based auth (same-origin) mirrors the rest of admin's fetch calls. */
const fetchDefaults: RequestInit = {
  credentials: 'same-origin',
};

// ─────────────────────────────────────────────────────────────────────────
// Response normalisation — snake_case from Python → camelCase for UI
// ─────────────────────────────────────────────────────────────────────────

interface BackendAuditLogRow {
  id: string;
  tenant_id: string;
  seq_num: number;
  user_id: string;
  action: string;
  category: string;
  severity: string;
  resource_type: string;
  resource_id: string;
  correlation_id: string | null;
  ip_address: string | null;
  success: boolean;
  error_code: string | null;
  error_message: string | null;
  details: Record<string, unknown> | null;
  old_value: Record<string, unknown> | null;
  new_value: Record<string, unknown> | null;
  entry_hash: string;
  created_at: string;
}

interface BackendPaginatedResponse {
  items: BackendAuditLogRow[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

function mapRow(raw: BackendAuditLogRow): FieldAuditEvent {
  return {
    id: raw.id,
    tenantId: raw.tenant_id,
    seqNum: raw.seq_num,
    userId: raw.user_id,
    action: raw.action,
    category: raw.category,
    severity: raw.severity,
    resourceType: raw.resource_type,
    resourceId: raw.resource_id,
    correlationId: raw.correlation_id,
    ipAddress: raw.ip_address,
    success: raw.success,
    errorCode: raw.error_code,
    errorMessage: raw.error_message,
    // audit-service returns {} rather than null when details is empty; keep
    // the dict shape either way so consumers don't need to null-check.
    details: raw.details ?? {},
    oldValue: raw.old_value,
    newValue: raw.new_value,
    entryHash: raw.entry_hash,
    createdAt: raw.created_at,
  };
}

/** Exported so unit tests can exercise the mapper independently of fetch(). */
export function mapBackendPage(
  body: BackendPaginatedResponse,
): FieldAuditTrailPage {
  return {
    items: body.items.map(mapRow),
    total: body.total,
    skip: body.skip,
    limit: body.limit,
    hasMore: body.has_more,
  };
}

// ─────────────────────────────────────────────────────────────────────────
// Query-param assembly
// ─────────────────────────────────────────────────────────────────────────

/** Build the query string sent to `/audit/logs`.
 *
 *  Targets the general LOGS endpoint with the field id pinned via
 *  resource_type + resource_id, NOT the per-resource RESOURCE_TRAIL
 *  endpoint. Reasoning: the trail endpoint only accepts skip + limit
 *  (see audit-service main.py::get_resource_audit_trail). The LOGS
 *  endpoint accepts the full filter set we promise the operator on
 *  the page (category, user, date range), so we use it and pin the
 *  field-scope via the path-equivalent query params.
 *
 *  Wire-format quirks worth preserving:
 *    * Date inputs are date-only (YYYY-MM-DD); we widen `endDate` to
 *      23:59:59.999Z so "today" actually covers today.
 *    * Empty strings from uncontrolled form fields are treated the same
 *      as undefined; audit-service would otherwise match exact-empty-string
 *      user IDs which is never what the operator wants.
 */
export function buildTrailQuery(
  fieldId: string,
  filters: FieldAuditFilters,
  pagination: PaginationState,
): URLSearchParams {
  const qp = new URLSearchParams();
  // Pin the scope. resource_type/resource_id replace the path params we
  // would have used on the RESOURCE_TRAIL endpoint.
  qp.set('resource_type', RESOURCE_TYPE_FIELD);
  qp.set('resource_id', fieldId);
  qp.set('skip', String(pagination.skip));
  qp.set('limit', String(pagination.limit));

  if (filters.category && filters.category.length) {
    qp.set('category', filters.category);
  }
  if (filters.userId && filters.userId.length) {
    qp.set('user_id', filters.userId);
  }
  // Mirror the category/userId `.length` check below. JavaScript
  // truthiness would skip '' anyway, but a future refactor that
  // switches to explicit `!== undefined` comparisons would otherwise
  // start shipping `start_date=T00:00:00Z` (malformed) on empty input
  // and audit-service would reject the request. Cheap defence in depth.
  if (filters.startDate && filters.startDate.length) {
    // Start-of-day UTC; audit-service compares against TIMESTAMPTZ.
    qp.set('start_date', `${filters.startDate}T00:00:00Z`);
  }
  if (filters.endDate && filters.endDate.length) {
    qp.set('end_date', `${filters.endDate}T23:59:59.999Z`);
  }
  return qp;
}

// ─────────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────────

export class FieldAuditHistoryError extends Error {
  readonly status: number | null;
  readonly fieldId: string;

  constructor(message: string, opts: { status: number | null; fieldId: string; cause?: unknown }) {
    super(message);
    this.name = 'FieldAuditHistoryError';
    this.status = opts.status;
    this.fieldId = opts.fieldId;
    if (opts.cause !== undefined) {
      // Cause is standard in ES2022 but some bundlers strip it; attach as
      // a plain property too so logs always get it.
      (this as Error & { cause?: unknown }).cause = opts.cause;
    }
  }
}

export const fieldAuditHistoryApi = {
  /** Fetch a page of audit events for a specific field.
   *
   *  Throws `FieldAuditHistoryError` on HTTP failures and network
   *  errors so `useFieldAuditTrail` can surface a real error banner
   *  to the operator. Earlier versions of this client swallowed
   *  failures and returned an empty page — clean for the happy path
   *  but made the hook's `error` state unreachable, so operators
   *  couldn't distinguish "connection lost" from "no events recorded".
   *  Callers that genuinely want the degrade-to-empty behavior should
   *  wrap the call in a try/catch at their own layer. */
  async getFieldTrail(
    fieldId: string,
    filters: FieldAuditFilters = {},
    pagination: PaginationState = { skip: 0, limit: 50 },
  ): Promise<FieldAuditTrailPage> {
    // Use the general LOGS endpoint with the field id pinned via
    // resource_type/resource_id. The dedicated RESOURCE_TRAIL endpoint
    // (still in our contracts surface) only accepts skip/limit, so it
    // can't honour the page's category/user/date filters — see
    // audit-service main.py::get_resource_audit_trail.
    const url = `${API_URLS.auditEndpoints.logs}?${buildTrailQuery(
      fieldId,
      filters,
      pagination,
    ).toString()}`;

    let response: Response;
    try {
      response = await fetch(url, fetchDefaults);
    } catch (cause) {
      logger.error('field-audit-history: fetch failed', { fieldId, cause });
      throw new FieldAuditHistoryError(
        'Failed to reach audit-service',
        { status: null, fieldId, cause },
      );
    }

    if (!response.ok) {
      logger.error('field-audit-history: backend rejected trail request', {
        fieldId,
        status: response.status,
      });
      throw new FieldAuditHistoryError(
        `audit-service returned ${response.status}`,
        { status: response.status, fieldId },
      );
    }

    const body = (await response.json()) as BackendPaginatedResponse;
    // Defensive: an older audit-service deploy might respond with a bare
    // array instead of the PaginatedResponse wrapper. Detect and adapt
    // so the UI doesn't crash on a version-skew backend.
    if (Array.isArray(body)) {
      const items = (body as BackendAuditLogRow[]).map(mapRow);
      return {
        items,
        total: items.length,
        skip: pagination.skip,
        limit: pagination.limit,
        hasMore: false,
      };
    }
    return mapBackendPage(body);
  },
};
