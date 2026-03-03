/**
 * HTTP Exception Filter - Unified Error Handling
 *
 * Features:
 * - Bilingual error messages (Arabic/English)
 * - Structured error response
 * - Request ID tracking
 * - Error logging with context
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
import { Prisma } from "../../prisma/generated/client";

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

interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    messageAr: string;
    details?: any;
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
    let errorCode: string = "ERR_UNKNOWN";
    let message: string = "An unexpected error occurred";
    let messageAr: string = "حدث خطأ غير متوقع";
    let details: any;

    // Handle different exception types
    if (exception instanceof HttpException) {
      status = exception.getStatus();
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === "string") {
        message = exceptionResponse;
        messageAr = ERROR_MESSAGES[status]?.ar || "خطأ غير معروف";
      } else if (typeof exceptionResponse === "object") {
        const resp = exceptionResponse as any;
        message = resp.message || resp.error || "Unknown error";
        messageAr = resp.messageAr || ERROR_MESSAGES[status]?.ar || "خطأ غير معروف";
        details = resp.details;
        errorCode = resp.code;
      }
    } else if (this.isPrismaError(exception)) {
      const prismaError = this.handlePrismaError(exception);
      status = prismaError.status;
      errorCode = prismaError.code;
      message = prismaError.message;
      messageAr = prismaError.messageAr;
      details = prismaError.details;
    } else if (exception instanceof Error) {
      status = HttpStatus.INTERNAL_SERVER_ERROR;
      message = exception.message;
      messageAr = "خطأ داخلي في الخادم";
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
    this.logger.error(
      `[${requestId}] ${request.method} ${request.url} - ${status} - ${message}`,
      exception instanceof Error ? exception.stack : undefined,
    );

    // Build response
    const errorResponse: ErrorResponse = {
      success: false,
      error: {
        code: errorCode,
        message,
        messageAr,
        ...(details && { details }),
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
   * Generate a unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 9)}`;
  }
}
