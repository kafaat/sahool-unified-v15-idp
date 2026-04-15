/**
 * Prisma Tenant Middleware Tests
 * اختبارات ميدل وير عزل المستأجرين لـ Prisma
 *
 * Tests for tenant isolation middleware including:
 * - createTenantExtension() structure and query hooks
 * - lowerFirst() case conversion
 * - TENANT_MODELS set contents
 * - initializeRlsContext() export and behavior
 * - injectTenantWhere() tenant ID injection
 */

import { describe, it, expect, vi } from 'vitest';
import {
  createTenantExtension,
  initializeRlsContext,
  TENANT_MODELS,
} from '../middleware/prisma-tenant.middleware';

// ─────────────────────────────────────────────────────────────────────────────
// TENANT_MODELS Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('TENANT_MODELS', () => {
  it('should be a Set', () => {
    expect(TENANT_MODELS).toBeInstanceOf(Set);
  });

  it('should contain expected core models', () => {
    const expectedModels = [
      'field',
      'farm',
      'task',
      'ndviReading',
      'product',
      'order',
      'message',
      'channel',
      'device',
      'assessment',
    ];

    for (const model of expectedModels) {
      expect(TENANT_MODELS.has(model)).toBe(true);
    }
  });

  it('should contain financial models', () => {
    const financialModels = [
      'wallet',
      'transaction',
      'loan',
      'creditEvent',
      'escrow',
      'scheduledPayment',
      'walletAuditLog',
    ];

    for (const model of financialModels) {
      expect(TENANT_MODELS.has(model)).toBe(true);
    }
  });

  it('should contain marketplace models', () => {
    const marketplaceModels = [
      'sellerProfile',
      'buyerProfile',
      'productReview',
      'reviewResponse',
      'orderItem',
    ];

    for (const model of marketplaceModels) {
      expect(TENANT_MODELS.has(model)).toBe(true);
    }
  });

  it('should contain research and intelligence models', () => {
    const researchModels = [
      'researchTrial',
      'experiment',
      'dataPoint',
      'cropModel',
      'growthStage',
      'yieldPrediction',
      'laiReading',
    ];

    for (const model of researchModels) {
      expect(TENANT_MODELS.has(model)).toBe(true);
    }
  });

  it('should not contain non-tenant models', () => {
    expect(TENANT_MODELS.has('user')).toBe(false);
    expect(TENANT_MODELS.has('tenant')).toBe(false);
    expect(TENANT_MODELS.has('role')).toBe(false);
    expect(TENANT_MODELS.has('permission')).toBe(false);
  });

  it('should have the expected total count of models', () => {
    expect(TENANT_MODELS.size).toBe(34);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// createTenantExtension() Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('createTenantExtension', () => {
  const tenantId = 'tenant-abc-123';

  it('should return an extension object with correct name', () => {
    const ext = createTenantExtension(tenantId);
    expect(ext.name).toBe('tenant-isolation');
  });

  it('should return an extension object with query hooks', () => {
    const ext = createTenantExtension(tenantId);
    expect(ext.query).toBeDefined();
    expect(ext.query.$allModels).toBeDefined();
  });

  it('should have all expected query operation hooks', () => {
    const ext = createTenantExtension(tenantId);
    const hooks = ext.query.$allModels;

    const expectedOps = [
      'findMany',
      'findFirst',
      'findUnique',
      'create',
      'createMany',
      'update',
      'updateMany',
      'delete',
      'deleteMany',
      'count',
      'aggregate',
    ];

    for (const op of expectedOps) {
      expect(typeof hooks[op]).toBe('function');
    }
  });

  // ─────────────────────────────────────────────────────────────────────────
  // injectTenantWhere via query hooks
  // ─────────────────────────────────────────────────────────────────────────

  describe('findMany hook - tenant where injection', () => {
    it('should inject tenantId for tenant-aware models (camelCase)', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue([]);
      const args: any = { where: { status: 'active' } };

      await ext.query.$allModels.findMany({
        args,
        query: mockQuery,
        model: 'field',
      });

      expect(args.where.tenantId).toBe(tenantId);
      expect(args.where.status).toBe('active');
      expect(mockQuery).toHaveBeenCalledWith(args);
    });

    it('should inject tenantId for PascalCase model names', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue([]);
      const args: any = { where: {} };

      await ext.query.$allModels.findMany({
        args,
        query: mockQuery,
        model: 'Field',
      });

      expect(args.where.tenantId).toBe(tenantId);
    });

    it('should NOT inject tenantId for non-tenant models', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue([]);
      const args: any = { where: { email: 'test@example.com' } };

      await ext.query.$allModels.findMany({
        args,
        query: mockQuery,
        model: 'User',
      });

      expect(args.where.tenantId).toBeUndefined();
      expect(args.where.email).toBe('test@example.com');
    });

    it('should create where clause if args.where is undefined', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue([]);
      const args: any = {};

      await ext.query.$allModels.findMany({
        args,
        query: mockQuery,
        model: 'Farm',
      });

      expect(args.where).toBeDefined();
      expect(args.where.tenantId).toBe(tenantId);
    });
  });

  describe('findFirst hook', () => {
    it('should inject tenantId into where clause', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue(null);
      const args: any = { where: { id: '123' } };

      await ext.query.$allModels.findFirst({
        args,
        query: mockQuery,
        model: 'Task',
      });

      expect(args.where.tenantId).toBe(tenantId);
      expect(args.where.id).toBe('123');
    });
  });

  describe('findUnique hook', () => {
    it('should inject tenantId into where clause', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue(null);
      const args: any = { where: { id: 'unique-1' } };

      await ext.query.$allModels.findUnique({
        args,
        query: mockQuery,
        model: 'NdviReading',
      });

      expect(args.where.tenantId).toBe(tenantId);
    });
  });

  describe('create hook', () => {
    it('should inject tenantId into data for tenant-aware models', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({ id: 'new-1' });
      const args: any = { data: { name: 'Test Field' } };

      await ext.query.$allModels.create({
        args,
        query: mockQuery,
        model: 'Field',
      });

      expect(args.data.tenantId).toBe(tenantId);
      expect(args.data.name).toBe('Test Field');
    });

    it('should NOT inject tenantId for non-tenant models on create', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({ id: 'new-1' });
      const args: any = { data: { email: 'test@test.com' } };

      await ext.query.$allModels.create({
        args,
        query: mockQuery,
        model: 'User',
      });

      expect(args.data.tenantId).toBeUndefined();
    });
  });

  describe('createMany hook', () => {
    it('should inject tenantId into each item when data is an array', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({ count: 2 });
      const args: any = {
        data: [{ name: 'Field A' }, { name: 'Field B' }],
      };

      await ext.query.$allModels.createMany({
        args,
        query: mockQuery,
        model: 'Field',
      });

      expect(args.data).toHaveLength(2);
      expect(args.data[0].tenantId).toBe(tenantId);
      expect(args.data[1].tenantId).toBe(tenantId);
      expect(args.data[0].name).toBe('Field A');
    });

    it('should inject tenantId when data is a single object', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({ count: 1 });
      const args: any = { data: { name: 'Single Field' } };

      await ext.query.$allModels.createMany({
        args,
        query: mockQuery,
        model: 'Farm',
      });

      expect(args.data.tenantId).toBe(tenantId);
    });
  });

  describe('update hook', () => {
    it('should inject tenantId into where clause', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({ id: '1' });
      const args: any = { where: { id: '1' }, data: { name: 'Updated' } };

      await ext.query.$allModels.update({
        args,
        query: mockQuery,
        model: 'Field',
      });

      expect(args.where.tenantId).toBe(tenantId);
    });
  });

  describe('delete hook', () => {
    it('should inject tenantId into where clause', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({ id: '1' });
      const args: any = { where: { id: '1' } };

      await ext.query.$allModels.delete({
        args,
        query: mockQuery,
        model: 'Task',
      });

      expect(args.where.tenantId).toBe(tenantId);
    });
  });

  describe('count hook', () => {
    it('should inject tenantId into where clause', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue(5);
      const args: any = { where: { status: 'active' } };

      await ext.query.$allModels.count({
        args,
        query: mockQuery,
        model: 'Device',
      });

      expect(args.where.tenantId).toBe(tenantId);
    });
  });

  describe('aggregate hook', () => {
    it('should inject tenantId into where clause', async () => {
      const ext = createTenantExtension(tenantId);
      const mockQuery = vi.fn().mockResolvedValue({});
      const args: any = { where: {} };

      await ext.query.$allModels.aggregate({
        args,
        query: mockQuery,
        model: 'Transaction',
      });

      expect(args.where.tenantId).toBe(tenantId);
    });
  });

  describe('tenant isolation between different tenants', () => {
    it('should use correct tenantId for each extension instance', async () => {
      const ext1 = createTenantExtension('tenant-A');
      const ext2 = createTenantExtension('tenant-B');

      const mockQuery = vi.fn().mockResolvedValue([]);
      const args1: any = { where: {} };
      const args2: any = { where: {} };

      await ext1.query.$allModels.findMany({
        args: args1,
        query: mockQuery,
        model: 'Field',
      });
      await ext2.query.$allModels.findMany({
        args: args2,
        query: mockQuery,
        model: 'Field',
      });

      expect(args1.where.tenantId).toBe('tenant-A');
      expect(args2.where.tenantId).toBe('tenant-B');
    });
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// initializeRlsContext Tests
// ─────────────────────────────────────────────────────────────────────────────

describe('initializeRlsContext', () => {
  it('should be exported as a function', () => {
    expect(typeof initializeRlsContext).toBe('function');
  });

  it('should call $transaction on the prisma client', async () => {
    const mockTransaction = vi.fn().mockImplementation(async (cb: any) => {
      await cb({
        $executeRaw: vi.fn().mockResolvedValue(undefined),
      });
    });
    const mockPrisma = { $transaction: mockTransaction };

    await initializeRlsContext(mockPrisma, 'tenant-123');

    expect(mockTransaction).toHaveBeenCalledOnce();
  });

  it('should set RLS context with tenant ID and default isAdmin=false', async () => {
    const executeRawCalls: any[] = [];
    const mockTransaction = vi.fn().mockImplementation(async (cb: any) => {
      await cb({
        $executeRaw: vi.fn().mockImplementation((...args: any[]) => {
          executeRawCalls.push(args);
          return Promise.resolve(undefined);
        }),
      });
    });
    const mockPrisma = { $transaction: mockTransaction };

    await initializeRlsContext(mockPrisma, 'tenant-xyz');

    // Should have called $executeRaw twice: once for tenant, once for admin flag
    expect(executeRawCalls).toHaveLength(2);
  });

  it('should not throw when $transaction fails (defense-in-depth)', async () => {
    const mockPrisma = {
      $transaction: vi.fn().mockRejectedValue(new Error('DB connection lost')),
    };

    // Should not throw
    await expect(initializeRlsContext(mockPrisma, 'tenant-123')).resolves.toBeUndefined();
  });

  it('should accept isAdmin parameter', async () => {
    const mockTransaction = vi.fn().mockImplementation(async (cb: any) => {
      await cb({
        $executeRaw: vi.fn().mockResolvedValue(undefined),
      });
    });
    const mockPrisma = { $transaction: mockTransaction };

    await initializeRlsContext(mockPrisma, 'tenant-123', true);

    expect(mockTransaction).toHaveBeenCalledOnce();
  });

  it('should call $executeRaw directly when given a transaction client', async () => {
    const executeRawCalls: any[] = [];
    const mockTxClient = {
      $executeRaw: vi.fn().mockImplementation((...args: any[]) => {
        executeRawCalls.push(args);
        return Promise.resolve(undefined);
      }),
    };

    await initializeRlsContext(mockTxClient, 'tenant-tx-123');

    // Should call $executeRaw directly (no $transaction wrapper)
    expect(executeRawCalls).toHaveLength(2);
  });

  it('should not throw when $executeRaw fails on transaction client', async () => {
    const mockTxClient = {
      $executeRaw: vi.fn().mockRejectedValue(new Error('connection lost')),
    };

    await expect(initializeRlsContext(mockTxClient, 'tenant-123')).resolves.toBeUndefined();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// lowerFirst (tested indirectly via createTenantExtension)
// ─────────────────────────────────────────────────────────────────────────────

describe('lowerFirst (indirect)', () => {
  const tenantId = 'tenant-test';

  it("should convert PascalCase 'Field' to match 'field' in TENANT_MODELS", async () => {
    const ext = createTenantExtension(tenantId);
    const mockQuery = vi.fn().mockResolvedValue([]);
    const args: any = { where: {} };

    await ext.query.$allModels.findMany({
      args,
      query: mockQuery,
      model: 'Field',
    });

    // If lowerFirst works, tenantId is injected because "field" is in TENANT_MODELS
    expect(args.where.tenantId).toBe(tenantId);
  });

  it("should convert PascalCase 'NdviReading' to 'ndviReading'", async () => {
    const ext = createTenantExtension(tenantId);
    const mockQuery = vi.fn().mockResolvedValue([]);
    const args: any = { where: {} };

    await ext.query.$allModels.findMany({
      args,
      query: mockQuery,
      model: 'NdviReading',
    });

    expect(args.where.tenantId).toBe(tenantId);
  });

  it('should handle already-lowercase model names', async () => {
    const ext = createTenantExtension(tenantId);
    const mockQuery = vi.fn().mockResolvedValue([]);
    const args: any = { where: {} };

    await ext.query.$allModels.findMany({
      args,
      query: mockQuery,
      model: 'farm',
    });

    expect(args.where.tenantId).toBe(tenantId);
  });

  it('should not match unknown model names', async () => {
    const ext = createTenantExtension(tenantId);
    const mockQuery = vi.fn().mockResolvedValue([]);
    const args: any = { where: {} };

    await ext.query.$allModels.findMany({
      args,
      query: mockQuery,
      model: 'UnknownModel',
    });

    expect(args.where.tenantId).toBeUndefined();
  });

  it("should handle 'FieldBoundaryHistory' (multi-word PascalCase)", async () => {
    const ext = createTenantExtension(tenantId);
    const mockQuery = vi.fn().mockResolvedValue([]);
    const args: any = { where: {} };

    await ext.query.$allModels.findMany({
      args,
      query: mockQuery,
      model: 'FieldBoundaryHistory',
    });

    expect(args.where.tenantId).toBe(tenantId);
  });
});
