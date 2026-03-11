/**
 * Prisma Service - Database Connection with Enhanced Features
 * - Connection pooling configuration
 * - Health check support
 * - Query logging for slow queries
 * - Graceful shutdown
 */

import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from "@nestjs/common";
import { PrismaClient, Prisma } from "../../prisma/generated/client";

// Slow query threshold in milliseconds
const SLOW_QUERY_THRESHOLD = 1000;

@Injectable()
export class PrismaService
  extends PrismaClient<Prisma.PrismaClientOptions, "query" | "error">
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(PrismaService.name);
  private isConnected = false;
  private readonly isTestEnvironment: boolean;

  constructor() {
    super({
      log: [
        { level: "query", emit: "event" },
        { level: "error", emit: "stdout" },
        { level: "warn", emit: "stdout" },
      ],
      datasources: {
        db: {
          url: process.env.DATABASE_URL,
        },
      },
    });

    this.isTestEnvironment = ["test", "ci", "testing"].includes(
      (process.env.ENVIRONMENT || process.env.NODE_ENV || "").toLowerCase(),
    );

    // Log slow queries
    this.$on("query", (event) => {
      if (event.duration > SLOW_QUERY_THRESHOLD) {
        this.logger.warn(
          `Slow query detected (${event.duration}ms): ${event.query.substring(0, 200)}...`,
        );
      }
    });
  }

  async onModuleInit() {
    try {
      await this.$connect();
      this.isConnected = true;
      this.logger.log("Field Management Database connected successfully");

      // Enable PostGIS extension if not exists
      try {
        await this.$queryRaw`CREATE EXTENSION IF NOT EXISTS postgis`;
        this.logger.log("PostGIS extension verified");
      } catch (e) {
        this.logger.debug("PostGIS extension may already exist");
      }
    } catch (error) {
      if (this.isTestEnvironment) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        this.logger.warn(
          `Database connection failed in test environment: ${errorMessage}`,
        );
        this.logger.warn("Running in degraded mode without database");
        this.isConnected = false;
      } else {
        throw error;
      }
    }
  }

  async onModuleDestroy() {
    if (this.isConnected) {
      await this.$disconnect();
      this.logger.log("Field Management Database disconnected");
    }
  }

  /**
   * Check if database is connected
   */
  isHealthy(): boolean {
    return this.isConnected;
  }

  /**
   * Get detailed connection status
   */
  async getConnectionStatus() {
    try {
      await this.$queryRaw`SELECT 1`;
      return {
        connected: true,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error("Database connection check failed:", error);
      return {
        connected: false,
        timestamp: new Date().toISOString(),
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }
}
