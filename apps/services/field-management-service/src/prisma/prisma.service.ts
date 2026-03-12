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
    if (this.isTestEnvironment) {
      try {
        await this.$connect();
        this.isConnected = true;
        this.logger.log("Field Management Database connected successfully");
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        this.logger.warn(`Database connection failed in test environment: ${errorMessage}`);
        this.logger.warn("Running in degraded mode without database");
        this.isConnected = false;
      }
      return;
    }

    // In production: attempt initial connection but do not crash the app on failure.
    // The service starts in degraded mode and retries in the background so the
    // /healthz liveness probe can respond immediately, preventing docker-compose
    // from marking the container unhealthy while waiting for the database.
    await this.connectWithRetry();
  }

  /**
   * Attempt to connect with exponential backoff.
   * On final failure the service starts in degraded mode (isConnected = false)
   * and schedules a background reconnection loop so it recovers automatically
   * when the database becomes available.
   */
  private async connectWithRetry(attempt = 1): Promise<void> {
    const maxInitialRetries = 5;
    // Delay grows with each attempt: 3 s, 6 s, 9 s, 12 s, 15 s (capped)
    const delay = Math.min(attempt * 3000, 15000);

    try {
      await this.$connect();
      this.isConnected = true;
      this.logger.log(`Field Management Database connected successfully (attempt ${attempt})`);

      // Verify PostGIS extension
      try {
        await this.$queryRaw`CREATE EXTENSION IF NOT EXISTS postgis`;
        this.logger.log("PostGIS extension verified");
      } catch {
        this.logger.debug("PostGIS extension may already exist or is unavailable via pooler");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);

      if (attempt < maxInitialRetries) {
        this.logger.warn(
          `Database connection failed (attempt ${attempt}/${maxInitialRetries}): ${errorMessage}. Retrying in ${delay}ms...`,
        );
        await new Promise((resolve) => setTimeout(resolve, delay));
        return this.connectWithRetry(attempt + 1);
      }

      // All initial attempts exhausted — start in degraded mode and keep retrying.
      this.isConnected = false;
      this.logger.error(
        `Database connection failed after ${maxInitialRetries} attempts: ${errorMessage}. ` +
          "Service starting in degraded mode. Background reconnection scheduled.",
      );
      this.scheduleBackgroundReconnect();
    }
  }

  /**
   * Retry the database connection in the background (exponential backoff, capped at 60 s,
   * max 30 background attempts ≈ 50 minutes of retrying after the initial failures).
   * This allows the service to recover automatically when the database becomes available
   * without crashing or blocking the HTTP server.
   */
  private scheduleBackgroundReconnect(attempt = 1): void {
    const maxBackgroundAttempts = 30;
    const delay = Math.min(attempt * 5000, 60000); // 5 s, 10 s, …, 60 s (cap reached at attempt 12)

    if (attempt > maxBackgroundAttempts) {
      this.logger.error(
        `Background reconnect gave up after ${maxBackgroundAttempts} attempts. ` +
          "Check database availability and restart the service manually.",
      );
      return;
    }

    setTimeout(async () => {
      if (this.isConnected) return; // already reconnected

      try {
        await this.$connect();
        this.isConnected = true;
        this.logger.log("Field Management Database reconnected successfully");
        try {
          await this.$queryRaw`CREATE EXTENSION IF NOT EXISTS postgis`;
        } catch {
          // ignored
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        this.logger.warn(`Background reconnect attempt ${attempt} failed: ${errorMessage}`);
        this.scheduleBackgroundReconnect(attempt + 1);
      }
    }, delay);
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
