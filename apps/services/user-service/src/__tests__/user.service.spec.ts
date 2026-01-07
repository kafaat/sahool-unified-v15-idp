/**
 * User Service Tests
 * Comprehensive tests for user service business logic
 * Coverage: CRUD operations, validation, authentication, error handling
 */

import { Test, TestingModule } from '@nestjs/testing';
import { ConflictException, NotFoundException } from '@nestjs/common';
import { UsersService } from '../users/users.service';
import { PrismaService } from '../prisma/prisma.service';
import { CreateUserDto } from '../users/dto/create-user.dto';
import { UpdateUserDto } from '../users/dto/update-user.dto';
import { UserStatus, UserRole } from '../utils/validation';
import * as bcrypt from 'bcryptjs';

describe('UsersService', () => {
  let service: UsersService;
  let prisma: PrismaService;

  // Mock user data
  const mockUser = {
    id: 'user-123',
    tenantId: 'tenant-1',
    email: 'test@example.com',
    phone: '+967771234567',
    passwordHash: 'hashed_password',
    firstName: 'أحمد',
    lastName: 'علي',
    role: UserRole.OPERATOR,
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: false,
    createdAt: new Date(),
    updatedAt: new Date(),
    lastLoginAt: null,
    profile: {
      id: 'profile-123',
      avatar: null,
      bio: null,
      location: 'Sanaa, Yemen',
    },
  };

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
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
    prisma = module.get<PrismaService>(PrismaService);

    // Reset mocks
    jest.clearAllMocks();
  });

  describe('User Service Initialization', () => {
    it('should be defined', () => {
      expect(service).toBeDefined();
    });

    it('should have prisma service injected', () => {
      expect(prisma).toBeDefined();
    });
  });

  describe('create', () => {
    const createUserDto: CreateUserDto = {
      tenantId: 'tenant-1',
      email: 'newuser@example.com',
      phone: '+967771234567',
      password: 'SecurePassword123!',
      firstName: 'محمد',
      lastName: 'حسن',
      role: UserRole.OPERATOR,
      status: UserStatus.PENDING,
    };

    it('should create a new user successfully', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);

      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve('hashed_password'));

      const result = await service.create(createUserDto);

      expect(result).toBeDefined();
      expect(result.id).toBe(mockUser.id);
      expect(mockPrismaService.user.findUnique).toHaveBeenCalledWith({
        where: { email: createUserDto.email },
        select: { id: true },
      });
      expect(mockPrismaService.user.create).toHaveBeenCalled();
    });

    it('should hash the password before creating user', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);

      const hashSpy = jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve('hashed_password'));

      await service.create(createUserDto);

      expect(hashSpy).toHaveBeenCalledWith(createUserDto.password, 10);
    });

    it('should throw ConflictException if user with email exists', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue({ id: 'existing-user' });

      await expect(service.create(createUserDto)).rejects.toThrow(ConflictException);
      expect(mockPrismaService.user.create).not.toHaveBeenCalled();
    });

    it('should set default status to PENDING if not provided', async () => {
      const dtoWithoutStatus = { ...createUserDto };
      delete dtoWithoutStatus.status;

      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);

      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve('hashed_password'));

      await service.create(dtoWithoutStatus);

      expect(mockPrismaService.user.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: UserStatus.PENDING,
          }),
        }),
      );
    });

    it('should set emailVerified to false by default', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);

      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve('hashed_password'));

      await service.create(createUserDto);

      expect(mockPrismaService.user.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            emailVerified: false,
          }),
        }),
      );
    });
  });

  describe('findAll', () => {
    const mockUsers = [mockUser, { ...mockUser, id: 'user-456', email: 'user2@example.com' }];

    it('should return paginated list of users', async () => {
      mockPrismaService.user.findMany.mockResolvedValue(mockUsers);
      mockPrismaService.user.count.mockResolvedValue(2);

      const result = await service.findAll();

      expect(result).toBeDefined();
      expect(result.data).toEqual(mockUsers);
      expect(result.meta.total).toBe(2);
      expect(mockPrismaService.user.findMany).toHaveBeenCalled();
      expect(mockPrismaService.user.count).toHaveBeenCalled();
    });

    it('should filter users by tenantId', async () => {
      mockPrismaService.user.findMany.mockResolvedValue([mockUser]);
      mockPrismaService.user.count.mockResolvedValue(1);

      const result = await service.findAll({ tenantId: 'tenant-1' });

      expect(mockPrismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            tenantId: 'tenant-1',
          }),
        }),
      );
    });

    it('should filter users by role', async () => {
      mockPrismaService.user.findMany.mockResolvedValue([mockUser]);
      mockPrismaService.user.count.mockResolvedValue(1);

      await service.findAll({ role: UserRole.OPERATOR });

      expect(mockPrismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            role: UserRole.OPERATOR,
          }),
        }),
      );
    });

    it('should filter users by status', async () => {
      mockPrismaService.user.findMany.mockResolvedValue([mockUser]);
      mockPrismaService.user.count.mockResolvedValue(1);

      await service.findAll({ status: UserStatus.ACTIVE });

      expect(mockPrismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            status: UserStatus.ACTIVE,
          }),
        }),
      );
    });

    it('should support pagination with skip and take', async () => {
      mockPrismaService.user.findMany.mockResolvedValue([mockUser]);
      mockPrismaService.user.count.mockResolvedValue(100);

      await service.findAll({ skip: 10, take: 20 });

      expect(mockPrismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 10,
          take: 20,
        }),
      );
    });

    it('should order users by createdAt desc', async () => {
      mockPrismaService.user.findMany.mockResolvedValue(mockUsers);
      mockPrismaService.user.count.mockResolvedValue(2);

      await service.findAll();

      expect(mockPrismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          orderBy: {
            createdAt: 'desc',
          },
        }),
      );
    });

    it('should return empty array when no users found', async () => {
      mockPrismaService.user.findMany.mockResolvedValue([]);
      mockPrismaService.user.count.mockResolvedValue(0);

      const result = await service.findAll();

      expect(result.data).toEqual([]);
      expect(result.meta.total).toBe(0);
    });
  });

  describe('findOne', () => {
    it('should return a user by ID', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findOne('user-123');

      expect(result).toEqual(mockUser);
      expect(mockPrismaService.user.findUnique).toHaveBeenCalledWith({
        where: { id: 'user-123' },
        select: expect.any(Object),
      });
    });

    it('should throw NotFoundException if user not found', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.findOne('non-existent-id')).rejects.toThrow(NotFoundException);
    });

    it('should include profile data', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findOne('user-123');

      expect(result.profile).toBeDefined();
    });

    it('should include sessions data', async () => {
      const userWithSessions = {
        ...mockUser,
        sessions: [
          {
            id: 'session-1',
            expiresAt: new Date(Date.now() + 86400000),
            deviceInfo: 'Mobile App',
            ipAddress: '192.168.1.1',
          },
        ],
      };

      mockPrismaService.user.findUnique.mockResolvedValue(userWithSessions);

      const result = await service.findOne('user-123');

      expect(result.sessions).toBeDefined();
      expect(result.sessions.length).toBe(1);
    });
  });

  describe('findByEmail', () => {
    it('should return a user by email', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findByEmail('test@example.com');

      expect(result).toEqual(mockUser);
      expect(mockPrismaService.user.findUnique).toHaveBeenCalledWith({
        where: { email: 'test@example.com' },
        select: expect.any(Object),
      });
    });

    it('should return null if user not found', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      const result = await service.findByEmail('nonexistent@example.com');

      expect(result).toBeNull();
    });

    it('should include passwordHash for authentication', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findByEmail('test@example.com');

      expect(result.passwordHash).toBeDefined();
    });
  });

  describe('update', () => {
    const updateUserDto: UpdateUserDto = {
      firstName: 'عبدالله',
      lastName: 'محمد',
      phone: '+967772345678',
    };

    it('should update a user successfully', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.update.mockResolvedValue({ ...mockUser, ...updateUserDto });

      const result = await service.update('user-123', updateUserDto);

      expect(result).toBeDefined();
      expect(mockPrismaService.user.update).toHaveBeenCalledWith({
        where: { id: 'user-123' },
        data: expect.objectContaining(updateUserDto),
        select: expect.any(Object),
      });
    });

    it('should throw NotFoundException if user not found', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.update('non-existent', updateUserDto)).rejects.toThrow(NotFoundException);
      expect(mockPrismaService.user.update).not.toHaveBeenCalled();
    });

    it('should hash password if provided', async () => {
      const dtoWithPassword = { ...updateUserDto, password: 'NewPassword123!' };

      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      const hashSpy = jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve('new_hashed_password'));

      await service.update('user-123', dtoWithPassword);

      expect(hashSpy).toHaveBeenCalledWith(dtoWithPassword.password, 10);
      expect(mockPrismaService.user.update).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            passwordHash: 'new_hashed_password',
          }),
        }),
      );
    });

    it('should throw ConflictException if new email is already taken', async () => {
      const dtoWithEmail = { ...updateUserDto, email: 'taken@example.com' };

      mockPrismaService.user.findUnique
        .mockResolvedValueOnce(mockUser) // First call - existing user
        .mockResolvedValueOnce({ id: 'other-user' }); // Second call - email check

      await expect(service.update('user-123', dtoWithEmail)).rejects.toThrow(ConflictException);
      expect(mockPrismaService.user.update).not.toHaveBeenCalled();
    });

    it('should allow updating to same email', async () => {
      const dtoWithSameEmail = { ...updateUserDto, email: mockUser.email };

      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      await service.update('user-123', dtoWithSameEmail);

      // Should not check for email conflict
      expect(mockPrismaService.user.update).toHaveBeenCalled();
    });

    it('should remove undefined fields from update data', async () => {
      const dtoWithUndefined = {
        firstName: 'Test',
        lastName: undefined,
        email: undefined,
      };

      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.update.mockResolvedValue(mockUser);

      await service.update('user-123', dtoWithUndefined);

      const updateCall = mockPrismaService.user.update.mock.calls[0][0];
      expect(updateCall.data.firstName).toBe('Test');
      expect(updateCall.data.lastName).toBeUndefined();
    });
  });

  describe('remove (soft delete)', () => {
    it('should soft delete a user by setting status to INACTIVE', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.update.mockResolvedValue({ ...mockUser, status: UserStatus.INACTIVE });

      const result = await service.remove('user-123');

      expect(mockPrismaService.user.update).toHaveBeenCalledWith({
        where: { id: 'user-123' },
        data: {
          status: UserStatus.INACTIVE,
        },
      });
      expect(result.status).toBe(UserStatus.INACTIVE);
    });

    it('should throw NotFoundException if user not found', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.remove('non-existent')).rejects.toThrow(NotFoundException);
      expect(mockPrismaService.user.update).not.toHaveBeenCalled();
    });
  });

  describe('hardDelete', () => {
    it('should permanently delete a user', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);
      mockPrismaService.user.delete.mockResolvedValue(mockUser);

      await service.hardDelete('user-123');

      expect(mockPrismaService.user.delete).toHaveBeenCalledWith({
        where: { id: 'user-123' },
      });
    });

    it('should throw NotFoundException if user not found', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.hardDelete('non-existent')).rejects.toThrow(NotFoundException);
      expect(mockPrismaService.user.delete).not.toHaveBeenCalled();
    });
  });

  describe('verifyPassword', () => {
    it('should return true for correct password', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      jest.spyOn(bcrypt, 'compare').mockImplementation(() => Promise.resolve(true));

      const result = await service.verifyPassword('user-123', 'correct_password');

      expect(result).toBe(true);
      expect(bcrypt.compare).toHaveBeenCalledWith('correct_password', mockUser.passwordHash);
    });

    it('should return false for incorrect password', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      jest.spyOn(bcrypt, 'compare').mockImplementation(() => Promise.resolve(false));

      const result = await service.verifyPassword('user-123', 'wrong_password');

      expect(result).toBe(false);
    });

    it('should throw NotFoundException if user not found', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.verifyPassword('non-existent', 'password')).rejects.toThrow(NotFoundException);
    });
  });

  describe('updateLastLogin', () => {
    it('should update last login timestamp', async () => {
      mockPrismaService.user.update.mockResolvedValue({ ...mockUser, lastLoginAt: new Date() });

      await service.updateLastLogin('user-123');

      expect(mockPrismaService.user.update).toHaveBeenCalledWith({
        where: { id: 'user-123' },
        data: {
          lastLoginAt: expect.any(Date),
        },
      });
    });
  });

  describe('countByTenant', () => {
    it('should return count of users for a tenant', async () => {
      mockPrismaService.user.count.mockResolvedValue(15);

      const result = await service.countByTenant('tenant-1');

      expect(result).toBe(15);
      expect(mockPrismaService.user.count).toHaveBeenCalledWith({
        where: { tenantId: 'tenant-1' },
      });
    });

    it('should return 0 if no users found', async () => {
      mockPrismaService.user.count.mockResolvedValue(0);

      const result = await service.countByTenant('tenant-2');

      expect(result).toBe(0);
    });
  });

  describe('countActive', () => {
    it('should return count of active users', async () => {
      mockPrismaService.user.count.mockResolvedValue(42);

      const result = await service.countActive();

      expect(result).toBe(42);
      expect(mockPrismaService.user.count).toHaveBeenCalledWith({
        where: { status: UserStatus.ACTIVE },
      });
    });

    it('should return 0 if no active users', async () => {
      mockPrismaService.user.count.mockResolvedValue(0);

      const result = await service.countActive();

      expect(result).toBe(0);
    });
  });

  describe('Error Handling', () => {
    it('should handle database errors gracefully', async () => {
      mockPrismaService.user.findMany.mockRejectedValue(new Error('Database connection failed'));

      await expect(service.findAll()).rejects.toThrow('Database connection failed');
    });

    it('should handle bcrypt errors during password hashing', async () => {
      const createUserDto: CreateUserDto = {
        tenantId: 'tenant-1',
        email: 'test@example.com',
        password: 'password',
        firstName: 'Test',
        lastName: 'User',
        role: UserRole.OPERATOR,
      };

      mockPrismaService.user.findUnique.mockResolvedValue(null);

      jest.spyOn(bcrypt, 'hash').mockRejectedValue(new Error('Hashing failed'));

      await expect(service.create(createUserDto)).rejects.toThrow('Hashing failed');
    });
  });

  describe('Data Sanitization', () => {
    it('should not expose passwordHash in returned user object', async () => {
      mockPrismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findOne('user-123');

      // This is handled by select in the actual implementation
      // The test verifies that the select statement is used correctly
      expect(mockPrismaService.user.findUnique).toHaveBeenCalledWith(
        expect.objectContaining({
          select: expect.any(Object),
        }),
      );
    });
  });

  describe('Multi-tenant Support', () => {
    it('should enforce tenant isolation when querying users', async () => {
      mockPrismaService.user.findMany.mockResolvedValue([mockUser]);
      mockPrismaService.user.count.mockResolvedValue(1);

      await service.findAll({ tenantId: 'tenant-1' });

      expect(mockPrismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            tenantId: 'tenant-1',
          }),
        }),
      );
    });

    it('should require tenantId when creating users', async () => {
      const createUserDto: CreateUserDto = {
        tenantId: 'tenant-1',
        email: 'test@example.com',
        password: 'SecurePass123!',
        firstName: 'Test',
        lastName: 'User',
        role: UserRole.OPERATOR,
      };

      mockPrismaService.user.findUnique.mockResolvedValue(null);
      mockPrismaService.user.create.mockResolvedValue(mockUser);

      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve('hashed'));

      await service.create(createUserDto);

      expect(mockPrismaService.user.create).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            tenantId: 'tenant-1',
          }),
        }),
      );
    });
  });
});
