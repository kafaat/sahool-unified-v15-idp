/**
 * Shared Express Middleware for Sahool Services
 *
 * This module exports reusable middleware for Express-based services:
 * - Security headers (OWASP best practices)
 * - CORS configuration (strict origin validation)
 * - Additional security utilities
 */

export {
    securityHeaders,
    customCSP,
    removeSensitiveHeaders
} from './securityHeaders';

export {
    createSecureCorsOptions,
    secureCors,
    corsWithServerSupport,
    corsWithCustomOrigins
} from './corsConfig';
