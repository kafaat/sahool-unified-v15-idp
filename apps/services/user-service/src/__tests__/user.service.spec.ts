/**
 * User Service Unit Tests
 * اختبارات وحدة خدمة المستخدمين
 *
 * Coverage:
 * - Health endpoint responses
 * - Module initialization
 * - DTO validation (CreateUserDto)
 * - Password strength & phone validation constraints
 * - UserRole and UserStatus enum values
 *
 * NOTE: JwtAuthGuard tests are in src/auth/jwt-auth.guard.spec.ts
 * NOTE: RolesGuard tests are in src/auth/roles.guard.spec.ts
 * NOTE: UsersService CRUD tests are in src/users/users.service.spec.ts
 * NOTE: AuthService tests are in src/auth/auth.service.spec.ts
 */

import { Test, TestingModule } from "@nestjs/testing";
import {
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { UsersService } from "../users/users.service";
import { PrismaService } from "../prisma/prisma.service";
import { UserEventsService } from "../events/user-events.service";

// Shared no-op events stub for every TestingModule below — UsersService
// emits NATS events on every CRUD path now, but tests don't care about
// those side-effects.
const userEventsStub = {
  publishUserCreated: jest.fn().mockResolvedValue(undefined),
  publishUserUpdated: jest.fn().mockResolvedValue(undefined),
  publishUserRoleChanged: jest.fn().mockResolvedValue(undefined),
  publishUserStatusChanged: jest.fn().mockResolvedValue(undefined),
  publishUserDeleted: jest.fn().mockResolvedValue(undefined),
  isConnected: jest.fn().mockReturnValue(false),
};
import { CreateUserDto } from "../users/dto/create-user.dto";
import {
  UserStatus,
  UserRole,
  IsStrongPasswordConstraint,
  IsYemeniPhoneConstraint,
} from "../utils/validation";
import {
  HealthController,
  HealthzController,
} from "../health/health.controller";
import { RolesGuard } from "../auth/roles.guard";
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { validate } from "class-validator";
import { plainToInstance } from "class-transformer";

// ═══════════════════════════════════════════════════════════════════════════
// 1. HEALTH ENDPOINT TESTS | اختبارات نقاط فحص الصحة
// ═══════════════════════════════════════════════════════════════════════════

describe("HealthController", () => {
  let healthController: HealthController;
  let healthzController: HealthzController;
  let mockPrisma: any;
  let mockRedisStore: any;

  beforeEach(async () => {
    mockPrisma = {
      getConnectionStatus: jest.fn(),
      $queryRaw: jest.fn(),
    };
    mockRedisStore = {
      healthCheck: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController, HealthzController],
      providers: [
        { provide: PrismaService, useValue: mockPrisma },
          { provide: UserEventsService, useValue: userEventsStub },
        { provide: RedisTokenRevocationStore, useValue: mockRedisStore },
      ],
    }).compile();

    healthController = module.get<HealthController>(HealthController);
    healthzController = module.get<HealthzController>(HealthzController);
  });

  describe("GET /health (basic check)", () => {
    it("should return healthy status with correct service metadata", () => {
      const result = healthController.check();

      expect(result.success).toBe(true);
      expect(result.service).toBe("user-service");
      expect(result.version).toBe("16.0.0");
      expect(result.status).toBe("healthy");
      expect(result.timestamp).toBeDefined();
      expect(typeof result.uptime).toBe("number");
      expect(result.uptime).toBeGreaterThanOrEqual(0);
    });

    it("should return a valid ISO timestamp", () => {
      const result = healthController.check();
      const date = new Date(result.timestamp);
      expect(date.toISOString()).toBe(result.timestamp);
    });
  });

  describe("GET /health/live (liveness probe)", () => {
    it("should return healthy status for liveness check", () => {
      const result = healthController.liveness();

      expect(result.success).toBe(true);
      expect(result.status).toBe("healthy");
      expect(result.service).toBe("user-service");
    });
  });

  describe("GET /health/ready (readiness probe)", () => {
    it("should return healthy when both database and redis are connected", async () => {
      mockPrisma.getConnectionStatus.mockResolvedValue({ connected: true });
      mockRedisStore.healthCheck.mockResolvedValue(true);

      const result = await healthController.readiness();

      expect(result.success).toBe(true);
      expect(result.status).toBe("healthy");
      expect(result.dependencies).toEqual({
        database: "connected",
        redis: "connected",
      });
    });

    it("should return degraded when database is up but redis is down", async () => {
      mockPrisma.getConnectionStatus.mockResolvedValue({ connected: true });
      mockRedisStore.healthCheck.mockResolvedValue(false);

      const result = await healthController.readiness();

      expect(result.success).toBe(true);
      expect(result.status).toBe("degraded");
      expect(result.dependencies!.database).toBe("connected");
      expect(result.dependencies!.redis).toBe("disconnected");
    });

    it("should throw 503 when database is disconnected", async () => {
      mockPrisma.getConnectionStatus.mockResolvedValue({ connected: false });
      mockRedisStore.healthCheck.mockResolvedValue(true);

      await expect(healthController.readiness()).rejects.toThrow(HttpException);

      try {
        await healthController.readiness();
      } catch (e: any) {
        expect(e.getStatus()).toBe(HttpStatus.SERVICE_UNAVAILABLE);
        const response = e.getResponse();
        expect(response.success).toBe(false);
        expect(response.status).toBe("unhealthy");
      }
    });

    it("should handle database connection check throwing an error", async () => {
      mockPrisma.getConnectionStatus.mockRejectedValue(
        new Error("Connection refused"),
      );
      mockRedisStore.healthCheck.mockResolvedValue(true);

      await expect(healthController.readiness()).rejects.toThrow(HttpException);
    });

    it("should handle redis store being undefined (optional)", async () => {
      // Test the controller with no redis store injected
      const module: TestingModule = await Test.createTestingModule({
        controllers: [HealthController],
        providers: [
          { provide: PrismaService, useValue: mockPrisma },
          { provide: UserEventsService, useValue: userEventsStub },
          // RedisTokenRevocationStore not provided
        ],
      }).compile();

      const controller = module.get<HealthController>(HealthController);
      mockPrisma.getConnectionStatus.mockResolvedValue({ connected: true });

      const result = await controller.readiness();

      // DB connected but no redis -> degraded
      expect(result.status).toBe("degraded");
      expect(result.dependencies!.redis).toBe("disconnected");
    });
  });

  describe("GET /healthz (Kubernetes liveness probe)", () => {
    it("should return healthy status from root-level healthz", () => {
      const result = healthzController.healthz();

      expect(result.success).toBe(true);
      expect(result.service).toBe("user-service");
      expect(result.version).toBe("16.0.0");
      expect(result.status).toBe("healthy");
    });
  });

  describe("GET /readyz (Kubernetes readiness probe)", () => {
    it("should check database and redis for readiness", async () => {
      mockPrisma.getConnectionStatus.mockResolvedValue({ connected: true });
      mockRedisStore.healthCheck.mockResolvedValue(true);

      const result = await healthzController.readyz();

      expect(result.success).toBe(true);
      expect(result.status).toBe("healthy");
      expect(result.dependencies).toBeDefined();
    });

    it("should throw 503 when database is not ready", async () => {
      mockPrisma.getConnectionStatus.mockResolvedValue({ connected: false });
      mockRedisStore.healthCheck.mockResolvedValue(false);

      await expect(healthzController.readyz()).rejects.toThrow(HttpException);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// 2. MODULE INITIALIZATION TESTS | اختبارات تهيئة الوحدة
// ═══════════════════════════════════════════════════════════════════════════

describe("Module Initialization", () => {
  describe("UsersService", () => {
    let service: UsersService;
    let prisma: PrismaService;

    const mockPrismaService = {
      user: {
        findUnique: jest.fn(),
        findMany: jest.fn(),
        create: jest.fn(),
        update: jest.fn(),
        delete: jest.fn(),
        count: jest.fn(),
      },
    };

    beforeEach(async () => {
      const module: TestingModule = await Test.createTestingModule({
        providers: [
          UsersService,
          { provide: PrismaService, useValue: mockPrismaService },
          { provide: UserEventsService, useValue: userEventsStub },
        ],
      }).compile();

      service = module.get<UsersService>(UsersService);
      prisma = module.get<PrismaService>(PrismaService);
    });

    it("should be defined after module compilation", () => {
      expect(service).toBeDefined();
    });

    it("should have PrismaService injected", () => {
      expect(prisma).toBeDefined();
    });

    it("should expose all CRUD methods", () => {
      expect(typeof service.create).toBe("function");
      expect(typeof service.findAll).toBe("function");
      expect(typeof service.findOne).toBe("function");
      expect(typeof service.findByEmail).toBe("function");
      expect(typeof service.update).toBe("function");
      expect(typeof service.remove).toBe("function");
      expect(typeof service.hardDelete).toBe("function");
    });

    it("should expose utility methods", () => {
      expect(typeof service.verifyPassword).toBe("function");
      expect(typeof service.updateLastLogin).toBe("function");
      expect(typeof service.countByTenant).toBe("function");
      expect(typeof service.countActive).toBe("function");
    });
  });

  describe("HealthController initialization", () => {
    it("should compile HealthController with required dependencies", async () => {
      const module: TestingModule = await Test.createTestingModule({
        controllers: [HealthController],
        providers: [
          {
            provide: PrismaService,
            useValue: { getConnectionStatus: jest.fn() },
          },
        ],
      }).compile();

      const controller = module.get<HealthController>(HealthController);
      expect(controller).toBeDefined();
    });
  });

  describe("RolesGuard initialization", () => {
    it("should compile RolesGuard with Reflector", async () => {
      const module: TestingModule = await Test.createTestingModule({
        providers: [RolesGuard, Reflector],
      }).compile();

      const guard = module.get<RolesGuard>(RolesGuard);
      expect(guard).toBeDefined();
    });
  });
});

// NOTE: JwtAuthGuard tests are in src/auth/jwt-auth.guard.spec.ts
// NOTE: RolesGuard tests are in src/auth/roles.guard.spec.ts

// ═══════════════════════════════════════════════════════════════════════════
// 3. USER CREATION VALIDATION TESTS | اختبارات التحقق من إنشاء المستخدم
// ═══════════════════════════════════════════════════════════════════════════

describe("User Creation Validation", () => {
  describe("CreateUserDto validation", () => {
    it("should pass with all valid fields", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "123e4567-e89b-4d3b-a456-426614174000",
        email: "farmer@sahool.app",
        password: "SecurePassword123!",
        firstName: "Ahmed",
        lastName: "Ali",
        role: UserRole.FARMER,
      });

      const errors = await validate(dto);
      // Filter out phone validation (optional field not provided) and custom decorators
      const criticalErrors = errors.filter(
        (e) => e.property !== "phone" && e.property !== "password",
      );
      expect(criticalErrors.length).toBe(0);
    });

    it("should fail with invalid email format", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "not-an-email",
        password: "SecurePassword123!",
        firstName: "Ahmed",
        lastName: "Ali",
      });

      const errors = await validate(dto);
      const emailError = errors.find((e) => e.property === "email");
      expect(emailError).toBeDefined();
    });

    it("should fail with empty email", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "",
        password: "SecurePassword123!",
        firstName: "Ahmed",
        lastName: "Ali",
      });

      const errors = await validate(dto);
      const emailError = errors.find((e) => e.property === "email");
      expect(emailError).toBeDefined();
    });

    it("should fail with missing tenantId", async () => {
      const dto = plainToInstance(CreateUserDto, {
        email: "farmer@sahool.app",
        password: "SecurePassword123!",
        firstName: "Ahmed",
        lastName: "Ali",
      });

      const errors = await validate(dto);
      const tenantError = errors.find((e) => e.property === "tenantId");
      expect(tenantError).toBeDefined();
    });

    it("should fail with firstName shorter than 2 characters", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "farmer@sahool.app",
        password: "SecurePassword123!",
        firstName: "A",
        lastName: "Ali",
      });

      const errors = await validate(dto);
      const firstNameError = errors.find((e) => e.property === "firstName");
      expect(firstNameError).toBeDefined();
    });

    it("should fail with lastName exceeding 100 characters", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "123e4567-e89b-12d3-a456-426614174000",
        email: "farmer@sahool.app",
        password: "SecurePassword123!",
        firstName: "Ahmed",
        lastName: "A".repeat(101),
      });

      const errors = await validate(dto);
      const lastNameError = errors.find((e) => e.property === "lastName");
      expect(lastNameError).toBeDefined();
    });

    it("should accept valid UserRole enum values", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "admin@sahool.app",
        password: "SecurePassword123!",
        firstName: "Admin",
        lastName: "User",
        role: UserRole.ADMIN,
      });

      const errors = await validate(dto);
      const roleError = errors.find((e) => e.property === "role");
      expect(roleError).toBeUndefined();
    });

    it("should reject invalid role values", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "admin@sahool.app",
        password: "SecurePassword123!",
        firstName: "Admin",
        lastName: "User",
        role: "SUPERADMIN" as any,
      });

      const errors = await validate(dto);
      const roleError = errors.find((e) => e.property === "role");
      expect(roleError).toBeDefined();
    });

    it("should accept valid UserStatus enum values", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "user@sahool.app",
        password: "SecurePassword123!",
        firstName: "Test",
        lastName: "User",
        status: UserStatus.ACTIVE,
      });

      const errors = await validate(dto);
      const statusError = errors.find((e) => e.property === "status");
      expect(statusError).toBeUndefined();
    });

    it("should accept Arabic names", async () => {
      const dto = plainToInstance(CreateUserDto, {
        tenantId: "tenant-123",
        email: "farmer@sahool.app",
        password: "SecurePassword123!",
        firstName: "أحمد",
        lastName: "محمد",
      });

      const errors = await validate(dto);
      const nameErrors = errors.filter(
        (e) => e.property === "firstName" || e.property === "lastName",
      );
      expect(nameErrors.length).toBe(0);
    });
  });

  // NOTE: UsersService.create tests are in src/users/users.service.spec.ts
});

// ═══════════════════════════════════════════════════════════════════════════
// 5. PASSWORD VALIDATION TESTS | اختبارات التحقق من كلمة المرور
// ═══════════════════════════════════════════════════════════════════════════

describe("Password Validation", () => {
  describe("IsStrongPasswordConstraint", () => {
    let validator: IsStrongPasswordConstraint;

    beforeEach(() => {
      validator = new IsStrongPasswordConstraint();
    });

    const createArgs = (minLength: number = 8) =>
      ({
        constraints: [minLength],
        property: "password",
        object: {},
        value: "",
        targetName: "CreateUserDto",
      }) as any;

    it("should accept a strong password with all requirements", () => {
      expect(validator.validate("SecurePass123!", createArgs())).toBe(true);
    });

    it("should reject password shorter than minimum length", () => {
      expect(validator.validate("Abc1!x", createArgs(8))).toBe(false);
    });

    it("should reject password without uppercase letter", () => {
      expect(validator.validate("securepass123!", createArgs())).toBe(false);
    });

    it("should reject password without lowercase letter", () => {
      expect(validator.validate("SECUREPASS123!", createArgs())).toBe(false);
    });

    it("should reject password without digit", () => {
      expect(validator.validate("SecurePassword!", createArgs())).toBe(false);
    });

    it("should reject password without special character", () => {
      expect(validator.validate("SecurePassword123", createArgs())).toBe(false);
    });

    it("should reject non-string input", () => {
      expect(validator.validate(12345678, createArgs())).toBe(false);
      expect(validator.validate(null, createArgs())).toBe(false);
      expect(validator.validate(undefined, createArgs())).toBe(false);
    });

    it("should accept password with various special characters", () => {
      expect(validator.validate("Password1@", createArgs())).toBe(true);
      expect(validator.validate("Password1#", createArgs())).toBe(true);
      expect(validator.validate("Password1$", createArgs())).toBe(true);
      expect(validator.validate("Password1%", createArgs())).toBe(true);
      expect(validator.validate("Password1&", createArgs())).toBe(true);
      expect(validator.validate("Password1*", createArgs())).toBe(true);
    });

    it("should respect custom minimum length", () => {
      // 10-char minimum
      expect(validator.validate("Short1!aB", createArgs(10))).toBe(false);
      expect(validator.validate("LongEnough1!", createArgs(10))).toBe(true);
    });

    it("should return descriptive error message", () => {
      const message = validator.defaultMessage(createArgs(8));
      expect(message).toContain("8 characters");
      expect(message).toContain("uppercase");
      expect(message).toContain("lowercase");
      expect(message).toContain("number");
      expect(message).toContain("special character");
    });
  });

  describe("IsYemeniPhoneConstraint", () => {
    let validator: IsYemeniPhoneConstraint;

    beforeEach(() => {
      validator = new IsYemeniPhoneConstraint();
    });

    const args = {
      property: "phone",
      object: {},
      value: "",
      constraints: [],
      targetName: "",
    } as any;

    it("should accept phone with +967 prefix", () => {
      expect(validator.validate("+967712345678", args)).toBe(true);
    });

    it("should accept phone with 967 prefix (no plus)", () => {
      expect(validator.validate("967712345678", args)).toBe(true);
    });

    it("should accept phone with 00967 prefix", () => {
      expect(validator.validate("00967712345678", args)).toBe(true);
    });

    it("should accept local 9-digit number starting with 7", () => {
      expect(validator.validate("712345678", args)).toBe(true);
    });

    it("should accept numbers starting with 77 or 78", () => {
      expect(validator.validate("771234567", args)).toBe(true);
      expect(validator.validate("781234567", args)).toBe(true);
    });

    it("should reject non-Yemeni phone numbers", () => {
      expect(validator.validate("+1234567890", args)).toBe(false);
      expect(validator.validate("1234567890", args)).toBe(false);
    });

    it("should reject non-string values", () => {
      expect(validator.validate(712345678, args)).toBe(false);
      expect(validator.validate(null, args)).toBe(false);
    });

    it("should return descriptive error message", () => {
      const message = validator.defaultMessage(args);
      expect(message).toContain("Yemeni phone number");
    });
  });

  // NOTE: Password hashing/verification tests via UsersService are in src/users/users.service.spec.ts

  describe("UserRole enum values", () => {
    it("should define all expected roles", () => {
      expect(UserRole.ADMIN).toBe("ADMIN");
      expect(UserRole.MANAGER).toBe("MANAGER");
      expect(UserRole.FARMER).toBe("FARMER");
      expect(UserRole.WORKER).toBe("WORKER");
      expect(UserRole.VIEWER).toBe("VIEWER");
    });

    it("should have exactly 5 roles", () => {
      const roleValues = Object.values(UserRole);
      expect(roleValues.length).toBe(5);
    });
  });

  describe("UserStatus enum values", () => {
    it("should define all expected statuses", () => {
      expect(UserStatus.ACTIVE).toBe("ACTIVE");
      expect(UserStatus.INACTIVE).toBe("INACTIVE");
      expect(UserStatus.PENDING).toBe("PENDING");
      expect(UserStatus.SUSPENDED).toBe("SUSPENDED");
    });

    it("should have exactly 4 statuses", () => {
      const statusValues = Object.values(UserStatus);
      expect(statusValues.length).toBe(4);
    });
  });
});
