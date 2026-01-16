/**
 * JWT Token Verification Utilities
 * Server-side JWT validation and role extraction
 */

import { jwtVerify, decodeJwt, JWTPayload } from "jose";
import { User } from "@/lib/auth";

/**
 * Extended JWT payload with user information
 */
export interface TokenPayload extends JWTPayload {
  sub: string; // user ID
  email: string;
  role: "admin" | "supervisor" | "viewer";
  name?: string;
  tenant_id?: string;
}

/**
 * Verify JWT token and extract payload
 * @param token - JWT token string
 * @returns Decoded and verified token payload
 * @throws Error if token is invalid, expired, or signature verification fails
 */
export async function verifyToken(token: string): Promise<TokenPayload> {
  try {
    // Get JWT secret from environment
    // SECURITY: Never use NEXT_PUBLIC_* for secrets - they are exposed to the client
    const secret = process.env.JWT_SECRET;

    if (!secret) {
      throw new Error("JWT_SECRET is not configured");
    }

    // Verify token signature and expiry
    const { payload } = await jwtVerify(
      token,
      new TextEncoder().encode(secret),
    );

    // Validate required fields
    if (!payload.sub || !payload.email) {
      throw new Error("Invalid token payload: missing required fields");
    }

    return payload as TokenPayload;
  } catch (error) {
    if (error instanceof Error) {
      // Handle specific JWT errors
      if (error.message.includes("expired")) {
        throw new Error("Token has expired");
      }
      if (error.message.includes("signature")) {
        throw new Error("Invalid token signature");
      }
    }
    throw new Error("Token verification failed");
  }
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
  verified: boolean = true,
): Promise<"admin" | "supervisor" | "viewer" | null> {
  try {
    if (verified) {
      const payload = await verifyToken(token);
      return payload.role || null;
    } else {
      const payload = decodeTokenUnsafe(token);
      return payload?.role || null;
    }
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

    return {
      id: payload.sub,
      email: payload.email,
      name: payload.name || payload.email,
      role: payload.role || "viewer",
      tenant_id: payload.tenant_id,
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
  userRole: "admin" | "supervisor" | "viewer",
  requiredRole: "admin" | "supervisor" | "viewer",
): boolean {
  const roleHierarchy: Record<"admin" | "supervisor" | "viewer", number> = {
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
  userRole: "admin" | "supervisor" | "viewer",
  allowedRoles: Array<"admin" | "supervisor" | "viewer">,
): boolean {
  return allowedRoles.some((role) => hasRequiredRole(userRole, role));
}
