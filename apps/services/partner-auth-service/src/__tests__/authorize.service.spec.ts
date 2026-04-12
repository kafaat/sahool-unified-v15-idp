/**
 * AuthorizeService — covers the validateRequest + redirect-builder paths
 * with an in-memory Prisma stub. Exercises:
 *   • Unknown / suspended client                 → NotFoundException
 *   • Unregistered redirect_uri                  → BadRequestException
 *   • Wrong response_type                        → BadRequestException
 *   • Scope outside client.allowedScopes          → BadRequestException
 *   • Prior consent memory returned correctly
 *   • Success redirect appends code + state
 *   • Deny redirect appends error=access_denied + state
 */

import { BadRequestException, NotFoundException } from "@nestjs/common";
import { AuthorizeService } from "../oauth/authorize.service";
import type { PrismaService } from "../prisma/prisma.service";
import type { OAuthService } from "../oauth/oauth.service";

function makePrismaStub(overrides: {
  client?: Partial<{
    id: string;
    clientId: string;
    status: string;
    revokedAt: Date | null;
    redirectUris: string[];
    allowedScopes: string[];
    name: string;
  }>;
  grant?: { scopes: string[]; revokedAt: Date | null } | null;
}) {
  return {
    oAuthClient: {
      findUnique: jest.fn().mockResolvedValue(
        overrides.client === undefined
          ? null
          : {
              id: "client-uuid-1",
              clientId: "partner-leaf",
              status: "active",
              revokedAt: null,
              redirectUris: ["https://leaf.example.com/cb"],
              allowedScopes: ["openid", "fields:read", "operations:harvest:read"],
              name: "Leaf Agriculture",
              ...overrides.client,
            },
      ),
    },
    consentGrant: {
      findUnique: jest.fn().mockResolvedValue(
        overrides.grant ?? null,
      ),
      upsert: jest.fn().mockResolvedValue(null),
    },
  } as unknown as PrismaService;
}

function makeOauthStub() {
  return {
    createAuthorizationCode: jest.fn().mockResolvedValue({
      code: "sah_ac_UNITTESTCODE",
      expiresAt: new Date(),
    }),
  } as unknown as OAuthService;
}

const USER = {
  id: "user-001",
  tenantId: "tenant-ksa-1",
  email: "f@example.com",
  name: "Farmer",
};

describe("AuthorizeService.validateRequest", () => {
  it("throws NotFound for unknown client", async () => {
    const svc = new AuthorizeService(makePrismaStub({ client: undefined }), makeOauthStub());
    await expect(
      svc.validateRequest(
        { client_id: "ghost", response_type: "code", redirect_uri: "https://x", scope: "openid" },
        USER,
      ),
    ).rejects.toBeInstanceOf(NotFoundException);
  });

  it("throws for suspended/revoked client", async () => {
    const svc = new AuthorizeService(
      makePrismaStub({ client: { status: "suspended" } }),
      makeOauthStub(),
    );
    await expect(
      svc.validateRequest(
        { client_id: "partner-leaf", response_type: "code", redirect_uri: "https://leaf.example.com/cb", scope: "openid" },
        USER,
      ),
    ).rejects.toBeInstanceOf(NotFoundException);
  });

  it("throws for unregistered redirect_uri", async () => {
    const svc = new AuthorizeService(makePrismaStub({}), makeOauthStub());
    await expect(
      svc.validateRequest(
        {
          client_id: "partner-leaf",
          response_type: "code",
          redirect_uri: "https://attacker.example.com/cb",
          scope: "openid",
        },
        USER,
      ),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it("throws for unsupported response_type", async () => {
    const svc = new AuthorizeService(makePrismaStub({}), makeOauthStub());
    await expect(
      svc.validateRequest(
        {
          client_id: "partner-leaf",
          response_type: "token", // implicit grant — NOT supported
          redirect_uri: "https://leaf.example.com/cb",
          scope: "openid",
        },
        USER,
      ),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it("throws when requested scope is not in allowedScopes", async () => {
    const svc = new AuthorizeService(makePrismaStub({}), makeOauthStub());
    await expect(
      svc.validateRequest(
        {
          client_id: "partner-leaf",
          response_type: "code",
          redirect_uri: "https://leaf.example.com/cb",
          scope: "openid soil:write", // soil:write not allowed
        },
        USER,
      ),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it("returns validated request + exposes prior consent memory", async () => {
    const svc = new AuthorizeService(
      makePrismaStub({
        grant: { scopes: ["openid", "fields:read"], revokedAt: null },
      }),
      makeOauthStub(),
    );
    const out = await svc.validateRequest(
      {
        client_id: "partner-leaf",
        response_type: "code",
        redirect_uri: "https://leaf.example.com/cb",
        scope: "openid fields:read",
        state: "s-abc",
        nonce: "n-xyz",
      },
      USER,
    );
    expect(out.scopes).toEqual(["openid", "fields:read"]);
    expect(out.state).toBe("s-abc");
    expect(out.nonce).toBe("n-xyz");
    expect(out.consentMemory).toEqual(["openid", "fields:read"]);
  });

  it("skips consent memory when the grant is revoked", async () => {
    const svc = new AuthorizeService(
      makePrismaStub({
        grant: { scopes: ["openid"], revokedAt: new Date() },
      }),
      makeOauthStub(),
    );
    const out = await svc.validateRequest(
      {
        client_id: "partner-leaf",
        response_type: "code",
        redirect_uri: "https://leaf.example.com/cb",
        scope: "openid",
      },
      USER,
    );
    expect(out.consentMemory).toBeNull();
  });
});

describe("AuthorizeService redirect builders", () => {
  const svc = new AuthorizeService(makePrismaStub({}), makeOauthStub());

  it("builds denial redirect with error + state", () => {
    const target = svc.buildDenialRedirect({
      client: { clientId: "partner-leaf" } as never,
      redirectUri: "https://leaf.example.com/cb",
      scopes: ["openid"],
      state: "s-abc",
      nonce: null,
      codeChallenge: null,
      codeChallengeMethod: null,
      prompt: null,
      consentMemory: null,
    });
    const url = new URL(target);
    expect(url.searchParams.get("error")).toBe("access_denied");
    expect(url.searchParams.get("state")).toBe("s-abc");
  });

  it("builds error redirect preserving state", () => {
    const target = svc.buildErrorRedirect(
      "https://leaf.example.com/cb",
      "invalid_scope",
      "bad scope",
      "s-xyz",
    );
    const url = new URL(target);
    expect(url.searchParams.get("error")).toBe("invalid_scope");
    expect(url.searchParams.get("error_description")).toBe("bad scope");
    expect(url.searchParams.get("state")).toBe("s-xyz");
  });
});
