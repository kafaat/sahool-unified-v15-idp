/**
 * Security Audit Service for NestJS Authentication
 * خدمة تدقيق الأمان للمصادقة
 *
 * Provides comprehensive audit logging for security-related events.
 * All security events are logged with structured data for analysis and compliance.
 *
 * SECURITY: This service is critical for incident response and compliance.
 */

import { Injectable, Logger } from "@nestjs/common";

/**
 * Security event types for audit logging
 */
export enum SecurityEventType {
  // Authentication events
  AUTH_SUCCESS = "auth.success",
  AUTH_FAILURE = "auth.failure",
  AUTH_TOKEN_EXPIRED = "auth.token_expired",
  AUTH_TOKEN_INVALID = "auth.token_invalid",
  AUTH_TOKEN_REVOKED = "auth.token_revoked",
  AUTH_TOKEN_MISSING = "auth.token_missing",

  // Authorization events
  AUTHZ_SUCCESS = "authz.success",
  AUTHZ_FAILURE = "authz.failure",
  AUTHZ_ROLE_CHECK_FAILED = "authz.role_check_failed",
  AUTHZ_PERMISSION_CHECK_FAILED = "authz.permission_check_failed",
  AUTHZ_FARM_ACCESS_DENIED = "authz.farm_access_denied",

  // Account events
  ACCOUNT_DISABLED_ACCESS = "account.disabled_access",
  ACCOUNT_UNVERIFIED_ACCESS = "account.unverified_access",
  ACCOUNT_SUSPENDED_ACCESS = "account.suspended_access",
  ACCOUNT_DELETED_ACCESS = "account.deleted_access",

  // Token events
  TOKEN_REVOCATION = "token.revocation",
  TOKEN_USER_REVOCATION = "token.user_revocation",
  TOKEN_TENANT_REVOCATION = "token.tenant_revocation",
  TOKEN_REVOCATION_CHECK_FAILED = "token.revocation_check_failed",

  // Security incidents
  SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious_activity",
  SECURITY_BRUTE_FORCE_ATTEMPT = "security.brute_force_attempt",
  SECURITY_TOKEN_REUSE = "security.token_reuse",
  SECURITY_CLOCK_SKEW = "security.clock_skew",
}

/**
 * Severity levels for security events
 */
export enum SecurityEventSeverity {
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  CRITICAL = "critical",
}

/**
 * Security audit event interface
 */
export interface SecurityAuditEvent {
  /** Event type */
  type: SecurityEventType;
  /** Event severity */
  severity: SecurityEventSeverity;
  /** Timestamp (ISO 8601) */
  timestamp: string;
  /** User ID (if known) */
  userId?: string;
  /** Tenant ID (if known) */
  tenantId?: string;
  /** Token ID (JTI) */
  tokenId?: string;
  /** Request path */
  path?: string;
  /** HTTP method */
  method?: string;
  /** Client IP address */
  clientIp?: string;
  /** User agent */
  userAgent?: string;
  /** Request ID for correlation */
  requestId?: string;
  /** Additional context */
  context?: Record<string, unknown>;
  /** Human-readable message (English) */
  message: string;
  /** Human-readable message (Arabic) */
  messageAr?: string;
}

/**
 * Security Audit Service
 *
 * Centralized service for logging security events with structured data.
 * Supports various event types and severity levels.
 *
 * @example
 * ```typescript
 * @Injectable()
 * export class MyGuard {
 *   constructor(private securityAudit: SecurityAuditService) {}
 *
 *   canActivate(context: ExecutionContext): boolean {
 *     // ... validation logic
 *     if (!valid) {
 *       this.securityAudit.logAuthFailure(userId, 'invalid_token', context);
 *       throw new UnauthorizedException();
 *     }
 *   }
 * }
 * ```
 */
@Injectable()
export class SecurityAuditService {
  private readonly logger = new Logger("SecurityAudit");

  /**
   * Log a security event
   */
  log(event: SecurityAuditEvent): void {
    const logEntry = {
      ...event,
      timestamp: event.timestamp || new Date().toISOString(),
      service: "nestjs-auth",
    };

    // Use appropriate log level based on severity
    switch (event.severity) {
      case SecurityEventSeverity.CRITICAL:
        this.logger.error(JSON.stringify(logEntry));
        break;
      case SecurityEventSeverity.ERROR:
        this.logger.error(JSON.stringify(logEntry));
        break;
      case SecurityEventSeverity.WARNING:
        this.logger.warn(JSON.stringify(logEntry));
        break;
      case SecurityEventSeverity.INFO:
      default:
        this.logger.log(JSON.stringify(logEntry));
        break;
    }
  }

  /**
   * Log successful authentication
   */
  logAuthSuccess(
    userId: string,
    options: {
      tenantId?: string;
      tokenId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
      userAgent?: string;
      requestId?: string;
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.AUTH_SUCCESS,
      severity: SecurityEventSeverity.INFO,
      timestamp: new Date().toISOString(),
      userId,
      message: `Authentication successful for user ${userId}`,
      messageAr: `المصادقة ناجحة للمستخدم ${userId}`,
      ...options,
    });
  }

  /**
   * Log authentication failure
   */
  logAuthFailure(
    reason: string,
    options: {
      userId?: string;
      tenantId?: string;
      tokenId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
      userAgent?: string;
      requestId?: string;
      context?: Record<string, unknown>;
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.AUTH_FAILURE,
      severity: SecurityEventSeverity.WARNING,
      timestamp: new Date().toISOString(),
      message: `Authentication failed: ${reason}`,
      messageAr: `فشلت المصادقة: ${reason}`,
      ...options,
    });
  }

  /**
   * Log token expiration
   */
  logTokenExpired(
    userId: string,
    options: {
      tokenId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.AUTH_TOKEN_EXPIRED,
      severity: SecurityEventSeverity.INFO,
      timestamp: new Date().toISOString(),
      userId,
      message: `Token expired for user ${userId}`,
      messageAr: `انتهت صلاحية الرمز للمستخدم ${userId}`,
      ...options,
    });
  }

  /**
   * Log token revocation access attempt
   */
  logRevokedTokenAccess(
    userId: string,
    reason: string,
    options: {
      tenantId?: string;
      tokenId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.AUTH_TOKEN_REVOKED,
      severity: SecurityEventSeverity.WARNING,
      timestamp: new Date().toISOString(),
      userId,
      message: `Revoked token access attempt for user ${userId}: ${reason}`,
      messageAr: `محاولة وصول برمز ملغى للمستخدم ${userId}: ${reason}`,
      context: { revocationReason: reason },
      ...options,
    });
  }

  /**
   * Log authorization failure
   */
  logAuthzFailure(
    userId: string,
    resource: string,
    requiredRoles?: string[],
    requiredPermissions?: string[],
    options: {
      tenantId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
      userRoles?: string[];
      userPermissions?: string[];
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.AUTHZ_FAILURE,
      severity: SecurityEventSeverity.WARNING,
      timestamp: new Date().toISOString(),
      userId,
      message: `Authorization denied for user ${userId} accessing ${resource}`,
      messageAr: `رفض التفويض للمستخدم ${userId} عند الوصول إلى ${resource}`,
      context: {
        resource,
        requiredRoles,
        requiredPermissions,
        userRoles: options.userRoles,
        userPermissions: options.userPermissions,
      },
      ...options,
    });
  }

  /**
   * Log account status access attempt
   */
  logAccountStatusDenied(
    userId: string,
    status: "disabled" | "unverified" | "suspended" | "deleted",
    options: {
      tenantId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
    } = {},
  ): void {
    const typeMap = {
      disabled: SecurityEventType.ACCOUNT_DISABLED_ACCESS,
      unverified: SecurityEventType.ACCOUNT_UNVERIFIED_ACCESS,
      suspended: SecurityEventType.ACCOUNT_SUSPENDED_ACCESS,
      deleted: SecurityEventType.ACCOUNT_DELETED_ACCESS,
    };

    this.log({
      type: typeMap[status],
      severity: SecurityEventSeverity.WARNING,
      timestamp: new Date().toISOString(),
      userId,
      message: `Access denied for ${status} account: ${userId}`,
      messageAr: `رفض الوصول للحساب ${status === "disabled" ? "المعطل" : status === "unverified" ? "غير الموثق" : status === "suspended" ? "المعلق" : "المحذوف"}: ${userId}`,
      context: { accountStatus: status },
      ...options,
    });
  }

  /**
   * Log token revocation action
   */
  logTokenRevocation(
    action: "token" | "user" | "tenant",
    targetId: string,
    reason: string,
    options: {
      performedBy?: string;
      tenantId?: string;
    } = {},
  ): void {
    const typeMap = {
      token: SecurityEventType.TOKEN_REVOCATION,
      user: SecurityEventType.TOKEN_USER_REVOCATION,
      tenant: SecurityEventType.TOKEN_TENANT_REVOCATION,
    };

    this.log({
      type: typeMap[action],
      severity: SecurityEventSeverity.INFO,
      timestamp: new Date().toISOString(),
      message: `${action} tokens revoked for ${targetId}: ${reason}`,
      messageAr: `تم إلغاء رموز ${action === "token" ? "الرمز" : action === "user" ? "المستخدم" : "المستأجر"} لـ ${targetId}: ${reason}`,
      context: {
        action,
        targetId,
        reason,
        performedBy: options.performedBy,
      },
      ...options,
    });
  }

  /**
   * Log suspicious security activity
   */
  logSuspiciousActivity(
    description: string,
    options: {
      userId?: string;
      tenantId?: string;
      tokenId?: string;
      path?: string;
      method?: string;
      clientIp?: string;
      userAgent?: string;
      context?: Record<string, unknown>;
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.SECURITY_SUSPICIOUS_ACTIVITY,
      severity: SecurityEventSeverity.ERROR,
      timestamp: new Date().toISOString(),
      message: `Suspicious activity detected: ${description}`,
      messageAr: `تم اكتشاف نشاط مشبوه: ${description}`,
      ...options,
    });
  }

  /**
   * Log potential brute force attempt
   */
  logBruteForceAttempt(
    clientIp: string,
    attemptCount: number,
    options: {
      userId?: string;
      path?: string;
      timeWindow?: number;
    } = {},
  ): void {
    this.log({
      type: SecurityEventType.SECURITY_BRUTE_FORCE_ATTEMPT,
      severity: SecurityEventSeverity.CRITICAL,
      timestamp: new Date().toISOString(),
      clientIp,
      message: `Potential brute force attack from ${clientIp}: ${attemptCount} attempts`,
      messageAr: `هجوم محتمل بالقوة الغاشمة من ${clientIp}: ${attemptCount} محاولات`,
      context: {
        attemptCount,
        timeWindow: options.timeWindow,
      },
      ...options,
    });
  }

  /**
   * Extract request metadata from ExecutionContext
   */
  extractRequestMetadata(request: any): {
    path?: string;
    method?: string;
    clientIp?: string;
    userAgent?: string;
    requestId?: string;
  } {
    return {
      path: request?.url || request?.path,
      method: request?.method,
      clientIp:
        request?.ip ||
        request?.headers?.["x-forwarded-for"]?.split(",")[0] ||
        request?.connection?.remoteAddress,
      userAgent: request?.headers?.["user-agent"],
      requestId:
        request?.headers?.["x-request-id"] || request?.headers?.["x-correlation-id"],
    };
  }
}
