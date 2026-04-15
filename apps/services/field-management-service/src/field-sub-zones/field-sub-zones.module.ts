/**
 * Field Sub-Zones Module - per-field sub-polygon management (terraced farms)
 */

import { Module } from "@nestjs/common";
import { FieldSubZonesController } from "./field-sub-zones.controller";
import { FieldSubZonesService } from "./field-sub-zones.service";
import { OutboxModule } from "../outbox/outbox.module";
import { IdempotencyModule } from "../idempotency/idempotency.module";

@Module({
  imports: [OutboxModule, IdempotencyModule],
  controllers: [FieldSubZonesController],
  providers: [FieldSubZonesService],
  exports: [FieldSubZonesService],
})
export class FieldSubZonesModule {}
