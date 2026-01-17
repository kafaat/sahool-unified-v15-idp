/**
 * Database Utilities for Research Core Service
 * أدوات قاعدة البيانات لخدمة البحث
 */

import { Logger } from "@nestjs/common";

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

export const MAX_PAGE_SIZE = 100;
export const DEFAULT_PAGE_SIZE = 20;
export const SLOW_QUERY_THRESHOLD = 1000;

/**
 * Transaction configuration for general operations
 */
export const GENERAL_TRANSACTION_CONFIG = {
  maxWait: 5000,
  timeout: 15000,
  isolationLevel: "ReadCommitted" as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Logging
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create query logger for Prisma
 */
export function createQueryLogger(logger: Logger) {
  return (event: any) => {
    const duration = event.duration || 0;
    if (duration > SLOW_QUERY_THRESHOLD) {
      logger.warn(
        `Slow query detected (${duration}ms): ${event.query?.substring(0, 200)}...`,
      );
    }
  };
}
