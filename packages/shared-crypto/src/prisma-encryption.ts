/**
 * Prisma Encryption Middleware
 * =============================
 *
 * Automatic encryption/decryption middleware for Prisma ORM
 * Intercepts database operations to encrypt data before saving
 * and decrypt data after reading.
 *
 * @module prisma-encryption
 * @author SAHOOL Team
 */

import { Prisma } from "@prisma/client";
import { encrypt, decrypt, encryptSearchable } from "./field-encryption";

// ═══════════════════════════════════════════════════════════════════════════
// Types and Interfaces
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Encryption type for a field
 */
export type EncryptionType = "standard" | "deterministic";

/**
 * Configuration for a single field
 */
export interface FieldEncryptionConfig {
  type: EncryptionType;
  /** Optional: Disable decryption on read (for write-only encryption) */
  skipDecryption?: boolean;
}

/**
 * Configuration for a model (table)
 */
export interface ModelEncryptionConfig {
  [fieldName: string]: FieldEncryptionConfig;
}

/**
 * Overall encryption configuration
 */
export interface EncryptionConfig {
  [modelName: string]: ModelEncryptionConfig;
}

/**
 * Middleware options
 */
export interface MiddlewareOptions {
  /** Log encryption/decryption operations (for debugging) */
  debug?: boolean;
  /** Custom error handler */
  onError?: (
    error: Error,
    context: { model: string; field: string; operation: string },
  ) => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Encryption Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Encrypt a field value based on configuration
 */
function encryptField(
  value: any,
  config: FieldEncryptionConfig,
  modelName: string,
  fieldName: string,
  options?: MiddlewareOptions,
): any {
  if (value === null || value === undefined || typeof value !== "string") {
    return value;
  }

  try {
    const encrypted =
      config.type === "deterministic"
        ? encryptSearchable(value)
        : encrypt(value);

    if (options?.debug) {
      console.log(
        `[Prisma Encryption] Encrypted ${modelName}.${fieldName} (${config.type})`,
      );
    }

    return encrypted;
  } catch (error) {
    const err =
      error instanceof Error ? error : new Error("Unknown encryption error");

    if (options?.onError) {
      options.onError(err, {
        model: modelName,
        field: fieldName,
        operation: "encrypt",
      });
    } else {
      console.error(
        `[Prisma Encryption] Failed to encrypt ${modelName}.${fieldName}:`,
        err,
      );
    }

    // Return original value on error to prevent data loss
    return value;
  }
}

/**
 * Decrypt a field value based on configuration
 */
function decryptField(
  value: any,
  config: FieldEncryptionConfig,
  modelName: string,
  fieldName: string,
  options?: MiddlewareOptions,
): any {
  if (value === null || value === undefined || typeof value !== "string") {
    return value;
  }

  if (config.skipDecryption) {
    return value;
  }

  try {
    // Deterministic encryption uses searchable which can't be decrypted without hint
    // So we keep it encrypted for search purposes
    if (config.type === "deterministic") {
      return value; // Keep encrypted for searching
    }

    const decrypted = decrypt(value);

    if (options?.debug) {
      console.log(`[Prisma Encryption] Decrypted ${modelName}.${fieldName}`);
    }

    return decrypted;
  } catch (error) {
    const err =
      error instanceof Error ? error : new Error("Unknown decryption error");

    if (options?.onError) {
      options.onError(err, {
        model: modelName,
        field: fieldName,
        operation: "decrypt",
      });
    } else {
      console.error(
        `[Prisma Encryption] Failed to decrypt ${modelName}.${fieldName}:`,
        err,
      );
    }

    // Return original value on error
    return value;
  }
}

/**
 * Encrypt data object based on model configuration
 */
function encryptData(
  data: any,
  modelName: string,
  modelConfig: ModelEncryptionConfig,
  options?: MiddlewareOptions,
): any {
  if (!data || typeof data !== "object") {
    return data;
  }

  const result = { ...data };

  for (const [fieldName, fieldConfig] of Object.entries(modelConfig)) {
    if (fieldName in result) {
      result[fieldName] = encryptField(
        result[fieldName],
        fieldConfig,
        modelName,
        fieldName,
        options,
      );
    }
  }

  return result;
}

/**
 * Decrypt data object based on model configuration
 */
function decryptData(
  data: any,
  modelName: string,
  modelConfig: ModelEncryptionConfig,
  options?: MiddlewareOptions,
): any {
  if (!data || typeof data !== "object") {
    return data;
  }

  // Handle arrays (for findMany, etc.)
  if (Array.isArray(data)) {
    return data.map((item) =>
      decryptData(item, modelName, modelConfig, options),
    );
  }

  const result = { ...data };

  for (const [fieldName, fieldConfig] of Object.entries(modelConfig)) {
    if (fieldName in result) {
      result[fieldName] = decryptField(
        result[fieldName],
        fieldConfig,
        modelName,
        fieldName,
        options,
      );
    }
  }

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// Query Transformation
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Transform where clause to encrypt searchable fields
 */
function transformWhereClause(
  where: any,
  modelName: string,
  modelConfig: ModelEncryptionConfig,
  options?: MiddlewareOptions,
): any {
  if (!where || typeof where !== "object") {
    return where;
  }

  const result = { ...where };

  for (const [key, value] of Object.entries(result)) {
    // Handle nested conditions (AND, OR, NOT)
    if (key === "AND" || key === "OR" || key === "NOT") {
      if (Array.isArray(value)) {
        result[key] = value.map((item) =>
          transformWhereClause(item, modelName, modelConfig, options),
        );
      } else {
        result[key] = transformWhereClause(
          value,
          modelName,
          modelConfig,
          options,
        );
      }
      continue;
    }

    // Check if this field should be encrypted
    const fieldConfig = modelConfig[key];
    if (fieldConfig && fieldConfig.type === "deterministic") {
      // Encrypt the value for searching
      if (typeof value === "string") {
        result[key] = encryptSearchable(value);
        if (options?.debug) {
          console.log(
            `[Prisma Encryption] Encrypted where clause for ${modelName}.${key}`,
          );
        }
      } else if (typeof value === "object" && value !== null) {
        // Handle comparison operators (equals, in, etc.)
        for (const [op, opValue] of Object.entries(value)) {
          if (typeof opValue === "string") {
            result[key][op] = encryptSearchable(opValue);
          } else if (Array.isArray(opValue)) {
            result[key][op] = opValue.map((v) =>
              typeof v === "string" ? encryptSearchable(v) : v,
            );
          }
        }
      }
    }
  }

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Middleware
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create Prisma encryption middleware
 *
 * @param config - Encryption configuration for models and fields
 * @param options - Middleware options
 * @returns Prisma middleware function
 *
 * @example
 * ```typescript
 * import { PrismaClient } from '@prisma/client';
 * import { createPrismaEncryptionMiddleware } from '@sahool/shared-crypto';
 *
 * const prisma = new PrismaClient();
 *
 * const encryptionConfig = {
 *   User: {
 *     phone: { type: 'deterministic' },
 *   },
 *   UserProfile: {
 *     nationalId: { type: 'deterministic' },
 *     dateOfBirth: { type: 'standard' },
 *   },
 * };
 *
 * prisma.$use(createPrismaEncryptionMiddleware(encryptionConfig));
 * ```
 */
export function createPrismaEncryptionMiddleware(
  config: EncryptionConfig,
  options?: MiddlewareOptions,
): (params: any, next: (params: any) => Promise<any>) => Promise<any> {
  return async (params: any, next: any) => {
    const { model, action } = params;

    // Skip if no model or model not in config
    if (!model || !config[model]) {
      return next(params);
    }

    const modelConfig = config[model];

    // ═══════════════════════════════════════════════════════════════════
    // CREATE Operations - Encrypt data before insertion
    // ═══════════════════════════════════════════════════════════════════

    if (action === "create") {
      if (params.args.data) {
        params.args.data = encryptData(
          params.args.data,
          model,
          modelConfig,
          options,
        );
      }
    }

    // ═══════════════════════════════════════════════════════════════════
    // UPDATE Operations - Encrypt data before update
    // ═══════════════════════════════════════════════════════════════════

    if (action === "update" || action === "updateMany") {
      if (params.args.data) {
        params.args.data = encryptData(
          params.args.data,
          model,
          modelConfig,
          options,
        );
      }

      // Transform where clause for searchable fields
      if (params.args.where) {
        params.args.where = transformWhereClause(
          params.args.where,
          model,
          modelConfig,
          options,
        );
      }
    }

    // ═══════════════════════════════════════════════════════════════════
    // UPSERT Operations - Encrypt both create and update data
    // ═══════════════════════════════════════════════════════════════════

    if (action === "upsert") {
      if (params.args.create) {
        params.args.create = encryptData(
          params.args.create,
          model,
          modelConfig,
          options,
        );
      }
      if (params.args.update) {
        params.args.update = encryptData(
          params.args.update,
          model,
          modelConfig,
          options,
        );
      }
      if (params.args.where) {
        params.args.where = transformWhereClause(
          params.args.where,
          model,
          modelConfig,
          options,
        );
      }
    }

    // ═══════════════════════════════════════════════════════════════════
    // FIND Operations - Transform where clause for searching
    // ═══════════════════════════════════════════════════════════════════

    if (
      action === "findUnique" ||
      action === "findFirst" ||
      action === "findMany" ||
      action === "findFirstOrThrow" ||
      action === "findUniqueOrThrow"
    ) {
      if (params.args?.where) {
        params.args.where = transformWhereClause(
          params.args.where,
          model,
          modelConfig,
          options,
        );
      }
    }

    // ═══════════════════════════════════════════════════════════════════
    // DELETE Operations - Transform where clause
    // ═══════════════════════════════════════════════════════════════════

    if (action === "delete" || action === "deleteMany") {
      if (params.args?.where) {
        params.args.where = transformWhereClause(
          params.args.where,
          model,
          modelConfig,
          options,
        );
      }
    }

    // Execute the query
    const result = await next(params);

    // ═══════════════════════════════════════════════════════════════════
    // Decrypt results after reading from database
    // ═══════════════════════════════════════════════════════════════════

    const readActions = [
      "findUnique",
      "findFirst",
      "findMany",
      "create",
      "update",
      "upsert",
      "findUniqueOrThrow",
      "findFirstOrThrow",
    ];

    if (readActions.includes(action) && result) {
      return decryptData(result, model, modelConfig, options);
    }

    return result;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create a basic encryption config for common sensitive fields
 *
 * @returns Basic encryption configuration
 */
export function createBasicEncryptionConfig(): EncryptionConfig {
  return {
    User: {
      phone: { type: "deterministic" },
      email: { type: "deterministic" },
    },
    UserProfile: {
      nationalId: { type: "deterministic" },
      dateOfBirth: { type: "standard" },
      address: { type: "standard" },
    },
  };
}

/**
 * Merge multiple encryption configs
 *
 * @param configs - Array of configs to merge
 * @returns Merged configuration
 */
export function mergeEncryptionConfigs(
  ...configs: EncryptionConfig[]
): EncryptionConfig {
  const result: EncryptionConfig = {};

  for (const config of configs) {
    for (const [model, fields] of Object.entries(config)) {
      if (!result[model]) {
        result[model] = {};
      }
      result[model] = { ...result[model], ...fields };
    }
  }

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// Exports
// ═══════════════════════════════════════════════════════════════════════════

export default {
  createPrismaEncryptionMiddleware,
  createBasicEncryptionConfig,
  mergeEncryptionConfigs,
};
