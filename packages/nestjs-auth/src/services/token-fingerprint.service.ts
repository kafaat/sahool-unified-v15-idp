/**
 * Token Fingerprinting Service for NestJS Authentication
 * خدمة بصمة الرمز للمصادقة
 *
 * Provides token binding to client characteristics to prevent token theft.
 * Generates and validates fingerprints based on client metadata.
 *
 * SECURITY: Token fingerprinting adds an extra layer of protection against
 * token theft by binding tokens to client characteristics.
 */

import { Injectable, Logger } from "@nestjs/common";
import { createHash } from "crypto";

/**
 * Client fingerprint components
 */
export interface FingerprintComponents {
  /** Client User-Agent header */
  userAgent?: string;
  /** Accept-Language header */
  acceptLanguage?: string;
  /** Client IP address (use with caution - IPs can change) */
  clientIp?: string;
  /** Custom client identifier (e.g., device ID) */
  clientId?: string;
  /** TLS fingerprint or certificate info */
  tlsFingerprint?: string;
}

/**
 * Fingerprint validation result
 */
export interface FingerprintValidationResult {
  /** Whether the fingerprint is valid */
  isValid: boolean;
  /** Reason for validation failure (if any) */
  reason?: string;
  /** Partial match score (0-1) for soft validation */
  matchScore?: number;
}

/**
 * Fingerprint configuration options
 */
export interface FingerprintConfig {
  /** Include User-Agent in fingerprint (default: true) */
  includeUserAgent?: boolean;
  /** Include Accept-Language in fingerprint (default: false) */
  includeAcceptLanguage?: boolean;
  /** Include client IP in fingerprint (default: false - IPs change frequently) */
  includeClientIp?: boolean;
  /** Include custom client ID in fingerprint (default: true if provided) */
  includeClientId?: boolean;
  /** Use strict validation (all components must match) vs soft (score-based) */
  strictValidation?: boolean;
  /** Minimum match score for soft validation (default: 0.5) */
  minMatchScore?: number;
  /** Hash algorithm (default: sha256) */
  hashAlgorithm?: string;
}

/**
 * Token Fingerprint Service
 *
 * Generates and validates token fingerprints to bind tokens to clients.
 *
 * @example
 * ```typescript
 * // Generate fingerprint during token creation
 * const fingerprint = this.fingerprintService.generateFingerprint({
 *   userAgent: request.headers['user-agent'],
 *   clientId: request.headers['x-client-id'],
 * });
 *
 * // Include fingerprint in token payload
 * const token = this.jwtService.sign({
 *   sub: userId,
 *   fph: fingerprint,
 * });
 *
 * // Validate fingerprint during authentication
 * const result = this.fingerprintService.validateFingerprint(
 *   tokenPayload.fph,
 *   { userAgent: request.headers['user-agent'], clientId: request.headers['x-client-id'] }
 * );
 * ```
 */
@Injectable()
export class TokenFingerprintService {
  private readonly logger = new Logger(TokenFingerprintService.name);
  private readonly config: FingerprintConfig;

  constructor(config: FingerprintConfig = {}) {
    this.config = {
      includeUserAgent: true,
      includeAcceptLanguage: false,
      includeClientIp: false,
      includeClientId: true,
      strictValidation: false,
      minMatchScore: 0.5,
      hashAlgorithm: "sha256",
      ...config,
    };
  }

  /**
   * Generate a fingerprint hash from client components
   *
   * @param components - Client fingerprint components
   * @returns Fingerprint hash string
   */
  generateFingerprint(components: FingerprintComponents): string {
    const parts: string[] = [];

    if (this.config.includeUserAgent && components.userAgent) {
      // Normalize User-Agent to handle minor variations
      parts.push(`ua:${this.normalizeUserAgent(components.userAgent)}`);
    }

    if (this.config.includeAcceptLanguage && components.acceptLanguage) {
      parts.push(`al:${components.acceptLanguage}`);
    }

    if (this.config.includeClientIp && components.clientIp) {
      parts.push(`ip:${components.clientIp}`);
    }

    if (this.config.includeClientId && components.clientId) {
      parts.push(`cid:${components.clientId}`);
    }

    if (components.tlsFingerprint) {
      parts.push(`tls:${components.tlsFingerprint}`);
    }

    if (parts.length === 0) {
      this.logger.warn("No fingerprint components provided");
      return "";
    }

    const fingerprintData = parts.sort().join("|");
    const hash = createHash(this.config.hashAlgorithm || "sha256")
      .update(fingerprintData)
      .digest("hex")
      .substring(0, 32); // Use first 32 chars for shorter fingerprint

    this.logger.debug(`Generated fingerprint from ${parts.length} components`);
    return hash;
  }

  /**
   * Validate a fingerprint against current client components
   *
   * @param storedFingerprint - Fingerprint from token
   * @param currentComponents - Current client components
   * @returns Validation result
   */
  validateFingerprint(
    storedFingerprint: string | undefined,
    currentComponents: FingerprintComponents,
  ): FingerprintValidationResult {
    // If no fingerprint in token, skip validation (backward compatibility)
    if (!storedFingerprint) {
      this.logger.debug("No fingerprint in token - skipping validation");
      return { isValid: true, reason: "no_fingerprint_in_token" };
    }

    // Generate current fingerprint
    const currentFingerprint = this.generateFingerprint(currentComponents);

    if (!currentFingerprint) {
      this.logger.warn("Could not generate fingerprint from current components");
      return {
        isValid: false,
        reason: "missing_components",
        matchScore: 0,
      };
    }

    // Strict validation: exact match required
    if (this.config.strictValidation) {
      const isValid = storedFingerprint === currentFingerprint;
      if (!isValid) {
        this.logger.warn("Fingerprint mismatch (strict validation)");
      }
      return {
        isValid,
        reason: isValid ? undefined : "fingerprint_mismatch",
        matchScore: isValid ? 1 : 0,
      };
    }

    // Soft validation: calculate match score
    const matchScore = this.calculateMatchScore(
      storedFingerprint,
      currentFingerprint,
      currentComponents,
    );

    const minScore = this.config.minMatchScore || 0.5;
    const isValid = matchScore >= minScore;

    if (!isValid) {
      this.logger.warn(
        `Fingerprint match score ${matchScore.toFixed(2)} below threshold ${minScore}`,
      );
    }

    return {
      isValid,
      reason: isValid ? undefined : "fingerprint_score_too_low",
      matchScore,
    };
  }

  /**
   * Calculate match score for soft validation
   * Compares individual components to allow partial matches
   */
  private calculateMatchScore(
    storedFingerprint: string,
    currentFingerprint: string,
    components: FingerprintComponents,
  ): number {
    // If fingerprints match exactly, return 1
    if (storedFingerprint === currentFingerprint) {
      return 1;
    }

    // For soft validation, we could decode and compare individual components
    // For now, return 0 for mismatch (could be enhanced with component-level comparison)
    // In production, you might store individual component hashes for partial matching
    return 0;
  }

  /**
   * Normalize User-Agent string to handle minor variations
   * Removes version numbers that change frequently
   */
  private normalizeUserAgent(userAgent: string): string {
    // Remove specific version numbers to allow minor browser updates
    // Keep major browser identification
    return userAgent
      .replace(/\d+\.\d+\.\d+\.\d+/g, "X.X.X.X") // Chrome version
      .replace(/\d+\.\d+\.\d+/g, "X.X.X") // Firefox version
      .replace(/\d+\.\d+/g, "X.X") // Safari version
      .replace(/Safari\/\d+/g, "Safari/X") // Safari build
      .replace(/Chrome\/\d+/g, "Chrome/X") // Chrome build
      .replace(/Firefox\/\d+/g, "Firefox/X"); // Firefox build
  }

  /**
   * Extract fingerprint components from HTTP request
   *
   * @param request - HTTP request object
   * @returns Fingerprint components
   */
  extractFromRequest(request: any): FingerprintComponents {
    return {
      userAgent: request?.headers?.["user-agent"],
      acceptLanguage: request?.headers?.["accept-language"],
      clientIp:
        request?.ip ||
        request?.headers?.["x-forwarded-for"]?.split(",")[0] ||
        request?.connection?.remoteAddress,
      clientId:
        request?.headers?.["x-client-id"] || request?.headers?.["x-device-id"],
      tlsFingerprint: request?.headers?.["x-tls-fingerprint"],
    };
  }
}

/**
 * Create default fingerprint service with recommended configuration
 */
export function createDefaultFingerprintService(): TokenFingerprintService {
  return new TokenFingerprintService({
    includeUserAgent: true,
    includeAcceptLanguage: false,
    includeClientIp: false, // IPs change too frequently
    includeClientId: true,
    strictValidation: false,
    minMatchScore: 0.5,
    hashAlgorithm: "sha256",
  });
}
