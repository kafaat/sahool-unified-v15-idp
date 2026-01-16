/**
 * HTTP Exception Filter
 * مرشح استثناءات HTTP
 *
 * @module shared/errors
 * @description Global exception filter for consistent error handling
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
import { AppException } from "./exceptions";
import { ErrorResponseDto, FieldErrorDto } from "./error-response.dto";
import { ErrorCode, ERROR_REGISTRY } from "./error-codes";

/**
 * Global HTTP Exception Filter
 * مرشح استثناءات HTTP العام
 *
 * @description Catches all exceptions and returns a standardized error response
 */
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    let errorResponse: ErrorResponseDto;
    let httpStatus: HttpStatus;

    // Handle AppException (our custom exceptions)
    if (exception instanceof AppException) {
      httpStatus = exception.getStatus();
      errorResponse = this.handleAppException(exception, request);
    }
    // Handle NestJS HttpException
    else if (exception instanceof HttpException) {
      httpStatus = exception.getStatus();
      errorResponse = this.handleHttpException(exception, request);
    }
    // Handle unknown errors
    else {
      httpStatus = HttpStatus.INTERNAL_SERVER_ERROR;
      errorResponse = this.handleUnknownError(exception, request);
    }

    // Log the error
    this.logError(exception, request, httpStatus);

    // Send response
    response.status(httpStatus).json(errorResponse);
  }

  /**
   * Handle AppException
   * معالجة AppException
   */
  private handleAppException(
    exception: AppException,
    request: Request,
  ): ErrorResponseDto {
    const metadata = ERROR_REGISTRY[exception.errorCode];

    return new ErrorResponseDto(
      exception.errorCode,
      exception.messageEn,
      exception.messageAr,
      exception.retryable,
      {
        category: metadata.category,
        path: request.url,
        details: exception.details,
        requestId: this.getRequestId(request),
        stack: this.shouldIncludeStack() ? exception.stack : undefined,
      },
    );
  }

  /**
   * Handle NestJS HttpException
   * معالجة HttpException من NestJS
   */
  private handleHttpException(
    exception: HttpException,
    request: Request,
  ): ErrorResponseDto {
    const status = exception.getStatus();
    const exceptionResponse = exception.getResponse();

    // Handle validation errors from class-validator
    if (this.isValidationError(exceptionResponse)) {
      return this.handleValidationError(exceptionResponse, request);
    }

    // Map HTTP status to error code
    const errorCode = this.mapHttpStatusToErrorCode(status);
    const metadata = ERROR_REGISTRY[errorCode];

    // Extract message from exception
    let message = metadata.message.en;
    let messageAr = metadata.message.ar;

    if (typeof exceptionResponse === "string") {
      message = exceptionResponse;
    } else if (
      typeof exceptionResponse === "object" &&
      "message" in exceptionResponse
    ) {
      message =
        typeof exceptionResponse.message === "string"
          ? exceptionResponse.message
          : Array.isArray(exceptionResponse.message)
            ? exceptionResponse.message.join(", ")
            : metadata.message.en;
    }

    return new ErrorResponseDto(errorCode, message, messageAr, false, {
      category: metadata.category,
      path: request.url,
      requestId: this.getRequestId(request),
      stack: this.shouldIncludeStack() ? exception.stack : undefined,
    });
  }

  /**
   * Handle validation errors from class-validator
   * معالجة أخطاء التحقق من class-validator
   */
  private handleValidationError(
    exceptionResponse: any,
    request: Request,
  ): ErrorResponseDto {
    const fieldErrors: FieldErrorDto[] = [];

    if (Array.isArray(exceptionResponse.message)) {
      exceptionResponse.message.forEach((error: any) => {
        if (typeof error === "object" && "constraints" in error) {
          const constraints = error.constraints;
          const messages = Object.values(constraints);
          fieldErrors.push({
            field: error.property,
            message: messages[0] as string,
            constraint: Object.keys(constraints)[0],
            value: error.value,
          });
        } else if (typeof error === "string") {
          fieldErrors.push({
            field: "unknown",
            message: error,
          });
        }
      });
    }

    const metadata = ERROR_REGISTRY[ErrorCode.VALIDATION_ERROR];

    return new ErrorResponseDto(
      ErrorCode.VALIDATION_ERROR,
      metadata.message.en,
      metadata.message.ar,
      false,
      {
        category: metadata.category,
        path: request.url,
        details: { fields: fieldErrors },
        requestId: this.getRequestId(request),
      },
    );
  }

  /**
   * Handle unknown errors
   * معالجة الأخطاء غير المعروفة
   */
  private handleUnknownError(
    exception: any,
    request: Request,
  ): ErrorResponseDto {
    const metadata = ERROR_REGISTRY[ErrorCode.INTERNAL_SERVER_ERROR];

    // Log the full error for debugging
    this.logger.error("Unknown error occurred", exception);

    return new ErrorResponseDto(
      ErrorCode.INTERNAL_SERVER_ERROR,
      metadata.message.en,
      metadata.message.ar,
      true,
      {
        category: metadata.category,
        path: request.url,
        requestId: this.getRequestId(request),
        stack: this.shouldIncludeStack() ? exception?.stack : undefined,
        details: this.shouldIncludeStack()
          ? {
              error: exception?.message || "Unknown error",
              type: exception?.constructor?.name,
            }
          : undefined,
      },
    );
  }

  /**
   * Check if response is a validation error
   * التحقق من كون الاستجابة خطأ تحقق
   */
  private isValidationError(response: any): boolean {
    return (
      typeof response === "object" &&
      "message" in response &&
      Array.isArray(response.message) &&
      response.message.length > 0 &&
      (typeof response.message[0] === "object" ||
        (typeof response.message[0] === "string" &&
          response.statusCode === HttpStatus.BAD_REQUEST))
    );
  }

  /**
   * Map HTTP status to error code
   * ربط حالة HTTP بكود الخطأ
   */
  private mapHttpStatusToErrorCode(status: HttpStatus): ErrorCode {
    const statusMap: Record<number, ErrorCode> = {
      [HttpStatus.BAD_REQUEST]: ErrorCode.VALIDATION_ERROR,
      [HttpStatus.UNAUTHORIZED]: ErrorCode.AUTHENTICATION_FAILED,
      [HttpStatus.FORBIDDEN]: ErrorCode.FORBIDDEN,
      [HttpStatus.NOT_FOUND]: ErrorCode.RESOURCE_NOT_FOUND,
      [HttpStatus.CONFLICT]: ErrorCode.RESOURCE_ALREADY_EXISTS,
      [HttpStatus.UNPROCESSABLE_ENTITY]: ErrorCode.BUSINESS_RULE_VIOLATION,
      [HttpStatus.TOO_MANY_REQUESTS]: ErrorCode.RATE_LIMIT_EXCEEDED,
      [HttpStatus.INTERNAL_SERVER_ERROR]: ErrorCode.INTERNAL_SERVER_ERROR,
      [HttpStatus.BAD_GATEWAY]: ErrorCode.EXTERNAL_SERVICE_ERROR,
      [HttpStatus.SERVICE_UNAVAILABLE]: ErrorCode.SERVICE_UNAVAILABLE,
      [HttpStatus.GATEWAY_TIMEOUT]: ErrorCode.EXTERNAL_SERVICE_ERROR,
    };

    return statusMap[status] || ErrorCode.INTERNAL_SERVER_ERROR;
  }

  /**
   * Get request ID from headers or generate one
   * الحصول على معرف الطلب من الرؤوس أو إنشاء واحد
   */
  private getRequestId(request: Request): string {
    return (
      (request.headers["x-request-id"] as string) ||
      (request.headers["x-correlation-id"] as string) ||
      `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    );
  }

  /**
   * Should include stack trace in response
   * هل يجب تضمين تتبع المكدس في الاستجابة
   */
  private shouldIncludeStack(): boolean {
    return (
      process.env.NODE_ENV === "development" ||
      process.env.INCLUDE_STACK_TRACE === "true"
    );
  }

  /**
   * Log error with appropriate level
   * تسجيل الخطأ بمستوى مناسب
   */
  private logError(exception: any, request: Request, status: HttpStatus) {
    const message = `${request.method} ${request.url} - Status: ${status}`;

    // Log as error for 5xx errors, warn for 4xx errors
    if (status >= 500) {
      this.logger.error(message, exception?.stack || exception);
    } else if (status >= 400) {
      this.logger.warn(message, {
        error: exception?.message || exception,
        requestId: this.getRequestId(request),
      });
    }

    // Log additional context in development
    if (this.shouldIncludeStack()) {
      this.logger.debug("Request details", {
        method: request.method,
        url: request.url,
        headers: request.headers,
        body: request.body,
        params: request.params,
        query: request.query,
      });
    }
  }
}

/**
 * Language-aware Exception Filter
 * مرشح استثناءات واعي باللغة
 *
 * @description Returns error messages based on Accept-Language header
 */
@Catch()
export class LanguageAwareExceptionFilter extends HttpExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const request = ctx.getRequest<Request>();
    const response = ctx.getResponse<Response>();

    // Get preferred language from headers
    const language = this.getPreferredLanguage(request);

    // Call parent filter
    super.catch(exception, host);

    // Modify response based on language (if needed)
    // This is handled in the response DTO which includes both languages
  }

  /**
   * Get preferred language from request
   * الحصول على اللغة المفضلة من الطلب
   */
  private getPreferredLanguage(request: Request): "en" | "ar" {
    const acceptLanguage = request.headers["accept-language"];
    if (!acceptLanguage) {
      return "en";
    }

    // Parse Accept-Language header
    const languages = acceptLanguage.split(",").map((lang) => {
      const [code, priority = "1"] = lang.trim().split(";q=");
      return { code: code.toLowerCase(), priority: parseFloat(priority) };
    });

    // Sort by priority
    languages.sort((a, b) => b.priority - a.priority);

    // Check for Arabic
    const hasArabic = languages.some(
      (lang) => lang.code.startsWith("ar") || lang.code === "ar",
    );

    return hasArabic ? "ar" : "en";
  }
}
