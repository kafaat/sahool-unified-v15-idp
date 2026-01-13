import { Injectable, Logger } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import * as crypto from "crypto";

export interface SignaturePayload {
  entityType: string;
  entityId: string;
  signerId: string;
  timestamp: Date;
  data: Record<string, unknown>;
}

export interface SignatureResult {
  signatureHash: string;
  payloadHash: string;
  algorithm: string;
  timestamp: Date;
}

export interface VerificationResult {
  isValid: boolean;
  message: string;
  details?: Record<string, unknown>;
}

@Injectable()
export class SignatureService {
  private readonly logger = new Logger(SignatureService.name);
  private readonly algorithm = "sha256";
  private readonly secretKey: string;

  constructor(private readonly configService: ConfigService) {
    this.secretKey =
      this.configService.get<string>("SIGNATURE_SECRET_KEY") ||
      this.configService.get<string>("JWT_SECRET_KEY") ||
      "default-signature-key-change-in-production";
  }

  /**
   * Generate HMAC-SHA256 signature for research data
   * توليد توقيع رقمي للبيانات البحثية
   */
  generateSignature(payload: SignaturePayload): SignatureResult {
    const timestamp = payload.timestamp || new Date();

    // Create deterministic payload string
    const payloadString = this.createPayloadString(payload);

    // Generate payload hash
    const payloadHash = this.hashData(payloadString);

    // Generate HMAC signature
    const signatureData = `${payloadHash}:${payload.signerId}:${timestamp.toISOString()}`;
    const signatureHash = this.createHmac(signatureData);

    this.logger.debug(
      `Generated signature for ${payload.entityType}:${payload.entityId}`,
    );

    return {
      signatureHash,
      payloadHash,
      algorithm: `HMAC-${this.algorithm.toUpperCase()}`,
      timestamp,
    };
  }

  /**
   * Verify signature integrity
   * التحقق من سلامة التوقيع
   */
  verifySignature(
    payload: SignaturePayload,
    expectedSignatureHash: string,
    expectedPayloadHash: string,
  ): VerificationResult {
    try {
      // Regenerate payload hash
      const payloadString = this.createPayloadString(payload);
      const currentPayloadHash = this.hashData(payloadString);

      // Check payload integrity
      if (currentPayloadHash !== expectedPayloadHash) {
        return {
          isValid: false,
          message: "Data integrity check failed - payload has been modified",
          details: {
            expectedHash: expectedPayloadHash,
            currentHash: currentPayloadHash,
          },
        };
      }

      // Regenerate signature
      const signatureData = `${currentPayloadHash}:${payload.signerId}:${payload.timestamp.toISOString()}`;
      const currentSignatureHash = this.createHmac(signatureData);

      // Verify signature
      const isValid = crypto.timingSafeEqual(
        Buffer.from(currentSignatureHash),
        Buffer.from(expectedSignatureHash),
      );

      if (!isValid) {
        return {
          isValid: false,
          message: "Signature verification failed - invalid signature",
        };
      }

      this.logger.debug(
        `Signature verified for ${payload.entityType}:${payload.entityId}`,
      );

      return {
        isValid: true,
        message: "Signature verified successfully",
      };
    } catch (error) {
      this.logger.error(`Signature verification error: ${error.message}`);
      return {
        isValid: false,
        message: `Verification error: ${error.message}`,
      };
    }
  }

  /**
   * Generate hash for research log data
   * توليد تجزئة لبيانات السجل البحثي
   */
  hashResearchLog(logData: {
    experimentId: string;
    plotId?: string;
    logDate: Date;
    category: string;
    notes?: string;
    measurements?: Record<string, unknown>;
    recordedBy: string;
  }): string {
    const dataString = [
      logData.experimentId || "",
      logData.plotId || "",
      logData.logDate?.toISOString() || "",
      logData.category || "",
      logData.notes || "",
      JSON.stringify(logData.measurements || {}),
      logData.recordedBy || "",
    ].join("|");

    return this.hashData(dataString);
  }

  /**
   * Create deterministic payload string for hashing
   * إنشاء سلسلة حمولة حتمية للتجزئة
   */
  private createPayloadString(payload: SignaturePayload): string {
    // Sort keys to ensure deterministic ordering
    const sortedData = this.sortObject(payload.data);

    return JSON.stringify({
      entityType: payload.entityType,
      entityId: payload.entityId,
      data: sortedData,
    });
  }

  /**
   * Recursively sort object keys for deterministic serialization
   */
  private sortObject(obj: Record<string, unknown>): Record<string, unknown> {
    if (obj === null || typeof obj !== "object") {
      return obj;
    }

    if (Array.isArray(obj)) {
      return obj.map((item) =>
        typeof item === "object"
          ? this.sortObject(item as Record<string, unknown>)
          : item,
      ) as unknown as Record<string, unknown>;
    }

    const sorted: Record<string, unknown> = {};
    const keys = Object.keys(obj).sort();

    for (const key of keys) {
      const value = obj[key];
      sorted[key] =
        typeof value === "object" && value !== null
          ? this.sortObject(value as Record<string, unknown>)
          : value;
    }

    return sorted;
  }

  /**
   * Create SHA-256 hash of data
   */
  private hashData(data: string): string {
    return crypto.createHash(this.algorithm).update(data, "utf8").digest("hex");
  }

  /**
   * Create HMAC signature
   */
  private createHmac(data: string): string {
    return crypto
      .createHmac(this.algorithm, this.secretKey)
      .update(data, "utf8")
      .digest("hex");
  }

  /**
   * Generate unique offline ID for sync
   * توليد معرف فريد للمزامنة غير المتصلة
   */
  generateOfflineId(deviceId: string, timestamp: Date): string {
    const data = `${deviceId}:${timestamp.toISOString()}:${crypto.randomBytes(8).toString("hex")}`;
    return this.hashData(data).substring(0, 32);
  }
}
