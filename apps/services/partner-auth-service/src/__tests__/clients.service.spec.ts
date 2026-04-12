/**
 * Unit tests for ClientsService — stubs the Prisma client in-memory so
 * we can exercise validation + transformation logic without a DB.
 */

import { BadRequestException, ConflictException, NotFoundException } from "@nestjs/common";
import { ClientsService } from "../admin/clients.service";
import type { PrismaService } from "../prisma/prisma.service";
import type { OAuthClient } from "../../prisma/generated/client";

function stubClient(overrides: Partial<OAuthClient> = {}): OAuthClient {
  return {
    id: "uuid-1",
    clientId: "test-client",
    clientSecretHash: "bcrypt-hash",
    name: "Test Partner",
    nameAr: null,
    description: null,
    homepageUrl: null,
    logoUrl: null,
    redirectUris: ["https://test.example.com/cb"],
    allowedScopes: ["openid", "fields:read"],
    apiKeyHash: "sha256-hash",
    rateTier: "starter",
    status: "active",
    contactEmail: null,
    createdAt: new Date("2026-01-01"),
    updatedAt: new Date("2026-01-01"),
    revokedAt: null,
    ...overrides,
  } as OAuthClient;
}

function makePrisma(overrides: Partial<{
  findUnique: jest.Mock;
  findFirst: jest.Mock;
  findMany: jest.Mock;
  count: jest.Mock;
  create: jest.Mock;
  update: jest.Mock;
  transaction: jest.Mock;
}> = {}) {
  return {
    oAuthClient: {
      findUnique: overrides.findUnique ?? jest.fn(),
      findFirst: overrides.findFirst ?? jest.fn(),
      findMany: overrides.findMany ?? jest.fn(),
      count: overrides.count ?? jest.fn(),
      create: overrides.create ?? jest.fn(),
      update: overrides.update ?? jest.fn(),
    },
    accessToken: { updateMany: jest.fn().mockResolvedValue({ count: 0 }) },
    refreshToken: { updateMany: jest.fn().mockResolvedValue({ count: 0 }) },
    consentGrant: { updateMany: jest.fn().mockResolvedValue({ count: 0 }) },
    $transaction: overrides.transaction ?? jest.fn().mockImplementation((ops: Promise<unknown>[]) => Promise.all(ops)),
  } as unknown as PrismaService;
}

describe("ClientsService.create", () => {
  it("generates client_id + plaintext secret + api key, returns them once", async () => {
    const prisma = makePrisma({
      create: jest.fn().mockResolvedValue(stubClient({ clientId: "test-partner-abc12345" })),
    });
    const svc = new ClientsService(prisma);

    const out = await svc.create(
      {
        name: "Test Partner",
        redirectUris: ["https://test.example.com/cb"],
        allowedScopes: ["openid", "fields:read"],
      },
      "admin-1",
    );

    expect(out.clientId).toMatch(/^test-partner-/);
    expect(out.clientSecret).toMatch(/^sah_cs_/);
    expect(out.partnerApiKey).toMatch(/^sahk_/);
    expect(out.status).toBe("active");
  });

  it("rejects unknown scopes", async () => {
    const prisma = makePrisma();
    const svc = new ClientsService(prisma);
    await expect(
      svc.create(
        {
          name: "Bad",
          redirectUris: ["https://x/cb"],
          allowedScopes: ["totally:invalid"],
        },
        "admin-1",
      ),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it("rejects redirect_uri containing a fragment", async () => {
    const prisma = makePrisma();
    const svc = new ClientsService(prisma);
    await expect(
      svc.create(
        {
          name: "Bad",
          redirectUris: ["https://x/cb#fragment"],
          allowedScopes: ["openid"],
        },
        "admin-1",
      ),
    ).rejects.toBeInstanceOf(BadRequestException);
  });
});

describe("ClientsService.get", () => {
  it("throws NotFoundException for unknown clientId", async () => {
    const prisma = makePrisma({
      findUnique: jest.fn().mockResolvedValue(null),
    });
    await expect(new ClientsService(prisma).get("ghost")).rejects.toBeInstanceOf(
      NotFoundException,
    );
  });

  it("returns sanitized public view (no secret hashes)", async () => {
    const prisma = makePrisma({
      findUnique: jest.fn().mockResolvedValue(stubClient()),
    });
    const out = await new ClientsService(prisma).get("test-client");
    expect(out.clientId).toBe("test-client");
    expect((out as unknown as Record<string, unknown>).clientSecretHash).toBeUndefined();
    expect((out as unknown as Record<string, unknown>).apiKeyHash).toBeUndefined();
  });
});

describe("ClientsService.rotateSecret / rotateApiKey", () => {
  it("rotateSecret returns new plaintext ONCE", async () => {
    const prisma = makePrisma({
      findUnique: jest.fn().mockResolvedValue(stubClient()),
      update: jest.fn().mockResolvedValue(stubClient()),
    });
    const out = await new ClientsService(prisma).rotateSecret("test-client", "admin-1");
    expect(out.clientSecret).toMatch(/^sah_cs_/);
  });

  it("rotateApiKey returns new plaintext ONCE", async () => {
    const prisma = makePrisma({
      findUnique: jest.fn().mockResolvedValue(stubClient()),
      update: jest.fn().mockResolvedValue(stubClient()),
    });
    const out = await new ClientsService(prisma).rotateApiKey("test-client", "admin-1");
    expect(out.partnerApiKey).toMatch(/^sahk_/);
  });
});

describe("ClientsService.setStatus", () => {
  it("refuses to reactivate a revoked client", async () => {
    const prisma = makePrisma({
      findUnique: jest.fn().mockResolvedValue(stubClient({ status: "revoked", revokedAt: new Date() })),
    });
    await expect(
      new ClientsService(prisma).setStatus("test-client", "active", "admin-1"),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it("cascade revokes all tokens when status→revoked", async () => {
    const prisma = makePrisma({
      findUnique: jest.fn().mockResolvedValue(stubClient()),
      update: jest.fn().mockResolvedValue(stubClient({ status: "revoked", revokedAt: new Date() })),
    });
    await new ClientsService(prisma).setStatus("test-client", "revoked", "admin-1");
    expect((prisma as unknown as { accessToken: { updateMany: jest.Mock } }).accessToken.updateMany).toHaveBeenCalled();
    expect((prisma as unknown as { refreshToken: { updateMany: jest.Mock } }).refreshToken.updateMany).toHaveBeenCalled();
    expect((prisma as unknown as { consentGrant: { updateMany: jest.Mock } }).consentGrant.updateMany).toHaveBeenCalled();
  });
});
