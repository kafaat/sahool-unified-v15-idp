/**
 * Safe Parsing Utilities
 * أدوات التحليل الآمن
 *
 * Provides safe parsing functions that never throw, returning Result types instead.
 * توفر دوال تحليل آمنة لا تُلقي استثناءات، وتُرجع أنواع النتيجة بدلاً من ذلك.
 */

// ─────────────────────────────────────────────────────────────────────────────
// Result Type
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Success result
 * نتيجة النجاح
 */
export interface Success<T> {
  readonly success: true;
  readonly value: T;
}

/**
 * Failure result
 * نتيجة الفشل
 */
export interface Failure<E = Error> {
  readonly success: false;
  readonly error: E;
}

/**
 * Result type - either success with value or failure with error
 * نوع النتيجة - إما نجاح مع قيمة أو فشل مع خطأ
 */
export type Result<T, E = Error> = Success<T> | Failure<E>;

/**
 * Create a success result
 * إنشاء نتيجة نجاح
 */
export function ok<T>(value: T): Success<T> {
  return { success: true, value };
}

/**
 * Create a failure result
 * إنشاء نتيجة فشل
 */
export function err<E = Error>(error: E): Failure<E> {
  return { success: false, error };
}

/**
 * Check if result is success
 * التحقق مما إذا كانت النتيجة نجاحاً
 */
export function isOk<T, E>(result: Result<T, E>): result is Success<T> {
  return result.success === true;
}

/**
 * Check if result is failure
 * التحقق مما إذا كانت النتيجة فشلاً
 */
export function isErr<T, E>(result: Result<T, E>): result is Failure<E> {
  return result.success === false;
}

/**
 * Unwrap result or throw
 * فك النتيجة أو إلقاء استثناء
 */
export function unwrap<T, E>(result: Result<T, E>): T {
  if (isOk(result)) {
    return result.value;
  }
  throw result.error;
}

/**
 * Unwrap result or return default
 * فك النتيجة أو إرجاع القيمة الافتراضية
 */
export function unwrapOr<T, E>(result: Result<T, E>, defaultValue: T): T {
  return isOk(result) ? result.value : defaultValue;
}

/**
 * Map result value if success
 * تحويل قيمة النتيجة إذا كانت نجاحاً
 */
export function mapResult<T, U, E>(
  result: Result<T, E>,
  fn: (value: T) => U,
): Result<U, E> {
  if (isOk(result)) {
    return ok(fn(result.value));
  }
  return result;
}

// ─────────────────────────────────────────────────────────────────────────────
// Safe JSON Parsing
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Safely parse JSON string
 * تحليل JSON بشكل آمن
 *
 * @param text - النص - JSON string to parse
 * @param reviver - المُحوّل - Optional reviver function
 * @returns النتيجة - Result with parsed value or error
 *
 * @example
 * const result = safeJsonParse('{"name": "test"}');
 * if (result.success) {
 *   console.log(result.value.name);
 * }
 */
export function safeJsonParse<T = unknown>(
  text: string,
  reviver?: (key: string, value: unknown) => unknown,
): Result<T, SyntaxError> {
  try {
    const value = JSON.parse(text, reviver) as T;
    return ok(value);
  } catch (error) {
    return err(error instanceof SyntaxError ? error : new SyntaxError(String(error)));
  }
}

/**
 * Safely stringify to JSON
 * تحويل إلى JSON بشكل آمن
 *
 * @param value - القيمة - Value to stringify
 * @param replacer - المُستبدل - Optional replacer
 * @param space - المسافة - Optional indentation
 * @returns النتيجة - Result with JSON string or error
 */
export function safeJsonStringify(
  value: unknown,
  replacer?: (key: string, value: unknown) => unknown,
  space?: string | number,
): Result<string, TypeError> {
  try {
    const json = JSON.stringify(value, replacer, space);
    if (json === undefined) {
      return err(new TypeError("Value cannot be converted to JSON"));
    }
    return ok(json);
  } catch (error) {
    return err(error instanceof TypeError ? error : new TypeError(String(error)));
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Safe Number Parsing
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Parse error for number parsing
 * خطأ التحليل للأرقام
 */
export class ParseNumberError extends Error {
  constructor(
    message: string,
    public readonly input: string,
  ) {
    super(message);
    this.name = "ParseNumberError";
  }
}

/**
 * Safely parse integer
 * تحليل عدد صحيح بشكل آمن
 *
 * @param text - النص - String to parse
 * @param radix - الأساس - Radix (default: 10)
 * @returns النتيجة - Result with integer or error
 */
export function safeParseInt(
  text: string,
  radix: number = 10,
): Result<number, ParseNumberError> {
  const trimmed = text.trim();

  if (trimmed === "") {
    return err(new ParseNumberError("Cannot parse empty string as integer", text));
  }

  const parsed = parseInt(trimmed, radix);

  if (Number.isNaN(parsed)) {
    return err(new ParseNumberError(`Cannot parse "${text}" as integer`, text));
  }

  return ok(parsed);
}

/**
 * Safely parse float
 * تحليل عدد عشري بشكل آمن
 *
 * @param text - النص - String to parse
 * @returns النتيجة - Result with float or error
 */
export function safeParseFloat(text: string): Result<number, ParseNumberError> {
  const trimmed = text.trim();

  if (trimmed === "") {
    return err(new ParseNumberError("Cannot parse empty string as float", text));
  }

  const parsed = parseFloat(trimmed);

  if (Number.isNaN(parsed)) {
    return err(new ParseNumberError(`Cannot parse "${text}" as float`, text));
  }

  if (!Number.isFinite(parsed)) {
    return err(new ParseNumberError(`"${text}" is not a finite number`, text));
  }

  return ok(parsed);
}

/**
 * Parse number with validation
 * تحليل رقم مع التحقق
 *
 * @param value - القيمة - Value to parse
 * @param options - الخيارات - Parse options
 * @returns النتيجة - Result with number or error
 */
export function safeParseNumber(
  value: unknown,
  options: {
    min?: number;
    max?: number;
    integer?: boolean;
    positive?: boolean;
    nonZero?: boolean;
  } = {},
): Result<number, Error> {
  const { min, max, integer, positive, nonZero } = options;

  let num: number;

  if (typeof value === "number") {
    num = value;
  } else if (typeof value === "string") {
    const result = safeParseFloat(value);
    if (!result.success) {
      return result;
    }
    num = result.value;
  } else {
    return err(new Error(`Cannot parse ${typeof value} as number`));
  }

  if (Number.isNaN(num)) {
    return err(new Error("Value is NaN"));
  }

  if (!Number.isFinite(num)) {
    return err(new Error("Value is not finite"));
  }

  if (integer && !Number.isInteger(num)) {
    return err(new Error(`${num} is not an integer`));
  }

  if (positive && num < 0) {
    return err(new Error(`${num} is not positive`));
  }

  if (nonZero && num === 0) {
    return err(new Error("Value cannot be zero"));
  }

  if (min !== undefined && num < min) {
    return err(new Error(`${num} is less than minimum ${min}`));
  }

  if (max !== undefined && num > max) {
    return err(new Error(`${num} is greater than maximum ${max}`));
  }

  return ok(num);
}

// ─────────────────────────────────────────────────────────────────────────────
// Safe Date Parsing
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Parse date error
 * خطأ تحليل التاريخ
 */
export class ParseDateError extends Error {
  constructor(
    message: string,
    public readonly input: string | number | Date,
  ) {
    super(message);
    this.name = "ParseDateError";
  }
}

/**
 * Safely parse date
 * تحليل تاريخ بشكل آمن
 *
 * @param value - القيمة - Value to parse as date
 * @returns النتيجة - Result with Date or error
 */
export function safeParseDate(
  value: string | number | Date,
): Result<Date, ParseDateError> {
  if (value instanceof Date) {
    if (Number.isNaN(value.getTime())) {
      return err(new ParseDateError("Invalid Date object", value));
    }
    return ok(value);
  }

  if (typeof value === "string" && value.trim() === "") {
    return err(new ParseDateError("Cannot parse empty string as date", value));
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return err(new ParseDateError(`Cannot parse "${value}" as date`, value));
  }

  return ok(date);
}

/**
 * Safely parse ISO date string
 * تحليل تاريخ ISO بشكل آمن
 *
 * @param text - النص - ISO date string
 * @returns النتيجة - Result with Date or error
 */
export function safeParseISODate(text: string): Result<Date, ParseDateError> {
  // Basic ISO 8601 pattern validation
  const isoPattern = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2})?)?$/;

  if (!isoPattern.test(text)) {
    return err(new ParseDateError(`"${text}" is not a valid ISO date format`, text));
  }

  return safeParseDate(text);
}

// ─────────────────────────────────────────────────────────────────────────────
// Safe URL Parsing
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Safely parse URL
 * تحليل رابط بشكل آمن
 *
 * @param text - النص - URL string to parse
 * @param base - القاعدة - Optional base URL
 * @returns النتيجة - Result with URL or error
 */
export function safeParseURL(
  text: string,
  base?: string | URL,
): Result<URL, TypeError> {
  try {
    const url = new URL(text, base);
    return ok(url);
  } catch (error) {
    return err(error instanceof TypeError ? error : new TypeError(String(error)));
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Safe Boolean Parsing
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Safely parse boolean from various representations
 * تحليل قيمة منطقية من تمثيلات مختلفة
 *
 * @param value - القيمة - Value to parse
 * @returns النتيجة - Result with boolean or error
 */
export function safeParseBoolean(value: unknown): Result<boolean, Error> {
  if (typeof value === "boolean") {
    return ok(value);
  }

  if (typeof value === "number") {
    if (value === 1) return ok(true);
    if (value === 0) return ok(false);
    return err(new Error(`Cannot parse number ${value} as boolean`));
  }

  if (typeof value === "string") {
    const normalized = value.toLowerCase().trim();

    // True values
    if (["true", "1", "yes", "on", "y", "نعم"].includes(normalized)) {
      return ok(true);
    }

    // False values
    if (["false", "0", "no", "off", "n", "لا"].includes(normalized)) {
      return ok(false);
    }

    return err(new Error(`Cannot parse string "${value}" as boolean`));
  }

  return err(new Error(`Cannot parse ${typeof value} as boolean`));
}

// ─────────────────────────────────────────────────────────────────────────────
// Try-Catch Wrapper
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Wrap a function to return Result instead of throwing
 * تغليف دالة لإرجاع Result بدلاً من إلقاء استثناء
 *
 * @param fn - الدالة - Function to wrap
 * @returns دالة مغلفة - Wrapped function returning Result
 */
export function tryCatch<T, Args extends unknown[]>(
  fn: (...args: Args) => T,
): (...args: Args) => Result<T, Error> {
  return (...args: Args): Result<T, Error> => {
    try {
      return ok(fn(...args));
    } catch (error) {
      return err(error instanceof Error ? error : new Error(String(error)));
    }
  };
}

/**
 * Wrap an async function to return Result instead of throwing
 * تغليف دالة غير متزامنة لإرجاع Result بدلاً من إلقاء استثناء
 *
 * @param fn - الدالة - Async function to wrap
 * @returns دالة مغلفة - Wrapped async function returning Result
 */
export function tryCatchAsync<T, Args extends unknown[]>(
  fn: (...args: Args) => Promise<T>,
): (...args: Args) => Promise<Result<T, Error>> {
  return async (...args: Args): Promise<Result<T, Error>> => {
    try {
      const value = await fn(...args);
      return ok(value);
    } catch (error) {
      return err(error instanceof Error ? error : new Error(String(error)));
    }
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Validation Pipeline
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validator function type
 * نوع دالة التحقق
 */
export type Validator<T, E = Error> = (value: T) => Result<T, E> | true | string;

/**
 * Run validation pipeline
 * تشغيل خط أنابيب التحقق
 *
 * @param value - القيمة - Value to validate
 * @param validators - المُتحققون - Array of validator functions
 * @returns النتيجة - Result with validated value or first error
 */
export function validate<T>(
  value: T,
  validators: Array<Validator<T>>,
): Result<T, Error> {
  for (const validator of validators) {
    const result = validator(value);

    if (result === true) {
      continue;
    }

    if (typeof result === "string") {
      return err(new Error(result));
    }

    if (!result.success) {
      return result;
    }
  }

  return ok(value);
}

/**
 * Create a validator that checks a condition
 * إنشاء مُتحقق يفحص شرطاً
 */
export function createValidator<T>(
  predicate: (value: T) => boolean,
  errorMessage: string,
): Validator<T> {
  return (value: T) => (predicate(value) ? true : errorMessage);
}

// ─────────────────────────────────────────────────────────────────────────────
// Common Validators
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Validator: value is not null or undefined
 * مُتحقق: القيمة ليست null أو undefined
 */
export const required: Validator<unknown> = (value) =>
  value !== null && value !== undefined ? true : "Value is required";

/**
 * Validator: string is not empty
 * مُتحقق: النص ليس فارغاً
 */
export const notEmpty: Validator<string> = (value) =>
  value.trim().length > 0 ? true : "Value cannot be empty";

/**
 * Create min length validator
 * إنشاء مُتحقق الحد الأدنى للطول
 */
export function minLength(min: number): Validator<string> {
  return (value) =>
    value.length >= min ? true : `Value must be at least ${min} characters`;
}

/**
 * Create max length validator
 * إنشاء مُتحقق الحد الأقصى للطول
 */
export function maxLength(max: number): Validator<string> {
  return (value) =>
    value.length <= max ? true : `Value must be at most ${max} characters`;
}

/**
 * Create min value validator
 * إنشاء مُتحقق الحد الأدنى للقيمة
 */
export function minValue(min: number): Validator<number> {
  return (value) => (value >= min ? true : `Value must be at least ${min}`);
}

/**
 * Create max value validator
 * إنشاء مُتحقق الحد الأقصى للقيمة
 */
export function maxValue(max: number): Validator<number> {
  return (value) => (value <= max ? true : `Value must be at most ${max}`);
}

/**
 * Create pattern validator
 * إنشاء مُتحقق النمط
 */
export function pattern(regex: RegExp, message?: string): Validator<string> {
  return (value) => (regex.test(value) ? true : message || "Value does not match pattern");
}
