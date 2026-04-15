/**
 * ERP Sync Module
 * وحدة تكامل ERP
 */

import { Module } from "@nestjs/common";
import { ErpSyncController } from "./erp-sync.controller";
import { ErpSyncService } from "./erp-sync.service";
import { WebhookErpAdapter } from "./webhook-erp.adapter";
import { IdempotencyModule } from "../idempotency/idempotency.module";

@Module({
  imports: [IdempotencyModule],
  controllers: [ErpSyncController],
  providers: [ErpSyncService, WebhookErpAdapter],
  exports: [ErpSyncService],
})
export class ErpSyncModule {}
