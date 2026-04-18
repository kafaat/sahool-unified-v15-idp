/**
 * Field Audit History — Types
 * أنواع سجل تدقيق الحقل
 *
 * Mirrors the audit-service `AuditLogResponse` shape (see
 * apps/services/audit-service/src/main.py) but normalised to the
 * camelCase + Date-string form the admin UI works in.
 */

/** A single audit_log row scoped to a specific field (resource_type="field"). */
export interface FieldAuditEvent {
  id: string;
  tenantId: string;
  seqNum: number;
  userId: string;
  /** Free-form action verb, e.g. "field.boundary.updated", "field.created". */
  action: string;
  /** One of the audit_log chk_category values. */
  category: string;
  /** "debug" | "info" | "warning" | "error" | "critical" */
  severity: string;
  resourceType: string;
  resourceId: string;
  correlationId: string | null;
  ipAddress: string | null;
  success: boolean;
  errorCode: string | null;
  errorMessage: string | null;
  /** Free-form structured payload. */
  details: Record<string, unknown>;
  /** Old value for change events; null for create/delete/read. */
  oldValue: Record<string, unknown> | null;
  /** New value for change events; null for reads and deletes. */
  newValue: Record<string, unknown> | null;
  /** SHA-256 or HMAC-SHA-256 entry hash (depends on AUDIT_HASH_SECRET). */
  entryHash: string;
  /** ISO-8601 timestamp, always UTC. */
  createdAt: string;
}

/** UI-side filter state. All fields are optional; omitted = no filter. */
export interface FieldAuditFilters {
  /** Restrict to one or more categories (AND-across-categories is not supported
   *  by audit-service today; the UI picks one at a time). */
  category?: string;
  /** Exact-match user filter — the audit-service does not fuzzy-match. */
  userId?: string;
  /** ISO date-only string (YYYY-MM-DD). Inclusive lower bound. */
  startDate?: string;
  /** ISO date-only string. Inclusive upper bound — widened to end-of-day by the client. */
  endDate?: string;
}

/** Paginated page returned by `fieldAuditHistoryApi.getFieldTrail()`.
 *  Sourced from audit-service's `/audit/logs?resource_type=field&resource_id=<id>`
 *  endpoint (NOT the dedicated `/resources/{type}/{id}/trail`, which only
 *  supports skip+limit — see comments in api.ts). Keeping the interface
 *  named "TrailPage" because the UX semantics are the same even though
 *  the wire endpoint differs. */
export interface FieldAuditTrailPage {
  items: FieldAuditEvent[];
  total: number;
  skip: number;
  limit: number;
  hasMore: boolean;
}

/** Pagination cursor maintained by the UI hook. */
export interface PaginationState {
  skip: number;
  limit: number;
}

/** The minimum we need to reconstruct "state at timestamp T" from a trail.
 *  The reconstruction is best-effort: it walks events chronologically and
 *  applies each `newValue`. If the trail is truncated (retention), the
 *  result is labelled `partial = true` in the UI. */
export interface ReplayedState {
  asOf: string;
  eventsApplied: number;
  partial: boolean;
  state: Record<string, unknown>;
}
