/**
 * SAHOOL Common Types
 * Base types, utility types, and branded identifiers
 *
 * This module provides foundational type definitions used across the SAHOOL platform.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// Branded Types (Nominal Typing)
// These prevent accidentally mixing up different ID types at compile time
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Brand type for creating nominal types
 * @internal
 */
declare const __brand: unique symbol;

/**
 * Creates a branded type that prevents accidental type mixing
 * @example
 * type UserId = Brand<string, 'UserId'>;
 * type FieldId = Brand<string, 'FieldId'>;
 * // UserId and FieldId are incompatible even though both are strings
 */
export type Brand<T, B> = T & { readonly [__brand]: B };

/** Unique identifier for a user */
export type UserId = Brand<string, "UserId">;

/** Unique identifier for a tenant/organization */
export type TenantId = Brand<string, "TenantId">;

/** Unique identifier for a field */
export type FieldId = Brand<string, "FieldId">;

/** Unique identifier for a farm */
export type FarmId = Brand<string, "FarmId">;

/** Unique identifier for a task */
export type TaskId = Brand<string, "TaskId">;

/** Unique identifier for an alert */
export type AlertId = Brand<string, "AlertId">;

/** Unique identifier for a sensor */
export type SensorId = Brand<string, "SensorId">;

/** Unique identifier for equipment */
export type EquipmentId = Brand<string, "EquipmentId">;

// ═══════════════════════════════════════════════════════════════════════════════
// Base Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Base entity with common fields
 * All database entities should extend this interface
 */
export interface BaseEntity {
  /** Unique identifier */
  id: string;
  /** ISO 8601 timestamp of creation */
  createdAt: string;
  /** ISO 8601 timestamp of last update */
  updatedAt: string;
}

/**
 * Entity with tenant isolation
 * Used for multi-tenant data isolation
 */
export interface TenantEntity extends BaseEntity {
  /** Tenant/organization identifier for data isolation */
  tenantId: string;
}

/**
 * Entity with soft delete support
 */
export interface SoftDeletableEntity extends BaseEntity {
  /** ISO 8601 timestamp of deletion, null if active */
  deletedAt: string | null;
  /** Whether the entity is deleted */
  isDeleted: boolean;
}

/**
 * Entity with audit trail
 */
export interface AuditableEntity extends BaseEntity {
  /** User ID who created the entity */
  createdBy: string;
  /** User ID who last updated the entity */
  updatedBy?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Common Enums and Union Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Supported locales for bilingual content
 * ar = Arabic (العربية), en = English
 */
export type Locale = "ar" | "en";

/**
 * Priority levels for tasks, alerts, and notifications
 */
export type Priority = "urgent" | "high" | "medium" | "low";

/**
 * Severity levels for alerts and issues
 */
export type Severity = "low" | "medium" | "high" | "critical";

/**
 * Trend direction for KPIs and indicators
 */
export type TrendDirection = "up" | "down" | "stable";

/**
 * Health status for fields and crops
 */
export type HealthStatus =
  | "excellent"
  | "good"
  | "moderate"
  | "warning"
  | "critical"
  | "healthy"
  | "stressed";

/**
 * Log levels for debugging and monitoring
 */
export type LogLevel = "none" | "error" | "warn" | "info" | "debug";

// ═══════════════════════════════════════════════════════════════════════════════
// Bilingual Content Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Content available in both Arabic and English
 * @typeParam T - The type of the content value
 */
export interface BilingualContent<T = string> {
  /** English content */
  en: T;
  /** Arabic content (العربية) */
  ar: T;
}

/**
 * Entity with optional bilingual name
 */
export interface BilingualName {
  /** Name in English */
  name: string;
  /** Name in Arabic (optional) */
  nameAr?: string;
}

/**
 * Entity with optional bilingual description
 */
export interface BilingualDescription {
  /** Description in English */
  description?: string;
  /** Description in Arabic (optional) */
  descriptionAr?: string;
}

/**
 * Helper type for snake_case bilingual fields (for API compatibility)
 */
export interface BilingualNameSnakeCase {
  /** Name in English */
  name: string;
  /** Name in Arabic (optional) */
  name_ar?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Utility Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Makes all properties of T optional recursively
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Makes all properties of T required recursively
 */
export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

/**
 * Makes specific keys K of T required
 */
export type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * Makes specific keys K of T optional
 */
export type OptionalKeys<T, K extends keyof T> = Omit<T, K> &
  Partial<Pick<T, K>>;

/**
 * Extracts keys of T that have values assignable to V
 */
export type KeysOfType<T, V> = {
  [K in keyof T]: T[K] extends V ? K : never;
}[keyof T];

/**
 * Picks only string keys from T
 */
export type StringKeys<T> = Extract<keyof T, string>;

/**
 * Creates a type that allows either T or null
 */
export type Nullable<T> = T | null;

/**
 * Creates a type that allows T, null, or undefined
 */
export type Maybe<T> = T | null | undefined;

/**
 * Ensures at least one property is defined
 */
export type AtLeastOne<T, Keys extends keyof T = keyof T> = Partial<T> &
  { [K in Keys]: Required<Pick<T, K>> }[Keys];

/**
 * Ensures exactly one property is defined
 */
export type ExactlyOne<T, Keys extends keyof T = keyof T> = {
  [K in Keys]: Required<Pick<T, K>> &
    Partial<Record<Exclude<Keys, K>, never>>;
}[Keys];

// ═══════════════════════════════════════════════════════════════════════════════
// Result Types (Discriminated Unions)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Represents a successful operation result
 * @typeParam T - The type of the data payload
 */
export interface SuccessResult<T> {
  readonly success: true;
  readonly data: T;
  readonly message?: string;
}

/**
 * Represents a failed operation result
 * @typeParam E - The type of the error (defaults to Error)
 */
export interface FailureResult<E = Error> {
  readonly success: false;
  readonly error: E;
  readonly message?: string;
}

/**
 * Result type for operations that can succeed or fail
 * Use type narrowing with `result.success` to access the appropriate fields
 *
 * @typeParam T - The success data type
 * @typeParam E - The error type (defaults to Error)
 *
 * @example
 * function divide(a: number, b: number): Result<number, string> {
 *   if (b === 0) return { success: false, error: 'Division by zero' };
 *   return { success: true, data: a / b };
 * }
 *
 * const result = divide(10, 2);
 * if (result.success) {
 *   console.log(result.data); // 5
 * } else {
 *   console.error(result.error);
 * }
 */
export type Result<T, E = Error> = SuccessResult<T> | FailureResult<E>;

/**
 * Async result type alias
 */
export type AsyncResult<T, E = Error> = Promise<Result<T, E>>;

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for successful results
 */
export function isSuccess<T, E>(result: Result<T, E>): result is SuccessResult<T> {
  return result.success === true;
}

/**
 * Type guard for failed results
 */
export function isFailure<T, E>(result: Result<T, E>): result is FailureResult<E> {
  return result.success === false;
}

/**
 * Type guard for non-null/undefined values
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * Type guard for string values
 */
export function isString(value: unknown): value is string {
  return typeof value === "string";
}

/**
 * Type guard for number values
 */
export function isNumber(value: unknown): value is number {
  return typeof value === "number" && !Number.isNaN(value);
}

/**
 * Type guard to check if object has a specific key
 */
export function hasKey<K extends string>(
  obj: unknown,
  key: K
): obj is Record<K, unknown> {
  return typeof obj === "object" && obj !== null && key in obj;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Date/Time Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * ISO 8601 date string (YYYY-MM-DD)
 */
export type ISODateString = string;

/**
 * ISO 8601 datetime string (YYYY-MM-DDTHH:mm:ss.sssZ)
 */
export type ISODateTimeString = string;

/**
 * Date range for filtering
 */
export interface DateRange {
  /** Start date (inclusive) */
  startDate: ISODateString;
  /** End date (inclusive) */
  endDate: ISODateString;
}

/**
 * DateTime range for filtering
 */
export interface DateTimeRange {
  /** Start datetime (inclusive) */
  startDateTime: ISODateTimeString;
  /** End datetime (inclusive) */
  endDateTime: ISODateTimeString;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Measurement Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Value with its unit of measurement
 */
export interface Measurement<T = number> {
  /** The numeric value */
  value: T;
  /** Unit of measurement (e.g., "ha", "mm", "kg/ha") */
  unit: string;
}

/**
 * Common agricultural measurement units
 */
export type AreaUnit = "ha" | "m2" | "km2" | "acre" | "dunam";
export type LengthUnit = "m" | "km" | "cm" | "mm";
export type VolumeUnit = "l" | "m3" | "mm";
export type MassUnit = "kg" | "g" | "t";
export type TemperatureUnit = "C" | "F" | "K";
export type SpeedUnit = "km/h" | "m/s" | "knots";
export type PressureUnit = "hPa" | "mbar" | "mmHg";

/**
 * Rate measurement (e.g., kg/ha, l/h)
 */
export interface RateMeasurement {
  /** The numeric value */
  value: number;
  /** Numerator unit */
  numeratorUnit: string;
  /** Denominator unit */
  denominatorUnit: string;
}
