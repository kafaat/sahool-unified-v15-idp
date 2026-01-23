// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL API Client - Type Validation & Runtime Checks
// التحقق من الأنواع وفحوصات وقت التشغيل
// ═══════════════════════════════════════════════════════════════════════════════

import type {
  Task,
  Field,
  Farm,
  WeatherData,
  DiagnosisRecord,
  Notification,
  Equipment,
  Alert,
  User,
  PaginatedResponse,
  ApiResponse,
} from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validation result
 */
export interface ValidationResult<T> {
  success: boolean;
  data?: T;
  errors: ValidationError[];
}

/**
 * Single validation error
 */
export interface ValidationError {
  path: string;
  message: string;
  messageAr: string;
  expected?: string;
  received?: string;
}

/**
 * Schema definition for validation
 */
export interface Schema<T> {
  validate: (data: unknown) => ValidationResult<T>;
  parse: (data: unknown) => T;
  safeParse: (data: unknown) => ValidationResult<T>;
  isValid: (data: unknown) => data is T;
}

/**
 * Field schema definition
 */
export interface FieldSchema {
  type:
    | "string"
    | "number"
    | "boolean"
    | "array"
    | "object"
    | "date"
    | "enum"
    | "any";
  required?: boolean;
  nullable?: boolean;
  min?: number;
  max?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  enum?: readonly unknown[];
  items?: FieldSchema;
  properties?: Record<string, FieldSchema>;
  custom?: (value: unknown) => boolean | string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Validation Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if value is null or undefined
 */
function isNullish(value: unknown): value is null | undefined {
  return value === null || value === undefined;
}

/**
 * Get type of value as string
 */
function getTypeName(value: unknown): string {
  if (value === null) return "null";
  if (value === undefined) return "undefined";
  if (Array.isArray(value)) return "array";
  return typeof value;
}

/**
 * Validate a field against a schema
 */
function validateField(
  value: unknown,
  schema: FieldSchema,
  path: string,
): ValidationError[] {
  const errors: ValidationError[] = [];

  // Handle required check
  if (isNullish(value)) {
    if (schema.required && !schema.nullable) {
      errors.push({
        path,
        message: `Field "${path}" is required`,
        messageAr: `الحقل "${path}" مطلوب`,
        expected: schema.type,
        received: getTypeName(value),
      });
    }
    return errors;
  }

  // Type validation
  switch (schema.type) {
    case "string":
      if (typeof value !== "string") {
        errors.push({
          path,
          message: `Expected string, got ${getTypeName(value)}`,
          messageAr: `متوقع نص، تم استلام ${getTypeName(value)}`,
          expected: "string",
          received: getTypeName(value),
        });
      } else {
        if (schema.minLength !== undefined && value.length < schema.minLength) {
          errors.push({
            path,
            message: `String length must be at least ${schema.minLength}`,
            messageAr: `طول النص يجب أن يكون على الأقل ${schema.minLength}`,
          });
        }
        if (schema.maxLength !== undefined && value.length > schema.maxLength) {
          errors.push({
            path,
            message: `String length must be at most ${schema.maxLength}`,
            messageAr: `طول النص يجب أن يكون على الأكثر ${schema.maxLength}`,
          });
        }
        if (schema.pattern && !schema.pattern.test(value)) {
          errors.push({
            path,
            message: `String does not match pattern`,
            messageAr: `النص لا يطابق النمط المطلوب`,
          });
        }
      }
      break;

    case "number":
      if (typeof value !== "number" || isNaN(value)) {
        errors.push({
          path,
          message: `Expected number, got ${getTypeName(value)}`,
          messageAr: `متوقع رقم، تم استلام ${getTypeName(value)}`,
          expected: "number",
          received: getTypeName(value),
        });
      } else {
        if (schema.min !== undefined && value < schema.min) {
          errors.push({
            path,
            message: `Number must be at least ${schema.min}`,
            messageAr: `الرقم يجب أن يكون على الأقل ${schema.min}`,
          });
        }
        if (schema.max !== undefined && value > schema.max) {
          errors.push({
            path,
            message: `Number must be at most ${schema.max}`,
            messageAr: `الرقم يجب أن يكون على الأكثر ${schema.max}`,
          });
        }
      }
      break;

    case "boolean":
      if (typeof value !== "boolean") {
        errors.push({
          path,
          message: `Expected boolean, got ${getTypeName(value)}`,
          messageAr: `متوقع قيمة منطقية، تم استلام ${getTypeName(value)}`,
          expected: "boolean",
          received: getTypeName(value),
        });
      }
      break;

    case "array":
      if (!Array.isArray(value)) {
        errors.push({
          path,
          message: `Expected array, got ${getTypeName(value)}`,
          messageAr: `متوقع مصفوفة، تم استلام ${getTypeName(value)}`,
          expected: "array",
          received: getTypeName(value),
        });
      } else {
        if (schema.min !== undefined && value.length < schema.min) {
          errors.push({
            path,
            message: `Array must have at least ${schema.min} items`,
            messageAr: `المصفوفة يجب أن تحتوي على الأقل ${schema.min} عناصر`,
          });
        }
        if (schema.max !== undefined && value.length > schema.max) {
          errors.push({
            path,
            message: `Array must have at most ${schema.max} items`,
            messageAr: `المصفوفة يجب أن تحتوي على الأكثر ${schema.max} عناصر`,
          });
        }
        if (schema.items) {
          value.forEach((item, index) => {
            errors.push(
              ...validateField(item, schema.items!, `${path}[${index}]`),
            );
          });
        }
      }
      break;

    case "object":
      if (typeof value !== "object" || Array.isArray(value)) {
        errors.push({
          path,
          message: `Expected object, got ${getTypeName(value)}`,
          messageAr: `متوقع كائن، تم استلام ${getTypeName(value)}`,
          expected: "object",
          received: getTypeName(value),
        });
      } else if (schema.properties) {
        const obj = value as Record<string, unknown>;
        for (const [key, fieldSchema] of Object.entries(schema.properties)) {
          errors.push(
            ...validateField(obj[key], fieldSchema, `${path}.${key}`),
          );
        }
      }
      break;

    case "date":
      if (typeof value === "string") {
        const date = new Date(value);
        if (isNaN(date.getTime())) {
          errors.push({
            path,
            message: `Invalid date format`,
            messageAr: `صيغة التاريخ غير صالحة`,
            expected: "ISO date string",
            received: String(value),
          });
        }
      } else if (!(value instanceof Date)) {
        errors.push({
          path,
          message: `Expected date string or Date, got ${getTypeName(value)}`,
          messageAr: `متوقع تاريخ، تم استلام ${getTypeName(value)}`,
          expected: "date",
          received: getTypeName(value),
        });
      }
      break;

    case "enum":
      if (schema.enum && !schema.enum.includes(value)) {
        errors.push({
          path,
          message: `Value must be one of: ${schema.enum.join(", ")}`,
          messageAr: `القيمة يجب أن تكون واحدة من: ${schema.enum.join(", ")}`,
          expected: schema.enum.join(" | "),
          received: String(value),
        });
      }
      break;

    case "any":
      // No validation needed
      break;
  }

  // Custom validation
  if (schema.custom) {
    const result = schema.custom(value);
    if (result !== true) {
      errors.push({
        path,
        message: typeof result === "string" ? result : "Custom validation failed",
        messageAr:
          typeof result === "string" ? result : "فشل التحقق المخصص",
      });
    }
  }

  return errors;
}

// ─────────────────────────────────────────────────────────────────────────────
// Schema Builder
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create a schema for validation
 */
export function createSchema<T>(
  schema: Record<string, FieldSchema>,
): Schema<T> {
  const validate = (data: unknown): ValidationResult<T> => {
    if (typeof data !== "object" || data === null) {
      return {
        success: false,
        errors: [
          {
            path: "",
            message: "Expected object",
            messageAr: "متوقع كائن",
            expected: "object",
            received: getTypeName(data),
          },
        ],
      };
    }

    const errors: ValidationError[] = [];
    const obj = data as Record<string, unknown>;

    for (const [key, fieldSchema] of Object.entries(schema)) {
      errors.push(...validateField(obj[key], fieldSchema, key));
    }

    return {
      success: errors.length === 0,
      data: errors.length === 0 ? (data as T) : undefined,
      errors,
    };
  };

  return {
    validate,
    safeParse: validate,
    parse: (data: unknown): T => {
      const result = validate(data);
      if (!result.success) {
        throw new ValidationException(result.errors);
      }
      return result.data!;
    },
    isValid: (data: unknown): data is T => validate(data).success,
  };
}

/**
 * Validation exception class
 */
export class ValidationException extends Error {
  public readonly errors: ValidationError[];

  constructor(errors: ValidationError[]) {
    const message = errors
      .map((e) => `${e.path}: ${e.message}`)
      .join("; ");
    super(`Validation failed: ${message}`);
    this.name = "ValidationException";
    this.errors = errors;

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Predefined Schemas
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Task schema
 */
export const TaskSchema = createSchema<Task>({
  id: { type: "string", required: true },
  tenant_id: { type: "string", required: true },
  field_id: { type: "string", required: true },
  title: { type: "string", required: true, minLength: 1 },
  status: {
    type: "enum",
    required: true,
    enum: ["open", "pending", "in_progress", "completed", "cancelled"],
  },
  priority: {
    type: "enum",
    required: true,
    enum: ["urgent", "high", "medium", "low"],
  },
  created_at: { type: "date", required: true },
  updated_at: { type: "date", required: true },
});

/**
 * Field schema
 */
export const FieldSchema = createSchema<Field>({
  id: { type: "string", required: true },
  name: { type: "string", required: true, minLength: 1 },
  farm_id: { type: "string", required: true },
  area: { type: "number", required: true, min: 0 },
  status: { type: "string", required: true },
});

/**
 * Farm schema
 */
export const FarmSchema = createSchema<Farm>({
  id: { type: "string", required: true },
  name: { type: "string", required: true, minLength: 1 },
  ownerId: { type: "string", required: true },
  governorate: { type: "string", required: true },
  area: { type: "number", required: true, min: 0 },
  coordinates: {
    type: "object",
    required: true,
    properties: {
      lat: { type: "number", required: true, min: -90, max: 90 },
      lng: { type: "number", required: true, min: -180, max: 180 },
    },
  },
  crops: { type: "array", required: true, items: { type: "string" } },
  status: { type: "enum", required: true, enum: ["active", "inactive", "suspended"] },
  healthScore: { type: "number", required: true, min: 0, max: 100 },
  lastUpdated: { type: "date", required: true },
  createdAt: { type: "date", required: true },
});

/**
 * Weather data schema
 */
export const WeatherDataSchema = createSchema<WeatherData>({
  location_id: { type: "string", required: true },
  temperature_c: { type: "number", required: true },
  humidity_percent: { type: "number", required: true, min: 0, max: 100 },
  wind_speed_kmh: { type: "number", required: true, min: 0 },
  condition: { type: "string", required: true },
  condition_ar: { type: "string", required: true },
});

/**
 * User schema
 */
export const UserSchema = createSchema<User>({
  id: { type: "string", required: true },
  email: {
    type: "string",
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  name: { type: "string", required: true, minLength: 1 },
  role: { type: "string", required: true },
  tenantId: { type: "string", required: true },
  isActive: { type: "boolean", required: true },
  createdAt: { type: "date", required: true },
});

// ─────────────────────────────────────────────────────────────────────────────
// Type Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Type guard for Task
 */
export function isTask(value: unknown): value is Task {
  return TaskSchema.isValid(value);
}

/**
 * Type guard for Field
 */
export function isField(value: unknown): value is Field {
  return FieldSchema.isValid(value);
}

/**
 * Type guard for Farm
 */
export function isFarm(value: unknown): value is Farm {
  return FarmSchema.isValid(value);
}

/**
 * Type guard for WeatherData
 */
export function isWeatherData(value: unknown): value is WeatherData {
  return WeatherDataSchema.isValid(value);
}

/**
 * Type guard for User
 */
export function isUser(value: unknown): value is User {
  return UserSchema.isValid(value);
}

/**
 * Type guard for API response wrapper
 */
export function isApiResponse<T>(
  value: unknown,
): value is ApiResponse<T> {
  if (typeof value !== "object" || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.success === "boolean" &&
    "data" in obj
  );
}

/**
 * Type guard for paginated response
 */
export function isPaginatedResponse<T>(
  value: unknown,
): value is PaginatedResponse<T> {
  if (typeof value !== "object" || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    Array.isArray(obj.data) &&
    typeof obj.total === "number" &&
    typeof obj.page === "number" &&
    typeof obj.limit === "number" &&
    typeof obj.hasMore === "boolean"
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Response Validators
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validate and transform API response
 */
export function validateResponse<T>(
  data: unknown,
  schema: Schema<T>,
): T {
  return schema.parse(data);
}

/**
 * Safely validate API response
 */
export function safeValidateResponse<T>(
  data: unknown,
  schema: Schema<T>,
): ValidationResult<T> {
  return schema.safeParse(data);
}

/**
 * Validate array response
 */
export function validateArrayResponse<T>(
  data: unknown,
  itemSchema: Schema<T>,
): T[] {
  if (!Array.isArray(data)) {
    throw new ValidationException([
      {
        path: "",
        message: "Expected array",
        messageAr: "متوقع مصفوفة",
        expected: "array",
        received: getTypeName(data),
      },
    ]);
  }

  return data.map((item, index) => {
    const result = itemSchema.safeParse(item);
    if (!result.success) {
      throw new ValidationException(
        result.errors.map((e) => ({
          ...e,
          path: `[${index}].${e.path}`,
        })),
      );
    }
    return result.data!;
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Discriminated Union Helpers
// ─────────────────────────────────────────────────────────────────────────────

/**
 * API operation result - success or error
 */
export type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

/**
 * Create a success result
 */
export function success<T>(data: T): Result<T, never> {
  return { success: true, data };
}

/**
 * Create an error result
 */
export function failure<E>(error: E): Result<never, E> {
  return { success: false, error };
}

/**
 * Wrap a promise in a Result type
 */
export async function toResult<T>(
  promise: Promise<T>,
): Promise<Result<T, Error>> {
  try {
    const data = await promise;
    return success(data);
  } catch (error) {
    return failure(error instanceof Error ? error : new Error(String(error)));
  }
}

/**
 * Map over a successful result
 */
export function mapResult<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => U,
): Result<U, E> {
  if (result.success) {
    return success(fn(result.data));
  }
  return result;
}

/**
 * Flatten nested results
 */
export function flatMapResult<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => Result<U, E>,
): Result<U, E> {
  if (result.success) {
    return fn(result.data);
  }
  return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// Async State Types
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Async operation state
 */
export type AsyncState<T, E = Error> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: E };

/**
 * Create idle state
 */
export function idle<T, E = Error>(): AsyncState<T, E> {
  return { status: "idle" };
}

/**
 * Create loading state
 */
export function loading<T, E = Error>(): AsyncState<T, E> {
  return { status: "loading" };
}

/**
 * Create success state
 */
export function successState<T>(data: T): AsyncState<T, never> {
  return { status: "success", data };
}

/**
 * Create error state
 */
export function errorState<E>(error: E): AsyncState<never, E> {
  return { status: "error", error };
}

/**
 * Check if state is loading
 */
export function isLoading<T, E>(state: AsyncState<T, E>): state is { status: "loading" } {
  return state.status === "loading";
}

/**
 * Check if state is success
 */
export function isSuccess<T, E>(
  state: AsyncState<T, E>,
): state is { status: "success"; data: T } {
  return state.status === "success";
}

/**
 * Check if state is error
 */
export function isError<T, E>(
  state: AsyncState<T, E>,
): state is { status: "error"; error: E } {
  return state.status === "error";
}

/**
 * Get data from success state or default value
 */
export function getDataOrDefault<T, E>(
  state: AsyncState<T, E>,
  defaultValue: T,
): T {
  return state.status === "success" ? state.data : defaultValue;
}
