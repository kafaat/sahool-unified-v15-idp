/**
 * SAHOOL Shared Authentication Module
 * @module @sahool/nestjs-auth
 *
 * Comprehensive authentication and authorization module for NestJS services
 */

// Export main module
export { AuthModule } from "./auth.module";
export type { AuthModuleOptions } from "./auth.module";

// Export guards
export {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  FarmAccessGuard,
  OptionalAuthGuard,
  ActiveAccountGuard,
} from "./guards/jwt.guard";

export {
  TokenRevocationGuard,
  TokenRevocationInterceptor,
  SkipRevocationCheck,
  SKIP_REVOCATION_CHECK_KEY,
} from "./guards/token-revocation.guard";

// Export strategy
export { JwtStrategy } from "./strategies/jwt.strategy";
export type { JwtPayload, AuthenticatedUser } from "./strategies/jwt.strategy";

// Export services
export { UserValidationService } from "./services/user-validation.service";
export type {
  IUserRepository,
  UserValidationData,
} from "./services/user-validation.service";

export { RedisTokenRevocationStore } from "./services/token-revocation";
export type {
  RevocationInfo,
  RevocationCheckResult,
  RevocationStats,
} from "./services/token-revocation";

// Export decorators
export {
  Public,
  Roles,
  RequirePermissions,
  CurrentUser,
  UserId,
  UserRoles,
  TenantId,
  UserPermissions,
  AuthToken,
  RequestLanguage,
  hasRole,
  hasAnyRole,
  hasPermission,
  hasAnyPermission,
} from "./decorators";

// Export config
export {
  JWTConfig,
  JWTConfigInterface,
  AuthErrors,
  AuthErrorMessage,
} from "./config/jwt.config";

// Export types
export * from "./interfaces";
