/**
 * JWT Token Verification Utilities
 * Server-side JWT validation and role extraction
 */

import { jwtVerify, decodeJwt, JWTPayload } from 'jose';

/** Validate UUID format for tenant_id injection prevention */
function isValidUUID(str: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str);
}

// ---------------------------------------------------------------------------
// Inline User type to avoid importing the @/lib/auth barrel which pulls in
// api-middleware -> @/lib/logger -> @sentry/nextjs (~300KB in edge bundle).
// This type MUST stay in sync with the User interface in @/lib/auth.ts.
// ---------------------------------------------------------------------------
export interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: 'admin' | 'supervisor' | 'viewer';
  tenant_id?: string;
}

/**
 * Extended JWT payload with user information
 */
export interface TokenPayload extends JWTPayload {
  sub: string; // user ID
  email: string;
  role?: 'admin' | 'supervisor' | 'viewer'; // Singular role (legacy/optional)
  roles?: string[]; // Roles array (backend user-service format)
  name?: string;
  tenant_id?: string;
  tid?: string; // Alternative tenant ID field
}

/**
 * Verify JWT token and extract payload
 * @param token - JWT token string
 * @returns Decoded and verified token payload
 * @throws Error if token is invalid, expired, or signature verification fails
 */
export async function verifyToken(token: string): Promise<TokenPayload> {
  // Configuration check must happen outside try-catch so the helpful error is
  // never swallowed into the generic "Token verification failed" message.
  // SECURITY: Never use NEXT_PUBLIC_* for secrets - they are exposed to the client
  const secret = process.env.JWT_SECRET || process.env.JWT_SECRET_KEY;
  if (!secret) {
    throw new Error(
      'JWT_SECRET is not configured. Set JWT_SECRET or JWT_SECRET_KEY environment variable.'
    );
  }
  let payload!: JWTPayload;
  try {
    // Verify token signature, expiry, issuer, and audience.
    // IMPORTANT: issuer/audience MUST match the user-service's JWTConfig values.
    // user-service defaults: JWT_ISSUER=sahool, JWT_AUDIENCE=sahool-api (from root .env)
    // The admin reads these from its own env so they can be overridden if needed.
    const issuer = process.env.JWT_ISSUER || 'sahool';
    const audience = process.env.JWT_AUDIENCE || 'sahool-api';
    const result = await jwtVerify(token, new TextEncoder().encode(secret), {
      issuer,
      audience,
    });
    payload = result.payload;
  } catch (error) {
    if (error instanceof Error) {
      // Use jose error codes for reliable classification — message text varies
      // across jose versions and must not be the only detection mechanism.
      const code = (error as { code?: string }).code;

      if (code === 'ERR_JWT_EXPIRED' || error.message.includes('expired')) {
        throw new Error('Token has expired', { cause: error });
      }
      if (
        code === 'ERR_JWS_SIGNATURE_VERIFICATION_FAILED' ||
        error.message.includes('signature')
      ) {
        throw new Error('Invalid token signature', { cause: error });
      }
      if (code === 'ERR_JWT_CLAIM_VALIDATION_FAILED' || code === 'ERR_JWT_INVALID_CLAIM_VALUE') {
        // Use a generic message to avoid leaking token structure details;
        // attach the original error as `cause` for dev-mode diagnostics.
        throw new Error('Token claim validation failed', { cause: error });
      }
      // Preserve cause for all other jose/runtime errors without leaking details.
      throw new Error('Token verification failed', { cause: error });
    }
    throw new Error('Token verification failed');
  }

  // Validate required fields outside the jose try-catch so that a missing
  // field produces a clear, specific error rather than "Token verification failed".
  if (!payload.sub || !payload.email) {
    throw new Error('Invalid token payload: missing required fields');
  }

  return payload as TokenPayload;
}

/**
 * Decode JWT token without verification (for quick role checks)
 * WARNING: This does not verify the token signature or expiry!
 * Only use when token has already been verified or for non-security-critical operations
 *
 * @param token - JWT token string
 * @returns Decoded token payload (unverified)
 */
export function decodeTokenUnsafe(token: string): TokenPayload | null {
  try {
    const payload = decodeJwt(token);
    return payload as TokenPayload;
  } catch {
    return null;
  }
}

/**
 * Extract user role from token
 * @param token - JWT token string
 * @param verified - Whether to verify token signature (default: true)
 * @returns User role or null if token is invalid
 */
export async function getUserRole(
  token: string,
  verified: boolean = true
): Promise<'admin' | 'supervisor' | 'viewer' | null> {
  try {
    let payload: TokenPayload | null;

    if (verified) {
      payload = await verifyToken(token);
    } else {
      payload = decodeTokenUnsafe(token);
    }

    if (!payload) return null;

    // Extract role from roles array or fallback to role field
    if (payload.roles && Array.isArray(payload.roles) && payload.roles.length > 0) {
      const firstRole = payload.roles[0];
      const extractedRole = firstRole ? firstRole.toLowerCase() : 'viewer';
      if (extractedRole === 'admin' || extractedRole === 'administrator') {
        return 'admin';
      } else if (extractedRole === 'supervisor' || extractedRole === 'manager') {
        return 'supervisor';
      } else {
        return 'viewer';
      }
    } else if (payload.role) {
      return payload.role;
    }

    return null;
  } catch {
    return null;
  }
}

/**
 * Extract user information from token
 * @param token - JWT token string
 * @returns User object or null if token is invalid
 */
export async function getUserFromToken(token: string): Promise<User | null> {
  try {
    const payload = await verifyToken(token);

    // Extract role from roles array or fallback to role field
    let userRole: 'admin' | 'supervisor' | 'viewer' = 'viewer';
    if (payload.roles && Array.isArray(payload.roles) && payload.roles.length > 0) {
      const firstRole = payload.roles[0];
      const extractedRole = firstRole ? firstRole.toLowerCase() : 'viewer';
      if (extractedRole === 'admin' || extractedRole === 'administrator') {
        userRole = 'admin';
      } else if (extractedRole === 'supervisor' || extractedRole === 'manager') {
        userRole = 'supervisor';
      }
    } else if (payload.role) {
      userRole = payload.role;
    }

    return {
      id: payload.sub,
      email: payload.email,
      name: payload.name || payload.email,
      role: userRole,
      tenant_id: (() => {
        const tid = payload.tenant_id || payload.tid;
        return typeof tid === 'string' && isValidUUID(tid) ? tid : undefined;
      })(),
    };
  } catch {
    return null;
  }
}

/**
 * Check if token is expired (without full verification)
 * @param token - JWT token string
 * @returns true if token is expired
 */
export function isTokenExpired(token: string): boolean {
  try {
    const payload = decodeTokenUnsafe(token);

    if (!payload || !payload.exp) {
      return true; // Treat invalid tokens as expired
    }

    // JWT exp is in seconds, Date.now() is in milliseconds
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

/**
 * Check if user has required role
 * @param userRole - User's current role
 * @param requiredRole - Required role for access
 * @returns true if user has sufficient permissions
 */
export function hasRequiredRole(
  userRole: 'admin' | 'supervisor' | 'viewer',
  requiredRole: 'admin' | 'supervisor' | 'viewer'
): boolean {
  const roleHierarchy: Record<'admin' | 'supervisor' | 'viewer', number> = {
    admin: 3,
    supervisor: 2,
    viewer: 1,
  };

  return roleHierarchy[userRole] >= roleHierarchy[requiredRole];
}

/**
 * Check if user has one of the allowed roles
 * @param userRole - User's current role
 * @param allowedRoles - Array of allowed roles
 * @returns true if user has one of the allowed roles
 */
export function hasAnyRole(
  userRole: 'admin' | 'supervisor' | 'viewer',
  allowedRoles: Array<'admin' | 'supervisor' | 'viewer'>
): boolean {
  return allowedRoles.some((role) => hasRequiredRole(userRole, role));
}
