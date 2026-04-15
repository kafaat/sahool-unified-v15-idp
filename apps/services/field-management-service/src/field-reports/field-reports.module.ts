/**
 * Field Reports Module - async HTML/PDF report generation
 *
 * The storage backend is resolved at module-init time from the
 * ``REPORT_STORAGE`` env var (default: in-memory). Set ``REPORT_STORAGE=s3``
 * (or ``minio``) to enable the S3/MinIO adapter — see
 * ``storage/s3-storage.adapter.ts`` for the required env vars.
 */

import { Module } from "@nestjs/common";
import { FieldReportsController } from "./field-reports.controller";
import { FieldReportsService } from "./field-reports.service";
import { FieldReportsWorker } from "./field-reports.worker";
import { HtmlReportRenderer } from "./renderers/html-report.renderer";
import { buildReportStorageProvider } from "./storage/storage.token";
import { OutboxModule } from "../outbox/outbox.module";
import { IdempotencyModule } from "../idempotency/idempotency.module";

@Module({
  imports: [OutboxModule, IdempotencyModule],
  controllers: [FieldReportsController],
  providers: [
    FieldReportsService,
    FieldReportsWorker,
    HtmlReportRenderer,
    buildReportStorageProvider(),
  ],
  exports: [FieldReportsService],
})
export class FieldReportsModule {}
