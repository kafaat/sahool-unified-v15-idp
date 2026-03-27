/**
 * @AuditField Decorator
 * Marks fields for special handling in audit logs
 */

import 'reflect-metadata';
import { AUDIT_METADATA, AuditFieldOptions } from '../audit-types';

/**
 * Decorator to mark a field for audit tracking
 *
 * @example
 * ```typescript
 * class UpdateProductDto {
 *   @AuditField()
 *   name: string;
 *
 *   @AuditField({ sensitive: true, redact: true })
 *   price: number;
 *
 *   @AuditField({ exclude: true })
 *   internalNotes: string;
 * }
 * ```
 */
export function AuditField(options: AuditFieldOptions = {}): PropertyDecorator {
  return (target: Object, propertyKey: string | symbol) => {
    // Get existing fields or create new array
    const existingFields =
      Reflect.getMetadata(AUDIT_METADATA.AUDIT_FIELD, target.constructor) || [];

    // Add this field
    existingFields.push({
      name: propertyKey,
      sensitive: options.sensitive ?? false,
      redact: options.redact ?? false,
      exclude: options.exclude ?? false,
    });

    // Store back
    Reflect.defineMetadata(AUDIT_METADATA.AUDIT_FIELD, existingFields, target.constructor);
  };
}

/**
 * Mark field as sensitive (should be redacted in logs)
 */
export function SensitiveField(): PropertyDecorator {
  return AuditField({ sensitive: true, redact: true });
}

/**
 * Exclude field from audit logs
 */
export function ExcludeFromAudit(): PropertyDecorator {
  return AuditField({ exclude: true });
}

/**
 * Helper to get audit field metadata
 */
export function getAuditFieldMetadata(target: any): Array<{
  name: string | symbol;
  sensitive: boolean;
  redact: boolean;
  exclude: boolean;
}> {
  return Reflect.getMetadata(AUDIT_METADATA.AUDIT_FIELD, target) || [];
}
