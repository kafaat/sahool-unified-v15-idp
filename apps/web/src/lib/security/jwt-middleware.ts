/**
 * JWT Middleware Validation
 * التحقق من JWT في الميدل وير
 *
 * Server-side JWT token validation for Next.js middleware
 * Uses jose library for secure JWT verification
 */

import type { NextRequest } from 'next/server';
import * as jose from 'jose';

/**
 * JWT validation result
 */
export interface JwtValidationResult {
  valid: boolean;
  error?: string;
  payload?: jose.JWTPayload;
}

/**
 * JWT configuration for middleware
 */
export interface JwtConfig {
  /**
   * Cookie name containing JWT token
   */
  cookieName?: string;

  /**
   * JWT secret key from environment
   */
  secretKey?: string;

  /**
   * JWT issuer to validate
   */
  issuer?: string;

  /**
   * JWT audience to validate
   */
  audience?: string;
}

/**
 * Get JWT configuration from environment variables
 *
 * @returns JWT configuration or null if not properly configured
 */
export function getJwtConfig(): JwtConfig | null {
  const secretKey = process.env.JWT_SECRET_KEY;
  const issuer = process.env.JWT_ISSUER;
  const audience = process.env.JWT_AUDIENCE;

  // All configuration must be present
  if (!secretKey || !issuer || !audience) {
    return null;
  }

  return {
    cookieName: 'access_token',
    secretKey,
    issuer,
    audience,
  };
}

/**
 * Validate JWT token from request
 *
 * @param request - Next.js request object
 * @param config - Optional JWT configuration (defaults to environment variables)
 * @returns Validation result with payload if valid
 */
export async function validateJwtToken(
  request: NextRequest,
  config?: JwtConfig
): Promise<JwtValidationResult> {
  // Get configuration
  const jwtConfig = config || getJwtConfig();
  if (!jwtConfig) {
    return {
      valid: false,
      error: 'JWT configuration not found',
    };
  }

  // Get token from cookie
  const token = request.cookies.get(jwtConfig.cookieName || 'access_token')?.value;
  if (!token) {
    return {
      valid: false,
      error: 'JWT token not found in cookies',
    };
  }

  try {
    // Verify JWT token with signature verification
    const secretKey = new TextEncoder().encode(jwtConfig.secretKey);
    const { payload } = await jose.jwtVerify(token, secretKey, {
      issuer: jwtConfig.issuer,
      audience: jwtConfig.audience,
    });

    // Validate required payload fields
    if (!payload.sub || typeof payload.sub !== 'string') {
      return {
        valid: false,
        error: 'Invalid JWT payload: missing or invalid subject',
      };
    }

    if (!payload.tenant_id || typeof payload.tenant_id !== 'string') {
      return {
        valid: false,
        error: 'Invalid JWT payload: missing or invalid tenant_id',
      };
    }

    // Token is valid
    return {
      valid: true,
      payload,
    };
  } catch (error) {
    // Handle specific JWT errors
    if (error instanceof jose.errors.JWTExpired) {
      return {
        valid: false,
        error: 'JWT token has expired',
      };
    }

    if (error instanceof jose.errors.JWTClaimValidationFailed) {
      return {
        valid: false,
        error: 'JWT claim validation failed',
      };
    }

    if (error instanceof jose.errors.JWSSignatureVerificationFailed) {
      return {
        valid: false,
        error: 'JWT signature verification failed',
      };
    }

    // Generic error
    return {
      valid: false,
      error: 'JWT validation failed',
    };
  }
}

/**
 * Extract JWT error information for logging
 *
 * @param request - Next.js request object
 * @param error - Error message
 * @returns Structured error information
 */
export function getJwtErrorInfo(request: NextRequest, error: string): {
  error: string;
  path: string;
  hasToken: boolean;
  configValid: boolean;
} {
  const config = getJwtConfig();
  const token = request.cookies.get('access_token')?.value;

  return {
    error,
    path: request.nextUrl.pathname,
    hasToken: !!token,
    configValid: !!config,
  };
}
