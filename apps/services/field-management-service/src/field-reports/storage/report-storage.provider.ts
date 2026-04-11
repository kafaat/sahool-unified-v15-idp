/**
 * Report Storage Provider
 * مزوّد التخزين للتقارير
 *
 * Abstract interface for the object-storage backend used to persist
 * rendered HTML/PDF reports. The service ships with two implementations:
 *
 *   1. InMemoryReportStorage — default; stores reports in the
 *      `field_reports.content_html` TEXT column. Good enough for up to
 *      ~500 KB reports; no external dependencies. Used in tests and
 *      local development.
 *
 *   2. S3ReportStorage — production; uploads to MinIO/S3 and returns
 *      a short-lived signed URL. Opts in via env `REPORT_STORAGE=s3`.
 *
 * The provider is pluggable so we can later add GCS / Azure Blob without
 * touching the calling services.
 */

export interface ReportUploadResult {
  /** Public or signed URL to fetch the report. */
  url: string;
  /** How long the URL stays valid. */
  expiresAt: Date;
  /** Bytes written — for cost accounting. */
  sizeBytes: number;
  /** MIME type of the stored object. */
  contentType: string;
}

export interface IReportStorageProvider {
  readonly name: string;
  /**
   * Persist a rendered report and return a URL. Implementations must be
   * idempotent on `key` — calling twice with the same key should yield
   * the same URL without creating a second copy.
   */
  store(args: {
    tenantId: string;
    fieldId: string;
    reportId: string;
    contentType: string;
    body: Buffer | string;
  }): Promise<ReportUploadResult>;
}
