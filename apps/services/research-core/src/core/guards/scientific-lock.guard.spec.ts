import {
  ForbiddenException,
  UnauthorizedException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { ScientificLockGuard } from "./scientific-lock.guard";

describe("ScientificLockGuard", () => {
  let guard: ScientificLockGuard;
  let prisma: any;
  let reflector: Reflector;

  beforeEach(() => {
    prisma = {
      experiment: {
        findFirst: jest.fn(),
        update: jest.fn(),
      },
      experimentAuditLog: {
        create: jest.fn(),
      },
    };
    reflector = new Reflector();
    guard = new ScientificLockGuard(reflector, prisma);
  });

  describe("lockExperiment", () => {
    it("should include tenantId in audit log when locking an experiment", async () => {
      const experimentId = "exp-001";
      const userId = "user-001";
      const tenantId = "tenant-001";
      const reason = "Data review";

      prisma.experiment.findFirst.mockResolvedValue({ tenantId });
      prisma.experiment.update.mockResolvedValue({
        id: experimentId,
        tenantId,
        status: "locked",
        lockedAt: new Date(),
        lockedBy: userId,
      });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.lockExperiment(experimentId, userId, tenantId, reason);

      // SECURITY: the pre-fetch MUST filter by tenantId — not just id —
      // otherwise the returned tenantId leaks a foreign tenant's row and
      // is then used to bind the update, which was the 2026-04-21
      // regression.
      expect(prisma.experiment.findFirst).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id: experimentId, tenantId },
        }),
      );
      expect(prisma.experiment.update).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id_tenantId: { id: experimentId, tenantId } },
        }),
      );
      expect(prisma.experimentAuditLog.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          tenantId,
          experimentId,
          entityType: "experiment",
          entityId: experimentId,
          action: "lock",
          changedBy: userId,
        }),
      });
    });

    it("should pass lock reason in newValues", async () => {
      const reason = "Final review";
      prisma.experiment.findFirst.mockResolvedValue({ tenantId: "tenant-001" });
      prisma.experiment.update.mockResolvedValue({
        id: "exp-001",
        tenantId: "tenant-001",
        status: "locked",
      });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.lockExperiment("exp-001", "user-001", "tenant-001", reason);

      expect(prisma.experimentAuditLog.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          newValues: { status: "locked", lockedBy: "user-001", reason },
        }),
      });
    });

    it("should use select to limit returned fields from experiment.update", async () => {
      prisma.experiment.findFirst.mockResolvedValue({ tenantId: "tenant-001" });
      prisma.experiment.update.mockResolvedValue({
        id: "exp-001",
        tenantId: "tenant-001",
      });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.lockExperiment("exp-001", "user-001", "tenant-001");

      expect(prisma.experiment.update).toHaveBeenCalledWith(
        expect.objectContaining({
          select: { id: true, tenantId: true },
        }),
      );
    });

    it("should throw ForbiddenException when experiment does not exist for tenant", async () => {
      prisma.experiment.findFirst.mockResolvedValue(null);

      await expect(
        guard.lockExperiment("missing", "user-001", "tenant-001"),
      ).rejects.toThrow(ForbiddenException);
      expect(prisma.experiment.update).not.toHaveBeenCalled();
    });

    it("should throw ForbiddenException when tenantId is empty", async () => {
      await expect(
        guard.lockExperiment("exp-001", "user-001", ""),
      ).rejects.toThrow(ForbiddenException);
      expect(prisma.experiment.findFirst).not.toHaveBeenCalled();
      expect(prisma.experiment.update).not.toHaveBeenCalled();
    });
  });

  describe("unlockExperiment", () => {
    it("should include tenantId in audit log when unlocking an experiment", async () => {
      const experimentId = "exp-002";
      const userId = "user-002";
      const tenantId = "tenant-002";
      const lockedAt = new Date("2026-01-01");

      prisma.experiment.findFirst.mockResolvedValue({
        tenantId,
        status: "locked",
        lockedAt,
        lockedBy: "user-001",
      });
      prisma.experiment.update.mockResolvedValue({ id: experimentId });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-002" });

      await guard.unlockExperiment(experimentId, userId, "Review complete", tenantId);

      // Pre-fetch must include tenantId to prevent the IDOR regression.
      expect(prisma.experiment.findFirst).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { id: experimentId, tenantId },
        }),
      );
      expect(prisma.experimentAuditLog.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          tenantId,
          experimentId,
          entityType: "experiment",
          entityId: experimentId,
          action: "unlock",
          changedBy: userId,
        }),
      });
    });

    it("should include old lock state in audit log", async () => {
      const lockedAt = new Date("2026-01-01");
      prisma.experiment.findFirst.mockResolvedValue({
        tenantId: "tenant-001",
        status: "locked",
        lockedAt,
        lockedBy: "user-001",
      });
      prisma.experiment.update.mockResolvedValue({ id: "exp-001" });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.unlockExperiment(
        "exp-001",
        "user-002",
        "Correction needed",
        "tenant-001",
      );

      expect(prisma.experimentAuditLog.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          oldValues: {
            status: "locked",
            lockedAt,
            lockedBy: "user-001",
          },
          newValues: { status: "active", unlockReason: "Correction needed" },
        }),
      });
    });

    it("should select tenantId from experiment and scope the pre-fetch to caller's tenant", async () => {
      prisma.experiment.findFirst.mockResolvedValue({
        tenantId: "tenant-001",
        status: "locked",
        lockedAt: new Date(),
        lockedBy: "user-001",
      });
      prisma.experiment.update.mockResolvedValue({ id: "exp-001" });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.unlockExperiment("exp-001", "user-002", "Done", "tenant-001");

      expect(prisma.experiment.findFirst).toHaveBeenCalledWith({
        where: { id: "exp-001", tenantId: "tenant-001" },
        select: expect.objectContaining({ tenantId: true }),
      });
    });

    it("should throw ForbiddenException if experiment is not locked", async () => {
      prisma.experiment.findFirst.mockResolvedValue({
        tenantId: "tenant-001",
        status: "active",
        lockedAt: null,
        lockedBy: null,
      });

      await expect(
        guard.unlockExperiment("exp-001", "user-001", "reason", "tenant-001"),
      ).rejects.toThrow(ForbiddenException);
    });

    it("should throw ForbiddenException if experiment not found in caller's tenant", async () => {
      prisma.experiment.findFirst.mockResolvedValue(null);

      await expect(
        guard.unlockExperiment("exp-999", "user-001", "reason", "tenant-001"),
      ).rejects.toThrow(ForbiddenException);
    });

    it("should throw ForbiddenException when tenantId is empty", async () => {
      await expect(
        guard.unlockExperiment("exp-001", "user-001", "reason", ""),
      ).rejects.toThrow(ForbiddenException);
      expect(prisma.experiment.findFirst).not.toHaveBeenCalled();
    });
  });

  describe("canActivate", () => {
    it("should allow GET requests without checking lock", async () => {
      const context = createMockContext("GET", {});
      jest.spyOn(reflector, "getAllAndOverride").mockReturnValue(false);

      const result = await guard.canActivate(context);
      expect(result).toBe(true);
    });

    it("should allow requests with bypass decorator", async () => {
      const context = createMockContext("POST", {});
      jest.spyOn(reflector, "getAllAndOverride").mockReturnValue(true);

      const result = await guard.canActivate(context);
      expect(result).toBe(true);
    });

    it("should throw UnauthorizedException when tenantId is missing from JWT", async () => {
      // extractTenantId() throws UnauthorizedException when req.user has no
      // `tid` / `tenantId` claim — canActivate surfaces that unchanged.
      const context = createMockContext("POST", {
        params: { experimentId: "exp-001" },
        user: { id: "user-001" },
      });
      jest.spyOn(reflector, "getAllAndOverride").mockReturnValue(false);

      await expect(guard.canActivate(context)).rejects.toThrow(
        UnauthorizedException,
      );
    });

    it("should block POST to locked experiment", async () => {
      const context = createMockContext("POST", {
        params: { experimentId: "exp-001" },
      });
      jest.spyOn(reflector, "getAllAndOverride").mockReturnValue(false);

      prisma.experiment.findFirst.mockResolvedValue({
        id: "exp-001",
        status: "locked",
        lockedAt: new Date(),
        lockedBy: "user-001",
      });

      await expect(guard.canActivate(context)).rejects.toThrow(
        ForbiddenException,
      );
    });
  });
});

function createMockContext(method: string, request: any): any {
  const req = {
    method,
    params: {},
    query: {},
    body: {},
    user: { id: "user-001", tenantId: "tenant-001" },
    ...request,
  };
  return {
    switchToHttp: () => ({
      getRequest: () => req,
    }),
    getHandler: () => ({}),
    getClass: () => ({}),
  } as any;
}
