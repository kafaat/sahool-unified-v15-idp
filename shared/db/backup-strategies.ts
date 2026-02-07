/**
 * SAHOOL Database Backup Strategies
 * استراتيجيات النسخ الاحتياطي لقاعدة بيانات سهول
 *
 * This module defines backup strategies, retention policies, and recovery procedures
 * for the SAHOOL platform database infrastructure.
 *
 * هذه الوحدة تحدد استراتيجيات النسخ الاحتياطي وسياسات الاحتفاظ وإجراءات الاسترداد
 * للبنية التحتية لقاعدة بيانات منصة سهول.
 */

/**
 * Backup types supported
 * أنواع النسخ الاحتياطي المدعومة
 */
export type BackupType =
  | 'full'         // Complete database backup / نسخة احتياطية كاملة
  | 'incremental'  // Changes since last backup / التغييرات منذ آخر نسخة
  | 'differential' // Changes since last full backup / التغييرات منذ آخر نسخة كاملة
  | 'logical'      // pg_dump (SQL format) / تنسيق SQL
  | 'physical';    // File system level / مستوى نظام الملفات

/**
 * Backup storage destinations
 * وجهات تخزين النسخ الاحتياطي
 */
export type BackupDestination =
  | 'local'        // Local disk storage
  | 's3'           // AWS S3 or compatible
  | 'gcs'          // Google Cloud Storage
  | 'azure'        // Azure Blob Storage
  | 'nfs';         // Network file system

/**
 * Backup schedule configuration
 * تكوين جدول النسخ الاحتياطي
 */
export interface BackupSchedule {
  /** Cron expression for backup timing */
  cronExpression: string;
  /** Backup type to perform */
  backupType: BackupType;
  /** Retention period in days */
  retentionDays: number;
  /** Whether this is enabled */
  enabled: boolean;
  /** Description */
  description: string;
  descriptionAr: string;
}

/**
 * Backup retention policy
 * سياسة الاحتفاظ بالنسخ الاحتياطية
 */
export interface RetentionPolicy {
  /** Keep daily backups for N days */
  dailyRetentionDays: number;
  /** Keep weekly backups for N weeks */
  weeklyRetentionWeeks: number;
  /** Keep monthly backups for N months */
  monthlyRetentionMonths: number;
  /** Keep yearly backups for N years */
  yearlyRetentionYears: number;
}

/**
 * Backup configuration for a database
 * تكوين النسخ الاحتياطي لقاعدة بيانات
 */
export interface BackupConfig {
  /** Database name */
  databaseName: string;
  /** Backup schedules */
  schedules: BackupSchedule[];
  /** Retention policy */
  retention: RetentionPolicy;
  /** Storage destinations (ordered by priority) */
  destinations: BackupDestination[];
  /** Compression enabled */
  compressionEnabled: boolean;
  /** Encryption enabled */
  encryptionEnabled: boolean;
  /** Parallel workers for backup */
  parallelWorkers: number;
  /** Verify backup after completion */
  verifyAfterBackup: boolean;
  /** Notify on failure */
  notifyOnFailure: boolean;
  /** Notification channels */
  notificationChannels: string[];
}

/**
 * Default backup schedules for SAHOOL databases
 * جداول النسخ الاحتياطي الافتراضية لقواعد بيانات سهول
 */
export const DEFAULT_BACKUP_SCHEDULES: BackupSchedule[] = [
  {
    cronExpression: '0 2 * * *',  // Daily at 2 AM
    backupType: 'incremental',
    retentionDays: 7,
    enabled: true,
    description: 'Daily incremental backup',
    descriptionAr: 'نسخة احتياطية تزايدية يومية',
  },
  {
    cronExpression: '0 3 * * 0',  // Weekly on Sunday at 3 AM
    backupType: 'full',
    retentionDays: 30,
    enabled: true,
    description: 'Weekly full backup',
    descriptionAr: 'نسخة احتياطية كاملة أسبوعية',
  },
  {
    cronExpression: '0 4 1 * *',  // Monthly on 1st at 4 AM
    backupType: 'logical',
    retentionDays: 365,
    enabled: true,
    description: 'Monthly logical backup (pg_dump)',
    descriptionAr: 'نسخة احتياطية منطقية شهرية',
  },
];

/**
 * Default retention policy
 * سياسة الاحتفاظ الافتراضية
 */
export const DEFAULT_RETENTION_POLICY: RetentionPolicy = {
  dailyRetentionDays: 7,
  weeklyRetentionWeeks: 4,
  monthlyRetentionMonths: 12,
  yearlyRetentionYears: 7,  // Compliance requirement
};

/**
 * Service-specific backup configurations
 * تكوينات النسخ الاحتياطي الخاصة بالخدمة
 */
export const SERVICE_BACKUP_CONFIGS: Record<string, Partial<BackupConfig>> = {
  'field-management': {
    databaseName: 'sahool_fields',
    parallelWorkers: 4,
    verifyAfterBackup: true,
    // PostGIS data requires special handling
  },
  'marketplace': {
    databaseName: 'sahool_marketplace',
    parallelWorkers: 2,
    verifyAfterBackup: true,
    // Financial data - strict retention
    retention: {
      ...DEFAULT_RETENTION_POLICY,
      yearlyRetentionYears: 10,  // Extended for financial compliance
    },
  },
  'user-service': {
    databaseName: 'sahool_users',
    parallelWorkers: 2,
    verifyAfterBackup: true,
    encryptionEnabled: true,  // PII data encryption
  },
  'iot-service': {
    databaseName: 'sahool_iot',
    parallelWorkers: 4,
    // High volume time-series data
    retention: {
      dailyRetentionDays: 3,
      weeklyRetentionWeeks: 2,
      monthlyRetentionMonths: 6,
      yearlyRetentionYears: 2,
    },
  },
  'research-core': {
    databaseName: 'sahool_research',
    parallelWorkers: 2,
    verifyAfterBackup: true,
    // Research data - long retention
    retention: {
      ...DEFAULT_RETENTION_POLICY,
      yearlyRetentionYears: 15,  // Research data archival
    },
  },
};

/**
 * Backup commands for PostgreSQL
 * أوامر النسخ الاحتياطي لـ PostgreSQL
 */
export const BACKUP_COMMANDS = {
  /**
   * Full logical backup with pg_dump
   * نسخة احتياطية منطقية كاملة باستخدام pg_dump
   */
  logicalBackup: (dbName: string, outputPath: string, parallelJobs: number = 4) => `
    pg_dump \\
      --host=\${DB_HOST} \\
      --port=\${DB_PORT} \\
      --username=\${DB_USER} \\
      --dbname=${dbName} \\
      --format=directory \\
      --jobs=${parallelJobs} \\
      --compress=6 \\
      --verbose \\
      --file=${outputPath}
  `.trim(),

  /**
   * Physical backup with pg_basebackup
   * نسخة احتياطية مادية باستخدام pg_basebackup
   */
  physicalBackup: (outputPath: string) => `
    pg_basebackup \\
      --host=\${DB_HOST} \\
      --port=\${DB_PORT} \\
      --username=\${DB_USER} \\
      --pgdata=${outputPath} \\
      --format=tar \\
      --gzip \\
      --checkpoint=fast \\
      --progress \\
      --wal-method=stream
  `.trim(),

  /**
   * Point-in-time recovery setup
   * إعداد الاسترداد في نقطة زمنية محددة
   */
  pitrSetup: () => `
    # Enable WAL archiving in postgresql.conf:
    # wal_level = replica
    # archive_mode = on
    # archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
    # archive_timeout = 300
  `.trim(),

  /**
   * Verify backup integrity
   * التحقق من سلامة النسخة الاحتياطية
   */
  verifyBackup: (backupPath: string) => `
    pg_restore \\
      --list \\
      ${backupPath} > /dev/null && echo "Backup verified successfully"
  `.trim(),

  /**
   * Restore from backup
   * الاستعادة من النسخة الاحتياطية
   */
  restore: (dbName: string, backupPath: string, parallelJobs: number = 4) => `
    pg_restore \\
      --host=\${DB_HOST} \\
      --port=\${DB_PORT} \\
      --username=\${DB_USER} \\
      --dbname=${dbName} \\
      --jobs=${parallelJobs} \\
      --clean \\
      --if-exists \\
      --verbose \\
      ${backupPath}
  `.trim(),
};

/**
 * Disaster recovery procedures
 * إجراءات التعافي من الكوارث
 */
export const DISASTER_RECOVERY = {
  /**
   * Recovery Time Objective (RTO) by tier
   * هدف وقت الاسترداد حسب المستوى
   */
  rto: {
    critical: '1 hour',   // Core services (fields, users)
    high: '4 hours',      // Important services (marketplace, IoT)
    medium: '8 hours',    // Supporting services (research, chat)
    low: '24 hours',      // Non-critical services
  },

  /**
   * Recovery Point Objective (RPO) by tier
   * هدف نقطة الاسترداد حسب المستوى
   */
  rpo: {
    critical: '5 minutes',  // Near real-time with WAL streaming
    high: '15 minutes',     // Frequent WAL archiving
    medium: '1 hour',       // Hourly incremental backups
    low: '24 hours',        // Daily backups
  },

  /**
   * Service tier assignments
   * تعيينات مستوى الخدمة
   */
  serviceTiers: {
    critical: ['field-management', 'user-service'],
    high: ['marketplace', 'iot-service'],
    medium: ['research-core', 'community-chat', 'weather-service'],
    low: ['disaster-assessment'],
  },

  /**
   * Recovery steps
   * خطوات الاسترداد
   */
  steps: [
    {
      step: 1,
      action: 'Assess the situation',
      actionAr: 'تقييم الوضع',
      description: 'Determine the extent of data loss and affected services',
    },
    {
      step: 2,
      action: 'Notify stakeholders',
      actionAr: 'إخطار أصحاب المصلحة',
      description: 'Alert the team and affected users about the incident',
    },
    {
      step: 3,
      action: 'Select recovery point',
      actionAr: 'اختيار نقطة الاسترداد',
      description: 'Choose the most recent valid backup for restoration',
    },
    {
      step: 4,
      action: 'Prepare recovery environment',
      actionAr: 'تحضير بيئة الاسترداد',
      description: 'Spin up recovery infrastructure if needed',
    },
    {
      step: 5,
      action: 'Restore database',
      actionAr: 'استعادة قاعدة البيانات',
      description: 'Execute pg_restore with verified backup',
    },
    {
      step: 6,
      action: 'Apply WAL logs (if PITR)',
      actionAr: 'تطبيق سجلات WAL',
      description: 'Replay WAL logs to reach desired recovery point',
    },
    {
      step: 7,
      action: 'Verify data integrity',
      actionAr: 'التحقق من سلامة البيانات',
      description: 'Run integrity checks and validate critical data',
    },
    {
      step: 8,
      action: 'Resume services',
      actionAr: 'استئناف الخدمات',
      description: 'Bring services back online in priority order',
    },
    {
      step: 9,
      action: 'Post-incident review',
      actionAr: 'مراجعة ما بعد الحادث',
      description: 'Document lessons learned and improve procedures',
    },
  ],
};

/**
 * Monitoring and alerting for backups
 * المراقبة والتنبيه للنسخ الاحتياطية
 */
export const BACKUP_MONITORING = {
  /**
   * Metrics to track
   * المقاييس للتتبع
   */
  metrics: [
    {
      name: 'backup_last_success_timestamp',
      description: 'Timestamp of last successful backup',
      alertThreshold: '25 hours',  // Alert if no backup in 25 hours
    },
    {
      name: 'backup_duration_seconds',
      description: 'Time taken to complete backup',
      alertThreshold: '4 hours',  // Alert if backup takes too long
    },
    {
      name: 'backup_size_bytes',
      description: 'Size of backup file',
      alertThreshold: '50% change',  // Alert on significant size change
    },
    {
      name: 'backup_verification_status',
      description: 'Result of backup verification',
      alertThreshold: 'failure',  // Alert on any verification failure
    },
    {
      name: 'backup_storage_usage_percent',
      description: 'Percentage of backup storage used',
      alertThreshold: '80%',  // Alert when storage is filling up
    },
  ],

  /**
   * Alert channels
   * قنوات التنبيه
   */
  alertChannels: ['slack', 'email', 'pagerduty'],

  /**
   * Runbook link
   * رابط دليل التشغيل
   */
  runbookUrl: 'https://docs.sahool.io/runbooks/database-backup-failure',
};

/**
 * Get backup configuration for a service
 * الحصول على تكوين النسخ الاحتياطي للخدمة
 */
export function getBackupConfig(serviceName: string): BackupConfig {
  const serviceConfig = SERVICE_BACKUP_CONFIGS[serviceName] || {};

  return {
    databaseName: serviceConfig.databaseName || `sahool_${serviceName.replace(/-/g, '_')}`,
    schedules: DEFAULT_BACKUP_SCHEDULES,
    retention: serviceConfig.retention || DEFAULT_RETENTION_POLICY,
    destinations: ['s3', 'local'],
    compressionEnabled: true,
    encryptionEnabled: serviceConfig.encryptionEnabled || false,
    parallelWorkers: serviceConfig.parallelWorkers || 2,
    verifyAfterBackup: serviceConfig.verifyAfterBackup || false,
    notifyOnFailure: true,
    notificationChannels: BACKUP_MONITORING.alertChannels,
    ...serviceConfig,
  };
}

export default {
  getBackupConfig,
  DEFAULT_BACKUP_SCHEDULES,
  DEFAULT_RETENTION_POLICY,
  SERVICE_BACKUP_CONFIGS,
  BACKUP_COMMANDS,
  DISASTER_RECOVERY,
  BACKUP_MONITORING,
};
