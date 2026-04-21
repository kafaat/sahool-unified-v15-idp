/**
 * Orders Module
 * وحدة الطلبات
 *
 * Registers the NATS subscribers that own the order lifecycle:
 *   - OrderDeliverySubscriber: sahool.delivery.completed → DELIVERED + re-publish
 *
 * Prisma and EventsService are injected (EventsService comes from the
 * @Global EventsModule — no re-provide).
 */

import { Module } from "@nestjs/common";
import { OrderDeliverySubscriber } from "./order-delivery.subscriber";
import { PrismaService } from "../prisma/prisma.service";

@Module({
  providers: [OrderDeliverySubscriber, PrismaService],
  exports: [],
})
export class OrdersModule {}
