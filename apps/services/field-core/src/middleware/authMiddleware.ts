/**
 * Authentication Middleware for Field Core Service
 * Validates JWT tokens and enforces tenant isolation
 */

import { Request, Response, NextFunction } from "express";
import * as jwt from "jsonwebtoken";

/**
 * Error messages for authentication failures
 */
export const AuthErrors = {
    MISSING_TOKEN: {
        en: "Authentication token is missing",
        ar: "رمز المصادقة مفقود",
        code: "missing_token",
    },
    INVALID_TOKEN: {
        en: "Invalid authentication token",
        ar: "رمز المصادقة غير صالح",
        code: "invalid_token",
    },
    EXPIRED_TOKEN: {
        en: "Authentication token has expired",
        ar: "انتهت صلاحية رمز المصادقة",
        code: "expired_token",
    },
    TENANT_MISMATCH: {
        en: "Access denied: tenant mismatch",
        ar: "رفض الوصول: عدم تطابق المستأجر",
        code: "tenant_mismatch",
    },
    MISSING_TENANT_ID: {
        en: "Tenant ID is required",
        ar: "معرف المستأجر مطلوب",
        code: "missing_tenant_id",
    },
    JWT_SECRET_NOT_CONFIGURED: {
        en: "JWT secret not configured",
        ar: "لم يتم تكوين سر JWT",
        code: "jwt_secret_not_configured",
    },
};

/**
 * User information extracted from JWT token
 */
export interface AuthUser {
    id: string;
    email?: string;
    roles?: string[];
    tenantId: string;
}

/**
 * Extend Express Request to include user information
 */
declare global {
    namespace Express {
        interface Request {
            user?: AuthUser;
        }
    }
}

/**
 * Authentication Middleware
 *
 * Validates JWT token from Authorization header and attaches user info to request
 *
 * @param req - Express request object
 * @param res - Express response object
 * @param next - Express next function
 * @returns void or error response
 */
export function authenticateToken(
    req: Request,
    res: Response,
    next: NextFunction
): void {
    const authHeader = req.headers.authorization;

    // Check for Authorization header
    if (!authHeader) {
        res.status(401).json({
            success: false,
            error: AuthErrors.MISSING_TOKEN.code,
            message: AuthErrors.MISSING_TOKEN.en,
            message_ar: AuthErrors.MISSING_TOKEN.ar,
        });
        return;
    }

    // Extract token from "Bearer <token>" format
    const [type, token] = authHeader.split(" ");

    if (type !== "Bearer" || !token) {
        res.status(401).json({
            success: false,
            error: AuthErrors.INVALID_TOKEN.code,
            message: "Invalid authorization format. Expected: Bearer <token>",
            message_ar: "تنسيق التفويض غير صالح",
        });
        return;
    }

    // Get JWT secret from environment
    const secret = process.env.JWT_SECRET_KEY || process.env.JWT_SECRET;
    if (!secret) {
        console.error("⚠️ JWT_SECRET_KEY or JWT_SECRET not configured");
        res.status(500).json({
            success: false,
            error: AuthErrors.JWT_SECRET_NOT_CONFIGURED.code,
            message: AuthErrors.JWT_SECRET_NOT_CONFIGURED.en,
            message_ar: AuthErrors.JWT_SECRET_NOT_CONFIGURED.ar,
        });
        return;
    }

    try {
        // Verify and decode JWT token with algorithm specification to prevent algorithm confusion attacks
        const decoded = jwt.verify(token, secret, { algorithms: ['HS256'] });

        // Validate decoded payload is an object
        if (typeof decoded !== 'object' || decoded === null) {
            throw new jwt.JsonWebTokenError('Invalid token payload');
        }

        const payload = decoded as jwt.JwtPayload;

        // Extract user information from token with proper type checking
        const userId = payload.sub || payload.user_id || payload.userId;
        const tenantId = payload.tenant_id || payload.tenantId;

        if (typeof userId !== 'string') {
            throw new jwt.JsonWebTokenError('Invalid user ID in token');
        }

        const user: AuthUser = {
            id: userId,
            email: typeof payload.email === 'string' ? payload.email : undefined,
            roles: Array.isArray(payload.roles) ? payload.roles : [],
            tenantId: typeof tenantId === 'string' ? tenantId : '',
        };

        // Validate tenant_id exists in token
        if (!user.tenantId) {
            res.status(403).json({
                success: false,
                error: AuthErrors.MISSING_TENANT_ID.code,
                message: "Token does not contain tenant_id",
                message_ar: "الرمز لا يحتوي على معرف المستأجر",
            });
            return;
        }

        // Attach user info to request for downstream handlers
        req.user = user;

        // Continue to next middleware/handler
        next();
    } catch (error) {
        if (error instanceof jwt.TokenExpiredError) {
            res.status(401).json({
                success: false,
                error: AuthErrors.EXPIRED_TOKEN.code,
                message: AuthErrors.EXPIRED_TOKEN.en,
                message_ar: AuthErrors.EXPIRED_TOKEN.ar,
            });
            return;
        }

        if (error instanceof jwt.JsonWebTokenError) {
            res.status(401).json({
                success: false,
                error: AuthErrors.INVALID_TOKEN.code,
                message: AuthErrors.INVALID_TOKEN.en,
                message_ar: AuthErrors.INVALID_TOKEN.ar,
            });
            return;
        }

        // Unknown error
        console.error("Authentication error:", error);
        res.status(401).json({
            success: false,
            error: AuthErrors.INVALID_TOKEN.code,
            message: "Authentication failed",
            message_ar: "فشلت المصادقة",
        });
        return;
    }
}

/**
 * Options for tenant isolation enforcement
 */
export interface TenantIsolationOptions {
    /**
     * If true, allows requests without tenant ID (bypasses tenant validation)
     * Default: false (tenant ID is required)
     *
     * SECURITY WARNING: Only set to true for routes that don't access tenant-specific data
     * (e.g., system-level endpoints, health checks, public APIs)
     */
    allowMissingTenantId?: boolean;
}

/**
 * Tenant Isolation Middleware Factory
 *
 * Ensures that the tenant_id from the JWT token matches the tenant_id in the request
 * This middleware should be used after authenticateToken middleware
 *
 * SECURITY: By default, this middleware REQUIRES tenant_id to be present in the request.
 * This prevents cross-tenant access vulnerabilities.
 *
 * Supports tenant_id from:
 * - Query parameters (req.query.tenantId)
 * - Request body (req.body.tenantId)
 * - Route parameters (req.params.tenantId)
 *
 * @param options - Configuration options for tenant isolation
 * @returns Express middleware function
 *
 * @example
 * // Default usage - tenant ID is required
 * app.get('/api/data', authenticateToken, enforceTenantIsolation(), handler);
 *
 * @example
 * // Optional tenant ID for system endpoints
 * app.get('/api/system/health', authenticateToken,
 *   enforceTenantIsolation({ allowMissingTenantId: true }), handler);
 */
export function enforceTenantIsolation(
    options: TenantIsolationOptions = {}
) {
    return (req: Request, res: Response, next: NextFunction): void => {
        // User should be attached by authenticateToken middleware
        if (!req.user) {
            res.status(401).json({
                success: false,
                error: "authentication_required",
                message: "Authentication required. Use authenticateToken middleware first.",
                message_ar: "المصادقة مطلوبة",
            });
            return;
        }

        // Extract tenant_id from request (query, body, or params)
        const requestTenantId =
            req.query.tenantId ||
            req.body.tenantId ||
            req.params.tenantId;

        // SECURITY: Require tenant ID by default to prevent cross-tenant access
        if (!requestTenantId) {
            // Allow bypass only if explicitly configured
            if (options.allowMissingTenantId === true) {
                console.debug(
                    `ℹ️ Tenant validation bypassed for user ${req.user.id} (tenant: ${req.user.tenantId}) - allowMissingTenantId enabled`
                );
                next();
                return;
            }

            // Tenant ID is required but missing - reject request
            console.warn(
                `⚠️ Tenant isolation violation: Request missing tenant ID for user ${req.user.id} (tenant: ${req.user.tenantId}) on ${req.method} ${req.path}`
            );

            res.status(400).json({
                success: false,
                error: AuthErrors.MISSING_TENANT_ID.code,
                message: AuthErrors.MISSING_TENANT_ID.en,
                message_ar: AuthErrors.MISSING_TENANT_ID.ar,
            });
            return;
        }

        // Verify tenant_id matches the token
        if (requestTenantId !== req.user.tenantId) {
            console.warn(
                `⚠️ Tenant isolation violation: User ${req.user.id} (tenant: ${req.user.tenantId}) ` +
                `attempted to access tenant: ${requestTenantId} on ${req.method} ${req.path}`
            );

            res.status(403).json({
                success: false,
                error: AuthErrors.TENANT_MISMATCH.code,
                message: AuthErrors.TENANT_MISMATCH.en,
                message_ar: AuthErrors.TENANT_MISMATCH.ar,
            });
            return;
        }

        // Tenant validation passed
        next();
    };
}

/**
 * Combined Authentication and Tenant Isolation Middleware
 *
 * Convenience middleware that combines authenticateToken and enforceTenantIsolation
 * with mandatory tenant ID validation (default behavior)
 *
 * @param req - Express request object
 * @param res - Express response object
 * @param next - Express next function
 *
 * @example
 * // Use for routes that require authentication and tenant isolation
 * app.get('/api/users', requireAuth, handler);
 */
export function requireAuth(
    req: Request,
    res: Response,
    next: NextFunction
): void {
    authenticateToken(req, res, (error?: any) => {
        if (error) {
            next(error);
            return;
        }
        // Call the factory function and immediately invoke the returned middleware
        enforceTenantIsolation()(req, res, next);
    });
}
