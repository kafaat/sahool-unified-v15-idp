/**
 * Field Reports Module - async HTML/PDF report generation
 */

import { Module } from "@nestjs/common";
import { FieldReportsController } from "./field-reports.controller";
import { FieldReportsService } from "./field-reports.service";
import { FieldReportsWorker } from "./field-reports.worker";
import { HtmlReportRenderer } from "./renderers/html-report.renderer";
import { InMemoryReportStorage } from "./storage/inmemory-storage.adapter";
import { OutboxModule } from "../outbox/outbox.module";
import { IdempotencyModule } from "../idempotency/idempotency.module";

@Module({
  imports: [OutboxModule, IdempotencyModule],
  controllers: [FieldReportsController],
  providers: [
    FieldReportsService,
    FieldReportsWorker,
    HtmlReportRenderer,
    InMemoryReportStorage,
  ],
  exports: [FieldReportsService],
})
export class FieldReportsModule {}
