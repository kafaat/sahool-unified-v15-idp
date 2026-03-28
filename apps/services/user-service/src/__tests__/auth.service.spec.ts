/**
 * AuthService Tests
 * اختبارات خدمة المصادقة
 *
 * Comprehensive tests for authentication business logic:
 * - Login with account lockout protection
 * - Token generation and refresh with rotation
 * - Logout and token revocation
 * - Password reset flow
 * - OTP send/verify flow
 * - Progressive delay on failed attempts
 */

import { Test, TestingModule } from "@nestjs/testing";
import { UnauthorizedException, BadRequestException } from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcryptjs";
import * as crypto from "crypto";
import { AuthService, JwtPayload, LoginDto, RegisterDto } from "../auth/auth.service";
import { PrismaService } from "../prisma/prisma.service";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { UserStatus } from "../utils/validation";

describe("AuthService", () => {
  let service: AuthService;
  let prisma: PrismaService;
  let jwtService: JwtService;
  let revocationStore: RedisTokenRevocationStore;

  // Mock user data
  const mockUser = {
    id: "user-auth-123",
    tenantId: "tenant-1",
    email: "farmer@sahool.app",
    passwordHash: "$2a$12$hashedpassword",
    firstName: "أحمد",
    lastName: "المزارع",
    role: "FARMER",
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: false,
    failedLoginAttempts: 0,
    lockoutUntil: null,
    lastFailedLoginAt: null,
    lastLoginAt: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockPrismaService: any = {
    user: {
      findUnique: jest.fn(),
      findFirst: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
    refreshToken: {
      create: jest.fn(),
      findUnique: jest.fn(),
      findMany: jest.fn(),
      update: jest.fn(),
      updateMany: jest.fn(),
    },
  };
  // $transaction executes the callback passing the mock itself as the tx client
  mockPrismaService.$transaction = jest.fn((cb: (tx: any) => Promise<any>) => cb(mockPrismaService));

  const mockJwtService = {
    sign: jest.fn().mockReturnValue("mock-jwt-token"),
    verify: jest.fn(),
    decode: jest.fn(),
  };

  const mockRevocationStore = {
    revokeToken: jest.fn().mockResolvedValue(true),
    revokeAllUserTokens: jest.fn().mockResolvedValue(true),
    isTokenRevoked: jest.fn().mockResolvedValue(false),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        { provide: PrismaService, useValue: mockPrismaService },
        { provide: JwtService, useValue: mockJwtService },
        { provide: RedisTokenRevocationStore, useValue: mockRevocationStore },
      ],
    }).compile();

    service = module.get<AuthService>(AuthService);
    prisma = module.get<PrismaService>(PrismaService);
    jwtService = module.get<JwtService>(JwtService);
    revocationStore = module.get<RedisTokenRevocationStore>(RedisTokenRevocationStore);

    jest.clearAllMocks();
  });

  describe("Service Initialization", () => {
    it("should be defined", () => {
      expect(service).toBeDefined();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // LOGIN TESTS | اختبارات تسجيل الدخول
  // ═══════════════════════════════════════════════════════════════════════

  describe("login", () => {
    const loginDto: LoginDto = {
      email: "farmer@sahool.app",
      password: "SecurePass123!",
    };

    it("should login successfully with valid credentials", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser) // Find by email
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null }); // Lockout check

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      const result = await service.login(loginDto);

      expect(result).toBeDefined();
      expect(result.access_token).toBeDefined();
      expect(result.refresh_token).toBeDefined();
      expect(result.token_type).toBe("Bearer");
      expect(result.user.email).toBe(loginDto.email);
      expect(result.user.role).toBe("FARMER");
    });

    it("should throw UnauthorizedException for non-existent user", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.login(loginDto)).rejects.toThrow(UnauthorizedException);
    });

    it("should throw UnauthorizedException for wrong password", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null })
        .mockResolvedValueOnce({ failedLoginAttempts: 0 }); // recordFailedLoginAttempt

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(false));
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      await expect(service.login(loginDto)).rejects.toThrow(UnauthorizedException);
    });

    it("should throw UnauthorizedException if account is locked", async () => {
      const lockedUser = {
        ...mockUser,
        failedLoginAttempts: 5,
        lockoutUntil: new Date(Date.now() + 30 * 60 * 1000), // 30 min from now
      };
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(lockedUser)
        .mockResolvedValueOnce({
          failedLoginAttempts: 5,
          lockoutUntil: lockedUser.lockoutUntil,
        });

      await expect(service.login(loginDto)).rejects.toThrow(
        /Account is temporarily locked/,
      );
    });

    it("should throw UnauthorizedException for inactive user", async () => {
      const inactiveUser = { ...mockUser, status: UserStatus.INACTIVE };
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(inactiveUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null });

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));

      await expect(service.login(loginDto)).rejects.toThrow(UnauthorizedException);
    });

    it("should reset failed login attempts on successful login", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce({ ...mockUser, failedLoginAttempts: 3 })
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null });

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});
      mockPrismaService.refreshToken.findMany.mockResolvedValue([]);

      await service.login(loginDto);

      // Verify reset was called (one of the update calls should reset attempts)
      const updateCalls = mockPrismaService.user.update.mock.calls;
      const resetCall = updateCalls.find(
        (call: any) => call[0].data.failedLoginAttempts === 0,
      );
      expect(resetCall).toBeDefined();
    });

    it("should record failed login attempt on wrong password", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null })
        .mockResolvedValueOnce({ failedLoginAttempts: 1 }); // For recordFailedLoginAttempt

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(false));
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      await expect(service.login(loginDto)).rejects.toThrow(UnauthorizedException);

      // Verify failedLoginAttempts was incremented
      const updateCalls = mockPrismaService.user.update.mock.calls;
      expect(updateCalls.length).toBeGreaterThan(0);
    });

    it("should include tenant ID in response", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null });

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      const result = await service.login(loginDto);

      expect(result.user.tenantId).toBe("tenant-1");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // LOGOUT TESTS | اختبارات تسجيل الخروج
  // ═══════════════════════════════════════════════════════════════════════

  describe("logout", () => {
    it("should revoke token on logout", async () => {
      const mockPayload: JwtPayload = {
        sub: "user-auth-123",
        email: "farmer@sahool.app",
        roles: ["FARMER"],
        tid: "tenant-1",
        jti: "token-jti-123",
        type: "access",
        exp: Math.floor(Date.now() / 1000) + 3600,
      };

      mockJwtService.decode.mockReturnValue(mockPayload);

      await service.logout("mock-token-string", "user-auth-123");

      expect(mockRevocationStore.revokeToken).toHaveBeenCalledWith(
        "token-jti-123",
        expect.objectContaining({
          reason: "user_logout",
          userId: "user-auth-123",
        }),
      );
    });

    it("should throw UnauthorizedException for token without JTI", async () => {
      mockJwtService.decode.mockReturnValue({ sub: "user-123" }); // No jti

      await expect(
        service.logout("invalid-token", "user-auth-123"),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should throw error when revocation fails", async () => {
      const mockPayload: JwtPayload = {
        sub: "user-auth-123",
        email: "farmer@sahool.app",
        roles: ["FARMER"],
        jti: "token-jti-123",
        type: "access",
      };

      mockJwtService.decode.mockReturnValue(mockPayload);
      mockRevocationStore.revokeToken.mockResolvedValue(false);

      await expect(
        service.logout("mock-token", "user-auth-123"),
      ).rejects.toThrow();
    });
  });

  describe("logoutAll", () => {
    it("should revoke all user tokens", async () => {
      await service.logoutAll("user-auth-123");

      expect(mockRevocationStore.revokeAllUserTokens).toHaveBeenCalledWith(
        "user-auth-123",
        "user_logout_all",
      );
    });

    it("should throw error when revoking all tokens fails", async () => {
      mockRevocationStore.revokeAllUserTokens.mockResolvedValue(false);

      await expect(service.logoutAll("user-auth-123")).rejects.toThrow();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // TOKEN REFRESH TESTS | اختبارات تحديث التوكن
  // ═══════════════════════════════════════════════════════════════════════

  describe("refreshToken", () => {
    const mockRefreshPayload: JwtPayload = {
      sub: "user-auth-123",
      email: "farmer@sahool.app",
      roles: ["FARMER"],
      tid: "tenant-1",
      jti: "refresh-jti-123",
      type: "refresh",
      family: "family-uuid-123",
    };

    const mockStoredToken = {
      jti: "refresh-jti-123",
      userId: "user-auth-123",
      family: "family-uuid-123",
      used: false,
      revoked: false,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
    };

    it("should refresh token successfully", async () => {
      mockJwtService.verify.mockReturnValue(mockRefreshPayload);
      mockPrismaService.refreshToken.findUnique.mockResolvedValue(mockStoredToken);
      mockPrismaService.refreshToken.update.mockResolvedValue({});
      mockPrismaService.refreshToken.create.mockResolvedValue({});
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockRevocationStore.revokeToken.mockResolvedValue(true);

      const result = await service.refreshToken("mock-refresh-token");

      expect(result).toBeDefined();
      expect(result.access_token).toBeDefined();
      expect(result.refresh_token).toBeDefined();
      expect(result.token_type).toBe("Bearer");
    });

    it("should throw UnauthorizedException for non-refresh token", async () => {
      mockJwtService.verify.mockReturnValue({
        ...mockRefreshPayload,
        type: "access",
      });

      await expect(
        service.refreshToken("access-token-not-refresh"),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should detect token reuse and invalidate family", async () => {
      mockJwtService.verify.mockReturnValue(mockRefreshPayload);
      mockPrismaService.refreshToken.findUnique.mockResolvedValue({
        ...mockStoredToken,
        used: true, // Already used!
      });
      mockPrismaService.refreshToken.updateMany.mockResolvedValue({ count: 3 });
      mockPrismaService.refreshToken.findMany.mockResolvedValue([
        { jti: "jti-1" },
        { jti: "jti-2" },
      ]);
      mockRevocationStore.revokeToken.mockResolvedValue(true);

      await expect(
        service.refreshToken("reused-refresh-token"),
      ).rejects.toThrow(/Token reuse detected/);

      // Verify entire family was invalidated
      expect(mockPrismaService.refreshToken.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { family: "family-uuid-123" },
          data: { revoked: true },
        }),
      );
    });

    it("should throw UnauthorizedException for revoked token", async () => {
      mockJwtService.verify.mockReturnValue(mockRefreshPayload);
      mockPrismaService.refreshToken.findUnique.mockResolvedValue({
        ...mockStoredToken,
        revoked: true,
      });

      await expect(
        service.refreshToken("revoked-refresh-token"),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should throw UnauthorizedException for expired token", async () => {
      mockJwtService.verify.mockReturnValue(mockRefreshPayload);
      mockPrismaService.refreshToken.findUnique.mockResolvedValue({
        ...mockStoredToken,
        expiresAt: new Date(Date.now() - 1000), // Expired
      });

      await expect(
        service.refreshToken("expired-refresh-token"),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should throw UnauthorizedException if user is inactive", async () => {
      mockJwtService.verify.mockReturnValue(mockRefreshPayload);
      mockPrismaService.refreshToken.findUnique.mockResolvedValue(mockStoredToken);
      mockPrismaService.user.findUnique.mockResolvedValue({
        ...mockUser,
        status: UserStatus.INACTIVE,
      });

      await expect(
        service.refreshToken("valid-refresh-token"),
      ).rejects.toThrow(UnauthorizedException);
    });

    it("should mark used token in database after rotation", async () => {
      mockJwtService.verify.mockReturnValue(mockRefreshPayload);
      mockPrismaService.refreshToken.findUnique.mockResolvedValue(mockStoredToken);
      mockPrismaService.refreshToken.update.mockResolvedValue({});
      mockPrismaService.refreshToken.create.mockResolvedValue({});
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockRevocationStore.revokeToken.mockResolvedValue(true);

      await service.refreshToken("mock-refresh-token");

      expect(mockPrismaService.refreshToken.update).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { jti: "refresh-jti-123" },
          data: expect.objectContaining({
            used: true,
            usedAt: expect.any(Date),
          }),
        }),
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // REGISTRATION TESTS | اختبارات التسجيل
  // ═══════════════════════════════════════════════════════════════════════

  describe("register", () => {
    const registerDto: RegisterDto = {
      email: "newfarmer@sahool.app",
      password: "NewSecurePass123!",
      firstName: "محمد",
      lastName: "العامري",
    };

    it("should register a new user successfully", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null); // No existing user
      mockPrismaService.user.create.mockResolvedValue({
        ...mockUser,
        email: registerDto.email,
        firstName: registerDto.firstName,
        lastName: registerDto.lastName,
      });
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      jest.spyOn(bcrypt, "hash").mockImplementation(() => Promise.resolve("hashed_password"));

      const result = await service.register(registerDto);

      expect(result).toBeDefined();
      expect(result.access_token).toBeDefined();
      expect(result.user.email).toBe(registerDto.email);
    });

    it("should throw if email already exists", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      await expect(service.register(registerDto)).rejects.toThrow(UnauthorizedException);
    });

    it("should hash password with salt rounds 12", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      const hashSpy = jest
        .spyOn(bcrypt, "hash")
        .mockImplementation(() => Promise.resolve("hashed_password"));

      await service.register(registerDto);

      expect(hashSpy).toHaveBeenCalledWith(registerDto.password, 12);
    });

    it("should assign FARMER role by default", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      jest.spyOn(bcrypt, "hash").mockImplementation(() => Promise.resolve("hashed"));

      await service.register(registerDto);

      expect(mockPrismaService.user.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            role: "FARMER",
          }),
        }),
      );
    });

    it("should assign default tenant if not provided", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      jest.spyOn(bcrypt, "hash").mockImplementation(() => Promise.resolve("hashed"));

      await service.register(registerDto);

      expect(mockPrismaService.user.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            tenantId: "a0000000-0000-0000-0000-000000000001",
          }),
        }),
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // PASSWORD RESET TESTS | اختبارات إعادة تعيين كلمة المرور
  // ═══════════════════════════════════════════════════════════════════════

  describe("forgotPassword", () => {
    it("should return success even for non-existent email (prevent enumeration)", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      const result = await service.forgotPassword("nonexistent@sahool.app");

      expect(result.success).toBe(true);
      expect(result.message).toContain("If an account");
    });

    it("should generate reset token for existing user", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      const result = await service.forgotPassword("farmer@sahool.app");

      expect(result.success).toBe(true);
      expect(mockPrismaService.user.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            passwordResetToken: expect.any(String),
            passwordResetExpiry: expect.any(Date),
          }),
        }),
      );
    });
  });

  describe("resetPassword", () => {
    it("should reset password with valid token", async () => {
      const resetToken = crypto.randomBytes(32).toString("hex");
      const tokenHash = crypto.createHash("sha256").update(resetToken).digest("hex");

      mockPrismaService.user.findFirst.mockResolvedValue({
        ...mockUser,
        passwordResetToken: tokenHash,
        passwordResetExpiry: new Date(Date.now() + 3600000),
      });
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.updateMany.mockResolvedValue({ count: 1 });

      jest.spyOn(bcrypt, "hash").mockImplementation(() => Promise.resolve("new_hash"));

      const result = await service.resetPassword(resetToken, "NewSecurePass123!");

      expect(result.success).toBe(true);
    });

    it("should throw BadRequestException for invalid/expired token", async () => {
      mockPrismaService.user.findFirst.mockResolvedValue(null);

      await expect(
        service.resetPassword("invalid-token", "NewPass123!"),
      ).rejects.toThrow(BadRequestException);
    });

    it("should throw BadRequestException for password shorter than 8 chars", async () => {
      const resetToken = crypto.randomBytes(32).toString("hex");
      const tokenHash = crypto.createHash("sha256").update(resetToken).digest("hex");

      mockPrismaService.user.findFirst.mockResolvedValue({
        ...mockUser,
        passwordResetToken: tokenHash,
        passwordResetExpiry: new Date(Date.now() + 3600000),
      });

      await expect(
        service.resetPassword(resetToken, "short"),
      ).rejects.toThrow(BadRequestException);
    });

    it("should revoke all existing refresh tokens after password reset", async () => {
      const resetToken = crypto.randomBytes(32).toString("hex");
      const tokenHash = crypto.createHash("sha256").update(resetToken).digest("hex");

      mockPrismaService.user.findFirst.mockResolvedValue({
        ...mockUser,
        passwordResetToken: tokenHash,
        passwordResetExpiry: new Date(Date.now() + 3600000),
      });
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.updateMany.mockResolvedValue({ count: 3 });

      jest.spyOn(bcrypt, "hash").mockImplementation(() => Promise.resolve("new_hash"));

      await service.resetPassword(resetToken, "NewSecurePass123!");

      expect(mockPrismaService.refreshToken.updateMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: { userId: mockUser.id },
          data: { revoked: true },
        }),
      );
    });

    it("should clear reset token and lockout after password reset", async () => {
      const resetToken = crypto.randomBytes(32).toString("hex");
      const tokenHash = crypto.createHash("sha256").update(resetToken).digest("hex");

      mockPrismaService.user.findFirst.mockResolvedValue({
        ...mockUser,
        passwordResetToken: tokenHash,
        passwordResetExpiry: new Date(Date.now() + 3600000),
      });
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.updateMany.mockResolvedValue({ count: 0 });

      jest.spyOn(bcrypt, "hash").mockImplementation(() => Promise.resolve("new_hash"));

      await service.resetPassword(resetToken, "NewSecurePass123!");

      expect(mockPrismaService.user.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            passwordResetToken: null,
            passwordResetExpiry: null,
            failedLoginAttempts: 0,
            lockoutUntil: null,
          }),
        }),
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // VALIDATE USER TESTS | اختبارات التحقق من المستخدم
  // ═══════════════════════════════════════════════════════════════════════

  describe("validateUser", () => {
    it("should return user object for valid credentials", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));

      const result = await service.validateUser("farmer@sahool.app", "correct-password");

      expect(result).toBeDefined();
      expect(result.id).toBe(mockUser.id);
      // Should not include passwordHash
      expect(result.passwordHash).toBeUndefined();
    });

    it("should return null for invalid credentials", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(false));

      const result = await service.validateUser("farmer@sahool.app", "wrong-password");

      expect(result).toBeNull();
    });

    it("should return null for non-existent user", async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      const result = await service.validateUser("ghost@sahool.app", "password");

      expect(result).toBeNull();
    });
  });

  // ═══════════════════════════════════════════════════════════════════════
  // SECURITY TESTS | اختبارات الأمان
  // ═══════════════════════════════════════════════════════════════════════

  describe("Security", () => {
    it("should not expose user password hash in login response", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null });

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      const result = await service.login({
        email: "farmer@sahool.app",
        password: "SecurePass123!",
      });

      expect((result.user as any).passwordHash).toBeUndefined();
    });

    it("should use same error message for wrong email and wrong password", async () => {
      // Wrong email
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      try {
        await service.login({ email: "wrong@sahool.app", password: "pass" });
      } catch (e: any) {
        expect(e.message).toContain("Invalid email or password");
      }

      // Wrong password (same error message - prevents email enumeration)
      jest.clearAllMocks();
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null })
        .mockResolvedValueOnce({ failedLoginAttempts: 0 });

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(false));
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      try {
        await service.login({ email: "farmer@sahool.app", password: "wrong" });
      } catch (e: any) {
        expect(e.message).toContain("Invalid email or password");
      }
    });

    it("should store refresh token hash in database, not plaintext", async () => {
      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce({ failedLoginAttempts: 0, lockoutUntil: null });

      jest.spyOn(bcrypt, "compare").mockImplementation(() => Promise.resolve(true));
      mockPrismaService.user.update.mockResolvedValue(mockUser);
      mockPrismaService.refreshToken.create.mockResolvedValue({});

      await service.login({ email: "farmer@sahool.app", password: "SecurePass123!" });

      // Verify the token stored is a hash (64 char hex string)
      const createCall = mockPrismaService.refreshToken.create.mock.calls[0][0];
      expect(createCall.data.token).toMatch(/^[a-f0-9]{64}$/);
    });
  });
});
