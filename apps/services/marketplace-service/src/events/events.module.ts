/**
 * Events Module for SAHOOL Marketplace Service
 * Handles NATS event bus initialization and event logging
 */

import { Module, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { EventsService } from './events.service';

@Module({
  providers: [EventsService],
  exports: [EventsService],
})
export class EventsModule implements OnModuleInit, OnModuleDestroy {
  constructor(private eventsService: EventsService) {}

  async onModuleInit() {
    await this.eventsService.connect();
  }

  async onModuleDestroy() {
    await this.eventsService.disconnect();
  }
}
