/**
 * Field Audit History — API Client
 * عميل API لسجل تدقيق الحقل
 *
 * Thin wrapper over audit-service's
 *   GET /api/v1/audit/resources/{resource_type}/{resource_id}/trail
 *
 * Why a separate module instead of extending advanced-services.ts:
 * The existing `auditService` targets the generic `/audit/logs` list and
 * has a different response shape (snake_case, different pagination meta).
 * Reusing it would require forking its response handling inline; a
 * dedicated module keeps the Field History page's contract obvious and
 * lets us evolve the per-resource endpoint independently (e.g. when the
 * audit-service teaches validate_chain() about retention events).
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

/** Build the query string for `/resources/.../trail`.
 *
 *  Handles two UX conventions that have to translate to the audit-service's
 *  wire format:
 *    * Date inputs are date-only (YYYY-MM-DD); we widen `endDate` to
 *      23:59:59.999Z so "today" actually covers today.
 *    * Empty strings from uncontrolled form fields are treated the same
 *      as undefined; audit-service would otherwise match exact-empty-string
 *      user IDs which is never what the operator wants.
 */
export function buildTrailQuery(
  filters: FieldAuditFilters,
  pagination: PaginationState,
): URLSearchParams {
  const qp = new URLSearchParams();
  qp.set('skip', String(pagination.skip));
  qp.set('limit', String(pagination.limit));

  if (filters.category && filters.category.length) {
    qp.set('category', filters.category);
  }
  if (filters.userId && filters.userId.length) {
    qp.set('user_id', filters.userId);
  }
  if (filters.startDate) {
    // Start-of-day UTC; audit-service compares against TIMESTAMPTZ.
    qp.set('start_date', `${filters.startDate}T00:00:00Z`);
  }
  if (filters.endDate) {
    qp.set('end_date', `${filters.endDate}T23:59:59.999Z`);
  }
  return qp;
}

// ─────────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────────

export const fieldAuditHistoryApi = {
  /** Fetch a page of audit events for a specific field.
   *
   *  Returns an empty page (not an exception) on HTTP failure so the UI
   *  can render a "no events / connection lost" empty state without a
   *  top-level error boundary. Real errors land in the logger with the
   *  HTTP status so operators can still trace what went wrong. */
  async getFieldTrail(
    fieldId: string,
    filters: FieldAuditFilters = {},
    pagination: PaginationState = { skip: 0, limit: 50 },
  ): Promise<FieldAuditTrailPage> {
    const url = `${API_URLS.auditEndpoints.resourceTrail(
      RESOURCE_TYPE_FIELD,
      fieldId,
    )}?${buildTrailQuery(filters, pagination).toString()}`;

    try {
      const response = await fetch(url, fetchDefaults);
      if (!response.ok) {
        logger.error('field-audit-history: backend rejected trail request', {
          fieldId,
          status: response.status,
        });
        return emptyPage(pagination);
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
    } catch (error) {
      logger.error('field-audit-history: fetch failed', { fieldId, error });
      return emptyPage(pagination);
    }
  },
};

function emptyPage(pagination: PaginationState): FieldAuditTrailPage {
  return {
    items: [],
    total: 0,
    skip: pagination.skip,
    limit: pagination.limit,
    hasMore: false,
  };
}
