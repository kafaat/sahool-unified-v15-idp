/**
 * Auth Service Unit Tests
 * اختبارات وحدة خدمة المصادقة
 *
 * Tests for:
 * - User login (valid/invalid credentials)
 * - Token generation and refresh
 * - Logout (single and all devices)
 * - Edge cases: expired tokens, token reuse detection, account status
 */

import { Test, TestingModule } from "@nestjs/testing";
import { UnauthorizedException } from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcryptjs";
import { AuthService, LoginDto, JwtPayload } from "./auth.service";
import { PrismaService } from "../prisma/prisma.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { UserEventsService } from "../events/user-events.service";
import { UserStatus } from "../utils/validation";

describe("AuthService", () => {
  let service: AuthService;
  let prismaService: any;
  let jwtService: jest.Mocked<JwtService>;
  let revocationStore: jest.Mocked<RedisTokenRevocationStore>;
  let userEvents: jest.Mocked<UserEventsService>;

  // Mock data
  const mockUserId = "user-123";
  const mockTenantId = "tenant-123";
  const mockEmail = "test@example.com";
  const mockPassword = "Password123!";
  const mockPasswordHash = "$2a$10$mockHashedPassword";
  const mockJti = "jti-123";
  const mockAccessToken = "mock.access.token";
  const mockRefreshToken = "mock.refresh.token";
  const mockFamily = "family-123";

  const mockUser = {
    id: mockUserId,
    email: mockEmail,
    passwordHash: mockPasswordHash,
    firstName: "Test",
    lastName: "User",
    role: "VIEWER",
    status: UserStatus.ACTIVE,
    emailVerified: true,
    tenantId: mockTenantId,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockRefreshTokenRecord = {
    id: "refresh-token-id",
    userId: mockUserId,
    jti: mockJti,
    family: mockFamily,
    token: mockRefreshToken,
    used: false,
    revoked: false,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    createdAt: new Date(),
    usedAt: null,
    replacedBy: null,
  };

  beforeEach(async () => {
    // Create mock instances
    const mockPrismaService = {
      user: {
        findUnique: jest.fn(),
        update: jest.fn(),
      },
      refreshToken: {
        create: jest.fn(),
        findUnique: jest.fn(),
        update: jest.fn(),
        updateMany: jest.fn(),
        findMany: jest.fn(),
      },
      // Interactive transaction: delegate to the shared mocks so individual
      // mock implementations are reused inside the transaction callback.
      $transaction: jest.fn().mockImplementation(async (callback: (tx: any) => Promise<any>) => {
        const tx = {
          user: { findUnique: jest.fn(), update: jest.fn() },
          refreshToken: {
            findUnique: jest.fn(),
            update: jest.fn(),
            updateMany: jest.fn(),
          },
        };
        // Proxy to the outer mocks so test setup works seamlessly
        tx.user.findUnique.mockImplementation((...args: any[]) =>
          (mockPrismaService.user.findUnique as jest.Mock)(...args),
        );
        tx.user.update.mockImplementation((...args: any[]) =>
          (mockPrismaService.user.update as jest.Mock)(...args),
        );
        tx.refreshToken.findUnique.mockImplementation((...args: any[]) =>
          (mockPrismaService.refreshToken.findUnique as jest.Mock)(...args),
        );
        tx.refreshToken.update.mockImplementation((...args: any[]) =>
          (mockPrismaService.refreshToken.update as jest.Mock)(...args),
        );
        tx.refreshToken.updateMany.mockImplementation((...args: any[]) =>
          (mockPrismaService.refreshToken.updateMany as jest.Mock)(...args),
        );
        return callback(tx);
      }),
    };

    const mockJwtService = {
      sign: jest.fn(),
      verify: jest.fn(),
      decode: jest.fn(),
    };

    const mockRevocationStore = {
      revokeToken: jest.fn(),
      revokeAllUserTokens: jest.fn(),
      isTokenRevoked: jest.fn(),
    };

    // Audit event publisher — records every publish call so tests can
    // assert the compliance trail is being emitted. Each method is a
    // mocked async no-op so the fire-and-forget `void …publish…(…)`
    // pattern resolves cleanly.
    const mockUserEvents: jest.Mocked<Partial<UserEventsService>> = {
      publishUserCreated: jest.fn().mockResolvedValue(undefined),
      publishUserUpdated: jest.fn().mockResolvedValue(undefined),
      publishUserAuthenticated: jest.fn().mockResolvedValue(undefined),
      publishUserLoginFailed: jest.fn().mockResolvedValue(undefined),
      publishUserLoggedOut: jest.fn().mockResolvedValue(undefined),
      publishUserLoggedOutAll: jest.fn().mockResolvedValue(undefined),
      publishUserAccountLocked: jest.fn().mockResolvedValue(undefined),
    } as any;

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
        {
          provide: JwtService,
          useValue: mockJwtService,
        },
        {
          provide: RedisTokenRevocationStore,
          useValue: mockRevocationStore,
        },
        {
          provide: UserEventsService,
          useValue: mockUserEvents,
        },
      ],
    }).compile();

    service = module.get<AuthService>(AuthService);
    prismaService = module.get(PrismaService);
    jwtService = module.get(JwtService);
    revocationStore = module.get(RedisTokenRevocationStore);
    userEvents = module.get(UserEventsService) as jest.Mocked<UserEventsService>;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe("login", () => {
    const loginDto: LoginDto = {
      email: mockEmail,
      password: mockPassword,
    };

    it("should successfully login with valid credentials", async () => {
      // Mock bcrypt.compare to return true
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));

      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.update.mockResolvedValue(mockUser);
      jwtService.sign
        .mockReturnValueOnce(mockAccessToken)
        .mockReturnValueOnce(mockRefreshToken);
      prismaService.refreshToken.create.mockResolvedValue(
        mockRefreshTokenRecord,
      );

      const result = await service.login(loginDto);

      expect(result).toMatchObject({
        access_token: mockAccessToken,
        refresh_token: mockRefreshToken,
        token_type: "Bearer",
        user: {
          id: mockUserId,
          email: mockEmail,
          firstName: "Test",
          lastName: "User",
          role: "VIEWER",
          tenantId: mockTenantId,
        },
      });

      expect(prismaService.user.findUnique).toHaveBeenCalledWith({
        where: { email: mockEmail },
      });
      expect(prismaService.user.update).toHaveBeenCalledWith({
        where: { id: mockUserId },
        data: { lastLoginAt: expect.any(Date) },
      });
      expect(jwtService.sign).toHaveBeenCalledTimes(2);
      expect(prismaService.refreshToken.create).toHaveBeenCalled();
    });

    it("should throw UnauthorizedException for non-existent user", async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.login(loginDto)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.login(loginDto)).rejects.toThrow(
        "Invalid email or password",
      );
    });

    it("should throw UnauthorizedException for invalid password", async () => {
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(false));
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      await expect(service.login(loginDto)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.login(loginDto)).rejects.toThrow(
        "Invalid email or password",
      );
    });

    it("should throw UnauthorizedException for inactive user", async () => {
      const inactiveUser = { ...mockUser, status: UserStatus.INACTIVE };
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));
      prismaService.user.findUnique.mockResolvedValue(inactiveUser);

      await expect(service.login(loginDto)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.login(loginDto)).rejects.toThrow(
        "Account is not available. Please contact support.",
      );
    });

    it("should throw UnauthorizedException for suspended user", async () => {
      const suspendedUser = { ...mockUser, status: UserStatus.SUSPENDED };
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));
      prismaService.user.findUnique.mockResolvedValue(suspendedUser);

      await expect(service.login(loginDto)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.login(loginDto)).rejects.toThrow(
        "Account is not available. Please contact support.",
      );
    });

    it("should allow login even if email is not verified", async () => {
      const unverifiedUser = { ...mockUser, emailVerified: false };
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));
      prismaService.user.findUnique.mockResolvedValue(unverifiedUser);
      prismaService.user.update.mockResolvedValue(unverifiedUser);
      jwtService.sign
        .mockReturnValueOnce(mockAccessToken)
        .mockReturnValueOnce(mockRefreshToken);
      prismaService.refreshToken.create.mockResolvedValue(
        mockRefreshTokenRecord,
      );

      const result = await service.login(loginDto);

      expect(result).toBeDefined();
      expect(result.access_token).toBe(mockAccessToken);
    });
  });

  describe("logout", () => {
    const mockToken = "Bearer mock.jwt.token";
    const mockDecodedPayload: JwtPayload = {
      sub: mockUserId,
      email: mockEmail,
      roles: ["VIEWER"],
      jti: mockJti,
      type: "access",
      exp: Math.floor(Date.now() / 1000) + 3600,
      tid: mockTenantId,
    };

    it("should successfully logout and revoke token", async () => {
      jwtService.decode.mockReturnValue(mockDecodedPayload);
      revocationStore.revokeToken.mockResolvedValue(true);

      await service.logout(mockToken, mockUserId);

      expect(jwtService.decode).toHaveBeenCalledWith(mockToken);
      expect(revocationStore.revokeToken).toHaveBeenCalledWith(
        mockJti,
        expect.objectContaining({
          reason: "user_logout",
          userId: mockUserId,
          tenantId: mockTenantId,
        }),
      );
    });

    it("should throw UnauthorizedException for invalid token (no JTI)", async () => {
      const invalidPayload = { ...mockDecodedPayload, jti: undefined };
      jwtService.decode.mockReturnValue(invalidPayload);

      await expect(service.logout(mockToken, mockUserId)).rejects.toThrow(
        UnauthorizedException,
      );
    });

    it("should throw error if revocation fails", async () => {
      jwtService.decode.mockReturnValue(mockDecodedPayload);
      revocationStore.revokeToken.mockResolvedValue(false);

      await expect(service.logout(mockToken, mockUserId)).rejects.toThrow(
        "Logout failed",
      );
    });

    it("should handle expired token during logout", async () => {
      const expiredPayload = {
        ...mockDecodedPayload,
        exp: Math.floor(Date.now() / 1000) - 3600, // Expired 1 hour ago
      };
      jwtService.decode.mockReturnValue(expiredPayload);
      revocationStore.revokeToken.mockResolvedValue(true);

      await service.logout(mockToken, mockUserId);

      expect(revocationStore.revokeToken).toHaveBeenCalledWith(
        mockJti,
        expect.objectContaining({
          expiresIn: 60, // Minimum TTL
        }),
      );
    });
  });

  describe("logoutAll", () => {
    it("should successfully logout from all devices", async () => {
      revocationStore.revokeAllUserTokens.mockResolvedValue(true);

      await service.logoutAll(mockUserId);

      expect(revocationStore.revokeAllUserTokens).toHaveBeenCalledWith(
        mockUserId,
        "user_logout_all",
      );
    });

    it("should throw error if revoking all tokens fails", async () => {
      revocationStore.revokeAllUserTokens.mockResolvedValue(false);

      await expect(service.logoutAll(mockUserId)).rejects.toThrow(
        "Logout from all devices failed",
      );
    });
  });

  // ── Audit events (Phase 2a — compliance trail) ─────────────────────
  //
  // These tests guarantee that every auth-related code path publishes
  // exactly one audit NATS event with the right shape. The events land
  // in audit-service which persists them to the audit_log table
  // (see apps/services/audit-service/src/persistence.py). A regression
  // here means compliance data stops flowing.
  describe("audit events", () => {
    const ctx = { ipAddress: "10.0.0.1", userAgent: "unit-test/1.0" };

    beforeEach(() => {
      jwtService.sign
        .mockReturnValue(mockAccessToken);
      prismaService.user.update.mockResolvedValue(mockUser);
      prismaService.refreshToken.create.mockResolvedValue(mockRefreshTokenRecord);
    });

    it("publishes UserAuthenticated on successful login", async () => {
      jest.spyOn(bcrypt, "compare").mockResolvedValue(true as never);
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      await service.login({ email: mockEmail, password: mockPassword }, ctx);

      expect(userEvents.publishUserAuthenticated).toHaveBeenCalledTimes(1);
      expect(userEvents.publishUserAuthenticated).toHaveBeenCalledWith(
        expect.objectContaining({
          tenantId: mockTenantId,
          userId: mockUserId,
          ipAddress: ctx.ipAddress,
          userAgent: ctx.userAgent,
        }),
      );
      expect(userEvents.publishUserLoginFailed).not.toHaveBeenCalled();
    });

    it("publishes UserLoginFailed with reason=user_not_found when user does not exist", async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(
        service.login({ email: "ghost@example.com", password: "x" }, ctx),
      ).rejects.toThrow(UnauthorizedException);

      expect(userEvents.publishUserLoginFailed).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: "user_not_found",
          identifier: "ghost@example.com",
          ipAddress: ctx.ipAddress,
        }),
      );
      expect(userEvents.publishUserAuthenticated).not.toHaveBeenCalled();
    });

    it("publishes UserLoginFailed with reason=invalid_password on wrong password", async () => {
      jest.spyOn(bcrypt, "compare").mockResolvedValue(false as never);
      prismaService.user.findUnique.mockResolvedValue({
        ...mockUser,
        failedLoginAttempts: 0,
        lockedUntil: null,
      });

      await expect(
        service.login({ email: mockEmail, password: "bad" }, ctx),
      ).rejects.toThrow(UnauthorizedException);

      expect(userEvents.publishUserLoginFailed).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: "invalid_password",
          userId: mockUserId,
          tenantId: mockTenantId,
        }),
      );
    });

    it("publishes UserLoggedOut when the single-session logout revokes successfully", async () => {
      const payload: JwtPayload = {
        sub: mockUserId,
        email: mockEmail,
        roles: ["VIEWER"],
        tid: mockTenantId,
        jti: mockJti,
        type: "access",
        exp: Math.floor(Date.now() / 1000) + 3600,
      };
      jwtService.decode.mockReturnValue(payload as any);
      revocationStore.revokeToken.mockResolvedValue(true);

      await service.logout("mock.jwt.token", mockUserId);

      expect(userEvents.publishUserLoggedOut).toHaveBeenCalledWith(
        expect.objectContaining({ tenantId: mockTenantId, userId: mockUserId }),
      );
    });

    it("publishes UserLoggedOutAll when the revoke-all path succeeds with a tenantId", async () => {
      revocationStore.revokeAllUserTokens.mockResolvedValue(true);

      await service.logoutAll(mockUserId, mockTenantId);

      expect(userEvents.publishUserLoggedOutAll).toHaveBeenCalledWith(
        expect.objectContaining({ userId: mockUserId, tenantId: mockTenantId }),
      );
    });

    it("does not fail the login flow if an audit publish rejects", async () => {
      jest.spyOn(bcrypt, "compare").mockResolvedValue(true as never);
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      (userEvents.publishUserAuthenticated as jest.Mock).mockRejectedValueOnce(
        new Error("NATS down"),
      );

      await expect(
        service.login({ email: mockEmail, password: mockPassword }, ctx),
      ).resolves.toMatchObject({ access_token: mockAccessToken });
    });
  });

  describe("refreshToken", () => {
    const mockRefreshPayload: JwtPayload = {
      sub: mockUserId,
      email: mockEmail,
      roles: ["VIEWER"],
      jti: mockJti,
      type: "refresh",
      family: mockFamily,
      exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
      tid: mockTenantId,
    };

    it("should successfully refresh token", async () => {
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(
        mockRefreshTokenRecord,
      );
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.refreshToken.update.mockResolvedValue({
        ...mockRefreshTokenRecord,
        used: true,
      });
      jwtService.sign
        .mockReturnValueOnce(mockAccessToken)
        .mockReturnValueOnce(mockRefreshToken);
      prismaService.refreshToken.create.mockResolvedValue(
        mockRefreshTokenRecord,
      );
      revocationStore.revokeToken.mockResolvedValue(true);

      const result = await service.refreshToken(mockRefreshToken);

      expect(result).toMatchObject({
        access_token: mockAccessToken,
        refresh_token: mockRefreshToken,
        token_type: "Bearer",
      });

      // The service makes exactly two separate update calls:
      // 1. Inside the transaction: mark token as used
      // 2. Outside the transaction: record the replacement JTI
      expect(prismaService.refreshToken.update).toHaveBeenCalledTimes(2);
      expect(prismaService.refreshToken.update).toHaveBeenNthCalledWith(
        1,
        expect.objectContaining({
          where: { jti: mockJti },
          data: expect.objectContaining({
            used: true,
            usedAt: expect.any(Date),
          }),
        }),
      );
      expect(prismaService.refreshToken.update).toHaveBeenNthCalledWith(
        2,
        expect.objectContaining({
          where: { jti: mockJti },
          data: expect.objectContaining({
            replacedBy: expect.any(String),
          }),
        }),
      );
    });

    it("should throw UnauthorizedException for invalid token type", async () => {
      const invalidPayload = { ...mockRefreshPayload, type: "access" };
      jwtService.verify.mockReturnValue(invalidPayload);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Invalid token type",
      );
    });

    it("should throw UnauthorizedException for unknown refresh token", async () => {
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(null);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Invalid refresh token",
      );
    });

    it("should detect token reuse and invalidate family", async () => {
      const usedToken = { ...mockRefreshTokenRecord, used: true };
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(usedToken);
      prismaService.refreshToken.updateMany.mockResolvedValue({ count: 2 });
      prismaService.refreshToken.findMany.mockResolvedValue([
        { jti: "jti-1" },
        { jti: "jti-2" },
      ]);
      revocationStore.revokeToken.mockResolvedValue(true);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Token reuse detected",
      );

      expect(prismaService.refreshToken.updateMany).toHaveBeenCalledWith({
        where: { family: mockFamily },
        data: { revoked: true },
      });
    });

    it("should throw UnauthorizedException for revoked token", async () => {
      const revokedToken = { ...mockRefreshTokenRecord, revoked: true };
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(revokedToken);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Token has been revoked",
      );
    });

    it("should throw UnauthorizedException for expired token", async () => {
      const expiredToken = {
        ...mockRefreshTokenRecord,
        expiresAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
      };
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(expiredToken);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Refresh token has expired",
      );
    });

    it("should throw UnauthorizedException if user is not active", async () => {
      const inactiveUser = { ...mockUser, status: UserStatus.INACTIVE };
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(
        mockRefreshTokenRecord,
      );
      prismaService.user.findUnique.mockResolvedValue(inactiveUser);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "User account is not active",
      );
    });

    it("should throw UnauthorizedException if user does not exist", async () => {
      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(
        mockRefreshTokenRecord,
      );
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "User account is not active",
      );
    });

    it("should handle JWT verification errors", async () => {
      jwtService.verify.mockImplementation(() => {
        throw new Error("Invalid signature");
      });

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        UnauthorizedException,
      );
      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Invalid refresh token",
      );
    });
  });

  describe("validateUser", () => {
    it("should return user without password for valid credentials", async () => {
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.validateUser(mockEmail, mockPassword);

      expect(result).toBeDefined();
      expect(result.id).toBe(mockUserId);
      expect(result.email).toBe(mockEmail);
      expect(result.passwordHash).toBeUndefined();
    });

    it("should return null for invalid credentials", async () => {
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(false));
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.validateUser(mockEmail, "wrongpassword");

      expect(result).toBeNull();
    });

    it("should return null for non-existent user", async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      const result = await service.validateUser(mockEmail, mockPassword);

      expect(result).toBeNull();
    });
  });

  describe("edge cases", () => {
    it("should handle database errors during login", async () => {
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));
      prismaService.user.findUnique.mockRejectedValue(
        new Error("Database error"),
      );

      await expect(
        service.login({ email: mockEmail, password: mockPassword }),
      ).rejects.toThrow();
    });

    it("should handle JWT signing errors", async () => {
      jest
        .spyOn(bcrypt, "compare")
        .mockImplementation(() => Promise.resolve(true));
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      jwtService.sign.mockImplementation(() => {
        throw new Error("Signing error");
      });

      await expect(
        service.login({ email: mockEmail, password: mockPassword }),
      ).rejects.toThrow();
    });

    it("should handle Redis errors during logout gracefully", async () => {
      const mockDecodedPayload: JwtPayload = {
        sub: mockUserId,
        email: mockEmail,
        roles: ["VIEWER"],
        jti: mockJti,
        type: "access",
        exp: Math.floor(Date.now() / 1000) + 3600,
      };

      jwtService.decode.mockReturnValue(mockDecodedPayload);
      revocationStore.revokeToken.mockRejectedValue(
        new Error("Redis connection error"),
      );

      await expect(service.logout("token", mockUserId)).rejects.toThrow();
    });
  });

  describe("token family security", () => {
    it("should maintain token family across refresh cycles", async () => {
      const mockRefreshPayload: JwtPayload = {
        sub: mockUserId,
        email: mockEmail,
        roles: ["VIEWER"],
        jti: mockJti,
        type: "refresh",
        family: mockFamily,
        exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
      };

      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(
        mockRefreshTokenRecord,
      );
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.refreshToken.update.mockResolvedValue({
        ...mockRefreshTokenRecord,
        used: true,
      });

      const capturedPayloads: any[] = [];
      jwtService.sign.mockImplementation((payload) => {
        capturedPayloads.push(payload);
        return "token";
      });

      prismaService.refreshToken.create.mockResolvedValue(
        mockRefreshTokenRecord,
      );
      revocationStore.revokeToken.mockResolvedValue(true);

      await service.refreshToken(mockRefreshToken);

      // Verify that refresh token has the same family
      const refreshPayload = capturedPayloads.find((p) => p.type === "refresh");
      expect(refreshPayload.family).toBe(mockFamily);
    });

    it("should revoke all tokens in family when reuse is detected", async () => {
      const usedToken = { ...mockRefreshTokenRecord, used: true };
      const mockRefreshPayload: JwtPayload = {
        sub: mockUserId,
        email: mockEmail,
        roles: ["VIEWER"],
        jti: mockJti,
        type: "refresh",
        family: mockFamily,
        exp: Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60,
      };

      jwtService.verify.mockReturnValue(mockRefreshPayload);
      prismaService.refreshToken.findUnique.mockResolvedValue(usedToken);
      prismaService.refreshToken.updateMany.mockResolvedValue({ count: 3 });
      prismaService.refreshToken.findMany.mockResolvedValue([
        { jti: "jti-1" },
        { jti: "jti-2" },
        { jti: "jti-3" },
      ]);
      revocationStore.revokeToken.mockResolvedValue(true);

      await expect(service.refreshToken(mockRefreshToken)).rejects.toThrow(
        "Token reuse detected",
      );

      expect(revocationStore.revokeToken).toHaveBeenCalledTimes(3);
    });
  });
});
