/**
 * JWT Authentication Configuration for SAHOOL Platform (TypeScript/NestJS)
 * Centralized configuration for JWT token handling
 *
 * Note: This configuration only supports HS256 algorithm.
 * RS256 with RSA keys has been deprecated.
 */

export interface JWTConfigInterface {
  secret: string;
  algorithm: string;
  accessTokenExpireMinutes: number;
  refreshTokenExpireDays: number;
  issuer: string;
  audience: string;
}

export class JWTConfig {
  /**
   * JWT Secret Key (required)
   */
  static readonly SECRET: string =
    process.env.JWT_SECRET_KEY || process.env.JWT_SECRET || "";

  /**
   * JWT Algorithm - HS256 only (RS256 deprecated)
   */
  static readonly ALGORITHM: string = "HS256";

  /**
   * Access token expiration time in minutes
   */
  static readonly ACCESS_TOKEN_EXPIRE_MINUTES: number = parseInt(
    process.env.JWT_ACCESS_TOKEN_EXPIRE_MINUTES || "30",
    10,
  );

  /**
   * Refresh token expiration time in days
   */
  static readonly REFRESH_TOKEN_EXPIRE_DAYS: number = parseInt(
    process.env.JWT_REFRESH_TOKEN_EXPIRE_DAYS || "7",
    10,
  );

  /**
   * JWT Issuer
   */
  static readonly ISSUER: string = process.env.JWT_ISSUER || "sahool-platform";

  /**
   * JWT Audience
   */
  static readonly AUDIENCE: string = process.env.JWT_AUDIENCE || "sahool-api";

  /**
   * Rate limiting configuration
   */
  static readonly RATE_LIMIT_ENABLED: boolean =
    process.env.RATE_LIMIT_ENABLED !== "false";

  static readonly RATE_LIMIT_REQUESTS: number = parseInt(
    process.env.RATE_LIMIT_REQUESTS || "100",
    10,
  );

  static readonly RATE_LIMIT_WINDOW_SECONDS: number = parseInt(
    process.env.RATE_LIMIT_WINDOW_SECONDS || "60",
    10,
  );

  /**
   * Token revocation configuration
   */
  static readonly TOKEN_REVOCATION_ENABLED: boolean =
    process.env.TOKEN_REVOCATION_ENABLED !== "false";

  /**
   * Redis configuration
   */
  static readonly REDIS_URL?: string = process.env.REDIS_URL;

  static readonly REDIS_HOST: string = process.env.REDIS_HOST || "localhost";

  static readonly REDIS_PORT: number = parseInt(
    process.env.REDIS_PORT || "6379",
    10,
  );

  static readonly REDIS_DB: number = parseInt(process.env.REDIS_DB || "0", 10);

  static readonly REDIS_PASSWORD?: string = process.env.REDIS_PASSWORD;

  /**
   * Validate JWT configuration
   * @throws Error if configuration is invalid
   */
  static validate(): void {
    const env = process.env.NODE_ENV || "development";

    if (env === "production" || env === "staging") {
      if (!this.SECRET || this.SECRET.length < 32) {
        throw new Error(
          "JWT_SECRET must be at least 32 characters in production",
        );
      }
    }
  }

  /**
   * Get signing key for token creation
   */
  static getSigningKey(): string {
    if (!this.SECRET) {
      throw new Error("JWT_SECRET_KEY not configured");
    }
    return this.SECRET;
  }

  /**
   * Get verification key for token validation
   */
  static getVerificationKey(): string {
    if (!this.SECRET) {
      throw new Error("JWT_SECRET_KEY not configured");
    }
    return this.SECRET;
  }

  /**
   * Get configuration object for passport-jwt
   */
  static getJwtOptions() {
    return {
      secret: this.getVerificationKey(),
      signOptions: {
        expiresIn: `${this.ACCESS_TOKEN_EXPIRE_MINUTES}m`,
        issuer: this.ISSUER,
        audience: this.AUDIENCE,
        algorithm: this.ALGORITHM,
      },
      verifyOptions: {
        issuer: this.ISSUER,
        audience: this.AUDIENCE,
        algorithms: [this.ALGORITHM],
      },
    };
  }

  /**
   * Export configuration as object
   */
  static toObject(): JWTConfigInterface {
    return {
      secret: this.SECRET,
      algorithm: this.ALGORITHM,
      accessTokenExpireMinutes: this.ACCESS_TOKEN_EXPIRE_MINUTES,
      refreshTokenExpireDays: this.REFRESH_TOKEN_EXPIRE_DAYS,
      issuer: this.ISSUER,
      audience: this.AUDIENCE,
    };
  }
}

/**
 * Error messages for authentication failures
 */
export interface AuthErrorMessage {
  en: string;
  ar: string;
  code: string;
}

export const AuthErrors = {
  INVALID_TOKEN: {
    en: "Invalid authentication token",
    ar: "رمز المصادقة غير صالح",
    code: "invalid_token",
  },
  EXPIRED_TOKEN: {
    en: "Authentication token has expired",
    ar: "انتهت صلاحية رمز المصادقة",
    code: "expired_token",
  },
  MISSING_TOKEN: {
    en: "Authentication token is missing",
    ar: "رمز المصادقة مفقود",
    code: "missing_token",
  },
  INVALID_CREDENTIALS: {
    en: "Invalid credentials provided",
    ar: "بيانات الاعتماد المقدمة غير صحيحة",
    code: "invalid_credentials",
  },
  INSUFFICIENT_PERMISSIONS: {
    en: "Insufficient permissions to access this resource",
    ar: "أذونات غير كافية للوصول إلى هذا المورد",
    code: "insufficient_permissions",
  },
  ACCOUNT_DISABLED: {
    en: "User account has been disabled",
    ar: "تم تعطيل حساب المستخدم",
    code: "account_disabled",
  },
  ACCOUNT_NOT_VERIFIED: {
    en: "User account is not verified",
    ar: "حساب المستخدم غير موثق",
    code: "account_not_verified",
  },
  TOKEN_REVOKED: {
    en: "Authentication token has been revoked",
    ar: "تم إلغاء رمز المصادقة",
    code: "token_revoked",
  },
  RATE_LIMIT_EXCEEDED: {
    en: "Too many requests. Please try again later",
    ar: "طلبات كثيرة جدا. الرجاء المحاولة مرة أخرى لاحقا",
    code: "rate_limit_exceeded",
  },
  INVALID_ISSUER: {
    en: "Invalid token issuer",
    ar: "مصدر الرمز غير صالح",
    code: "invalid_issuer",
  },
  INVALID_AUDIENCE: {
    en: "Invalid token audience",
    ar: "جمهور الرمز غير صالح",
    code: "invalid_audience",
  },
} as const;

export default JWTConfig;
