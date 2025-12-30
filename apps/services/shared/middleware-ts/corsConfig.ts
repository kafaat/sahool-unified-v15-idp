import cors from "cors";

/**
 * Secure CORS Configuration
 *
 * Implements a strict CORS policy that:
 * - Rejects requests without Origin header in production
 * - Only allows specific origins from environment variable
 * - Supports credentials (cookies, authorization headers)
 * - Allows specific HTTP methods and headers
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
 */

/**
 * Get allowed origins from environment variable or use defaults
 */
function getAllowedOrigins(): string[] {
    // Check for environment variable first
    if (process.env.ALLOWED_ORIGINS) {
        // Split by comma and trim whitespace
        return process.env.ALLOWED_ORIGINS.split(',').map(origin => origin.trim());
    }

    // Default allowed origins for production
    const productionOrigins = [
        'https://sahool.app',
        'https://admin.sahool.app',
        'https://api.sahool.app',
        'https://api.sahool.io'
    ];

    // Development origins (only in non-production environments)
    const developmentOrigins = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:8080',
        'http://localhost:4200',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:8080',
        'http://127.0.0.1:4200'
    ];

    // Only include development origins in non-production environments
    if (process.env.NODE_ENV !== 'production') {
        return [...productionOrigins, ...developmentOrigins];
    }

    return productionOrigins;
}

/**
 * Create CORS options with strict security
 *
 * @param options - Optional configuration overrides
 * @returns CORS configuration object
 */
export function createSecureCorsOptions(options?: {
    allowNoOrigin?: boolean;
    additionalOrigins?: string[];
    methods?: string[];
    allowedHeaders?: string[];
}): cors.CorsOptions {
    const allowedOrigins = [
        ...getAllowedOrigins(),
        ...(options?.additionalOrigins || [])
    ];

    const isProduction = process.env.NODE_ENV === 'production';

    return {
        origin: (origin, callback) => {
            // In production, reject requests without Origin header
            // These could be:
            // - Server-to-server requests (should use API keys instead)
            // - Direct browser requests (not from web pages)
            // - cURL or other tools (should use proper authentication)
            if (!origin) {
                if (isProduction && !options?.allowNoOrigin) {
                    console.warn('⚠️ CORS blocked request: No Origin header in production');
                    return callback(new Error('Not allowed by CORS - Origin header required'));
                }
                // Allow in development for testing with tools like Postman, cURL
                return callback(null, true);
            }

            // Check if origin is in allowed list
            if (allowedOrigins.includes(origin)) {
                callback(null, true);
            } else {
                console.warn(`⚠️ CORS blocked request from unauthorized origin: ${origin}`);
                callback(new Error('Not allowed by CORS'));
            }
        },

        // Enable credentials (cookies, authorization headers, TLS client certificates)
        credentials: true,

        // Allowed HTTP methods
        methods: options?.methods || ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],

        // Allowed request headers
        allowedHeaders: options?.allowedHeaders || [
            'Content-Type',
            'Authorization',
            'If-Match',
            'If-None-Match',
            'X-Request-ID',
            'X-Tenant-ID',
            'X-User-ID',
            'X-Device-ID'
        ],

        // Headers exposed to the browser
        exposedHeaders: [
            'ETag',
            'X-Request-ID',
            'X-RateLimit-Limit',
            'X-RateLimit-Remaining',
            'X-RateLimit-Reset'
        ],

        // How long browsers can cache the preflight response (24 hours)
        maxAge: 86400,

        // Continue to next middleware even if CORS succeeds
        preflightContinue: false,

        // Provide successful status for OPTIONS requests
        optionsSuccessStatus: 204
    };
}

/**
 * Default secure CORS middleware
 */
export const secureCors = cors(createSecureCorsOptions());

/**
 * CORS middleware that allows requests without Origin header
 * Use this for APIs that need to support server-to-server communication
 */
export const corsWithServerSupport = cors(
    createSecureCorsOptions({ allowNoOrigin: true })
);

/**
 * CORS middleware with custom origins
 *
 * @param additionalOrigins - Additional origins to allow
 * @returns CORS middleware
 */
export function corsWithCustomOrigins(additionalOrigins: string[]) {
    return cors(createSecureCorsOptions({ additionalOrigins }));
}
