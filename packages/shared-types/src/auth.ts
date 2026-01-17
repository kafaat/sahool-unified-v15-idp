/**
 * Authentication and Authorization Types
 * Shared types for user authentication and permissions
 */

export interface User {
  id: string;
  email: string;
  name: string;
  name_ar?: string;
  role: string;
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
  user: User;
}

export interface JWTPayload {
  sub: string;
  id?: string;
  email?: string;
  role?: string;
  tenantId?: string;
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
