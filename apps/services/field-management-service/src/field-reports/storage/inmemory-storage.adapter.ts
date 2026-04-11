/**
 * In-Memory Report Storage Adapter
 * مهيّئ تخزين التقارير في الذاكرة
 *
 * Default storage backend for development/testing. Keeps the rendered
 * HTML in the DB column (via caller) and returns a URL that points at
 * the existing `GET /field-reports/:id/content` endpoint. No external
 * infrastructure required — perfect for `docker compose up` local runs.
 *
 * For production, set REPORT_STORAGE=s3 and provide MinIO credentials.
 */

import { Injectable } from "@nestjs/common";
import type {
  IReportStorageProvider,
  ReportUploadResult,
} from "./report-storage.provider";

@Injectable()
export class InMemoryReportStorage implements IReportStorageProvider {
  readonly name = "inmemory";

  async store(args: {
    tenantId: string;
    fieldId: string;
    reportId: string;
    contentType: string;
    body: Buffer | string;
  }): Promise<ReportUploadResult> {
    const sizeBytes =
      typeof args.body === "string"
        ? Buffer.byteLength(args.body, "utf8")
        : args.body.length;

    // The URL points at our own service's content endpoint. The caller
    // (FieldReportsService) simultaneously stores the HTML in
    // content_html, so GET /field-reports/:id/content can serve it.
    const baseUrl =
      process.env.PUBLIC_BASE_URL ?? "/api/v1/field-reports";
    const url = `${baseUrl}/${args.reportId}/content`;

    // Reports in the default backend are good for 7 days — the DB row
    // lives forever (for audit), but the URL "expires" logically when
    // the next scheduled report replaces it.
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    return {
      url,
      expiresAt,
      sizeBytes,
      contentType: args.contentType,
    };
  }
}
