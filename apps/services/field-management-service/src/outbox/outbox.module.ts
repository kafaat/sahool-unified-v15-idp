/**
 * Outbox Module - transactional outbox pattern for reliable event publishing
 */

import { Module } from "@nestjs/common";
import { OutboxService } from "./outbox.service";
import { OutboxPublisher } from "./outbox.publisher";
import { FieldEventsService } from "../events/field-events.service";

@Module({
  providers: [OutboxService, OutboxPublisher, FieldEventsService],
  exports: [OutboxService],
})
export class OutboxModule {}
