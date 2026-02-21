/**
 * HTTP Exception Filter - Unified Error Handling for Marketplace Service
 *
 * Features:
 * - Bilingual error messages (Arabic/English)
 * - Structured error response format
 * - Request ID tracking
 * - Error logging with context
 * - Prisma error handling
 */

import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
  Logger,
} from "@nestjs/common";
import { Request, Response } from "express";
import { Prisma } from "@prisma/client";

// Bilingual error messages
const ERROR_MESSAGES: Record<number, { en: string; ar: string }> = {
  400: { en: "Bad Request", ar: "طلب غير صالح" },
  401: { en: "Unauthorized", ar: "غير مصرح" },
  403: { en: "Forbidden", ar: "محظور" },
  404: { en: "Not Found", ar: "غير موجود" },
  409: { en: "Conflict", ar: "تعارض" },
  422: { en: "Unprocessable Entity", ar: "كيان غير قابل للمعالجة" },
  429: { en: "Too Many Requests", ar: "طلبات كثيرة جداً" },
  500: { en: "Internal Server Error", ar: "خطأ داخلي في الخادم" },
  503: { en: "Service Unavailable", ar: "الخدمة غير متاحة" },
};

// Business-specific error codes
const BUSINESS_ERROR_CODES: Record<string, { en: string; ar: string }> = {
  INSUFFICIENT_BALANCE: { en: "Insufficient balance", ar: "الرصيد غير كافي" },
  PRODUCT_OUT_OF_STOCK: { en: "Product out of stock", ar: "المنتج غير متوفر" },
  WALLET_NOT_FOUND: { en: "Wallet not found", ar: "المحفظة غير موجودة" },
  ORDER_NOT_FOUND: { en: "Order not found", ar: "الطلب غير موجود" },
  PRODUCT_NOT_FOUND: { en: "Product not found", ar: "المنتج غير موجود" },
  LOAN_LIMIT_EXCEEDED: { en: "Loan limit exceeded", ar: "تم تجاوز حد القرض" },
  DAILY_LIMIT_EXCEEDED: { en: "Daily limit exceeded", ar: "تم تجاوز الحد اليومي" },
  ESCROW_NOT_FOUND: { en: "Escrow not found", ar: "الضمان غير موجود" },
  CREDIT_SCORE_TOO_LOW: { en: "Credit score too low", ar: "التصنيف الائتماني منخفض جداً" },
};

interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    messageAr: string;
    details?: any;
    validationErrors?: Array<{
      field: string;
      message: string;
      messageAr?: string;
    }>;
  };
  requestId?: string;
  timestamp: string;
}

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const request = ctx.getRequest<Request>();
    const response = ctx.getResponse<Response>();

    const requestId =
      (request.headers["x-request-id"] as string) || this.generateRequestId();

    let status: number = HttpStatus.INTERNAL_SERVER_ERROR;
    let errorCode: string = "";
    let message: string = "An unexpected error occurred";
    let messageAr: string = "حدث خطأ غير متوقع";
    let details: any = undefined;
    let validationErrors: any[] | undefined = undefined;

    // Handle different exception types
    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === "string") {
        message = exceptionResponse;
        messageAr = this.translateMessage(exceptionResponse, status);
      } else if (typeof exceptionResponse === "object") {
        const resp = exceptionResponse as any;

        // Handle validation errors from class-validator
        if (Array.isArray(resp.message)) {
          message = "Validation failed";
          messageAr = "فشل التحقق من الصحة";
          validationErrors = resp.message.map((msg: string) => ({
            field: this.extractFieldFromMessage(msg),
            message: msg,
            messageAr: this.translateValidationMessage(msg),
          }));
        } else {
          message = resp.message || resp.error || "Unknown error";
          messageAr = resp.messageAr || this.translateMessage(message, status);
          details = resp.details;
          errorCode = resp.code;
        }
      }
    } else if (this.isPrismaError(exception)) {
      const prismaError = this.handlePrismaError(exception);
      status = prismaError.status;
      errorCode = prismaError.code;
      message = prismaError.message;
      messageAr = prismaError.messageAr;
      details = prismaError.details;
    } else if (exception instanceof Error) {
      // Check for business-specific errors
      const businessError = this.checkBusinessError(exception.message);
      if (businessError) {
        status = HttpStatus.BAD_REQUEST;
        errorCode = businessError.code;
        message = businessError.en;
        messageAr = businessError.ar;
      } else {
        status = HttpStatus.INTERNAL_SERVER_ERROR;
        message = exception.message;
        messageAr = "خطأ داخلي في الخادم";
      }
    } else {
      status = HttpStatus.INTERNAL_SERVER_ERROR;
      message = "An unexpected error occurred";
      messageAr = "حدث خطأ غير متوقع";
    }

    // Default error code
    if (!errorCode) {
      errorCode = `ERR_${status}`;
    }

    // Log the error
    const logContext = {
      requestId,
      method: request.method,
      url: request.url,
      status,
      errorCode,
      userId: (request as any).user?.id,
    };

    if (status >= 500) {
      this.logger.error(
        `[${requestId}] ${request.method} ${request.url} - ${status} - ${message}`,
        exception instanceof Error ? exception.stack : undefined,
        logContext,
      );
    } else {
      this.logger.warn(
        `[${requestId}] ${request.method} ${request.url} - ${status} - ${message}`,
        logContext,
      );
    }

    // Build response
    const errorResponse: ErrorResponse = {
      success: false,
      error: {
        code: errorCode,
        message,
        messageAr,
        ...(details && { details }),
        ...(validationErrors && { validationErrors }),
      },
      requestId,
      timestamp: new Date().toISOString(),
    };

    response.status(status).json(errorResponse);
  }

  /**
   * Check if error is a Prisma error
   */
  private isPrismaError(error: unknown): boolean {
    return (
      error instanceof Prisma.PrismaClientKnownRequestError ||
      error instanceof Prisma.PrismaClientUnknownRequestError ||
      error instanceof Prisma.PrismaClientValidationError
    );
  }

  /**
   * Handle Prisma-specific errors
   */
  private handlePrismaError(error: unknown): {
    status: number;
    code: string;
    message: string;
    messageAr: string;
    details?: any;
  } {
    if (error instanceof Prisma.PrismaClientKnownRequestError) {
      switch (error.code) {
        case "P2002":
          return {
            status: HttpStatus.CONFLICT,
            code: "UNIQUE_CONSTRAINT_VIOLATION",
            message: "A record with this value already exists",
            messageAr: "يوجد سجل بهذه القيمة بالفعل",
            details: { field: error.meta?.target },
          };

        case "P2025":
          return {
            status: HttpStatus.NOT_FOUND,
            code: "RECORD_NOT_FOUND",
            message: "Record not found",
            messageAr: "السجل غير موجود",
          };

        case "P2003":
          return {
            status: HttpStatus.BAD_REQUEST,
            code: "FOREIGN_KEY_CONSTRAINT",
            message: "Related record not found",
            messageAr: "السجل المرتبط غير موجود",
            details: { field: error.meta?.field_name },
          };

        case "P2014":
          return {
            status: HttpStatus.BAD_REQUEST,
            code: "RELATION_VIOLATION",
            message: "The change you are trying to make would violate a relation",
            messageAr: "التغيير الذي تحاول إجراءه سينتهك علاقة",
          };

        default:
          return {
            status: HttpStatus.INTERNAL_SERVER_ERROR,
            code: `PRISMA_${error.code}`,
            message: "Database error occurred",
            messageAr: "حدث خطأ في قاعدة البيانات",
          };
      }
    }

    if (error instanceof Prisma.PrismaClientValidationError) {
      return {
        status: HttpStatus.BAD_REQUEST,
        code: "VALIDATION_ERROR",
        message: "Invalid data provided",
        messageAr: "البيانات المقدمة غير صالحة",
      };
    }

    return {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      code: "DATABASE_ERROR",
      message: "Database error occurred",
      messageAr: "حدث خطأ في قاعدة البيانات",
    };
  }

  /**
   * Check for business-specific errors in message
   */
  private checkBusinessError(
    message: string,
  ): { code: string; en: string; ar: string } | null {
    const lowerMessage = message.toLowerCase();

    for (const [code, translations] of Object.entries(BUSINESS_ERROR_CODES)) {
      if (
        lowerMessage.includes(code.toLowerCase().replace(/_/g, " ")) ||
        lowerMessage.includes(translations.en.toLowerCase()) ||
        message.includes(translations.ar)
      ) {
        return { code, ...translations };
      }
    }

    return null;
  }

  /**
   * Translate error message to Arabic
   */
  private translateMessage(message: string, status: number): string {
    // Check for business error translations
    const lowerMessage = message.toLowerCase();

    for (const translations of Object.values(BUSINESS_ERROR_CODES)) {
      if (lowerMessage.includes(translations.en.toLowerCase())) {
        return translations.ar;
      }
    }

    return ERROR_MESSAGES[status]?.ar || "خطأ غير معروف";
  }

  /**
   * Translate validation error message
   */
  private translateValidationMessage(message: string): string {
    // Common validation translations
    const translations: Record<string, string> = {
      "must be a string": "يجب أن يكون نصاً",
      "must be a number": "يجب أن يكون رقماً",
      "must be a positive number": "يجب أن يكون رقماً موجباً",
      "must not be empty": "لا يجب أن يكون فارغاً",
      "is not valid": "غير صالح",
      "must be an email": "يجب أن يكون بريداً إلكترونياً",
      "must be a UUID": "يجب أن يكون معرفاً فريداً",
      "must be a date": "يجب أن يكون تاريخاً",
    };

    for (const [en, ar] of Object.entries(translations)) {
      if (message.toLowerCase().includes(en.toLowerCase())) {
        return message.replace(new RegExp(en, "i"), ar);
      }
    }

    return message;
  }

  /**
   * Extract field name from validation message
   */
  private extractFieldFromMessage(message: string): string {
    // Try to extract field name from message like "field should not be empty"
    const match = message.match(/^(\w+)\s/);
    return match ? match[1] : "unknown";
  }

  /**
   * Generate a unique request ID
   */
  private generateRequestId(): string {
    return `mkt_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 9)}`;
  }
}
