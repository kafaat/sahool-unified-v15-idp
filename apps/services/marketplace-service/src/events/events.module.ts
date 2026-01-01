/**
 * Events Module Stub for SAHOOL Marketplace Service
 * Provides EventsService as a module when shared packages are not available
 */

import { Module, OnModuleInit, OnModuleDestroy, Global } from '@nestjs/common';
import { EventsService } from './events.service';

@Global()
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
