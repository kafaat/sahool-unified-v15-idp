/**
 * Fields Module - Field Management
 */

import { Module } from "@nestjs/common";
import { FieldsController } from "./fields.controller";
import { FieldsService } from "./fields.service";
import { KpiSnapshotService } from "./kpi-snapshot.service";
import { FieldAiDataService } from "./field-ai-data.service";
import { FieldEventsService } from "../events/field-events.service";
import { CacheModule } from "../cache/cache.module";

@Module({
  imports: [CacheModule],
  controllers: [FieldsController],
  providers: [FieldsService, KpiSnapshotService, FieldAiDataService, FieldEventsService],
  exports: [FieldsService, KpiSnapshotService, FieldAiDataService],
})
export class FieldsModule {}
