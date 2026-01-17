/**
 * @Auditable Decorator
 * Automatically logs audit events for controller methods
 */

import { SetMetadata } from "@nestjs/common";
import {
  AUDIT_METADATA,
  AuditableOptions,
  AuditCategory,
  AuditSeverity,
} from "../audit-types";

/**
 * Decorator to mark a controller method as auditable
 *
 * @example
 * ```typescript
 * @Auditable({
 *   action: 'product.create',
 *   category: AuditCategory.DATA,
 *   severity: AuditSeverity.INFO,
 *   trackChanges: true,
 * })
 * async createProduct(@Body() dto: CreateProductDto) {
 *   // ...
 * }
 * ```
 */
export const Auditable = (options: AuditableOptions = {}): MethodDecorator => {
  return SetMetadata(AUDIT_METADATA.AUDITABLE, {
    action: options.action,
    category: options.category || AuditCategory.DATA,
    severity: options.severity || AuditSeverity.INFO,
    resourceType: options.resourceType,
    trackChanges: options.trackChanges ?? false,
    excludeFields: options.excludeFields || [],
    redactFields: options.redactFields || [],
  });
};

/**
 * Pre-configured decorators for common actions
 */

/**
 * Audit create operations
 */
export const AuditCreate = (
  resourceType?: string,
  options: Partial<AuditableOptions> = {},
) => {
  return Auditable({
    action: options.action || `${resourceType || "resource"}.create`,
    category: AuditCategory.DATA,
    severity: AuditSeverity.INFO,
    resourceType,
    trackChanges: true,
    ...options,
  });
};

/**
 * Audit update operations
 */
export const AuditUpdate = (
  resourceType?: string,
  options: Partial<AuditableOptions> = {},
) => {
  return Auditable({
    action: options.action || `${resourceType || "resource"}.update`,
    category: AuditCategory.DATA,
    severity: AuditSeverity.INFO,
    resourceType,
    trackChanges: true,
    ...options,
  });
};

/**
 * Audit delete operations
 */
export const AuditDelete = (
  resourceType?: string,
  options: Partial<AuditableOptions> = {},
) => {
  return Auditable({
    action: options.action || `${resourceType || "resource"}.delete`,
    category: AuditCategory.DATA,
    severity: AuditSeverity.WARNING,
    resourceType,
    trackChanges: true,
    ...options,
  });
};

/**
 * Audit security-related operations
 */
export const AuditSecurity = (
  action: string,
  options: Partial<AuditableOptions> = {},
) => {
  return Auditable({
    action,
    category: AuditCategory.SECURITY,
    severity: AuditSeverity.WARNING,
    ...options,
  });
};

/**
 * Audit admin operations
 */
export const AuditAdmin = (
  action: string,
  options: Partial<AuditableOptions> = {},
) => {
  return Auditable({
    action,
    category: AuditCategory.ADMIN,
    severity: AuditSeverity.WARNING,
    ...options,
  });
};

/**
 * Audit financial operations
 */
export const AuditFinancial = (
  action: string,
  options: Partial<AuditableOptions> = {},
) => {
  return Auditable({
    action,
    category: AuditCategory.FINANCIAL,
    severity: AuditSeverity.WARNING,
    trackChanges: true,
    ...options,
  });
};
