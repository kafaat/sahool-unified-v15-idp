/**
 * AdminGuard — must reject anyone without role=ADMIN.
 */

import { ForbiddenException, UnauthorizedException } from "@nestjs/common";
import type { ExecutionContext } from "@nestjs/common";
import { SignJWT } from "jose";
import { AdminGuard } from "../admin/admin.guard";

const SECRET_STR = "unit-test-" + "x".repeat(32);

beforeAll(() => {
  process.env.SAHOOL_SESSION_SECRET = SECRET_STR;
});

function makeCtx(authz?: string): ExecutionContext {
  const req = { headers: authz ? { authorization: authz } : {} };
  const http = { getRequest: () => req };
  return { switchToHttp: () => http } as unknown as ExecutionContext;
}

async function sign(roles: string[], sub = "admin-1"): Promise<string> {
  const secret = new TextEncoder().encode(SECRET_STR);
  return await new SignJWT({ roles, email: "admin@sahool.com", tid: "sahool" })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(sub)
    .setIssuedAt()
    .setExpirationTime("1h")
    .sign(secret);
}

describe("AdminGuard", () => {
  const guard = new AdminGuard();

  it("rejects missing Authorization header", async () => {
    await expect(guard.canActivate(makeCtx())).rejects.toBeInstanceOf(
      UnauthorizedException,
    );
  });

  it("rejects non-Bearer scheme", async () => {
    await expect(
      guard.canActivate(makeCtx("Basic abc")),
    ).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it("rejects invalid JWT signature", async () => {
    await expect(
      guard.canActivate(makeCtx("Bearer not-a-real-jwt")),
    ).rejects.toBeInstanceOf(UnauthorizedException);
  });

  it("rejects valid JWT without ADMIN role", async () => {
    const token = await sign(["FARMER"]);
    await expect(
      guard.canActivate(makeCtx(`Bearer ${token}`)),
    ).rejects.toBeInstanceOf(ForbiddenException);
  });

  it("accepts valid JWT with ADMIN role (roles array)", async () => {
    const token = await sign(["FARMER", "ADMIN"]);
    const result = await guard.canActivate(makeCtx(`Bearer ${token}`));
    expect(result).toBe(true);
  });

  it("accepts valid JWT with role=ADMIN (singular string claim)", async () => {
    const secret = new TextEncoder().encode(SECRET_STR);
    const token = await new SignJWT({ role: "ADMIN", tid: "sahool" })
      .setProtectedHeader({ alg: "HS256" })
      .setSubject("admin-1")
      .setIssuedAt()
      .setExpirationTime("1h")
      .sign(secret);
    const result = await guard.canActivate(makeCtx(`Bearer ${token}`));
    expect(result).toBe(true);
  });
});
