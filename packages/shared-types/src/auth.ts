/**
 * Authentication and Authorization Types
 * Shared types for user authentication and permissions
 */

export interface User {
  id: string;
  email: string;
  name: string;
  /** Arabic display name */
  nameAr?: string;
  /** @deprecated Use `nameAr` instead */
  name_ar?: string;
  role: string;
  /** @deprecated Use `tenantId` instead */
  tenant_id?: string;
  tenantId?: string;
  permissions?: string[];
  createdAt?: string;
  updatedAt?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  /**
   * Whether a 2-FA verification step is required before the token is active.
   * When `true`, `access_token` is an empty string and `temp_token` should be
   * passed to the `/auth/login/2fa` endpoint to complete authentication.
   */
  requires_2fa?: boolean;
  /**
   * Short-lived token returned alongside `requires_2fa: true`.
   * Must be passed to `/auth/login/2fa` — not usable as a bearer token.
   */
  temp_token?: string;
  user: User;
}

export interface JWTPayload {
  sub: string;
  id?: string;
  email?: string;
  role?: string;
  tenantId?: string;
  /** @deprecated Use `tenantId` instead */
  tenant_id?: string;
  permissions?: string[];
  iat?: number;
  exp?: number;
}

export interface AuthenticatedUser extends User {
  token?: string;
}

export type UserRole =
  | "admin"
  | "super_admin"
  | "manager"
  | "operator"
  | "expert"
  | "farmer"
  | "agronomist"
  | "researcher"
  | "field_officer"
  | "viewer";

export interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
  scope?: "own" | "tenant" | "global";
}

export interface Role {
  id: string;
  name: string;
  displayName?: string;
  permissions: Permission[];
}
