/**
 * SAHOOL Enhanced Audit System
 * Comprehensive audit trail with field-level tracking, hash chain integrity, and alert triggers
 *
 * @packageDocumentation
 */

// Core types
export * from './audit-types';

// Logger
export { AuditLogger } from './audit-logger';

// Middleware
export {
  AuditMiddleware,
  AuditGuard,
  getAuditContext,
  Audit,
  TenantId,
  ActorId,
  CorrelationId,
  type AuditContext,
  type RequestWithAudit,
} from './audit-middleware';

// Alerts
export {
  AuditAlertService,
  consoleAlertHandler,
  emailAlertHandler,
  slackAlertHandler,
  createWebhookAlertHandler,
} from './audit-alerts';

// Decorators
export {
  // Main decorators
  Auditable,
  AuditField,
  SensitiveField,
  ExcludeFromAudit,
  getAuditFieldMetadata,

  // Convenience decorators
  AuditCreate,
  AuditUpdate,
  AuditDelete,
  AuditSecurity,
  AuditAdmin,
  AuditFinancial,

  // Interceptor
  AuditInterceptor,
} from './decorators';
