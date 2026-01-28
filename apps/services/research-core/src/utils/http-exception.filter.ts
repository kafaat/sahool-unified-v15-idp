/**
 * HTTP Exception Filter for Marketplace Service
 * فلتر استثناءات HTTP لخدمة السوق
 *
 * Provides unified error response format across the service.
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

/**
 * Error response structure
 * هيكل استجابة الخطأ
 */
interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    messageAr?: string;
    details?: Record<string, any>;
    timestamp: string;
    path: string;
    requestId?: string;
  };
}

/**
 * HTTP Exception Filter
 * يلتقط جميع استثناءات HTTP ويحولها إلى استجابة موحدة
 */
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  private readonly logger = new Logger(HttpExceptionFilter.name);

  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    // Determine status code
    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    // Extract error message
    let message = "An unexpected error occurred";
    let messageAr = "حدث خطأ غير متوقع";
    let code = "INTERNAL_ERROR";
    let details: Record<string, any> | undefined;

    if (exception instanceof HttpException) {
      const exceptionResponse = exception.getResponse();

      if (typeof exceptionResponse === "string") {
        message = exceptionResponse;
      } else if (typeof exceptionResponse === "object") {
        const resp = exceptionResponse as any;
        message = resp.message || resp.error || message;
        messageAr = resp.messageAr || resp.message_ar || messageAr;
        code = resp.code || resp.errorCode || this.getDefaultCode(status);
        details = resp.details || resp.errors;
      }
    } else if (exception instanceof Error) {
      message = exception.message;
    }

    // Get request ID from headers
    const requestId =
      (request.headers["x-request-id"] as string) ||
      (request.headers["x-correlation-id"] as string);

    // Build error response
    const errorResponse: ErrorResponse = {
      success: false,
      error: {
        code,
        message,
        messageAr,
        details,
        timestamp: new Date().toISOString(),
        path: request.url,
        requestId,
      },
    };

    // Log error
    if (status >= 500) {
      this.logger.error(
        `${request.method} ${request.url} - ${status} - ${message}`,
        exception instanceof Error ? exception.stack : undefined,
      );
    } else {
      this.logger.warn(
        `${request.method} ${request.url} - ${status} - ${message}`,
      );
    }

    // Send response
    response.status(status).json(errorResponse);
  }

  /**
   * Get default error code based on HTTP status
   */
  private getDefaultCode(status: number): string {
    const statusCodes: Record<number, string> = {
      400: "BAD_REQUEST",
      401: "UNAUTHORIZED",
      403: "FORBIDDEN",
      404: "NOT_FOUND",
      409: "CONFLICT",
      422: "UNPROCESSABLE_ENTITY",
      429: "TOO_MANY_REQUESTS",
      500: "INTERNAL_ERROR",
      502: "BAD_GATEWAY",
      503: "SERVICE_UNAVAILABLE",
    };

    return statusCodes[status] || "UNKNOWN_ERROR";
  }
}

/**
 * Language-aware exception filter
 * فلتر استثناءات مدرك للغة
 */
@Catch()
export class LanguageAwareExceptionFilter extends HttpExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost): void {
    const ctx = host.switchToHttp();
    const request = ctx.getRequest<Request>();

    // Detect preferred language from Accept-Language header
    const acceptLanguage = request.headers["accept-language"] || "en";
    const preferArabic = acceptLanguage.includes("ar");

    // Store language preference in request for use in response
    (request as any).preferArabic = preferArabic;

    super.catch(exception, host);
  }
}
