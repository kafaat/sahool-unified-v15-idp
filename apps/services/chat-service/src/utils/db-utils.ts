/**
 * Database Utilities for Chat Service
 * أدوات قاعدة البيانات لخدمة المحادثات
 */

import { Logger } from "@nestjs/common";

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

export const SLOW_QUERY_THRESHOLD = 1000; // 1 second

/**
 * Transaction configuration for general operations
 */
export const GENERAL_TRANSACTION_CONFIG = {
  maxWait: 5000,
  timeout: 15000,
  isolationLevel: "ReadCommitted" as const,
};

/**
 * Transaction configuration for read operations
 */
export const READ_TRANSACTION_CONFIG = {
  maxWait: 2000,
  timeout: 5000,
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
