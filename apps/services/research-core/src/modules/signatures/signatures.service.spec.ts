import { BadRequestException, NotFoundException } from "@nestjs/common";
import { SignaturesService } from "./signatures.service";

describe("SignaturesService", () => {
  let service: SignaturesService;
  let prisma: any;
  let signatureService: any;

  beforeEach(() => {
    prisma = {
      digitalSignature: {
        create: jest.fn(),
        findMany: jest.fn(),
        findFirst: jest.fn(),
        findUnique: jest.fn(),
        update: jest.fn(),
      },
    };
    signatureService = {
      generateSignature: jest.fn().mockReturnValue({
        signatureHash: "sig-hash-123",
        payloadHash: "payload-hash-456",
        algorithm: "HMAC-SHA256",
        timestamp: new Date("2026-03-07"),
      }),
      verifySignature: jest.fn(),
    };

    service = new SignaturesService(prisma, signatureService);
  });

  describe("signEntity", () => {
    it("should include tenantId when creating a digital signature", async () => {
      const tenantId = "tenant-001";
      prisma.digitalSignature.create.mockResolvedValue({
        id: "sig-001",
        signatureHash: "sig-hash-123",
        timestamp: new Date("2026-03-07"),
      });

      await service.signEntity(
        "experiment",
        "exp-001",
        "user-001",
        "approval",
        { result: "positive" },
        tenantId,
      );

      expect(prisma.digitalSignature.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          tenantId: "tenant-001",
          entityType: "experiment",
          entityId: "exp-001",
          signerId: "user-001",
          purpose: "approval",
        }),
      });
    });

    it("should throw BadRequestException when tenantId is empty", async () => {
      await expect(
        service.signEntity(
          "experiment",
          "exp-001",
          "user-001",
          "approval",
          {},
          "",
        ),
      ).rejects.toThrow(BadRequestException);
    });

    it("should pass request info when provided", async () => {
      prisma.digitalSignature.create.mockResolvedValue({
        id: "sig-001",
        signatureHash: "sig-hash-123",
        timestamp: new Date("2026-03-07"),
      });

      await service.signEntity(
        "experiment",
        "exp-001",
        "user-001",
        "approval",
        { data: "test" },
        "tenant-001",
        { ip: "192.168.1.1", userAgent: "TestAgent/1.0" },
      );

      expect(prisma.digitalSignature.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          tenantId: "tenant-001",
          ipAddress: "192.168.1.1",
          deviceInfo: { userAgent: "TestAgent/1.0" },
        }),
      });
    });

    it("should return signature result with id, hash, timestamp, and verified flag", async () => {
      const timestamp = new Date("2026-03-07");
      prisma.digitalSignature.create.mockResolvedValue({
        id: "sig-001",
        signatureHash: "sig-hash-123",
        timestamp,
      });

      const result = await service.signEntity(
        "experiment",
        "exp-001",
        "user-001",
        "approval",
        {},
        "tenant-001",
      );

      expect(result).toEqual({
        id: "sig-001",
        signatureHash: "sig-hash-123",
        timestamp,
        verified: true,
      });
    });

    it("should handle empty deviceInfo when no userAgent provided", async () => {
      prisma.digitalSignature.create.mockResolvedValue({
        id: "sig-001",
        signatureHash: "sig-hash-123",
        timestamp: new Date(),
      });

      await service.signEntity(
        "log",
        "log-001",
        "user-001",
        "review",
        {},
        "tenant-001",
        { ip: "10.0.0.1" },
      );

      expect(prisma.digitalSignature.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          deviceInfo: {},
        }),
      });
    });
  });

  describe("verifyEntity", () => {
    it("should return not verified when no signatures found", async () => {
      prisma.digitalSignature.findMany.mockResolvedValue([]);

      const result = await service.verifyEntity(
        "experiment",
        "exp-001",
        {},
        "tenant-001",
      );

      expect(result.verified).toBe(false);
    });

    it("should filter by tenantId when querying signatures", async () => {
      prisma.digitalSignature.findMany.mockResolvedValue([]);

      await service.verifyEntity("experiment", "exp-001", {}, "tenant-001");

      expect(prisma.digitalSignature.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({ tenantId: "tenant-001" }),
        orderBy: { timestamp: "desc" },
        take: 100,
      });
    });

    it("should verify with the latest signature", async () => {
      const sig = {
        id: "sig-001",
        signerId: "user-001",
        timestamp: new Date("2026-03-07"),
        signatureHash: "hash-1",
        payloadHash: "payload-1",
        purpose: "approval",
      };
      prisma.digitalSignature.findMany.mockResolvedValue([sig]);
      signatureService.verifySignature.mockReturnValue({
        isValid: true,
        message: "Signature verified successfully",
      });

      const result = await service.verifyEntity(
        "experiment",
        "exp-001",
        { data: "test" },
        "tenant-001",
      );

      expect(result.verified).toBe(true);
      expect(signatureService.verifySignature).toHaveBeenCalled();
    });
  });

  describe("getSignatureHistory", () => {
    it("should filter by tenantId when querying history", async () => {
      prisma.digitalSignature.findMany.mockResolvedValue([]);

      await service.getSignatureHistory("experiment", "exp-001", "tenant-001");

      expect(prisma.digitalSignature.findMany).toHaveBeenCalledWith({
        where: expect.objectContaining({ tenantId: "tenant-001" }),
        orderBy: { timestamp: "desc" },
        take: 100,
      });
    });
  });

  describe("invalidateSignature", () => {
    it("should throw NotFoundException when signature not found", async () => {
      prisma.digitalSignature.findFirst.mockResolvedValue(null);

      await expect(
        service.invalidateSignature("sig-999", "reason", "user-001", "tenant-001"),
      ).rejects.toThrow(NotFoundException);
    });

    it("should scope lookup by tenantId", async () => {
      prisma.digitalSignature.findFirst.mockResolvedValue({ id: "sig-001" });
      prisma.digitalSignature.update.mockResolvedValue({
        id: "sig-001",
        isValid: false,
      });

      await service.invalidateSignature(
        "sig-001",
        "Superseded",
        "user-001",
        "tenant-001",
      );

      expect(prisma.digitalSignature.findFirst).toHaveBeenCalledWith({
        where: { id: "sig-001", tenantId: "tenant-001" },
      });
    });

    it("should invalidate an existing signature", async () => {
      prisma.digitalSignature.findFirst.mockResolvedValue({ id: "sig-001" });
      prisma.digitalSignature.update.mockResolvedValue({
        id: "sig-001",
        isValid: false,
      });

      await service.invalidateSignature(
        "sig-001",
        "Superseded",
        "user-001",
        "tenant-001",
      );

      expect(prisma.digitalSignature.update).toHaveBeenCalledWith({
        where: { id: "sig-001" },
        data: expect.objectContaining({
          isValid: false,
          invalidatedReason: "Superseded",
        }),
      });
    });
  });
});
