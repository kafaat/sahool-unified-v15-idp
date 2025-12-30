/**
 * SAHOOL Error Localization Middleware
 * وسيط توطين الأخطاء
 *
 * Provides error localization support for Express.js applications.
 * يوفر دعم توطين الأخطاء لتطبيقات Express.js.
 */

import { Request, Response, NextFunction, ErrorRequestHandler } from "express";
import { randomBytes } from "crypto";
import {
    parseAcceptLanguage,
    getBilingualTranslation,
    getTranslation,
} from "./errorTranslations";

/**
 * Extended Request interface with language preference
 */
export interface LocalizedRequest extends Request {
    preferredLanguage?: "en" | "ar";
}

/**
 * Error response format
 */
export interface ErrorResponse {
    success: false;
    error: {
        code: string;
        message: string;
        message_ar: string;
        error?: string; // Localized message based on Accept-Language
        error_id?: string;
        details?: any;
    };
}

/**
 * Application Error class with bilingual support
 */
export class AppError extends Error {
    public statusCode: number;
    public errorCode: string;
    public messageAr: string;
    public details?: any;
    public isOperational: boolean;

    constructor(
        statusCode: number,
        errorCode: string,
        message: string,
        messageAr?: string,
        details?: any
    ) {
        super(message);
        this.statusCode = statusCode;
        this.errorCode = errorCode;
        this.messageAr = messageAr || message;
        this.details = details;
        this.isOperational = true;

        // Maintains proper stack trace for where our error was thrown
        Error.captureStackTrace(this, this.constructor);
    }
}

/**
 * Middleware to parse Accept-Language header and set preferred language
 */
export function languageParser() {
    return (req: LocalizedRequest, res: Response, next: NextFunction) => {
        const acceptLanguage = req.headers["accept-language"];
        req.preferredLanguage = parseAcceptLanguage(acceptLanguage);
        next();
    };
}

/**
 * List of sensitive keys that should be filtered from error details
 */
const SENSITIVE_KEYS = [
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "accesstoken",
    "refreshtoken",
    "privatekey",
    "sessionid",
    "cookie",
    "credentials",
    "authorization",
    "auth",
];

/**
 * Recursively filter sensitive data from objects
 * Removes any keys that match sensitive patterns (case-insensitive)
 */
function filterSensitiveData(data: any): any {
    if (data === null || data === undefined) {
        return data;
    }

    // Handle arrays
    if (Array.isArray(data)) {
        return data.map((item) => filterSensitiveData(item));
    }

    // Handle objects
    if (typeof data === "object") {
        const filtered: any = {};

        for (const [key, value] of Object.entries(data)) {
            // Check if key matches any sensitive pattern (case-insensitive)
            const keyLower = key.toLowerCase();
            const isSensitive = SENSITIVE_KEYS.some((sensitiveKey) =>
                keyLower.includes(sensitiveKey)
            );

            if (!isSensitive) {
                // Recursively filter nested objects/arrays
                filtered[key] = filterSensitiveData(value);
            }
        }

        return filtered;
    }

    // Return primitive values as-is
    return data;
}

/**
 * Create a standardized error response
 */
export function createErrorResponse(
    errorCode: string,
    message: string,
    messageAr: string,
    preferredLanguage?: "en" | "ar",
    errorId?: string,
    details?: any
): ErrorResponse {
    // Get translations from mapping
    const translations = getBilingualTranslation(errorCode, message, messageAr);

    const response: ErrorResponse = {
        success: false,
        error: {
            code: errorCode,
            message: translations.en,
            message_ar: translations.ar,
        },
    };

    // Add localized message based on preferred language
    if (preferredLanguage) {
        response.error.error = translations[preferredLanguage];
    }

    // Add error ID if provided
    if (errorId) {
        response.error.error_id = errorId;
    }

    // Add details if provided (filter sensitive data)
    if (details) {
        const safeDetails = filterSensitiveData(details);

        if (Object.keys(safeDetails).length > 0) {
            response.error.details = safeDetails;
        }
    }

    return response;
}

/**
 * Generate a short error ID for tracking using cryptographically secure random bytes
 */
function generateErrorId(): string {
    return randomBytes(4).toString('hex').toUpperCase();
}

/**
 * Error handling middleware - should be registered last
 */
export const errorHandler: ErrorRequestHandler = (
    err: Error | AppError,
    req: LocalizedRequest,
    res: Response,
    next: NextFunction
) => {
    // Generate error ID for tracking
    const errorId = generateErrorId();

    // Get preferred language
    const preferredLanguage = req.preferredLanguage || parseAcceptLanguage(req.headers["accept-language"]);

    // Handle AppError instances
    if (err instanceof AppError) {
        console.warn(`[${errorId}] AppError: ${err.errorCode} - ${err.message}`, {
            path: req.path,
            method: req.method,
            errorCode: err.errorCode,
            preferredLanguage,
        });

        return res.status(err.statusCode).json(
            createErrorResponse(
                err.errorCode,
                err.message,
                err.messageAr,
                preferredLanguage,
                errorId,
                err.details
            )
        );
    }

    // Handle validation errors from express-validator or similar
    if (err.name === "ValidationError") {
        const validationError = err as any;
        console.warn(`[${errorId}] ValidationError: ${err.message}`, {
            path: req.path,
            method: req.method,
            preferredLanguage,
        });

        return res.status(400).json(
            createErrorResponse(
                "VALIDATION_ERROR",
                err.message,
                "خطأ في التحقق من البيانات",
                preferredLanguage,
                errorId,
                validationError.errors || validationError.details
            )
        );
    }

    // Handle syntax errors (malformed JSON, etc.)
    if (err instanceof SyntaxError && "body" in err) {
        console.warn(`[${errorId}] SyntaxError: ${err.message}`, {
            path: req.path,
            method: req.method,
        });

        return res.status(400).json(
            createErrorResponse(
                "BAD_REQUEST",
                "Invalid JSON in request body",
                "JSON غير صالح في نص الطلب",
                preferredLanguage,
                errorId
            )
        );
    }

    // Handle all other errors as internal server errors
    console.error(`[${errorId}] UnhandledError: ${err.name} - ${err.message}`, {
        path: req.path,
        method: req.method,
        stack: err.stack,
        preferredLanguage,
    });

    // Never expose internal error details to clients
    return res.status(500).json(
        createErrorResponse(
            "INTERNAL_ERROR",
            "An internal error occurred. Please try again later.",
            "حدث خطأ داخلي. يرجى المحاولة لاحقاً.",
            preferredLanguage,
            errorId
        )
    );
};

/**
 * Not Found (404) handler
 */
export function notFoundHandler(req: LocalizedRequest, res: Response) {
    const preferredLanguage = req.preferredLanguage || parseAcceptLanguage(req.headers["accept-language"]);
    const errorId = generateErrorId();

    console.warn(`[${errorId}] NotFound: ${req.method} ${req.path}`, {
        preferredLanguage,
    });

    res.status(404).json(
        createErrorResponse(
            "NOT_FOUND",
            "The requested resource was not found",
            "المورد المطلوب غير موجود",
            preferredLanguage,
            errorId
        )
    );
}

/**
 * Async handler wrapper to catch errors in async route handlers
 */
export function asyncHandler(fn: Function) {
    return (req: Request, res: Response, next: NextFunction) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
}

// ════════════════════════════════════════════════════════════════════════
// PRE-DEFINED ERROR CLASSES
// فئات الأخطاء المحددة مسبقاً
// ════════════════════════════════════════════════════════════════════════

export class ValidationError extends AppError {
    constructor(message: string, messageAr?: string, details?: any) {
        super(
            400,
            "VALIDATION_ERROR",
            message,
            messageAr || "خطأ في التحقق من البيانات",
            details
        );
    }
}

export class AuthenticationError extends AppError {
    constructor(
        message: string = "Authentication required",
        messageAr: string = "المصادقة مطلوبة"
    ) {
        super(401, "AUTHENTICATION_ERROR", message, messageAr);
    }
}

export class AuthorizationError extends AppError {
    constructor(
        message: string = "Permission denied",
        messageAr: string = "الإذن مرفوض"
    ) {
        super(403, "AUTHORIZATION_ERROR", message, messageAr);
    }
}

export class NotFoundError extends AppError {
    constructor(resource: string, messageAr?: string) {
        super(
            404,
            "NOT_FOUND",
            `${resource} not found`,
            messageAr || `${resource} غير موجود`
        );
    }
}

export class ConflictError extends AppError {
    constructor(message: string, messageAr?: string, details?: any) {
        super(409, "CONFLICT", message, messageAr || "حدث تعارض", details);
    }
}

export class RateLimitError extends AppError {
    constructor(retryAfter: number = 60) {
        super(
            429,
            "RATE_LIMIT_EXCEEDED",
            "Too many requests. Please try again later.",
            "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
            { retry_after: retryAfter }
        );
    }
}

export class InternalError extends AppError {
    constructor(errorId?: string) {
        super(
            500,
            "INTERNAL_ERROR",
            "An internal error occurred. Please try again later.",
            "حدث خطأ داخلي. يرجى المحاولة لاحقاً.",
            errorId ? { error_id: errorId } : undefined
        );
    }
}

/**
 * Example usage in Express application:
 *
 * ```typescript
 * import express from 'express';
 * import {
 *   languageParser,
 *   errorHandler,
 *   notFoundHandler,
 *   asyncHandler,
 *   NotFoundError,
 *   ValidationError
 * } from './middleware/errorLocalization';
 *
 * const app = express();
 *
 * // Apply language parser middleware early
 * app.use(languageParser());
 *
 * // Your routes
 * app.get('/api/fields/:id', asyncHandler(async (req, res) => {
 *   const field = await getField(req.params.id);
 *   if (!field) {
 *     throw new NotFoundError('Field', 'الحقل');
 *   }
 *   res.json(field);
 * }));
 *
 * // 404 handler
 * app.use(notFoundHandler);
 *
 * // Error handler (must be last)
 * app.use(errorHandler);
 * ```
 */
