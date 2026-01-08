/**
 * Users Service Unit Tests
 * اختبارات وحدة خدمة المستخدمين
 *
 * Tests for:
 * - User CRUD operations (Create, Read, Update, Delete)
 * - User search and filtering
 * - Password operations
 * - Edge cases: duplicate emails, non-existent users, validation
 */

import { Test, TestingModule } from '@nestjs/testing';
import { ConflictException, NotFoundException } from '@nestjs/common';
import * as bcrypt from 'bcryptjs';
import { UsersService } from './users.service';
import { PrismaService } from '../prisma/prisma.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { UserStatus, UserRole } from '../utils/validation';

describe('UsersService', () => {
  let service: UsersService;
  let prismaService: jest.Mocked<PrismaService>;

  // Mock data
  const mockUserId = 'user-123';
  const mockTenantId = 'tenant-123';
  const mockEmail = 'test@example.com';
  const mockPasswordHash = '$2a$10$mockHashedPassword';

  const mockUser = {
    id: mockUserId,
    tenantId: mockTenantId,
    email: mockEmail,
    phone: '+967712345678',
    passwordHash: mockPasswordHash,
    firstName: 'Test',
    lastName: 'User',
    role: UserRole.VIEWER,
    status: UserStatus.ACTIVE,
    emailVerified: true,
    phoneVerified: false,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
    lastLoginAt: null,
    profile: {
      id: 'profile-123',
      avatar: null,
      bio: 'Test bio',
      location: 'Yemen',
      dateOfBirth: null,
      language: 'ar',
    },
  };

  const createUserDto: CreateUserDto = {
    tenantId: mockTenantId,
    email: 'newuser@example.com',
    phone: '+967712345678',
    password: 'Password123!',
    firstName: 'New',
    lastName: 'User',
    role: UserRole.VIEWER,
    status: UserStatus.PENDING,
    emailVerified: false,
    phoneVerified: false,
  };

  beforeEach(async () => {
    const mockPrismaService = {
      user: {
        create: jest.fn(),
        findMany: jest.fn(),
        findUnique: jest.fn(),
        update: jest.fn(),
        delete: jest.fn(),
        count: jest.fn(),
      },
    };

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
    prismaService = module.get(PrismaService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('create', () => {
    it('should successfully create a new user', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);
      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve(mockPasswordHash));
      prismaService.user.create.mockResolvedValue(mockUser);

      const result = await service.create(createUserDto);

      expect(result).toBeDefined();
      expect(result.email).toBe(mockUser.email);
      expect(prismaService.user.findUnique).toHaveBeenCalledWith({
        where: { email: createUserDto.email },
        select: { id: true },
      });
      expect(bcrypt.hash).toHaveBeenCalledWith(createUserDto.password, 10);
      expect(prismaService.user.create).toHaveBeenCalled();
    });

    it('should throw ConflictException if email already exists', async () => {
      prismaService.user.findUnique.mockResolvedValue({ id: 'existing-user' });

      await expect(service.create(createUserDto)).rejects.toThrow(ConflictException);
      await expect(service.create(createUserDto)).rejects.toThrow('User with this email already exists');
      expect(prismaService.user.create).not.toHaveBeenCalled();
    });

    it('should hash password before storing', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);
      const hashSpy = jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve(mockPasswordHash));
      prismaService.user.create.mockResolvedValue(mockUser);

      await service.create(createUserDto);

      expect(hashSpy).toHaveBeenCalledWith(createUserDto.password, 10);
      expect(prismaService.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          passwordHash: mockPasswordHash,
        }),
        select: expect.any(Object),
      });
    });

    it('should set default status to PENDING if not provided', async () => {
      const dtoWithoutStatus = { ...createUserDto };
      delete dtoWithoutStatus.status;

      prismaService.user.findUnique.mockResolvedValue(null);
      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve(mockPasswordHash));
      prismaService.user.create.mockResolvedValue(mockUser);

      await service.create(dtoWithoutStatus);

      expect(prismaService.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          status: UserStatus.PENDING,
        }),
        select: expect.any(Object),
      });
    });

    it('should set default emailVerified to false if not provided', async () => {
      const dtoWithoutEmailVerified = { ...createUserDto };
      delete dtoWithoutEmailVerified.emailVerified;

      prismaService.user.findUnique.mockResolvedValue(null);
      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve(mockPasswordHash));
      prismaService.user.create.mockResolvedValue(mockUser);

      await service.create(dtoWithoutEmailVerified);

      expect(prismaService.user.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          emailVerified: false,
        }),
        select: expect.any(Object),
      });
    });
  });

  describe('findAll', () => {
    const mockUsers = [mockUser, { ...mockUser, id: 'user-456', email: 'another@example.com' }];

    it('should return paginated list of users', async () => {
      prismaService.user.findMany.mockResolvedValue(mockUsers);
      prismaService.user.count.mockResolvedValue(2);

      const result = await service.findAll();

      expect(result).toMatchObject({
        data: mockUsers,
        meta: {
          total: 2,
          page: 1,
          limit: expect.any(Number),
          totalPages: expect.any(Number),
        },
      });
      expect(prismaService.user.findMany).toHaveBeenCalled();
      expect(prismaService.user.count).toHaveBeenCalled();
    });

    it('should filter users by tenantId', async () => {
      prismaService.user.findMany.mockResolvedValue([mockUser]);
      prismaService.user.count.mockResolvedValue(1);

      await service.findAll({ tenantId: mockTenantId });

      expect(prismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ tenantId: mockTenantId }),
        }),
      );
    });

    it('should filter users by role', async () => {
      prismaService.user.findMany.mockResolvedValue([mockUser]);
      prismaService.user.count.mockResolvedValue(1);

      await service.findAll({ role: UserRole.VIEWER });

      expect(prismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ role: UserRole.VIEWER }),
        }),
      );
    });

    it('should filter users by status', async () => {
      prismaService.user.findMany.mockResolvedValue([mockUser]);
      prismaService.user.count.mockResolvedValue(1);

      await service.findAll({ status: UserStatus.ACTIVE });

      expect(prismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({ status: UserStatus.ACTIVE }),
        }),
      );
    });

    it('should handle pagination parameters', async () => {
      prismaService.user.findMany.mockResolvedValue([mockUser]);
      prismaService.user.count.mockResolvedValue(50);

      await service.findAll({ page: 2, limit: 10 });

      expect(prismaService.user.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          skip: 10, // (page 2 - 1) * limit 10
          take: 10,
        }),
      );
    });

    it('should return empty array when no users found', async () => {
      prismaService.user.findMany.mockResolvedValue([]);
      prismaService.user.count.mockResolvedValue(0);

      const result = await service.findAll();

      expect(result.data).toEqual([]);
      expect(result.meta.total).toBe(0);
    });
  });

  describe('findOne', () => {
    it('should return a user by ID', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findOne(mockUserId);

      expect(result).toEqual(mockUser);
      expect(prismaService.user.findUnique).toHaveBeenCalledWith({
        where: { id: mockUserId },
        select: expect.any(Object),
      });
    });

    it('should throw NotFoundException if user not found', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.findOne('non-existent-id')).rejects.toThrow(NotFoundException);
      await expect(service.findOne('non-existent-id')).rejects.toThrow('User with ID non-existent-id not found');
    });

    it('should include related data (profile, sessions)', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      await service.findOne(mockUserId);

      expect(prismaService.user.findUnique).toHaveBeenCalledWith({
        where: { id: mockUserId },
        select: expect.objectContaining({
          profile: expect.any(Object),
          sessions: expect.any(Object),
        }),
      });
    });
  });

  describe('findByEmail', () => {
    it('should return a user by email', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      const result = await service.findByEmail(mockEmail);

      expect(result).toEqual(mockUser);
      expect(prismaService.user.findUnique).toHaveBeenCalledWith({
        where: { email: mockEmail },
        select: expect.any(Object),
      });
    });

    it('should return null if user not found', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      const result = await service.findByEmail('nonexistent@example.com');

      expect(result).toBeNull();
    });

    it('should include passwordHash in the result', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);

      await service.findByEmail(mockEmail);

      expect(prismaService.user.findUnique).toHaveBeenCalledWith({
        where: { email: mockEmail },
        select: expect.objectContaining({
          passwordHash: true,
        }),
      });
    });
  });

  describe('update', () => {
    const updateUserDto: UpdateUserDto = {
      firstName: 'Updated',
      lastName: 'Name',
      role: UserRole.OPERATOR,
    };

    it('should successfully update a user', async () => {
      const updatedUser = { ...mockUser, firstName: 'Updated', lastName: 'Name' };
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.update.mockResolvedValue(updatedUser);

      const result = await service.update(mockUserId, updateUserDto);

      expect(result.firstName).toBe('Updated');
      expect(result.lastName).toBe('Name');
      expect(prismaService.user.update).toHaveBeenCalledWith({
        where: { id: mockUserId },
        data: expect.objectContaining({
          firstName: 'Updated',
          lastName: 'Name',
          role: UserRole.OPERATOR,
        }),
        select: expect.any(Object),
      });
    });

    it('should throw NotFoundException if user not found', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.update('non-existent-id', updateUserDto)).rejects.toThrow(NotFoundException);
      await expect(service.update('non-existent-id', updateUserDto)).rejects.toThrow(
        'User with ID non-existent-id not found',
      );
    });

    it('should throw ConflictException if new email already exists', async () => {
      const updateWithEmail: UpdateUserDto = { email: 'taken@example.com' };
      prismaService.user.findUnique
        .mockResolvedValueOnce(mockUser) // First call - check if user exists
        .mockResolvedValueOnce({ id: 'another-user' }); // Second call - email check

      await expect(service.update(mockUserId, updateWithEmail)).rejects.toThrow('Email already in use');
    });

    it('should allow updating to the same email', async () => {
      const updateWithSameEmail: UpdateUserDto = { email: mockEmail };
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.update.mockResolvedValue(mockUser);

      await service.update(mockUserId, updateWithSameEmail);

      // Should not check for email existence since it's the same
      expect(prismaService.user.findUnique).toHaveBeenCalledTimes(1);
    });

    it('should hash password if provided in update', async () => {
      const updateWithPassword: UpdateUserDto = { password: 'NewPassword123!' };
      const newHash = '$2a$10$newHashedPassword';

      prismaService.user.findUnique.mockResolvedValue(mockUser);
      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve(newHash));
      prismaService.user.update.mockResolvedValue({ ...mockUser, passwordHash: newHash });

      await service.update(mockUserId, updateWithPassword);

      expect(bcrypt.hash).toHaveBeenCalledWith('NewPassword123!', 10);
      expect(prismaService.user.update).toHaveBeenCalledWith({
        where: { id: mockUserId },
        data: expect.objectContaining({
          passwordHash: newHash,
        }),
        select: expect.any(Object),
      });
    });

    it('should remove undefined fields from update data', async () => {
      const partialUpdate: UpdateUserDto = {
        firstName: 'Updated',
        lastName: undefined,
        email: undefined,
      };

      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.update.mockResolvedValue(mockUser);

      await service.update(mockUserId, partialUpdate);

      expect(prismaService.user.update).toHaveBeenCalledWith({
        where: { id: mockUserId },
        data: {
          firstName: 'Updated',
        },
        select: expect.any(Object),
      });
    });
  });

  describe('remove (soft delete)', () => {
    it('should soft delete a user by setting status to INACTIVE', async () => {
      const inactiveUser = { ...mockUser, status: UserStatus.INACTIVE };
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.update.mockResolvedValue(inactiveUser);

      const result = await service.remove(mockUserId);

      expect(result.status).toBe(UserStatus.INACTIVE);
      expect(prismaService.user.update).toHaveBeenCalledWith({
        where: { id: mockUserId },
        data: {
          status: UserStatus.INACTIVE,
        },
      });
      expect(prismaService.user.delete).not.toHaveBeenCalled();
    });

    it('should throw NotFoundException if user not found', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.remove('non-existent-id')).rejects.toThrow(NotFoundException);
      await expect(service.remove('non-existent-id')).rejects.toThrow('User with ID non-existent-id not found');
    });
  });

  describe('hardDelete (permanent deletion)', () => {
    it('should permanently delete a user', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.delete.mockResolvedValue(mockUser);

      await service.hardDelete(mockUserId);

      expect(prismaService.user.delete).toHaveBeenCalledWith({
        where: { id: mockUserId },
      });
    });

    it('should throw NotFoundException if user not found', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.hardDelete('non-existent-id')).rejects.toThrow(NotFoundException);
      await expect(service.hardDelete('non-existent-id')).rejects.toThrow('User with ID non-existent-id not found');
    });
  });

  describe('verifyPassword', () => {
    it('should return true for correct password', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      jest.spyOn(bcrypt, 'compare').mockImplementation(() => Promise.resolve(true));

      const result = await service.verifyPassword(mockUserId, 'correctPassword');

      expect(result).toBe(true);
      expect(bcrypt.compare).toHaveBeenCalledWith('correctPassword', mockPasswordHash);
    });

    it('should return false for incorrect password', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      jest.spyOn(bcrypt, 'compare').mockImplementation(() => Promise.resolve(false));

      const result = await service.verifyPassword(mockUserId, 'wrongPassword');

      expect(result).toBe(false);
    });

    it('should throw NotFoundException if user not found', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);

      await expect(service.verifyPassword('non-existent-id', 'password')).rejects.toThrow(NotFoundException);
      await expect(service.verifyPassword('non-existent-id', 'password')).rejects.toThrow(
        'User with ID non-existent-id not found',
      );
    });
  });

  describe('updateLastLogin', () => {
    it('should update last login timestamp', async () => {
      prismaService.user.update.mockResolvedValue({ ...mockUser, lastLoginAt: new Date() });

      await service.updateLastLogin(mockUserId);

      expect(prismaService.user.update).toHaveBeenCalledWith({
        where: { id: mockUserId },
        data: {
          lastLoginAt: expect.any(Date),
        },
      });
    });
  });

  describe('countByTenant', () => {
    it('should return count of users in a tenant', async () => {
      prismaService.user.count.mockResolvedValue(5);

      const result = await service.countByTenant(mockTenantId);

      expect(result).toBe(5);
      expect(prismaService.user.count).toHaveBeenCalledWith({
        where: { tenantId: mockTenantId },
      });
    });
  });

  describe('countActive', () => {
    it('should return count of active users', async () => {
      prismaService.user.count.mockResolvedValue(10);

      const result = await service.countActive();

      expect(result).toBe(10);
      expect(prismaService.user.count).toHaveBeenCalledWith({
        where: { status: UserStatus.ACTIVE },
      });
    });
  });

  describe('edge cases', () => {
    it('should handle database errors during create', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);
      jest.spyOn(bcrypt, 'hash').mockImplementation(() => Promise.resolve(mockPasswordHash));
      prismaService.user.create.mockRejectedValue(new Error('Database error'));

      await expect(service.create(createUserDto)).rejects.toThrow('Database error');
    });

    it('should handle database errors during update', async () => {
      prismaService.user.findUnique.mockResolvedValue(mockUser);
      prismaService.user.update.mockRejectedValue(new Error('Database error'));

      await expect(service.update(mockUserId, { firstName: 'Test' })).rejects.toThrow('Database error');
    });

    it('should handle bcrypt hashing errors', async () => {
      prismaService.user.findUnique.mockResolvedValue(null);
      jest.spyOn(bcrypt, 'hash').mockRejectedValue(new Error('Hashing error') as never);

      await expect(service.create(createUserDto)).rejects.toThrow('Hashing error');
    });
  });
});
