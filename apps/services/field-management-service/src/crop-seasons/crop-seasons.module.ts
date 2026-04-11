/**
 * Crop Seasons Module - per-field crop rotation archive
 */

import { Module } from "@nestjs/common";
import { CropSeasonsController } from "./crop-seasons.controller";
import { CropSeasonsService } from "./crop-seasons.service";
import { FieldEventsService } from "../events/field-events.service";
import { OutboxModule } from "../outbox/outbox.module";
import { IdempotencyModule } from "../idempotency/idempotency.module";

@Module({
  imports: [OutboxModule, IdempotencyModule],
  controllers: [CropSeasonsController],
  providers: [CropSeasonsService, FieldEventsService],
  exports: [CropSeasonsService],
})
export class CropSeasonsModule {}
