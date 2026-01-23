/**
 * SAHOOL Authentication and Authorization Types
 * Comprehensive type definitions for user authentication, JWT tokens, and RBAC
 *
 * The SAHOOL platform uses JWT-based authentication with role-based access control (RBAC).
 * Multi-tenant support is built-in with tenant isolation at the data level.
 */

import type { BilingualName, ISODateTimeString } from "./common";

// ═══════════════════════════════════════════════════════════════════════════════
// User Role Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * User roles in the SAHOOL platform
 *
 * Roles are hierarchical and determine access levels:
 * - super_admin: Platform-wide administration
 * - admin: Tenant-level administration
 * - manager: Farm/operation management
 * - agronomist: Agricultural expert with advisory capabilities
 * - expert: Domain expert (pest, disease, etc.)
 * - researcher: Research and data analysis
 * - field_officer: Field operations and inspections
 * - operator: Equipment and irrigation operation
 * - farmer: Primary user, farm owner/worker
 * - viewer: Read-only access
 */
export type UserRole =
  | "super_admin"
  | "admin"
  | "manager"
  | "agronomist"
  | "expert"
  | "researcher"
  | "field_officer"
  | "operator"
  | "farmer"
  | "viewer";

/**
 * Permission action types
 */
export type PermissionAction =
  | "create"
  | "read"
  | "update"
  | "delete"
  | "list"
  | "export"
  | "import"
  | "approve"
  | "assign"
  | "execute";

/**
 * Permission scope levels
 */
export type PermissionScope =
  | "own"     // Only own resources
  | "tenant"  // All resources within tenant
  | "global"; // All resources (super_admin only)

/**
 * Resource types that can have permissions
 */
export type PermissionResource =
  | "user"
  | "farm"
  | "field"
  | "task"
  | "alert"
  | "sensor"
  | "equipment"
  | "report"
  | "advisory"
  | "diagnosis"
  | "irrigation"
  | "settings"
  | "billing"
  | "audit";

// ═══════════════════════════════════════════════════════════════════════════════
// User Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Base user entity
 */
export interface User extends BilingualName {
  /** Unique user identifier */
  id: string;

  /** User email address (unique) */
  email: string;

  /** Primary role */
  role: UserRole;

  /** Additional roles (for users with multiple roles) */
  roles?: UserRole[];

  /** Tenant/organization identifier */
  tenantId: string;

  /** Tenant name (denormalized for display) */
  tenantName?: string;

  /** Granted permissions */
  permissions?: string[];

  /** User's governorate/region */
  governorate?: string;

  /** Contact phone number */
  phone?: string;

  /** Profile avatar URL */
  avatarUrl?: string;

  /** Whether user account is active */
  isActive: boolean;

  /** Whether email is verified */
  isEmailVerified?: boolean;

  /** Whether two-factor authentication is enabled */
  is2FAEnabled?: boolean;

  /** Preferred language */
  preferredLanguage?: "ar" | "en";

  /** Timezone */
  timezone?: string;

  /** Last login timestamp */
  lastLoginAt?: ISODateTimeString;

  /** Account creation timestamp */
  createdAt: ISODateTimeString;

  /** Last update timestamp */
  updatedAt: ISODateTimeString;
}

/**
 * User with snake_case properties (API compatibility)
 * @deprecated Use User interface with camelCase. This is for legacy API support.
 */
export interface UserSnakeCase {
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

/**
 * Authenticated user (includes auth token)
 */
export interface AuthenticatedUser extends User {
  /** Current access token */
  token?: string;

  /** Token expiration timestamp */
  tokenExpiresAt?: ISODateTimeString;
}

// ═══════════════════════════════════════════════════════════════════════════════
// JWT Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * JWT token payload structure
 */
export interface JWTPayload {
  /** Subject (user ID) - standard JWT claim */
  sub: string;

  /** User ID (alias for sub) */
  id?: string;

  /** User email */
  email?: string;

  /** User role */
  role?: UserRole;

  /** Tenant ID (camelCase) */
  tenantId?: string;

  /** Tenant ID (snake_case, legacy support) */
  tenant_id?: string;

  /** User permissions */
  permissions?: string[];

  /** Token type */
  type?: "access" | "refresh";

  /** Issued at timestamp (Unix seconds) */
  iat?: number;

  /** Expiration timestamp (Unix seconds) */
  exp?: number;

  /** Not before timestamp (Unix seconds) */
  nbf?: number;

  /** JWT ID (unique identifier) */
  jti?: string;

  /** Issuer */
  iss?: string;

  /** Audience */
  aud?: string | string[];
}

/**
 * Decoded and validated JWT token
 */
export interface ValidatedToken extends JWTPayload {
  /** Whether token is valid */
  isValid: true;

  /** Remaining time until expiration (seconds) */
  expiresIn: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Permission and Role Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Permission definition
 */
export interface Permission {
  /** Permission ID */
  id: string;

  /** Permission name (e.g., "field:create") */
  name: string;

  /** Display name */
  displayName?: string;

  /** Display name in Arabic */
  displayNameAr?: string;

  /** Resource this permission applies to */
  resource: PermissionResource;

  /** Action allowed */
  action: PermissionAction;

  /** Scope of the permission */
  scope?: PermissionScope;

  /** Description */
  description?: string;
}

/**
 * Role definition with permissions
 */
export interface Role {
  /** Role ID */
  id: string;

  /** Role name (e.g., "admin") */
  name: UserRole;

  /** Display name */
  displayName: string;

  /** Display name in Arabic */
  displayNameAr?: string;

  /** Description */
  description?: string;

  /** Permissions granted to this role */
  permissions: Permission[];

  /** Whether this is a system role (cannot be modified) */
  isSystemRole?: boolean;

  /** Role hierarchy level (higher = more privileges) */
  level?: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Authentication Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Login request
 */
export interface LoginRequest {
  /** User email */
  email: string;

  /** User password */
  password: string;

  /** Remember me flag (extends session) */
  rememberMe?: boolean;

  /** 2FA code (if enabled) */
  twoFactorCode?: string;

  /** Device fingerprint for security */
  deviceFingerprint?: string;
}

/**
 * Login response
 */
export interface LoginResponse {
  /** Access token (JWT) */
  accessToken: string;

  /** Refresh token */
  refreshToken?: string;

  /** Token type (usually "Bearer") */
  tokenType: string;

  /** Expires in seconds */
  expiresIn: number;

  /** Expiration timestamp */
  expiresAt?: ISODateTimeString;

  /** Authenticated user */
  user: User;

  /** Whether 2FA is required */
  requires2FA?: boolean;

  /** 2FA setup required */
  requiresSetup2FA?: boolean;
}

/**
 * Legacy login response format
 * @deprecated Use LoginResponse
 */
export interface LegacyLoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  user: User;
}

/**
 * Token refresh request
 */
export interface RefreshTokenRequest {
  /** Refresh token */
  refreshToken: string;
}

/**
 * Token refresh response
 */
export interface RefreshTokenResponse {
  /** New access token */
  accessToken: string;

  /** New refresh token (if rotated) */
  refreshToken?: string;

  /** Expires in seconds */
  expiresIn: number;
}

/**
 * Password reset request
 */
export interface PasswordResetRequest {
  /** User email */
  email: string;
}

/**
 * Password reset confirmation
 */
export interface PasswordResetConfirmRequest {
  /** Reset token from email */
  token: string;

  /** New password */
  newPassword: string;

  /** Confirm new password */
  confirmPassword: string;
}

/**
 * Password change request (for authenticated users)
 */
export interface PasswordChangeRequest {
  /** Current password */
  currentPassword: string;

  /** New password */
  newPassword: string;

  /** Confirm new password */
  confirmPassword: string;
}

/**
 * User registration request
 */
export interface RegisterRequest {
  /** Email address */
  email: string;

  /** Password */
  password: string;

  /** Full name */
  name: string;

  /** Name in Arabic */
  nameAr?: string;

  /** Phone number */
  phone?: string;

  /** Governorate/region */
  governorate?: string;

  /** Preferred language */
  preferredLanguage?: "ar" | "en";

  /** Tenant ID (if joining existing tenant) */
  tenantId?: string;

  /** Invitation code */
  invitationCode?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Session and Security Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * User session information
 */
export interface UserSession {
  /** Session ID */
  id: string;

  /** User ID */
  userId: string;

  /** Device type */
  deviceType?: "web" | "mobile" | "tablet" | "api";

  /** Browser/client info */
  userAgent?: string;

  /** IP address */
  ipAddress?: string;

  /** Geolocation (approximate) */
  location?: string;

  /** Session start time */
  createdAt: ISODateTimeString;

  /** Last activity time */
  lastActiveAt: ISODateTimeString;

  /** Session expiration */
  expiresAt: ISODateTimeString;

  /** Is current session */
  isCurrent?: boolean;
}

/**
 * Two-factor authentication setup
 */
export interface TwoFactorSetup {
  /** Secret key */
  secret: string;

  /** QR code data URL */
  qrCodeUrl: string;

  /** Backup codes */
  backupCodes: string[];
}

/**
 * Two-factor verification request
 */
export interface TwoFactorVerifyRequest {
  /** TOTP code */
  code: string;

  /** Use backup code */
  isBackupCode?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Authentication State Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Client-side authentication state
 */
export interface AuthState {
  /** Current user */
  user: User | null;

  /** Whether user is authenticated */
  isAuthenticated: boolean;

  /** Whether auth state is loading */
  isLoading: boolean;

  /** Current access token */
  token?: string;

  /** Token expiration */
  tokenExpiresAt?: ISODateTimeString;

  /** Auth error message */
  error?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards and Utilities
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for User
 */
export function isUser(obj: unknown): obj is User {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "email" in obj &&
    "role" in obj
  );
}

/**
 * Type guard for valid UserRole
 */
export function isUserRole(value: unknown): value is UserRole {
  const validRoles: UserRole[] = [
    "super_admin",
    "admin",
    "manager",
    "agronomist",
    "expert",
    "researcher",
    "field_officer",
    "operator",
    "farmer",
    "viewer",
  ];
  return typeof value === "string" && validRoles.includes(value as UserRole);
}

/**
 * Type guard for JWTPayload
 */
export function isJWTPayload(obj: unknown): obj is JWTPayload {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "sub" in obj &&
    typeof (obj as JWTPayload).sub === "string"
  );
}

/**
 * Type guard for LoginResponse
 */
export function isLoginResponse(obj: unknown): obj is LoginResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "accessToken" in obj &&
    "user" in obj
  );
}

/**
 * Check if user has a specific role
 */
export function hasRole(user: User, role: UserRole): boolean {
  if (user.role === role) return true;
  return user.roles?.includes(role) ?? false;
}

/**
 * Check if user has any of the specified roles
 */
export function hasAnyRole(user: User, roles: UserRole[]): boolean {
  return roles.some((role) => hasRole(user, role));
}

/**
 * Check if user is an admin (admin or super_admin)
 */
export function isAdmin(user: User): boolean {
  return hasAnyRole(user, ["admin", "super_admin"]);
}

/**
 * Check if user has a specific permission
 */
export function hasPermission(user: User, permission: string): boolean {
  return user.permissions?.includes(permission) ?? false;
}

/**
 * Get tenant ID from JWT payload (handles both formats)
 */
export function getTenantIdFromPayload(payload: JWTPayload): string | undefined {
  return payload.tenantId ?? payload.tenant_id;
}
