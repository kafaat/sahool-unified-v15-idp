import { Injectable, Logger, NotFoundException } from "@nestjs/common";
import { PrismaService } from "@/config/prisma.service";
import {
  SignatureService,
  SignaturePayload,
} from "@/core/services/signature.service";

@Injectable()
export class SignaturesService {
  private readonly logger = new Logger(SignaturesService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly signatureService: SignatureService,
  ) {}

  /**
   * Sign an entity (experiment, log, sample, etc.)
   * توقيع كيان (تجربة، سجل، عينة، إلخ)
   */
  async signEntity(
    entityType: string,
    entityId: string,
    signerId: string,
    purpose: string,
    data: Record<string, unknown>,
    request?: { ip?: string; userAgent?: string },
  ) {
    this.logger.log(`Signing ${entityType}:${entityId} by user ${signerId}`);

    const payload: SignaturePayload = {
      entityType,
      entityId,
      signerId,
      timestamp: new Date(),
      data,
    };

    const result = this.signatureService.generateSignature(payload);

    const signature = await this.prisma.digitalSignature.create({
      data: {
        entityType,
        entityId,
        signerId,
        signatureHash: result.signatureHash,
        payloadHash: result.payloadHash,
        algorithm: result.algorithm,
        timestamp: result.timestamp,
        purpose,
        ipAddress: request?.ip,
        deviceInfo: request?.userAgent ? { userAgent: request.userAgent } : {},
      },
    });

    return {
      id: signature.id,
      signatureHash: signature.signatureHash,
      timestamp: signature.timestamp,
      verified: true,
    };
  }

  /**
   * Verify an entity's signature
   * التحقق من توقيع كيان
   */
  async verifyEntity(
    entityType: string,
    entityId: string,
    data: Record<string, unknown>,
  ) {
    const signatures = await this.prisma.digitalSignature.findMany({
      where: {
        entityType,
        entityId,
        isValid: true,
      },
      orderBy: { timestamp: "desc" },
    });

    if (signatures.length === 0) {
      return {
        verified: false,
        message: "No valid signatures found for this entity",
      };
    }

    const latestSignature = signatures[0];

    const payload: SignaturePayload = {
      entityType,
      entityId,
      signerId: latestSignature.signerId,
      timestamp: latestSignature.timestamp,
      data,
    };

    const verification = this.signatureService.verifySignature(
      payload,
      latestSignature.signatureHash,
      latestSignature.payloadHash,
    );

    return {
      verified: verification.isValid,
      message: verification.message,
      signature: {
        id: latestSignature.id,
        signerId: latestSignature.signerId,
        timestamp: latestSignature.timestamp,
        purpose: latestSignature.purpose,
      },
    };
  }

  /**
   * Get signature history for an entity
   * الحصول على تاريخ التوقيعات لكيان
   */
  async getSignatureHistory(entityType: string, entityId: string) {
    return this.prisma.digitalSignature.findMany({
      where: { entityType, entityId },
      orderBy: { timestamp: "desc" },
    });
  }

  /**
   * Invalidate a signature
   * إبطال توقيع
   */
  async invalidateSignature(id: string, reason: string, userId: string) {
    const signature = await this.prisma.digitalSignature.findUnique({
      where: { id },
    });

    if (!signature) {
      throw new NotFoundException(`Signature ${id} not found`);
    }

    return this.prisma.digitalSignature.update({
      where: { id },
      data: {
        isValid: false,
        invalidatedAt: new Date(),
        invalidatedReason: reason,
      },
    });
  }
}
