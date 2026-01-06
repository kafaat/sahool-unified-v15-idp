/**
 * Validation Error Responses
 * استجابات أخطاء التحقق
 *
 * @module shared/validation
 * @description Standardized validation error responses
 */

import { BadRequestException, HttpException, HttpStatus } from '@nestjs/common';
import { ValidationError } from 'class-validator';

// ═══════════════════════════════════════════════════════════════════════════
// Error Response DTOs
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Field-level validation error
 */
export interface ValidationFieldError {
  /**
   * Field name
   */
  field: string;

  /**
   * Error message in English
   */
  message: string;

  /**
   * Error message in Arabic
   */
  messageAr?: string;

  /**
   * Constraint that failed
   */
  constraint?: string;

  /**
   * Invalid value (sanitized)
   */
  value?: any;

  /**
   * Additional context
   */
  context?: Record<string, any>;
}

/**
 * Validation error response
 */
export class ValidationErrorResponse {
  /**
   * Error type
   */
  readonly error: string = 'ValidationError';

  /**
   * HTTP status code
   */
  readonly statusCode: number = HttpStatus.BAD_REQUEST;

  /**
   * Overall error message
   */
  readonly message: string;

  /**
   * Overall error message in Arabic
   */
  readonly messageAr: string;

  /**
   * Array of field-level errors
   */
  readonly errors: ValidationFieldError[];

  /**
   * Request path
   */
  readonly path?: string;

  /**
   * Timestamp
   */
  readonly timestamp: string;

  /**
   * Request ID
   */
  readonly requestId?: string;

  constructor(
    errors: ValidationFieldError[],
    message?: string,
    messageAr?: string,
    path?: string,
    requestId?: string,
  ) {
    this.message = message || 'Validation failed';
    this.messageAr = messageAr || 'فشل التحقق من صحة البيانات';
    this.errors = errors;
    this.path = path;
    this.timestamp = new Date().toISOString();
    this.requestId = requestId;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Formatters
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Format class-validator errors into standardized format
 *
 * @param validationErrors - Array of ValidationError from class-validator
 * @returns Array of ValidationFieldError
 */
export function formatValidationErrors(
  validationErrors: ValidationError[],
): ValidationFieldError[] {
  const errors: ValidationFieldError[] = [];

  for (const error of validationErrors) {
    // Handle nested errors
    if (error.children && error.children.length > 0) {
      const nestedErrors = formatValidationErrors(error.children);
      for (const nestedError of nestedErrors) {
        errors.push({
          ...nestedError,
          field: `${error.property}.${nestedError.field}`,
        });
      }
      continue;
    }

    // Handle constraints
    if (error.constraints) {
      const constraintKeys = Object.keys(error.constraints);
      const constraint = constraintKeys[0];
      const message = error.constraints[constraint];

      errors.push({
        field: error.property,
        message: message,
        messageAr: getArabicErrorMessage(constraint, error.property),
        constraint: constraint,
        value: sanitizeErrorValue(error.value),
        context: error.contexts?.[constraint],
      });
    }
  }

  return errors;
}

/**
 * Sanitize error value for safe display
 * Prevents leaking sensitive data in error messages
 *
 * @param value - Original value
 * @returns Sanitized value
 */
function sanitizeErrorValue(value: any): any {
  // Don't include passwords or tokens in errors
  if (value === null || value === undefined) {
    return value;
  }

  // Redact long strings (potential secrets)
  if (typeof value === 'string' && value.length > 50) {
    return `${value.substring(0, 20)}...[REDACTED]`;
  }

  // Redact objects (potential sensitive data)
  if (typeof value === 'object' && value !== null) {
    return '[OBJECT]';
  }

  // Redact arrays
  if (Array.isArray(value)) {
    return `[ARRAY of ${value.length} items]`;
  }

  return value;
}

/**
 * Get Arabic error message for constraint
 *
 * @param constraint - Constraint name
 * @param field - Field name
 * @returns Arabic error message
 */
function getArabicErrorMessage(constraint: string, field: string): string {
  const arabicMessages: Record<string, string> = {
    // String validators
    isString: `يجب أن يكون ${field} نص`,
    isNotEmpty: `${field} مطلوب`,
    minLength: `${field} قصير جداً`,
    maxLength: `${field} طويل جداً`,
    matches: `${field} لا يطابق النمط المطلوب`,

    // Number validators
    isNumber: `يجب أن يكون ${field} رقماً`,
    isInt: `يجب أن يكون ${field} رقماً صحيحاً`,
    min: `${field} صغير جداً`,
    max: `${field} كبير جداً`,
    isPositive: `يجب أن يكون ${field} موجباً`,

    // Email/Phone
    isEmail: `عنوان البريد الإلكتروني غير صالح`,
    isPhoneNumber: `رقم الهاتف غير صالح`,
    isYemeniPhone: `رقم الهاتف اليمني غير صالح`,

    // Date validators
    isDateString: `يجب أن يكون ${field} تاريخاً صالحاً`,
    isISO8601: `يجب أن يكون ${field} تاريخاً بصيغة ISO 8601`,
    isFutureDate: `يجب أن يكون ${field} تاريخاً مستقبلياً`,
    isAfterDate: `يجب أن يكون ${field} بعد التاريخ المحدد`,

    // Boolean
    isBoolean: `يجب أن يكون ${field} قيمة منطقية (true/false)`,

    // Enum
    isEnum: `${field} يجب أن يكون من القيم المسموح بها`,

    // URL
    isUrl: `يجب أن يكون ${field} رابطاً صالحاً`,

    // Array
    isArray: `يجب أن يكون ${field} مصفوفة`,
    arrayMinSize: `${field} يجب أن يحتوي على عناصر كافية`,
    arrayMaxSize: `${field} يحتوي على عناصر كثيرة`,

    // Object
    isObject: `يجب أن يكون ${field} كائناً`,
    validateNested: `${field} يحتوي على بيانات غير صالحة`,

    // UUID
    isUUID: `يجب أن يكون ${field} معرفاً فريداً صالحاً`,

    // Custom
    containsArabic: `يجب أن يحتوي ${field} على أحرف عربية`,
    isArabicOnly: `يجب أن يحتوي ${field} على أحرف عربية فقط`,
    isWithinYemen: `يجب أن تكون الإحداثيات داخل اليمن`,
    isStrongPassword: `كلمة المرور ضعيفة - يجب أن تحتوي على أحرف كبيرة وصغيرة وأرقام ورموز خاصة`,
    isGeoJSONPolygon: `يجب أن يكون ${field} مضلعاً صالحاً بصيغة GeoJSON`,
    isValidFieldArea: `مساحة الحقل يجب أن تكون ضمن النطاق المسموح به`,
    isMoneyValue: `${field} يجب أن يكون قيمة نقدية صالحة`,
    isCreditCard: `رقم البطاقة الائتمانية غير صالح`,
    isEAN13: `الباركود غير صالح`,
  };

  return arabicMessages[constraint] || `${field} غير صالح`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Exception Classes
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Custom validation exception
 */
export class ValidationException extends BadRequestException {
  constructor(
    errors: ValidationFieldError[],
    message?: string,
    messageAr?: string,
  ) {
    const response = new ValidationErrorResponse(
      errors,
      message,
      messageAr,
    );
    super(response);
  }
}

/**
 * Business rule validation exception
 */
export class BusinessRuleException extends HttpException {
  constructor(
    rule: string,
    message: string,
    messageAr?: string,
    context?: Record<string, any>,
  ) {
    const response = {
      error: 'BusinessRuleViolation',
      statusCode: HttpStatus.UNPROCESSABLE_ENTITY,
      message,
      messageAr: messageAr || message,
      rule,
      context,
      timestamp: new Date().toISOString(),
    };
    super(response, HttpStatus.UNPROCESSABLE_ENTITY);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Validation Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create validation exception from class-validator errors
 *
 * @param validationErrors - Array of ValidationError
 * @param message - Optional custom message
 * @param messageAr - Optional custom Arabic message
 * @returns ValidationException
 */
export function createValidationException(
  validationErrors: ValidationError[],
  message?: string,
  messageAr?: string,
): ValidationException {
  const errors = formatValidationErrors(validationErrors);
  return new ValidationException(errors, message, messageAr);
}

/**
 * Validate business rule and throw exception if failed
 *
 * @param condition - Condition to check
 * @param rule - Rule name
 * @param message - Error message
 * @param messageAr - Arabic error message
 * @param context - Additional context
 */
export function assertBusinessRule(
  condition: boolean,
  rule: string,
  message: string,
  messageAr?: string,
  context?: Record<string, any>,
): void {
  if (!condition) {
    throw new BusinessRuleException(rule, message, messageAr, context);
  }
}

/**
 * Common business rule validators
 */
export const BusinessRules = {
  /**
   * Validate date range (end date must be after start date)
   */
  validateDateRange(
    startDate: Date,
    endDate: Date,
    fieldName: string = 'Date range',
  ): void {
    assertBusinessRule(
      endDate > startDate,
      'INVALID_DATE_RANGE',
      `${fieldName}: End date must be after start date`,
      `${fieldName}: يجب أن يكون تاريخ الانتهاء بعد تاريخ البداية`,
      { startDate, endDate },
    );
  },

  /**
   * Validate future date
   */
  validateFutureDate(date: Date, fieldName: string = 'Date'): void {
    assertBusinessRule(
      date > new Date(),
      'DATE_MUST_BE_FUTURE',
      `${fieldName} must be in the future`,
      `${fieldName} يجب أن يكون في المستقبل`,
      { date },
    );
  },

  /**
   * Validate positive amount
   */
  validatePositiveAmount(
    amount: number,
    fieldName: string = 'Amount',
  ): void {
    assertBusinessRule(
      amount > 0,
      'AMOUNT_MUST_BE_POSITIVE',
      `${fieldName} must be positive`,
      `${fieldName} يجب أن يكون موجباً`,
      { amount },
    );
  },

  /**
   * Validate stock availability
   */
  validateStockAvailability(
    available: number,
    requested: number,
    productName?: string,
  ): void {
    assertBusinessRule(
      available >= requested,
      'INSUFFICIENT_STOCK',
      `Insufficient stock${productName ? ` for ${productName}` : ''}. Available: ${available}, Requested: ${requested}`,
      `مخزون غير كافٍ${productName ? ` لـ ${productName}` : ''}. المتاح: ${available}، المطلوب: ${requested}`,
      { available, requested, productName },
    );
  },

  /**
   * Validate credit limit
   */
  validateCreditLimit(
    currentBalance: number,
    transactionAmount: number,
    creditLimit: number,
  ): void {
    const newBalance = currentBalance + transactionAmount;
    assertBusinessRule(
      newBalance <= creditLimit,
      'CREDIT_LIMIT_EXCEEDED',
      `Transaction would exceed credit limit. Current: ${currentBalance}, Transaction: ${transactionAmount}, Limit: ${creditLimit}`,
      `ستتجاوز المعاملة حد الائتمان. الرصيد الحالي: ${currentBalance}، المعاملة: ${transactionAmount}، الحد: ${creditLimit}`,
      { currentBalance, transactionAmount, creditLimit, newBalance },
    );
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Export all validation error utilities
// ═══════════════════════════════════════════════════════════════════════════

export const VALIDATION_ERROR_UTILITIES = {
  ValidationErrorResponse,
  ValidationException,
  BusinessRuleException,
  formatValidationErrors,
  createValidationException,
  assertBusinessRule,
  BusinessRules,
};
