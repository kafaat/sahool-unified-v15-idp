/**
 * SAHOOL Database Utilities Module
 * وحدة أدوات قاعدة البيانات سهول
 *
 * This module exports database configuration, connection pooling,
 * backup strategy utilities, and common database utilities for the SAHOOL platform.
 *
 * هذه الوحدة تصدر تكوين قاعدة البيانات وتجميع الاتصالات
 * واستراتيجية النسخ الاحتياطي والأدوات الشائعة لمنصة سهول.
 */

export * from './connection-pool-config';
export * from './backup-strategies';
export * from './db-utils';

// Re-export default configurations
import poolConfig from './connection-pool-config';
import backupConfig from './backup-strategies';
import dbUtils from './db-utils';

export const DatabaseConfig = {
  pool: poolConfig,
  backup: backupConfig,
  utils: dbUtils,
};

export default DatabaseConfig;
