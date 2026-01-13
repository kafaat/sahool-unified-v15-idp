/**
 * Service-to-Service Authentication for SAHOOL Platform (TypeScript)
 * JWT-based authentication for microservices communication
 */

import * as jwt from "jsonwebtoken";
import { v4 as uuidv4 } from "uuid";
import { JWTConfig } from "./config";

/**
 * List of services allowed to communicate with each other
 */
export const ALLOWED_SERVICES = [
  "idp-service",
  "farm-service",
  "field-service",
  "crop-service",
  "weather-service",
  "advisory-service",
  "analytics-service",
  "equipment-service",
  "precision-ag-service",
  "notification-service",
  "payment-service",
  "user-service",
  "tenant-service",
  "inventory-service",
];

/**
 * Service communication matrix - defines which services can call which
 * Format: {source_service: [list of allowed target services]}
 */
export const SERVICE_COMMUNICATION_MATRIX: Record<string, string[]> = {
  "idp-service": ALLOWED_SERVICES, // IDP can call all services
  "farm-service": [
    "field-service",
    "crop-service",
    "equipment-service",
    "user-service",
    "tenant-service",
  ],
  "field-service": ["crop-service", "weather-service", "precision-ag-service"],
  "crop-service": [
    "weather-service",
    "advisory-service",
    "precision-ag-service",
  ],
  "weather-service": ["advisory-service", "analytics-service"],
  "advisory-service": ["notification-service", "analytics-service"],
  "analytics-service": ["notification-service"],
  "equipment-service": ["inventory-service", "farm-service"],
  "precision-ag-service": ["weather-service", "field-service", "crop-service"],
  "notification-service": [], // Notification service only receives calls
  "payment-service": ["user-service", "tenant-service", "notification-service"],
  "user-service": ["tenant-service", "notification-service"],
  "tenant-service": ["notification-service"],
  "inventory-service": ["notification-service"],
};

/**
 * Service authentication specific error messages
 */
export const ServiceAuthErrors = {
  INVALID_SERVICE: {
    en: "Invalid service name",
    ar: "اسم الخدمة غير صالح",
    code: "invalid_service",
  },
  UNAUTHORIZED_SERVICE_CALL: {
    en: "Service is not authorized to call the target service",
    ar: "الخدمة غير مصرح لها باستدعاء الخدمة المستهدفة",
    code: "unauthorized_service_call",
  },
  INVALID_SERVICE_TOKEN: {
    en: "Invalid service authentication token",
    ar: "رمز مصادقة الخدمة غير صالح",
    code: "invalid_service_token",
  },
};

/**
 * Service token payload interface
 */
export interface ServiceTokenPayload {
  service_name: string;
  target_service: string;
  jti: string;
  exp: Date;
  iat: Date;
}

/**
 * Service authentication exception
 */
export class ServiceAuthException extends Error {
  constructor(
    public readonly error: { en: string; ar: string; code: string },
    public readonly statusCode: number = 401,
  ) {
    super(error.en);
    this.name = "ServiceAuthException";
  }

  toJSON(lang: string = "en") {
    return {
      error: this.error.code,
      message: lang === "ar" ? this.error.ar : this.error.en,
      statusCode: this.statusCode,
    };
  }
}

/**
 * Service Token Manager for service-to-service authentication.
 *
 * This class handles creation and verification of JWT tokens specifically
 * designed for inter-service communication in the SAHOOL platform.
 *
 * @example
 * ```typescript
 * // Create a service token
 * const token = ServiceToken.create(
 *   'farm-service',
 *   'field-service'
 * );
 *
 * // Verify a service token
 * const payload = ServiceToken.verify(token);
 * console.log(payload.service_name, payload.target_service);
 * ```
 */
export class ServiceToken {
  /**
   * Create a service-to-service JWT token.
   *
   * @param serviceName - Name of the calling service
   * @param targetService - Name of the target service
   * @param ttl - Time-to-live in seconds (default: 300 seconds / 5 minutes)
   * @param extraClaims - Additional claims to include in the token
   * @returns Encoded JWT token string
   * @throws {ServiceAuthException} If service names are invalid or unauthorized
   *
   * @example
   * ```typescript
   * const token = ServiceToken.create(
   *   'farm-service',
   *   'field-service',
   *   600
   * );
   * ```
   */
  static create(
    serviceName: string,
    targetService: string,
    ttl: number = 300,
    extraClaims?: Record<string, any>,
  ): string {
    // Validate service names
    if (!ALLOWED_SERVICES.includes(serviceName)) {
      throw new ServiceAuthException(ServiceAuthErrors.INVALID_SERVICE, 403);
    }

    if (!ALLOWED_SERVICES.includes(targetService)) {
      throw new ServiceAuthException(ServiceAuthErrors.INVALID_SERVICE, 403);
    }

    // Check if service is allowed to call target service
    const allowedTargets = SERVICE_COMMUNICATION_MATRIX[serviceName] || [];
    if (!allowedTargets.includes(targetService)) {
      throw new ServiceAuthException(
        ServiceAuthErrors.UNAUTHORIZED_SERVICE_CALL,
        403,
      );
    }

    const now = Math.floor(Date.now() / 1000);
    const exp = now + ttl;

    // Generate unique token ID
    const jti = uuidv4();

    const payload: any = {
      sub: serviceName, // Subject: calling service
      service_name: serviceName,
      target_service: targetService,
      type: "service", // Special type for service tokens
      exp,
      iat: now,
      iss: JWTConfig.ISSUER,
      aud: JWTConfig.AUDIENCE,
      jti,
    };

    if (extraClaims) {
      Object.assign(payload, extraClaims);
    }

    return jwt.sign(payload, JWTConfig.getSigningKey(), {
      algorithm: JWTConfig.ALGORITHM as jwt.Algorithm,
    });
  }

  /**
   * Verify and decode a service JWT token.
   *
   * @param token - JWT token string
   * @returns ServiceTokenPayload with service_name and target_service
   * @throws {ServiceAuthException} If token is invalid, expired, or not a service token
   *
   * @example
   * ```typescript
   * const payload = ServiceToken.verify(token);
   * const service = payload.service_name;
   * const target = payload.target_service;
   * ```
   */
  static verify(token: string): ServiceTokenPayload {
    try {
      // SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
      // Never trust algorithm from environment variables or token header
      const ALLOWED_ALGORITHMS: jwt.Algorithm[] = [
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
      ];

      // Decode header without verification to check algorithm
      const header = jwt.decode(token, { complete: true })?.header;
      if (!header || !header.alg) {
        throw new ServiceAuthException(
          ServiceAuthErrors.INVALID_SERVICE_TOKEN,
          401,
        );
      }

      // Reject 'none' algorithm explicitly
      if (header.alg.toLowerCase() === "none") {
        throw new ServiceAuthException(
          ServiceAuthErrors.INVALID_SERVICE_TOKEN,
          401,
        );
      }

      // Verify algorithm is in whitelist
      if (!ALLOWED_ALGORITHMS.includes(header.alg as jwt.Algorithm)) {
        throw new ServiceAuthException(
          ServiceAuthErrors.INVALID_SERVICE_TOKEN,
          401,
        );
      }

      const decoded = jwt.verify(token, JWTConfig.getVerificationKey(), {
        algorithms: ALLOWED_ALGORITHMS,
        issuer: JWTConfig.ISSUER,
        audience: JWTConfig.AUDIENCE,
      }) as any;

      // Verify it's a service token
      if (decoded.type !== "service") {
        throw new ServiceAuthException(
          ServiceAuthErrors.INVALID_SERVICE_TOKEN,
          401,
        );
      }

      // Verify required fields
      const serviceName = decoded.service_name;
      const targetService = decoded.target_service;

      if (!serviceName || !targetService) {
        throw new ServiceAuthException(
          ServiceAuthErrors.INVALID_SERVICE_TOKEN,
          401,
        );
      }

      // Verify service names are valid
      if (
        !ALLOWED_SERVICES.includes(serviceName) ||
        !ALLOWED_SERVICES.includes(targetService)
      ) {
        throw new ServiceAuthException(ServiceAuthErrors.INVALID_SERVICE, 403);
      }

      return {
        service_name: serviceName,
        target_service: targetService,
        jti: decoded.jti,
        exp: new Date(decoded.exp * 1000),
        iat: new Date(decoded.iat * 1000),
      };
    } catch (error) {
      if (error instanceof ServiceAuthException) {
        throw error;
      }

      if (error instanceof jwt.TokenExpiredError) {
        throw new ServiceAuthException(
          {
            en: "Authentication token has expired",
            ar: "انتهت صلاحية رمز المصادقة",
            code: "expired_token",
          },
          401,
        );
      }

      if (error instanceof jwt.JsonWebTokenError) {
        throw new ServiceAuthException(
          ServiceAuthErrors.INVALID_SERVICE_TOKEN,
          401,
        );
      }

      throw new ServiceAuthException(
        ServiceAuthErrors.INVALID_SERVICE_TOKEN,
        401,
      );
    }
  }
}

/**
 * Create a service-to-service JWT token.
 *
 * Convenience function for ServiceToken.create().
 *
 * @param serviceName - Name of the calling service
 * @param targetService - Name of the target service
 * @param ttl - Time-to-live in seconds (default: 300 seconds / 5 minutes)
 * @param extraClaims - Additional claims to include in the token
 * @returns Encoded JWT token string
 * @throws {ServiceAuthException} If service names are invalid or unauthorized
 *
 * @example
 * ```typescript
 * const token = createServiceToken(
 *   'farm-service',
 *   'field-service'
 * );
 * ```
 */
export function createServiceToken(
  serviceName: string,
  targetService: string,
  ttl: number = 300,
  extraClaims?: Record<string, any>,
): string {
  return ServiceToken.create(serviceName, targetService, ttl, extraClaims);
}

/**
 * Verify and decode a service JWT token.
 *
 * Convenience function for ServiceToken.verify().
 *
 * @param token - JWT token string
 * @returns ServiceTokenPayload with service_name and target_service
 * @throws {ServiceAuthException} If token is invalid, expired, or not a service token
 *
 * @example
 * ```typescript
 * const payload = verifyServiceToken(token);
 * console.log(`Service: ${payload.service_name} -> ${payload.target_service}`);
 * ```
 */
export function verifyServiceToken(token: string): ServiceTokenPayload {
  return ServiceToken.verify(token);
}

/**
 * Check if a service is authorized to call another service.
 *
 * @param serviceName - Name of the calling service
 * @param targetService - Name of the target service
 * @returns True if authorized, false otherwise
 *
 * @example
 * ```typescript
 * if (isServiceAuthorized('farm-service', 'field-service')) {
 *   // Make the service call
 * }
 * ```
 */
export function isServiceAuthorized(
  serviceName: string,
  targetService: string,
): boolean {
  if (!ALLOWED_SERVICES.includes(serviceName)) {
    return false;
  }

  if (!ALLOWED_SERVICES.includes(targetService)) {
    return false;
  }

  const allowedTargets = SERVICE_COMMUNICATION_MATRIX[serviceName] || [];
  return allowedTargets.includes(targetService);
}

/**
 * Get list of services that a given service can call.
 *
 * @param serviceName - Name of the service
 * @returns List of allowed target service names
 *
 * @example
 * ```typescript
 * const targets = getAllowedTargets('farm-service');
 * console.log(targets); // ['field-service', 'crop-service', ...]
 * ```
 */
export function getAllowedTargets(serviceName: string): string[] {
  return SERVICE_COMMUNICATION_MATRIX[serviceName] || [];
}
