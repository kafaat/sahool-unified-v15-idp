/**
 * Enhanced Audit Types for SAHOOL Platform
 * Provides comprehensive type safety for audit logging
 */

/**
 * Audit event severity levels
 */
export enum AuditSeverity {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical',
}

/**
 * Audit event categories for classification
 */
export enum AuditCategory {
  SECURITY = 'security',      // Security-related events (auth, permissions)
  DATA = 'data',              // Data modifications (CRUD operations)
  CONFIG = 'config',          // Configuration changes
  ACCESS = 'access',          // Resource access attempts
  ADMIN = 'admin',            // Administrative actions
  COMPLIANCE = 'compliance',  // Compliance-related events
  FINANCIAL = 'financial',    // Financial transactions
  SYSTEM = 'system',          // System events
}

/**
 * Actor types for audit events
 */
export enum ActorType {
  USER = 'user',
  SERVICE = 'service',
  SYSTEM = 'system',
  API_KEY = 'api_key',
  ADMIN = 'admin',
}

/**
 * Field-level change tracking
 */
export interface FieldChange {
  field: string;
  oldValue: unknown;
  newValue: unknown;
  type: 'create' | 'update' | 'delete';
}

/**
 * Diff result for automatic change detection
 */
export interface AuditDiff {
  added: Record<string, unknown>;
  modified: FieldChange[];
  deleted: Record<string, unknown>;
}

/**
 * Core audit event structure
 */
export interface AuditEvent {
  // Identity
  tenantId: string;
  actorId?: string;
  actorType: ActorType;

  // Event classification
  action: string;
  category: AuditCategory;
  severity: AuditSeverity;

  // Resource information
  resourceType: string;
  resourceId: string;

  // Request context
  correlationId: string;
  sessionId?: string;

  // Network context
  ipAddress?: string;
  userAgent?: string;

  // Change tracking
  changes?: FieldChange[];
  diff?: AuditDiff;

  // Additional metadata
  metadata?: Record<string, unknown>;

  // Result
  success: boolean;
  errorCode?: string;
  errorMessage?: string;

  // Timestamp (set by logger)
  timestamp?: Date;

  // Hash chain (set by logger)
  prevHash?: string;
  entryHash?: string;
}

/**
 * Options for audit logging
 */
export interface AuditLogOptions {
  // Whether to track field-level changes
  trackChanges?: boolean;

  // Whether to generate automatic diffs
  generateDiff?: boolean;

  // Fields to exclude from tracking (e.g., passwords, tokens)
  excludeFields?: string[];

  // Fields to redact in logs (will show as [REDACTED])
  redactFields?: string[];

  // Custom metadata to include
  metadata?: Record<string, unknown>;

  // Whether to trigger alerts for this event
  triggerAlerts?: boolean;
}

/**
 * Audit logger configuration
 */
export interface AuditLoggerConfig {
  // Database connection (Prisma client)
  prisma?: any;

  // Default tenant ID (if not multi-tenant)
  defaultTenantId?: string;

  // Whether to enable hash chain validation
  enableHashChain?: boolean;

  // Whether to enable alert triggers
  enableAlerts?: boolean;

  // Alert configuration
  alertConfig?: AlertConfig;

  // Fields to always redact
  globalRedactFields?: string[];

  // Custom hash function
  hashFunction?: (data: string) => string;
}

/**
 * Alert configuration
 */
export interface AlertConfig {
  // Alert handlers
  handlers?: AlertHandler[];

  // Alert rules
  rules?: AlertRule[];

  // Whether to batch alerts
  batchAlerts?: boolean;

  // Batch window in milliseconds
  batchWindowMs?: number;
}

/**
 * Alert handler interface
 */
export interface AlertHandler {
  name: string;
  handle: (alert: AuditAlert) => Promise<void>;
}

/**
 * Alert rule for pattern detection
 */
export interface AlertRule {
  name: string;
  description: string;

  // Conditions to trigger alert
  conditions: AlertCondition[];

  // Severity to assign to alert
  severity: AuditSeverity;

  // Whether to batch similar alerts
  batchSimilar?: boolean;

  // Custom alert handler
  handler?: string;
}

/**
 * Alert condition
 */
export interface AlertCondition {
  field: keyof AuditEvent;
  operator: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'matches' | 'greaterThan' | 'lessThan';
  value: unknown;
}

/**
 * Audit alert
 */
export interface AuditAlert {
  id: string;
  rule: string;
  severity: AuditSeverity;
  message: string;
  events: AuditEvent[];
  timestamp: Date;
  resolved?: boolean;
  resolvedAt?: Date;
  resolvedBy?: string;
}

/**
 * Query options for audit logs
 */
export interface AuditQueryOptions {
  tenantId: string;
  actorId?: string;
  resourceType?: string;
  resourceId?: string;
  action?: string;
  category?: AuditCategory;
  severity?: AuditSeverity;
  startDate?: Date;
  endDate?: Date;
  limit?: number;
  offset?: number;
  orderBy?: 'asc' | 'desc';
}

/**
 * Audit statistics
 */
export interface AuditStats {
  tenantId: string;
  date: Date;
  totalEvents: number;
  eventsByCategory: Record<AuditCategory, number>;
  eventsBySeverity: Record<AuditSeverity, number>;
  uniqueActors: number;
  uniqueResources: number;
  failedEvents: number;
  criticalEvents: number;
}

/**
 * Decorator metadata keys
 */
export const AUDIT_METADATA = {
  AUDITABLE: 'audit:auditable',
  AUDIT_FIELD: 'audit:field',
  AUDIT_ACTION: 'audit:action',
  AUDIT_CATEGORY: 'audit:category',
  AUDIT_SEVERITY: 'audit:severity',
};

/**
 * Decorator options for @Auditable
 */
export interface AuditableOptions {
  action?: string;
  category?: AuditCategory;
  severity?: AuditSeverity;
  resourceType?: string;
  trackChanges?: boolean;
  excludeFields?: string[];
  redactFields?: string[];
}

/**
 * Decorator options for @AuditField
 */
export interface AuditFieldOptions {
  sensitive?: boolean;
  redact?: boolean;
  exclude?: boolean;
}

/**
 * Hash chain entry
 */
export interface HashChainEntry {
  id: string;
  tenantId: string;
  prevHash?: string;
  entryHash: string;
  createdAt: Date;
}

/**
 * Hash chain validation result
 */
export interface HashChainValidation {
  valid: boolean;
  invalidEntries: string[];
  totalEntries: number;
  validatedEntries: number;
  errors: string[];
}
