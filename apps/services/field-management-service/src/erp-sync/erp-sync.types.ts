/**
 * ERP Sync Types
 * أنواع تكامل ERP
 *
 * Contract definition for external accounting / ERP system integrations.
 * New providers (QuickBooks, SAP, Odoo, Xero, Oracle NetSuite, Zoho
 * Books, SAP Business One, Microsoft Dynamics 365, …) implement the
 * `IErpAdapter` interface and register themselves in ErpSyncService.
 */

/**
 * Normalised accounting document that every adapter must consume.
 * Matches the OpenERP / QuickBooks "Bill" shape: a set of line items
 * plus metadata (vendor, date, reference, cost-center mapping).
 */
export interface ErpPostingDocument {
  /** Idempotency key — stable id the adapter uses to dedupe replays. */
  documentId: string;
  tenantId: string;
  /** Vendor identifier (external or internal SKU). */
  vendorId?: string;
  vendorName?: string;
  /** Source invoice reference, if any. */
  invoiceNumber?: string;
  invoiceDate?: string; // ISO 8601
  /** Cost center + project + GL account for double-entry bookkeeping. */
  costCenter?: string;
  projectCode?: string;
  /** Primary GL account — adapters map this to their native chart of accounts. */
  glAccount?: string;
  /** Accounting period — free-form (adapters translate as needed). */
  fiscalPeriod?: string;
  currency: string; // ISO 4217 (SAR, USD, EGP, ...)
  exchangeRate?: number;
  baseCurrency?: string;

  /** Line-item breakdown. Adapters render each line as a journal entry. */
  lines: ErpPostingLine[];

  /** Tax summary (VAT, sales tax). */
  taxAmount?: number;
  taxRate?: number;

  /** Total amount (sum of line totals + tax). */
  totalAmount: number;

  /** Free-form reference text (operation type, field name, season). */
  memo?: string;

  /** Event / business metadata for downstream traceability. */
  aggregateType: "FieldOperation" | "CropSeason";
  aggregateId: string;
  occurredAt: string; // ISO 8601
}

export interface ErpPostingLine {
  description: string;
  descriptionAr?: string;
  quantity?: number;
  unit?: string;
  unitPrice?: number;
  amount: number;
  /** Optional per-line GL override. */
  glAccount?: string;
  costCenter?: string;
}

/**
 * Result of a posting attempt. Adapters return this so the caller can
 * update posted_to_erp / posting_reference / posting_error on the
 * source record.
 */
export interface ErpPostingResult {
  success: boolean;
  /** External reference (adapter-native id) — stored on source record. */
  externalRef?: string;
  /** Error message for failed postings. */
  error?: string;
  /** Whether the caller should retry (transient) or give up (permanent). */
  retryable?: boolean;
}

/**
 * Adapter interface. Each external accounting provider implements this
 * and registers itself with `ErpSyncService`. Adapters are pure (no
 * direct DB access) — they only know how to translate the normalised
 * ErpPostingDocument into their native API calls.
 */
export interface IErpAdapter {
  /** Short name — used as the `external_source` column value. */
  readonly sourceName: string;

  /** Human-readable display name (for admin UI dropdowns). */
  readonly displayName: string;

  /** Whether this adapter is currently enabled (via env config). */
  isEnabled(): boolean;

  /**
   * Post a single document to the external system. Must be idempotent
   * on `documentId` — calling twice with the same id should return the
   * same result without creating duplicate postings.
   */
  postDocument(doc: ErpPostingDocument): Promise<ErpPostingResult>;

  /**
   * Health check — returns true if the adapter can reach the external
   * system. Called by /readyz and the admin dashboard.
   */
  ping?(): Promise<boolean>;
}
