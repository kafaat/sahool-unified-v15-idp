/**
 * Field Operations Module - per-field operation log (tillage, sowing, ...)
 */

import { Module } from "@nestjs/common";
import { FieldOperationsController } from "./field-operations.controller";
import { FieldOperationsService } from "./field-operations.service";
import { FieldEventsService } from "../events/field-events.service";
import { OutboxModule } from "../outbox/outbox.module";
import { IdempotencyModule } from "../idempotency/idempotency.module";

@Module({
  imports: [OutboxModule, IdempotencyModule],
  controllers: [FieldOperationsController],
  providers: [FieldOperationsService, FieldEventsService],
  exports: [FieldOperationsService],
})
export class FieldOperationsModule {}
