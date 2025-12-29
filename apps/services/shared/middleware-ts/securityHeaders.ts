import { Request, Response, NextFunction } from "express";

/**
 * Security Headers Middleware
 *
 * Adds comprehensive security headers to protect against common web vulnerabilities:
 * - X-Content-Type-Options: Prevents MIME type sniffing
 * - X-Frame-Options: Prevents clickjacking attacks
 * - X-XSS-Protection: Enables browser XSS protection
 * - Strict-Transport-Security: Enforces HTTPS connections
 * - Content-Security-Policy: Prevents XSS, data injection, and other attacks
 *
 * @see https://owasp.org/www-project-secure-headers/
 */
export function securityHeaders(req: Request, res: Response, next: NextFunction): void {
    // Prevent MIME type sniffing
    // This header prevents browsers from trying to guess content types
    res.setHeader("X-Content-Type-Options", "nosniff");

    // Prevent clickjacking by disallowing the page to be embedded in frames
    // DENY: The page cannot be displayed in a frame, regardless of the site attempting to do so
    res.setHeader("X-Frame-Options", "DENY");

    // Enable XSS protection in older browsers
    // Modern browsers have XSS Auditor deprecated in favor of CSP
    // 1; mode=block: Enable XSS filtering and block the page if attack is detected
    res.setHeader("X-XSS-Protection", "1; mode=block");

    // Enforce HTTPS connections (HSTS)
    // Only set in production to avoid local development issues
    // max-age=31536000: Cache this header for 1 year (in seconds)
    // includeSubDomains: Apply this rule to all subdomains
    if (process.env.NODE_ENV === "production") {
        res.setHeader(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains"
        );
    }

    // Content Security Policy (CSP)
    // Provides a robust defense against XSS and data injection attacks
    const cspDirectives = [
        // default-src: Fallback for other directives
        "default-src 'self'",

        // script-src: Controls which scripts can be executed
        // 'self': Allow scripts from same origin
        // 'unsafe-inline': Allow inline scripts (required for some frameworks)
        // Note: Consider using nonces or hashes instead of 'unsafe-inline' for better security
        "script-src 'self' 'unsafe-inline'",

        // style-src: Controls which stylesheets can be applied
        "style-src 'self' 'unsafe-inline'",

        // img-src: Controls which images can be loaded
        // data:: Allow data URIs (for inline images)
        // https:: Allow images from HTTPS sources
        "img-src 'self' data: https:",

        // font-src: Controls which fonts can be loaded
        "font-src 'self' data:",

        // connect-src: Controls which URLs can be loaded using script interfaces
        // This is important for API calls, WebSockets, etc.
        "connect-src 'self'",

        // frame-ancestors: Controls which sites can embed this page
        // 'none': No one can embed this page (similar to X-Frame-Options: DENY)
        "frame-ancestors 'none'",

        // base-uri: Restricts URLs that can be used in <base> element
        "base-uri 'self'",

        // form-action: Restricts URLs that can be used as form submission targets
        "form-action 'self'",

        // object-src: Controls plugins like Flash, Java, etc.
        "object-src 'none'",

        // upgrade-insecure-requests: Automatically upgrade HTTP requests to HTTPS
        // Only enable in production
        ...(process.env.NODE_ENV === "production" ? ["upgrade-insecure-requests"] : [])
    ];

    res.setHeader("Content-Security-Policy", cspDirectives.join("; "));

    // Additional security headers

    // Referrer-Policy: Controls how much referrer information is sent
    // no-referrer-when-downgrade: Default, send full URL unless HTTPS to HTTP
    // strict-origin-when-cross-origin: Better privacy option
    res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");

    // Permissions-Policy (formerly Feature-Policy)
    // Disables potentially dangerous browser features
    const permissionsPolicy = [
        "geolocation=(self)", // Allow geolocation only from same origin
        "microphone=()",      // Disable microphone
        "camera=()",          // Disable camera
        "payment=()",         // Disable payment API
        "usb=()",             // Disable USB API
        "magnetometer=()",    // Disable magnetometer
        "gyroscope=()",       // Disable gyroscope
        "accelerometer=()"    // Disable accelerometer
    ];

    res.setHeader("Permissions-Policy", permissionsPolicy.join(", "));

    // X-Permitted-Cross-Domain-Policies: Controls cross-domain policy files
    // none: No policy files are allowed anywhere on the target server
    res.setHeader("X-Permitted-Cross-Domain-Policies", "none");

    next();
}

/**
 * Custom CSP Configuration
 *
 * Allows customization of CSP directives for specific routes or services
 *
 * @param customDirectives - Object with CSP directive overrides
 * @returns Express middleware function
 *
 * @example
 * ```typescript
 * app.use('/api/upload', customCSP({
 *   'img-src': "'self' https://cdn.example.com data:",
 *   'connect-src': "'self' https://api.example.com"
 * }));
 * ```
 */
export function customCSP(customDirectives: Record<string, string>) {
    return (req: Request, res: Response, next: NextFunction): void => {
        const baseDirectives: Record<string, string> = {
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data: https:",
            "font-src": "'self' data:",
            "connect-src": "'self'",
            "frame-ancestors": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
            "object-src": "'none'"
        };

        // Merge custom directives with base directives
        const mergedDirectives = { ...baseDirectives, ...customDirectives };

        // Add upgrade-insecure-requests in production
        const cspParts = Object.entries(mergedDirectives).map(
            ([key, value]) => `${key} ${value}`
        );

        if (process.env.NODE_ENV === "production") {
            cspParts.push("upgrade-insecure-requests");
        }

        res.setHeader("Content-Security-Policy", cspParts.join("; "));
        next();
    };
}

/**
 * Remove sensitive headers from responses
 * Prevents information disclosure
 */
export function removeSensitiveHeaders(req: Request, res: Response, next: NextFunction): void {
    // Remove server identification headers
    res.removeHeader("X-Powered-By");
    res.removeHeader("Server");

    next();
}
