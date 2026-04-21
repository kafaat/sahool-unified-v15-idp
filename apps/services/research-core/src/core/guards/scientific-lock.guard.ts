import {
  Injectable,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  InternalServerErrorException,
  Logger,
  Inject,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { PrismaService } from "@/config/prisma.service";
import { extractTenantId } from "../../utils/tenant.utils";

export const BYPASS_LOCK_KEY = "bypassScientificLock";
export const BypassScientificLock = () =>
  Reflect.metadata(BYPASS_LOCK_KEY, true);

export interface ExperimentLockStatus {
  isLocked: boolean;
  lockedAt?: Date;
  lockedBy?: string;
  status: string;
}

/**
 * Scientific Lock Guard
 * حارس قفل البيانات العلمية
 *
 * Prevents modification of locked experiments to maintain
 * scientific data integrity and auditability
 *
 * يمنع تعديل التجارب المقفلة للحفاظ على
 * سلامة البيانات العلمية وقابليتها للتدقيق
 */
@Injectable()
export class ScientificLockGuard implements CanActivate {
  private readonly logger = new Logger(ScientificLockGuard.name);

  constructor(
    private readonly reflector: Reflector,
    @Inject(PrismaService) private readonly prisma: PrismaService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    // Check if endpoint bypasses lock check
    const bypassLock = this.reflector.getAllAndOverride<boolean>(
      BYPASS_LOCK_KEY,
      [context.getHandler(), context.getClass()],
    );

    if (bypassLock) {
      return true;
    }

    const request = context.switchToHttp().getRequest();
    const method = request.method;

    // Only check for modifying operations
    if (!["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
      return true;
    }

    // Extract experiment ID from various sources
    const experimentId = this.extractExperimentId(request);

    if (!experimentId) {
      // No experiment context, allow the request
      return true;
    }

    // Check experiment lock status (scoped to tenant)
    const tenantId = extractTenantId(request);
    const lockStatus = await this.getExperimentLockStatus(experimentId, tenantId);

    if (lockStatus.isLocked) {
      this.logger.warn(
        `Blocked modification attempt on locked experiment ${experimentId} by user ${request.user?.id}`,
      );

      throw new ForbiddenException({
        statusCode: 403,
        error: "Experiment Locked",
        message:
          "لا يمكن تعديل البيانات في تجربة مقفلة. هذه التجربة مؤمنة للحفاظ على سلامة البيانات العلمية.",
        messageEn:
          "Cannot modify data in a locked experiment. This experiment is secured to maintain scientific data integrity.",
        experimentId,
        lockedAt: lockStatus.lockedAt,
        lockedBy: lockStatus.lockedBy,
      });
    }

    return true;
  }

  /**
   * Extract experiment ID from request
   * استخراج معرف التجربة من الطلب
   */
  private extractExperimentId(request: any): string | null {
    // From URL params
    if (request.params?.experimentId) {
      return request.params.experimentId;
    }

    // From query string
    if (request.query?.experimentId) {
      return request.query.experimentId;
    }

    // From request body
    if (request.body?.experimentId) {
      return request.body.experimentId;
    }

    // From nested experiment object
    if (request.body?.experiment?.id) {
      return request.body.experiment.id;
    }

    return null;
  }

  /**
   * Get experiment lock status from database
   * الحصول على حالة قفل التجربة من قاعدة البيانات
   */
  async getExperimentLockStatus(
    experimentId: string,
    tenantId: string,
  ): Promise<ExperimentLockStatus> {
    try {
      const experiment = await this.prisma.experiment.findFirst({
        where: { id: experimentId, tenantId },
        select: {
          id: true,
          status: true,
          lockedAt: true,
          lockedBy: true,
        },
      });

      if (!experiment) {
        return {
          isLocked: false,
          status: "not_found",
        };
      }

      return {
        isLocked: experiment.status === "locked",
        lockedAt: experiment.lockedAt ?? undefined,
        lockedBy: experiment.lockedBy ?? undefined,
        status: experiment.status,
      };
    } catch (error) {
      this.logger.error(
        `SECURITY: Failed to verify experiment lock status for experiment=${experimentId} tenant=${tenantId}. ` +
        `Failing closed to prevent unauthorized modification. Error: ${error instanceof Error ? error.message : String(error)}`,
      );
      // SECURITY: Fail closed - deny modification when lock status cannot be verified
      throw new InternalServerErrorException({
        statusCode: 500,
        error: "Lock Verification Failed",
        message:
          "تعذر التحقق من حالة قفل التجربة. تم رفض العملية للحفاظ على سلامة البيانات.",
        messageEn:
          "Unable to verify experiment lock status. Operation denied to maintain data integrity.",
        experimentId,
      });
    }
  }

  /**
   * Lock an experiment
   * قفل تجربة
   */
  async lockExperiment(
    experimentId: string,
    userId: string,
    reason?: string,
  ): Promise<void> {
    // Pre-fetch tenantId so the mutation can bind via the id_tenantId
    // composite unique. Skipping this and relying on {id} alone would let
    // a cross-tenant caller (should one ever slip past upstream auth)
    // flip an unrelated experiment to locked.
    const existing = await this.prisma.experiment.findFirst({
      where: { id: experimentId },
      select: { tenantId: true },
    });
    if (!existing) {
      throw new ForbiddenException("Experiment not found");
    }

    const experiment = await this.prisma.experiment.update({
      where: {
        id_tenantId: { id: experimentId, tenantId: existing.tenantId },
      },
      data: {
        status: "locked",
        lockedAt: new Date(),
        lockedBy: userId,
        metadata: {
          lockReason: reason,
        },
      },
      select: { id: true, tenantId: true },
    });

    // Log the lock action
    await this.prisma.experimentAuditLog.create({
      data: {
        tenantId: experiment.tenantId,
        experimentId,
        entityType: "experiment",
        entityId: experimentId,
        action: "lock",
        newValues: { status: "locked", lockedBy: userId, reason },
        changedBy: userId,
      },
    });

    this.logger.log(`Experiment ${experimentId} locked by user ${userId}`);
  }

  /**
   * Unlock an experiment (requires admin privileges)
   * فتح قفل تجربة (يتطلب صلاحيات المسؤول)
   */
  async unlockExperiment(
    experimentId: string,
    userId: string,
    reason: string,
  ): Promise<void> {
    const experiment = await this.prisma.experiment.findFirst({
      where: { id: experimentId },
      select: { tenantId: true, status: true, lockedAt: true, lockedBy: true },
    });

    if (!experiment || experiment.status !== "locked") {
      throw new ForbiddenException("Experiment is not locked");
    }

    await this.prisma.experiment.update({
      where: {
        id_tenantId: { id: experimentId, tenantId: experiment.tenantId },
      },
      data: {
        status: "active",
        lockedAt: null,
        lockedBy: null,
      },
    });

    // Log the unlock action with previous state
    await this.prisma.experimentAuditLog.create({
      data: {
        tenantId: experiment.tenantId,
        experimentId,
        entityType: "experiment",
        entityId: experimentId,
        action: "unlock",
        oldValues: {
          status: "locked",
          lockedAt: experiment.lockedAt,
          lockedBy: experiment.lockedBy,
        },
        newValues: { status: "active", unlockReason: reason },
        changedBy: userId,
      },
    });

    this.logger.log(
      `Experiment ${experimentId} unlocked by user ${userId}. Reason: ${reason}`,
    );
  }
}
