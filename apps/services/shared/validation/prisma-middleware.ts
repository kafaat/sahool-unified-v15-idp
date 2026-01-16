/**
 * Prisma Validation Middleware
 * وسيط التحقق من Prisma
 *
 * @module shared/validation
 * @description Middleware for Prisma to add runtime validation at database level
 */

import { Prisma } from "@prisma/client";
import { sanitizePlainText } from "./sanitization";

// ═══════════════════════════════════════════════════════════════════════════
// Validation Rules
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field validation rules
 */
export interface FieldValidationRule {
  /**
   * Field name
   */
  field: string;

  /**
   * Validation type
   */
  type:
    | "string"
    | "number"
    | "email"
    | "phone"
    | "url"
    | "date"
    | "boolean"
    | "enum";

  /**
   * Required field
   */
  required?: boolean;

  /**
   * Minimum length (for strings)
   */
  minLength?: number;

  /**
   * Maximum length (for strings)
   */
  maxLength?: number;

  /**
   * Minimum value (for numbers)
   */
  min?: number;

  /**
   * Maximum value (for numbers)
   */
  max?: number;

  /**
   * Regex pattern (for strings)
   */
  pattern?: RegExp;

  /**
   * Enum values
   */
  enumValues?: any[];

  /**
   * Custom validation function
   */
  customValidator?: (value: any) => boolean | Promise<boolean>;

  /**
   * Error message
   */
  errorMessage?: string;

  /**
   * Sanitize input
   */
  sanitize?: boolean;
}

/**
 * Model validation rules
 */
export interface ModelValidationRules {
  [modelName: string]: {
    fields: FieldValidationRule[];
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Validation Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Validate email format
 */
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate phone format (international format)
 */
function validatePhone(phone: string): boolean {
  // Basic international phone format
  const phoneRegex = /^\+?[1-9]\d{1,14}$/;
  return phoneRegex.test(phone.replace(/[\s-]/g, ""));
}

/**
 * Validate URL format
 */
function validateUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate field against rules
 */
async function validateField(
  value: any,
  rule: FieldValidationRule,
): Promise<{ valid: boolean; error?: string }> {
  // Check required
  if (rule.required && (value === null || value === undefined)) {
    return {
      valid: false,
      error: rule.errorMessage || `${rule.field} is required`,
    };
  }

  // Skip validation if value is null/undefined and not required
  if (value === null || value === undefined) {
    return { valid: true };
  }

  // Type-specific validation
  switch (rule.type) {
    case "string":
      if (typeof value !== "string") {
        return {
          valid: false,
          error: rule.errorMessage || `${rule.field} must be a string`,
        };
      }

      if (rule.minLength && value.length < rule.minLength) {
        return {
          valid: false,
          error:
            rule.errorMessage ||
            `${rule.field} must be at least ${rule.minLength} characters`,
        };
      }

      if (rule.maxLength && value.length > rule.maxLength) {
        return {
          valid: false,
          error:
            rule.errorMessage ||
            `${rule.field} must not exceed ${rule.maxLength} characters`,
        };
      }

      if (rule.pattern && !rule.pattern.test(value)) {
        return {
          valid: false,
          error:
            rule.errorMessage ||
            `${rule.field} does not match required pattern`,
        };
      }
      break;

    case "number":
      if (typeof value !== "number" || isNaN(value)) {
        return {
          valid: false,
          error: rule.errorMessage || `${rule.field} must be a number`,
        };
      }

      if (rule.min !== undefined && value < rule.min) {
        return {
          valid: false,
          error:
            rule.errorMessage || `${rule.field} must be at least ${rule.min}`,
        };
      }

      if (rule.max !== undefined && value > rule.max) {
        return {
          valid: false,
          error:
            rule.errorMessage || `${rule.field} must not exceed ${rule.max}`,
        };
      }
      break;

    case "email":
      if (typeof value !== "string" || !validateEmail(value)) {
        return {
          valid: false,
          error: rule.errorMessage || `${rule.field} must be a valid email`,
        };
      }
      break;

    case "phone":
      if (typeof value !== "string" || !validatePhone(value)) {
        return {
          valid: false,
          error:
            rule.errorMessage || `${rule.field} must be a valid phone number`,
        };
      }
      break;

    case "url":
      if (typeof value !== "string" || !validateUrl(value)) {
        return {
          valid: false,
          error: rule.errorMessage || `${rule.field} must be a valid URL`,
        };
      }
      break;

    case "date":
      const date = new Date(value);
      if (isNaN(date.getTime())) {
        return {
          valid: false,
          error: rule.errorMessage || `${rule.field} must be a valid date`,
        };
      }
      break;

    case "boolean":
      if (typeof value !== "boolean") {
        return {
          valid: false,
          error: rule.errorMessage || `${rule.field} must be a boolean`,
        };
      }
      break;

    case "enum":
      if (rule.enumValues && !rule.enumValues.includes(value)) {
        return {
          valid: false,
          error:
            rule.errorMessage ||
            `${rule.field} must be one of: ${rule.enumValues.join(", ")}`,
        };
      }
      break;
  }

  // Custom validator
  if (rule.customValidator) {
    const isValid = await rule.customValidator(value);
    if (!isValid) {
      return {
        valid: false,
        error: rule.errorMessage || `${rule.field} failed custom validation`,
      };
    }
  }

  return { valid: true };
}

/**
 * Sanitize data based on validation rules
 */
function sanitizeData(data: any, rules: FieldValidationRule[]): any {
  const sanitized = { ...data };

  for (const rule of rules) {
    if (rule.sanitize && sanitized[rule.field]) {
      if (typeof sanitized[rule.field] === "string") {
        sanitized[rule.field] = sanitizePlainText(sanitized[rule.field]);
      }
    }
  }

  return sanitized;
}

// ═══════════════════════════════════════════════════════════════════════════
// Prisma Middleware
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create Prisma validation middleware
 *
 * @param validationRules - Validation rules for models
 * @returns Prisma middleware function
 */
export function createValidationMiddleware(
  validationRules: ModelValidationRules,
): Prisma.Middleware {
  return async (params, next) => {
    const { model, action, args } = params;

    // Only validate on create and update operations
    if (
      !model ||
      !["create", "update", "updateMany", "upsert"].includes(action)
    ) {
      return next(params);
    }

    // Get validation rules for this model
    const modelRules = validationRules[model];
    if (!modelRules || !modelRules.fields || modelRules.fields.length === 0) {
      return next(params);
    }

    // Get data to validate
    let data: any;
    if (action === "create" || action === "update") {
      data = args.data;
    } else if (action === "updateMany") {
      data = args.data;
    } else if (action === "upsert") {
      data = { ...args.create, ...args.update };
    }

    if (!data) {
      return next(params);
    }

    // Sanitize data
    data = sanitizeData(data, modelRules.fields);

    // Validate each field
    const errors: string[] = [];
    for (const rule of modelRules.fields) {
      const fieldValue = data[rule.field];
      const result = await validateField(fieldValue, rule);

      if (!result.valid && result.error) {
        errors.push(result.error);
      }
    }

    // If there are validation errors, throw exception
    if (errors.length > 0) {
      throw new Error(`Validation failed: ${errors.join(", ")}`);
    }

    // Update args with sanitized data
    if (action === "create" || action === "update") {
      args.data = data;
    } else if (action === "updateMany") {
      args.data = data;
    } else if (action === "upsert") {
      args.create = data;
      args.update = data;
    }

    return next(params);
  };
}

/**
 * Create audit logging middleware for Prisma
 * Logs all create, update, and delete operations
 *
 * @param logger - Logger function
 * @returns Prisma middleware function
 */
export function createAuditLoggingMiddleware(
  logger: (message: string, context?: any) => void,
): Prisma.Middleware {
  return async (params, next) => {
    const { model, action, args } = params;

    // Log mutations
    if (
      model &&
      ["create", "update", "updateMany", "delete", "deleteMany"].includes(
        action,
      )
    ) {
      const timestamp = new Date().toISOString();
      logger(`[${timestamp}] Prisma ${action} on ${model}`, {
        model,
        action,
        args: JSON.stringify(args).substring(0, 500), // Limit arg length
      });
    }

    const result = await next(params);

    // Log result
    if (model && ["create", "update", "delete"].includes(action) && result) {
      logger(`${action} completed for ${model}`, {
        model,
        action,
        id: result.id || "N/A",
      });
    }

    return result;
  };
}

/**
 * Create soft delete middleware
 * Converts delete operations to updates that set deletedAt field
 *
 * @returns Prisma middleware function
 */
export function createSoftDeleteMiddleware(): Prisma.Middleware {
  return async (params, next) => {
    const { model, action, args } = params;

    // Convert delete to update with deletedAt
    if (action === "delete") {
      params.action = "update";
      params.args.data = { deletedAt: new Date() };
    }

    // Convert deleteMany to updateMany with deletedAt
    if (action === "deleteMany") {
      params.action = "updateMany";
      params.args.data = { deletedAt: new Date() };
    }

    // Filter out soft-deleted records on find operations
    if (action === "findUnique" || action === "findFirst") {
      params.args.where = { ...params.args.where, deletedAt: null };
    }

    if (action === "findMany") {
      if (params.args.where) {
        if (params.args.where.deletedAt === undefined) {
          params.args.where.deletedAt = null;
        }
      } else {
        params.args.where = { deletedAt: null };
      }
    }

    return next(params);
  };
}

/**
 * Create timestamp middleware
 * Automatically sets createdAt and updatedAt fields
 *
 * @returns Prisma middleware function
 */
export function createTimestampMiddleware(): Prisma.Middleware {
  return async (params, next) => {
    const { action, args } = params;

    // Set createdAt on create
    if (action === "create") {
      if (args.data) {
        args.data.createdAt = args.data.createdAt || new Date();
        args.data.updatedAt = args.data.updatedAt || new Date();
      }
    }

    // Set updatedAt on update
    if (action === "update" || action === "updateMany") {
      if (args.data) {
        args.data.updatedAt = new Date();
      }
    }

    return next(params);
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Common Validation Rules
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Common validation rules for User model
 */
export const USER_VALIDATION_RULES: FieldValidationRule[] = [
  {
    field: "email",
    type: "email",
    required: true,
    maxLength: 255,
    errorMessage: "Invalid email address",
    sanitize: true,
  },
  {
    field: "phone",
    type: "phone",
    required: false,
    maxLength: 20,
    errorMessage: "Invalid phone number",
    sanitize: true,
  },
  {
    field: "firstName",
    type: "string",
    required: true,
    minLength: 2,
    maxLength: 50,
    sanitize: true,
  },
  {
    field: "lastName",
    type: "string",
    required: true,
    minLength: 2,
    maxLength: 50,
    sanitize: true,
  },
];

/**
 * Common validation rules for Product model
 */
export const PRODUCT_VALIDATION_RULES: FieldValidationRule[] = [
  {
    field: "name",
    type: "string",
    required: true,
    minLength: 3,
    maxLength: 200,
    sanitize: true,
  },
  {
    field: "price",
    type: "number",
    required: true,
    min: 0,
    errorMessage: "Price must be positive",
  },
  {
    field: "stock",
    type: "number",
    required: true,
    min: 0,
    errorMessage: "Stock cannot be negative",
  },
  {
    field: "description",
    type: "string",
    required: false,
    maxLength: 2000,
    sanitize: true,
  },
];

/**
 * Common validation rules for Field model (agriculture)
 */
export const FIELD_VALIDATION_RULES: FieldValidationRule[] = [
  {
    field: "name",
    type: "string",
    required: true,
    minLength: 2,
    maxLength: 200,
    sanitize: true,
  },
  {
    field: "areaHectares",
    type: "number",
    required: true,
    min: 0.01,
    max: 10000,
    errorMessage: "Field area must be between 0.01 and 10,000 hectares",
  },
];

// ═══════════════════════════════════════════════════════════════════════════
// Export all middleware and utilities
// ═══════════════════════════════════════════════════════════════════════════

export const PRISMA_MIDDLEWARE_UTILITIES = {
  createValidationMiddleware,
  createAuditLoggingMiddleware,
  createSoftDeleteMiddleware,
  createTimestampMiddleware,
  USER_VALIDATION_RULES,
  PRODUCT_VALIDATION_RULES,
  FIELD_VALIDATION_RULES,
};
