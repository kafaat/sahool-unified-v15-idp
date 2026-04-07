/**
 * Fields Module - Field Management
 */

import { Module } from "@nestjs/common";
import { FieldsController } from "./fields.controller";
import { FieldsService } from "./fields.service";
import { KpiSnapshotService } from "./kpi-snapshot.service";
import { FieldEventsService } from "../events/field-events.service";

@Module({
  controllers: [FieldsController],
  providers: [FieldsService, KpiSnapshotService, FieldEventsService],
  exports: [FieldsService, KpiSnapshotService],
})
export class FieldsModule {}
