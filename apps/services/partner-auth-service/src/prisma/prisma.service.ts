/**
 * Prisma service with lifecycle hooks.
 * Connect on module init; disconnect on module destroy.
 */

import { Injectable, OnModuleInit, OnModuleDestroy, Logger } from "@nestjs/common";
import { PrismaClient } from "../../prisma/generated/client";

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(PrismaService.name);

  constructor() {
    super({
      log: process.env.NODE_ENV === "development"
        ? ["query", "warn", "error"]
        : ["warn", "error"],
    });
  }

  async onModuleInit() {
    try {
      await this.$connect();
      this.logger.log("Prisma connected to database");
    } catch (err) {
      this.logger.error(
        `Prisma connection failed: ${err instanceof Error ? err.message : err}`,
      );
      // Do not crash on startup — /readyz will reflect the outage.
    }
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
