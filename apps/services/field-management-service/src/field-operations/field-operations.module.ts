/**
 * Field Operations Module - per-field operation log (tillage, sowing, ...)
 */

import { Module } from "@nestjs/common";
import { FieldOperationsController } from "./field-operations.controller";
import { FieldOperationsService } from "./field-operations.service";
import { FieldEventsService } from "../events/field-events.service";

@Module({
  controllers: [FieldOperationsController],
  providers: [FieldOperationsService, FieldEventsService],
  exports: [FieldOperationsService],
})
export class FieldOperationsModule {}
