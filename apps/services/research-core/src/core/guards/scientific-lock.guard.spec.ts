import { ForbiddenException } from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { ScientificLockGuard } from "./scientific-lock.guard";

describe("ScientificLockGuard", () => {
  let guard: ScientificLockGuard;
  let prisma: any;
  let reflector: Reflector;

  beforeEach(() => {
    prisma = {
      experiment: {
        findUnique: jest.fn(),
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

      prisma.experiment.update.mockResolvedValue({
        id: experimentId,
        tenantId,
        status: "locked",
        lockedAt: new Date(),
        lockedBy: userId,
      });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.lockExperiment(experimentId, userId, reason);

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
      prisma.experiment.update.mockResolvedValue({
        id: "exp-001",
        tenantId: "tenant-001",
        status: "locked",
      });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.lockExperiment("exp-001", "user-001", reason);

      expect(prisma.experimentAuditLog.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          newValues: { status: "locked", lockedBy: "user-001", reason },
        }),
      });
    });

    it("should use select to limit returned fields from experiment.update", async () => {
      prisma.experiment.update.mockResolvedValue({
        id: "exp-001",
        tenantId: "tenant-001",
      });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.lockExperiment("exp-001", "user-001");

      expect(prisma.experiment.update).toHaveBeenCalledWith(
        expect.objectContaining({
          select: { id: true, tenantId: true },
        }),
      );
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

      await guard.unlockExperiment(experimentId, userId, "Review complete");

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

      await guard.unlockExperiment("exp-001", "user-002", "Correction needed");

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

    it("should select tenantId from experiment", async () => {
      prisma.experiment.findFirst.mockResolvedValue({
        tenantId: "tenant-001",
        status: "locked",
        lockedAt: new Date(),
        lockedBy: "user-001",
      });
      prisma.experiment.update.mockResolvedValue({ id: "exp-001" });
      prisma.experimentAuditLog.create.mockResolvedValue({ id: "audit-001" });

      await guard.unlockExperiment("exp-001", "user-002", "Done");

      expect(prisma.experiment.findFirst).toHaveBeenCalledWith({
        where: { id: "exp-001" },
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
        guard.unlockExperiment("exp-001", "user-001", "reason"),
      ).rejects.toThrow(ForbiddenException);
    });

    it("should throw ForbiddenException if experiment not found", async () => {
      prisma.experiment.findFirst.mockResolvedValue(null);

      await expect(
        guard.unlockExperiment("exp-999", "user-001", "reason"),
      ).rejects.toThrow(ForbiddenException);
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
    user: { id: "user-001" },
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
