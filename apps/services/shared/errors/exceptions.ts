/**
 * Custom Exception Classes
 * فئات الاستثناءات المخصصة
 *
 * @module shared/errors
 * @description Custom exception classes with bilingual support
 */

import { HttpException, HttpStatus } from '@nestjs/common';
import { ErrorCode, ERROR_REGISTRY } from './error-codes';

/**
 * Base Application Exception
 * الاستثناء الأساسي للتطبيق
 */
export class AppException extends HttpException {
  public readonly errorCode: ErrorCode;
  public readonly messageEn: string;
  public readonly messageAr: string;
  public readonly retryable: boolean;
  public readonly details?: any;
  public readonly timestamp: string;
  public readonly path?: string;

  constructor(
    errorCode: ErrorCode,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    const metadata = ERROR_REGISTRY[errorCode];
    const messageEn = customMessage?.en || metadata.message.en;
    const messageAr = customMessage?.ar || metadata.message.ar;

    super(
      {
        errorCode,
        message: messageEn,
        messageAr,
        details,
        timestamp: new Date().toISOString(),
      },
      metadata.httpStatus,
    );

    this.errorCode = errorCode;
    this.messageEn = messageEn;
    this.messageAr = messageAr;
    this.retryable = metadata.retryable;
    this.details = details;
    this.timestamp = new Date().toISOString();

    // Set prototype explicitly for instanceof checks
    Object.setPrototypeOf(this, AppException.prototype);
  }

  /**
   * Get error response object
   * الحصول على كائن استجابة الخطأ
   */
  toJSON() {
    return {
      success: false,
      error: {
        code: this.errorCode,
        message: this.messageEn,
        messageAr: this.messageAr,
        retryable: this.retryable,
        details: this.details,
        timestamp: this.timestamp,
        path: this.path,
      },
    };
  }
}

/**
 * Validation Exception
 * استثناء التحقق من صحة البيانات
 */
export class ValidationException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.VALIDATION_ERROR,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, ValidationException.prototype);
  }

  /**
   * Create validation exception from field errors
   * إنشاء استثناء التحقق من أخطاء الحقول
   */
  static fromFieldErrors(
    fieldErrors: Array<{ field: string; message: string; messageAr?: string }>,
  ): ValidationException {
    return new ValidationException(ErrorCode.VALIDATION_ERROR, undefined, {
      fields: fieldErrors,
    });
  }
}

/**
 * Authentication Exception
 * استثناء المصادقة
 */
export class AuthenticationException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.AUTHENTICATION_FAILED,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, AuthenticationException.prototype);
  }
}

/**
 * Authorization Exception
 * استثناء التفويض
 */
export class AuthorizationException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.FORBIDDEN,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, AuthorizationException.prototype);
  }
}

/**
 * Not Found Exception
 * استثناء عدم العثور على المورد
 */
export class NotFoundException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.RESOURCE_NOT_FOUND,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, NotFoundException.prototype);
  }

  /**
   * Create exception for specific resource types
   * إنشاء استثناء لأنواع موارد محددة
   */
  static user(userId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.USER_NOT_FOUND, undefined, { userId });
  }

  static farm(farmId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.FARM_NOT_FOUND, undefined, { farmId });
  }

  static field(fieldId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.FIELD_NOT_FOUND, undefined, { fieldId });
  }

  static crop(cropId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.CROP_NOT_FOUND, undefined, { cropId });
  }

  static sensor(sensorId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.SENSOR_NOT_FOUND, undefined, { sensorId });
  }

  static conversation(conversationId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.CONVERSATION_NOT_FOUND, undefined, {
      conversationId,
    });
  }

  static message(messageId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.MESSAGE_NOT_FOUND, undefined, {
      messageId,
    });
  }

  static wallet(walletId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.WALLET_NOT_FOUND, undefined, {
      walletId,
    });
  }

  static order(orderId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.ORDER_NOT_FOUND, undefined, { orderId });
  }

  static product(productId?: string): NotFoundException {
    return new NotFoundException(ErrorCode.PRODUCT_NOT_FOUND, undefined, {
      productId,
    });
  }
}

/**
 * Conflict Exception
 * استثناء التعارض
 */
export class ConflictException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.RESOURCE_ALREADY_EXISTS,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, ConflictException.prototype);
  }
}

/**
 * Business Logic Exception
 * استثناء منطق الأعمال
 */
export class BusinessLogicException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.BUSINESS_RULE_VIOLATION,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, BusinessLogicException.prototype);
  }

  /**
   * Create exception for specific business rules
   * إنشاء استثناء لقواعد عمل محددة
   */
  static insufficientBalance(
    available: number,
    required: number,
  ): BusinessLogicException {
    return new BusinessLogicException(ErrorCode.INSUFFICIENT_BALANCE, undefined, {
      available,
      required,
    });
  }

  static amountMustBePositive(amount: number): BusinessLogicException {
    return new BusinessLogicException(ErrorCode.AMOUNT_MUST_BE_POSITIVE, undefined, {
      amount,
    });
  }

  static invalidStateTransition(
    currentState: string,
    targetState: string,
  ): BusinessLogicException {
    return new BusinessLogicException(
      ErrorCode.INVALID_STATE_TRANSITION,
      undefined,
      {
        currentState,
        targetState,
      },
    );
  }

  static operationNotAllowed(
    operation: string,
    reason?: string,
  ): BusinessLogicException {
    return new BusinessLogicException(ErrorCode.OPERATION_NOT_ALLOWED, undefined, {
      operation,
      reason,
    });
  }
}

/**
 * External Service Exception
 * استثناء الخدمة الخارجية
 */
export class ExternalServiceException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.EXTERNAL_SERVICE_ERROR,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, ExternalServiceException.prototype);
  }

  /**
   * Create exception for specific external services
   * إنشاء استثناء لخدمات خارجية محددة
   */
  static weatherService(error?: any): ExternalServiceException {
    return new ExternalServiceException(
      ErrorCode.WEATHER_SERVICE_UNAVAILABLE,
      undefined,
      { originalError: error },
    );
  }

  static satelliteService(error?: any): ExternalServiceException {
    return new ExternalServiceException(
      ErrorCode.SATELLITE_SERVICE_UNAVAILABLE,
      undefined,
      { originalError: error },
    );
  }

  static paymentGateway(error?: any): ExternalServiceException {
    return new ExternalServiceException(
      ErrorCode.PAYMENT_GATEWAY_ERROR,
      undefined,
      { originalError: error },
    );
  }

  static smsService(error?: any): ExternalServiceException {
    return new ExternalServiceException(ErrorCode.SMS_SERVICE_ERROR, undefined, {
      originalError: error,
    });
  }

  static emailService(error?: any): ExternalServiceException {
    return new ExternalServiceException(ErrorCode.EMAIL_SERVICE_ERROR, undefined, {
      originalError: error,
    });
  }
}

/**
 * Database Exception
 * استثناء قاعدة البيانات
 */
export class DatabaseException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.DATABASE_ERROR,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, DatabaseException.prototype);
  }

  /**
   * Create exception from Prisma/TypeORM error
   * إنشاء استثناء من خطأ Prisma/TypeORM
   */
  static fromDatabaseError(error: any): DatabaseException {
    // Prisma error codes
    if (error.code === 'P2002') {
      return new DatabaseException(ErrorCode.UNIQUE_CONSTRAINT_VIOLATION, undefined, {
        fields: error.meta?.target,
      });
    }
    if (error.code === 'P2003') {
      return new DatabaseException(ErrorCode.FOREIGN_KEY_VIOLATION, undefined, {
        field: error.meta?.field_name,
      });
    }
    if (error.code === 'P2025') {
      return new DatabaseException(ErrorCode.RESOURCE_NOT_FOUND, undefined, {
        cause: error.meta?.cause,
      });
    }

    // Generic database error
    return new DatabaseException(ErrorCode.DATABASE_ERROR, undefined, {
      originalError: error.message,
    });
  }
}

/**
 * Internal Server Exception
 * استثناء الخادم الداخلي
 */
export class InternalServerException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, InternalServerException.prototype);
  }
}

/**
 * Rate Limit Exception
 * استثناء تجاوز الحد المسموح
 */
export class RateLimitException extends AppException {
  constructor(
    errorCode: ErrorCode = ErrorCode.RATE_LIMIT_EXCEEDED,
    customMessage?: { en?: string; ar?: string },
    details?: any,
  ) {
    super(errorCode, customMessage, details);
    Object.setPrototypeOf(this, RateLimitException.prototype);
  }

  /**
   * Create exception with retry information
   * إنشاء استثناء مع معلومات إعادة المحاولة
   */
  static withRetryAfter(retryAfterSeconds: number): RateLimitException {
    return new RateLimitException(ErrorCode.RATE_LIMIT_EXCEEDED, undefined, {
      retryAfter: retryAfterSeconds,
      retryAfterDate: new Date(
        Date.now() + retryAfterSeconds * 1000,
      ).toISOString(),
    });
  }
}
