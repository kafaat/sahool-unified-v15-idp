/**
 * Reviews Module
 * وحدة تقييمات المنتجات
 */

import { Module } from "@nestjs/common";
import { ReviewsService } from "./reviews.service";
import { ReviewsController } from "./reviews.controller";
import { ReviewVerificationSubscriber } from "./review-verification.subscriber";
import { PrismaService } from "../prisma/prisma.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";

// NOTE: `EventsService` is injected from the @Global() `EventsModule`
// in events/events.module.ts — do NOT re-provide it here, or NestJS
// will construct a second instance and open a second NATS connection.

@Module({
  controllers: [ReviewsController],
  providers: [
    ReviewsService,
    ReviewVerificationSubscriber,
    PrismaService,
    JwtAuthGuard,
  ],
  exports: [ReviewsService],
})
export class ReviewsModule {}
