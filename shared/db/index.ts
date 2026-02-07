/**
 * SAHOOL Database Utilities Module
 * وحدة أدوات قاعدة البيانات سهول
 *
 * This module exports database configuration, connection pooling,
 * and backup strategy utilities for the SAHOOL platform.
 *
 * هذه الوحدة تصدر تكوين قاعدة البيانات وتجميع الاتصالات
 * وأدوات استراتيجية النسخ الاحتياطي لمنصة سهول.
 */

export * from './connection-pool-config';
export * from './backup-strategies';

// Re-export default configurations
import poolConfig from './connection-pool-config';
import backupConfig from './backup-strategies';

export const DatabaseConfig = {
  pool: poolConfig,
  backup: backupConfig,
};

export default DatabaseConfig;
