/**
 * Type Guard Functions
 * دوال حراسة الأنواع
 *
 * Provides runtime type checking with TypeScript type narrowing.
 * توفر فحص الأنواع في وقت التشغيل مع تضييق أنواع TypeScript.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Primitive Type Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if value is a string
 * التحقق مما إذا كانت القيمة نصية
 */
export function isString(value: unknown): value is string {
  return typeof value === "string";
}

/**
 * Check if value is a number (and not NaN)
 * التحقق مما إذا كانت القيمة رقمية (وليست NaN)
 */
export function isNumber(value: unknown): value is number {
  return typeof value === "number" && !Number.isNaN(value);
}

/**
 * Check if value is a finite number
 * التحقق مما إذا كانت القيمة رقمية محدودة
 */
export function isFiniteNumber(value: unknown): value is number {
  return isNumber(value) && Number.isFinite(value);
}

/**
 * Check if value is an integer
 * التحقق مما إذا كانت القيمة عدد صحيح
 */
export function isInteger(value: unknown): value is number {
  return isNumber(value) && Number.isInteger(value);
}

/**
 * Check if value is a boolean
 * التحقق مما إذا كانت القيمة منطقية
 */
export function isBoolean(value: unknown): value is boolean {
  return typeof value === "boolean";
}

/**
 * Check if value is null
 * التحقق مما إذا كانت القيمة null
 */
export function isNull(value: unknown): value is null {
  return value === null;
}

/**
 * Check if value is undefined
 * التحقق مما إذا كانت القيمة undefined
 */
export function isUndefined(value: unknown): value is undefined {
  return value === undefined;
}

/**
 * Check if value is null or undefined
 * التحقق مما إذا كانت القيمة null أو undefined
 */
export function isNullish(value: unknown): value is null | undefined {
  return value === null || value === undefined;
}

/**
 * Check if value is defined (not null or undefined)
 * التحقق مما إذا كانت القيمة معرّفة
 */
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

/**
 * Check if value is a symbol
 * التحقق مما إذا كانت القيمة رمزاً
 */
export function isSymbol(value: unknown): value is symbol {
  return typeof value === "symbol";
}

/**
 * Check if value is a bigint
 * التحقق مما إذا كانت القيمة bigint
 */
export function isBigInt(value: unknown): value is bigint {
  return typeof value === "bigint";
}

// ─────────────────────────────────────────────────────────────────────────────
// Object Type Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if value is an object (not null, not array)
 * التحقق مما إذا كانت القيمة كائناً
 */
export function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Check if value is a plain object (not class instance)
 * التحقق مما إذا كانت القيمة كائناً بسيطاً
 */
export function isPlainObject(value: unknown): value is Record<string, unknown> {
  if (!isObject(value)) {
    return false;
  }

  const proto = Object.getPrototypeOf(value);
  return proto === null || proto === Object.prototype;
}

/**
 * Check if value is an array
 * التحقق مما إذا كانت القيمة مصفوفة
 */
export function isArray(value: unknown): value is unknown[] {
  return Array.isArray(value);
}

/**
 * Check if value is an array of specific type
 * التحقق مما إذا كانت القيمة مصفوفة من نوع محدد
 */
export function isArrayOf<T>(
  value: unknown,
  guard: (item: unknown) => item is T,
): value is T[] {
  return isArray(value) && value.every(guard);
}

/**
 * Check if value is a non-empty array
 * التحقق مما إذا كانت القيمة مصفوفة غير فارغة
 */
export function isNonEmptyArray<T>(value: T[] | unknown): value is [T, ...T[]] {
  return isArray(value) && value.length > 0;
}

/**
 * Check if value is a function
 * التحقق مما إذا كانت القيمة دالة
 */
export function isFunction(value: unknown): value is (...args: unknown[]) => unknown {
  return typeof value === "function";
}

/**
 * Check if value is a Date instance
 * التحقق مما إذا كانت القيمة تاريخاً
 */
export function isDate(value: unknown): value is Date {
  return value instanceof Date && !Number.isNaN(value.getTime());
}

/**
 * Check if value is a valid Date
 * التحقق مما إذا كانت القيمة تاريخاً صالحاً
 */
export function isValidDate(value: unknown): value is Date {
  return value instanceof Date && !Number.isNaN(value.getTime());
}

/**
 * Check if value is a RegExp
 * التحقق مما إذا كانت القيمة تعبيراً نمطياً
 */
export function isRegExp(value: unknown): value is RegExp {
  return value instanceof RegExp;
}

/**
 * Check if value is an Error
 * التحقق مما إذا كانت القيمة خطأ
 */
export function isError(value: unknown): value is Error {
  return value instanceof Error;
}

/**
 * Check if value is a Map
 * التحقق مما إذا كانت القيمة خريطة
 */
export function isMap<K = unknown, V = unknown>(value: unknown): value is Map<K, V> {
  return value instanceof Map;
}

/**
 * Check if value is a Set
 * التحقق مما إذا كانت القيمة مجموعة
 */
export function isSet<T = unknown>(value: unknown): value is Set<T> {
  return value instanceof Set;
}

/**
 * Check if value is a Promise
 * التحقق مما إذا كانت القيمة وعداً
 */
export function isPromise<T = unknown>(value: unknown): value is Promise<T> {
  return (
    value instanceof Promise ||
    (isObject(value) &&
      isFunction((value as Record<string, unknown>).then) &&
      isFunction((value as Record<string, unknown>).catch))
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// String Type Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if value is a non-empty string
 * التحقق مما إذا كانت القيمة نصاً غير فارغ
 */
export function isNonEmptyString(value: unknown): value is string {
  return isString(value) && value.trim().length > 0;
}

/**
 * Check if string is a valid UUID
 * التحقق مما إذا كان النص UUID صالحاً
 */
export function isUUID(value: unknown): value is string {
  if (!isString(value)) {
    return false;
  }
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(value);
}

/**
 * Check if string is a valid URL
 * التحقق مما إذا كان النص رابطاً صالحاً
 */
export function isURL(value: unknown): value is string {
  if (!isString(value)) {
    return false;
  }
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if string is a valid ISO date string
 * التحقق مما إذا كان النص تاريخاً ISO صالحاً
 */
export function isISODateString(value: unknown): value is string {
  if (!isString(value)) {
    return false;
  }
  const date = new Date(value);
  return !Number.isNaN(date.getTime()) && value.includes("-");
}

/**
 * Check if string is valid JSON
 * التحقق مما إذا كان النص JSON صالحاً
 */
export function isJSONString(value: unknown): value is string {
  if (!isString(value)) {
    return false;
  }
  try {
    JSON.parse(value);
    return true;
  } catch {
    return false;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Number Range Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if number is positive
 * التحقق مما إذا كان الرقم موجباً
 */
export function isPositive(value: unknown): value is number {
  return isNumber(value) && value > 0;
}

/**
 * Check if number is negative
 * التحقق مما إذا كان الرقم سالباً
 */
export function isNegative(value: unknown): value is number {
  return isNumber(value) && value < 0;
}

/**
 * Check if number is within a range (inclusive)
 * التحقق مما إذا كان الرقم ضمن نطاق
 */
export function isInRange(value: unknown, min: number, max: number): value is number {
  return isNumber(value) && value >= min && value <= max;
}

/**
 * Check if number is a valid percentage (0-100)
 * التحقق مما إذا كان الرقم نسبة مئوية صالحة
 */
export function isPercentage(value: unknown): value is number {
  return isNumber(value) && value >= 0 && value <= 100;
}

// ─────────────────────────────────────────────────────────────────────────────
// Object Property Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if object has a specific property
 * التحقق مما إذا كان الكائن يحتوي على خاصية محددة
 */
export function hasProperty<K extends string>(
  obj: unknown,
  key: K,
): obj is Record<K, unknown> {
  return isObject(obj) && key in obj;
}

/**
 * Check if object has specific properties
 * التحقق مما إذا كان الكائن يحتوي على خصائص محددة
 */
export function hasProperties<K extends string>(
  obj: unknown,
  keys: K[],
): obj is Record<K, unknown> {
  return isObject(obj) && keys.every((key) => key in obj);
}

/**
 * Check if object has a property of specific type
 * التحقق مما إذا كان الكائن يحتوي على خاصية من نوع محدد
 */
export function hasPropertyOfType<K extends string, T>(
  obj: unknown,
  key: K,
  guard: (value: unknown) => value is T,
): obj is Record<K, T> {
  return hasProperty(obj, key) && guard(obj[key]);
}

// ─────────────────────────────────────────────────────────────────────────────
// Utility Types for Type Guards
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Type for a type guard function
 * نوع لدالة حراسة النوع
 */
export type TypeGuard<T> = (value: unknown) => value is T;

/**
 * Extract the type from a type guard
 * استخراج النوع من حراسة النوع
 */
export type GuardedType<G> = G extends TypeGuard<infer T> ? T : never;

/**
 * Create a type guard for a literal value
 * إنشاء حراسة نوع لقيمة حرفية
 */
export function isLiteral<T extends string | number | boolean>(
  literal: T,
): TypeGuard<T> {
  return (value: unknown): value is T => value === literal;
}

/**
 * Create a type guard for union of literals
 * إنشاء حراسة نوع لاتحاد القيم الحرفية
 */
export function isOneOf<T extends readonly (string | number | boolean)[]>(
  literals: T,
): TypeGuard<T[number]> {
  const set = new Set(literals);
  return (value: unknown): value is T[number] =>
    (isString(value) || isNumber(value) || isBoolean(value)) && set.has(value);
}

/**
 * Combine type guards with AND logic
 * دمج حراسات الأنواع بمنطق AND
 */
export function and<A, B>(
  guardA: TypeGuard<A>,
  guardB: TypeGuard<B>,
): TypeGuard<A & B> {
  return (value: unknown): value is A & B => guardA(value) && guardB(value);
}

/**
 * Combine type guards with OR logic
 * دمج حراسات الأنواع بمنطق OR
 */
export function or<A, B>(
  guardA: TypeGuard<A>,
  guardB: TypeGuard<B>,
): TypeGuard<A | B> {
  return (value: unknown): value is A | B => guardA(value) || guardB(value);
}

/**
 * Negate a type guard
 * نفي حراسة النوع
 */
export function not<T>(guard: TypeGuard<T>): (value: unknown) => value is Exclude<unknown, T> {
  return (value: unknown): value is Exclude<unknown, T> => !guard(value);
}

// ─────────────────────────────────────────────────────────────────────────────
// Assertion Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Assert that a condition is true, narrowing type
 * تأكيد أن الشرط صحيح مع تضييق النوع
 */
export function assert(condition: boolean, message?: string): asserts condition {
  if (!condition) {
    throw new Error(message || "Assertion failed");
  }
}

/**
 * Assert that value is defined (not null or undefined)
 * تأكيد أن القيمة معرّفة
 */
export function assertDefined<T>(
  value: T | null | undefined,
  message?: string,
): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message || "Value is null or undefined");
  }
}

/**
 * Assert that value matches a type guard
 * تأكيد أن القيمة تطابق حراسة النوع
 */
export function assertType<T>(
  value: unknown,
  guard: TypeGuard<T>,
  message?: string,
): asserts value is T {
  if (!guard(value)) {
    throw new TypeError(message || "Type assertion failed");
  }
}

/**
 * Assert unreachable code (exhaustive checks)
 * تأكيد رمز غير قابل للوصول
 */
export function assertNever(value: never, message?: string): never {
  throw new Error(message || `Unexpected value: ${value}`);
}
