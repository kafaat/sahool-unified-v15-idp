import { Global, Module } from "@nestjs/common";
import { ChatEventsService } from "./chat-events.service";

/**
 * Events Module (global) — exposes ChatEventsService platform-wide.
 */
@Global()
@Module({
  providers: [ChatEventsService],
  exports: [ChatEventsService],
})
export class EventsModule {}
