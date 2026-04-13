import { Module, Global } from "@nestjs/common";
import { UserEventsService } from "./user-events.service";

/**
 * Events Module (global) — exposes UserEventsService so any other
 * module (UsersModule, AuthModule, …) can `@Inject` it without
 * having to import EventsModule directly.
 */
@Global()
@Module({
  providers: [UserEventsService],
  exports: [UserEventsService],
})
export class EventsModule {}
