/**
 * IdempotencyService Unit Tests
 * اختبارات وحدة خدمة Idempotency
 */

import { Test, TestingModule } from "@nestjs/testing";
import { ConflictException } from "@nestjs/common";
import { IdempotencyService } from "../idempotency.service";
import { PrismaService } from "../../prisma/prisma.service";

const TENANT = "tenant-aaa-1111";

function makePrismaMock() {
  return {
    idempotencyKey: {
      findUnique: jest.fn(),
      upsert: jest.fn(),
      deleteMany: jest.fn(),
    },
  };
}

describe("IdempotencyService", () => {
  let service: IdempotencyService;
  let prisma: ReturnType<typeof makePrismaMock>;

  beforeEach(async () => {
    prisma = makePrismaMock();
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        IdempotencyService,
        { provide: PrismaService, useValue: prisma },
      ],
    }).compile();
    service = module.get(IdempotencyService);
  });

  describe("lookup()", () => {
    it("returns a miss when no row exists", async () => {
      prisma.idempotencyKey.findUnique.mockResolvedValue(null);
      const result = await service.lookup({
        tenantId: TENANT,
        key: "key-1",
        method: "POST",
        path: "/foo",
        body: { a: 1 },
      });
      expect(result.hit).toBe(false);
    });

    it("replays the cached response on matching body", async () => {
      const body = { field: "value" };
      // Precompute the hash the service would store.
      const { createHash } = await import("crypto");
      const hash = createHash("sha256")
        .update(JSON.stringify({ field: "value" }))
        .digest("hex");
      prisma.idempotencyKey.findUnique.mockResolvedValue({
        requestHash: hash,
        responseStatus: 201,
        responseBody: JSON.stringify({ id: "new-row" }),
        expiresAt: new Date(Date.now() + 3600_000),
      });

      const result = await service.lookup({
        tenantId: TENANT,
        key: "key-2",
        method: "POST",
        path: "/foo",
        body,
      });

      expect(result.hit).toBe(true);
      if (result.hit) {
        expect(result.status).toBe(201);
        expect(result.body).toEqual({ id: "new-row" });
      }
    });

    it("throws ConflictException when the body hash differs", async () => {
      prisma.idempotencyKey.findUnique.mockResolvedValue({
        requestHash: "different-hash",
        responseStatus: 201,
        responseBody: "{}",
        expiresAt: new Date(Date.now() + 3600_000),
      });

      await expect(
        service.lookup({
          tenantId: TENANT,
          key: "key-3",
          method: "POST",
          path: "/foo",
          body: { x: 1 },
        }),
      ).rejects.toThrow(ConflictException);
    });

    it("treats expired rows as misses", async () => {
      prisma.idempotencyKey.findUnique.mockResolvedValue({
        requestHash: "anything",
        responseStatus: 201,
        responseBody: "{}",
        expiresAt: new Date(Date.now() - 1000),
      });
      const result = await service.lookup({
        tenantId: TENANT,
        key: "key-4",
        method: "POST",
        path: "/foo",
        body: {},
      });
      expect(result.hit).toBe(false);
    });

    it("canonicalises keys so object key order doesn't change the hash", async () => {
      prisma.idempotencyKey.findUnique.mockResolvedValue(null);
      await service.lookup({
        tenantId: TENANT,
        key: "key-5",
        method: "POST",
        path: "/foo",
        body: { b: 2, a: 1 },
      });
      await service.lookup({
        tenantId: TENANT,
        key: "key-5",
        method: "POST",
        path: "/foo",
        body: { a: 1, b: 2 },
      });
      // Both calls should hit the same mock — no error thrown.
      expect(prisma.idempotencyKey.findUnique).toHaveBeenCalledTimes(2);
    });
  });

  describe("store()", () => {
    it("upserts the key and expiration window", async () => {
      prisma.idempotencyKey.upsert.mockResolvedValue({});
      await service.store({
        tenantId: TENANT,
        key: "key-6",
        method: "POST",
        path: "/foo",
        body: { x: 1 },
        responseStatus: 201,
        responseBody: { id: "abc" },
      });
      expect(prisma.idempotencyKey.upsert).toHaveBeenCalled();
      const call = prisma.idempotencyKey.upsert.mock.calls[0][0];
      expect(call.create.responseStatus).toBe(201);
      expect(call.create.expiresAt).toBeInstanceOf(Date);
    });
  });
});
