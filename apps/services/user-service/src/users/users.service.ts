/**
 * Users Service
 * خدمة المستخدمين
 */

import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
} from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { UserEventsService } from "../events/user-events.service";
import { CreateUserDto } from "./dto/create-user.dto";
import { UpdateUserDto } from "./dto/update-user.dto";
import * as bcrypt from "bcryptjs";
import { UserRole, UserStatus } from "../utils/validation";
import { BCRYPT_ROUNDS, splitFullName } from "../utils/security.config";

// User type - use when Prisma types are generated
type User = any;
import {
  calculatePagination,
  createPaginatedResponse,
  CommonSelects,
  type PaginationParams,
  type PaginatedResponse,
} from "../utils/db-utils";

@Injectable()
export class UsersService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly events: UserEventsService,
  ) {}

  /**
   * Create a new user
   * إنشاء مستخدم جديد
   */
  async create(createUserDto: CreateUserDto): Promise<User> {
    // Normalize email to lowercase to prevent duplicate accounts
    const email = createUserDto.email.toLowerCase().trim();

    // Check if user with email already exists
    const existingUser = await this.prisma.user.findUnique({
      where: { email },
      select: { id: true },
    });

    if (existingUser) {
      throw new ConflictException("User with this email already exists");
    }

    // Hash password
    const passwordHash = await bcrypt.hash(createUserDto.password, BCRYPT_ROUNDS);

    // Handle name splitting: if `name` provided, split into firstName/lastName
    const names = splitFullName(createUserDto.name, createUserDto.firstName, createUserDto.lastName);
    if (!names) {
      throw new BadRequestException(
        "Either 'name' or both 'firstName' and 'lastName' must be provided",
      );
    }
    const { firstName, lastName } = names;

    // Require explicit tenantId for admin user creation (tenant isolation)
    const tenantId = createUserDto.tenantId;
    if (!tenantId) {
      throw new BadRequestException(
        "Tenant ID is required for user creation",
      );
    }

    // Create user
    const user = await this.prisma.user.create({
      data: {
        tenantId,
        email,
        phone: createUserDto.phone,
        passwordHash,
        firstName,
        lastName,
        role: (createUserDto.role || UserRole.VIEWER) as any, // Cast to Prisma UserRole enum
        status: (createUserDto.status || UserStatus.PENDING) as any, // Cast to Prisma UserStatus enum
        emailVerified: createUserDto.emailVerified || false,
        phoneVerified: createUserDto.phoneVerified || false,
      },
      select: {
        ...CommonSelects.userBasic,
        profile: {
          select: {
            id: true,
            avatarUrl: true,
            address: true,
            city: true,
            region: true,
          },
        },
      },
    });

    // Fire-and-forget NATS publish — downstream services (audit, notification)
    // react to `sahool.user.created`. Do not block user-creation on event bus
    // availability; UserEventsService logs + swallows failures.
    void this.events.publishUserCreated({
      tenantId,
      userId: (user as User).id,
      email: (user as User).email,
      firstName: (user as User).firstName ?? undefined,
      lastName: (user as User).lastName ?? undefined,
      role: String((user as User).role),
      createdAt: (user as User).createdAt,
    });

    return user as User;
  }

  /**
   * Get all users with optional filtering and pagination
   * الحصول على جميع المستخدمين مع إمكانية التصفية والترقيم
   */
  async findAll(
    params?: {
      tenantId?: string;
      role?: string;
      status?: string;
    } & PaginationParams,
  ): Promise<PaginatedResponse<User>> {
    const { tenantId, role, status, ...paginationParams } = params || {};

    // Calculate pagination with enforced limits
    const { skip, take, page } = calculatePagination(paginationParams);

    // Build where clause
    const where: any = {
      ...(tenantId && { tenantId }),
      ...(role && { role: role as any }),
      ...(status && { status: status as any }),
    };

    // Execute queries in parallel
    const [data, total] = await Promise.all([
      this.prisma.user.findMany({
        where,
        select: {
          ...CommonSelects.userBasic,
          profile: {
            select: {
              id: true,
              avatarUrl: true,
              address: true,
              city: true,
              region: true,
            },
          },
        },
        skip,
        take,
        orderBy: {
          createdAt: "desc",
        },
      }),
      this.prisma.user.count({ where }),
    ]);

    return createPaginatedResponse(data as User[], total, { page, take });
  }

  /**
   * Get a single user by ID
   * الحصول على مستخدم واحد بواسطة المعرف
   */
  async findOne(id: string): Promise<User> {
    const user = await this.prisma.user.findUnique({
      where: { id },
      select: {
        ...CommonSelects.userBasic,
        phone: true,
        emailVerified: true,
        phoneVerified: true,
        lastLoginAt: true,
        tenantId: true,
        profile: {
          select: {
            id: true,
            avatarUrl: true,
            address: true,
            city: true,
            region: true,
            dateOfBirth: true,
          },
        },
        sessions: {
          where: {
            expiresAt: {
              gte: new Date(),
            },
          },
          select: {
            id: true,
            expiresAt: true,
            userAgent: true,
            ipAddress: true,
          },
        },
      },
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    return user as User;
  }

  /**
   * Get a user by email
   * الحصول على مستخدم بواسطة البريد الإلكتروني
   */
  async findByEmail(email: string): Promise<User | null> {
    const user = await this.prisma.user.findUnique({
      where: { email },
      select: {
        ...CommonSelects.userBasic,
        passwordHash: true, // Needed for authentication
        phone: true,
        emailVerified: true,
        phoneVerified: true,
        tenantId: true,
        profile: {
          select: {
            id: true,
            avatarUrl: true,
            address: true,
            city: true,
            region: true,
          },
        },
      },
    });

    return user as User | null;
  }

  /**
   * Update a user
   * تحديث مستخدم
   */
  async update(id: string, updateUserDto: UpdateUserDto): Promise<User> {
    // Check if user exists — also fetch role/status so we can detect role or
    // status changes and emit the dedicated events.
    const existingUser = await this.prisma.user.findUnique({
      where: { id },
      select: {
        id: true,
        email: true,
        role: true,
        status: true,
        tenantId: true,
      },
    });

    if (!existingUser) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    // If updating email, check if it's already taken
    if (updateUserDto.email && updateUserDto.email !== existingUser.email) {
      const emailExists = await this.prisma.user.findUnique({
        where: { email: updateUserDto.email },
        select: { id: true },
      });

      if (emailExists) {
        throw new ConflictException("Email already in use");
      }
    }

    // Prepare update data
    const updateData: any = {
      email: updateUserDto.email,
      phone: updateUserDto.phone,
      firstName: updateUserDto.firstName,
      lastName: updateUserDto.lastName,
      role: updateUserDto.role,
      status: updateUserDto.status,
      emailVerified: updateUserDto.emailVerified,
      phoneVerified: updateUserDto.phoneVerified,
    };

    // Hash password if provided
    if (updateUserDto.password) {
      updateData.passwordHash = await bcrypt.hash(updateUserDto.password, BCRYPT_ROUNDS);
    }

    // Remove undefined fields
    Object.keys(updateData).forEach(
      (key) => updateData[key] === undefined && delete updateData[key],
    );

    // Update user
    const user = await this.prisma.user.update({
      where: { id },
      data: updateData,
      select: {
        ...CommonSelects.userBasic,
        phone: true,
        emailVerified: true,
        phoneVerified: true,
        tenantId: true,
        profile: {
          select: {
            id: true,
            avatarUrl: true,
            address: true,
            city: true,
            region: true,
          },
        },
      },
    });

    const updated = user as User;

    // Emit generic "updated" event for any non-empty change set.
    void this.events.publishUserUpdated({
      tenantId: updated.tenantId,
      userId: updated.id,
      changes: {
        email: updateUserDto.email,
        firstName: updateUserDto.firstName,
        lastName: updateUserDto.lastName,
        role: updateUserDto.role,
      },
      updatedAt: new Date(),
    });

    // Specialised events — downstream audit & authorization caches can
    // invalidate more precisely when only the role or status flipped.
    if (updateUserDto.role && updateUserDto.role !== String(existingUser.role)) {
      void this.events.publishUserRoleChanged({
        tenantId: updated.tenantId,
        userId: updated.id,
        oldRole: String(existingUser.role),
        newRole: String(updateUserDto.role),
      });
    }

    if (
      updateUserDto.status &&
      updateUserDto.status !== String(existingUser.status)
    ) {
      void this.events.publishUserStatusChanged({
        tenantId: updated.tenantId,
        userId: updated.id,
        oldStatus: String(existingUser.status),
        newStatus: String(updateUserDto.status),
      });
    }

    return updated;
  }

  /**
   * Delete a user (soft delete by setting status to INACTIVE)
   * حذف مستخدم (حذف ناعم عن طريق تعيين الحالة إلى غير نشط)
   */
  async remove(id: string): Promise<User> {
    const user = await this.prisma.user.findUnique({
      where: { id },
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    // Soft delete by setting status to INACTIVE
    const deactivated = (await this.prisma.user.update({
      where: { id },
      data: {
        status: UserStatus.INACTIVE,
      },
      select: {
        ...CommonSelects.userBasic,
        tenantId: true,
      },
    })) as User;

    void this.events.publishUserDeleted({
      tenantId: deactivated.tenantId,
      userId: deactivated.id,
      hardDelete: false,
    });

    return deactivated;
  }

  /**
   * Hard delete a user (permanent deletion)
   * حذف صعب لمستخدم (حذف دائم)
   */
  async hardDelete(id: string): Promise<void> {
    const user = await this.prisma.user.findUnique({
      where: { id },
      select: { id: true, tenantId: true },
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${id} not found`);
    }

    await this.prisma.user.delete({
      where: { id },
    });

    void this.events.publishUserDeleted({
      tenantId: user.tenantId,
      userId: user.id,
      hardDelete: true,
    });
  }

  /**
   * Verify user password
   * التحقق من كلمة مرور المستخدم
   */
  async verifyPassword(userId: string, password: string): Promise<boolean> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user) {
      throw new NotFoundException(`User with ID ${userId} not found`);
    }

    return bcrypt.compare(password, user.passwordHash);
  }

  /**
   * Update last login timestamp
   * تحديث طابع الوقت لآخر تسجيل دخول
   */
  async updateLastLogin(userId: string): Promise<void> {
    await this.prisma.user.update({
      where: { id: userId },
      data: {
        lastLoginAt: new Date(),
      },
    });
  }

  /**
   * Get user count by tenant
   * الحصول على عدد المستخدمين حسب المستأجر
   */
  async countByTenant(tenantId: string): Promise<number> {
    return this.prisma.user.count({
      where: { tenantId },
    });
  }

  /**
   * Get active users count
   * الحصول على عدد المستخدمين النشطين
   */
  async countActive(tenantId: string): Promise<number> {
    return this.prisma.user.count({
      where: {
        status: UserStatus.ACTIVE,
        tenantId,
      },
    });
  }
}
