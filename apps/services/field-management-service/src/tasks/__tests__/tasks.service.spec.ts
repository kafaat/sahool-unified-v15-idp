/**
 * TasksService Unit Tests
 * اختبارات وحدة خدمة المهام الزراعية
 *
 * Tests task CRUD, status transitions, overdue filtering,
 * caching, and tenant isolation.
 */

import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException, ForbiddenException } from '@nestjs/common';
import { TasksService } from '../tasks.service';
import { PrismaService } from '../../prisma/prisma.service';
import { CacheService, CACHE_KEYS, CACHE_TTL } from '../../cache/cache.service';

// ---------------------------------------------------------------------------
// Enums (mirror the Prisma-generated types for isolation in unit tests)
// ---------------------------------------------------------------------------

enum TaskType {
  irrigation = 'irrigation',
  fertilization = 'fertilization',
  scouting = 'scouting',
  harvesting = 'harvesting',
  spraying = 'spraying',
  planting = 'planting',
  soil_preparation = 'soil_preparation',
  maintenance = 'maintenance',
  other = 'other',
}

enum Priority {
  low = 'low',
  medium = 'medium',
  high = 'high',
  urgent = 'urgent',
}

enum TaskState {
  pending = 'pending',
  in_progress = 'in_progress',
  completed = 'completed',
  cancelled = 'cancelled',
  skipped = 'skipped',
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const TENANT_A = 'tenant-aaa-1111';
const TENANT_B = 'tenant-bbb-2222';
const FIELD_ID = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';
const TASK_ID = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
const USER_ID = 'user-001';

const now = new Date('2026-03-30T10:00:00Z');

function makeTaskRow(overrides: Record<string, any> = {}) {
  return {
    id: TASK_ID,
    title: 'Apply nitrogen fertilizer',
    titleAr: 'تطبيق سماد النيتروجين',
    description: 'Apply 46 kg/ha Urea',
    taskType: TaskType.fertilization,
    priority: Priority.high,
    status: TaskState.pending,
    fieldId: FIELD_ID,
    tenantId: TENANT_A,
    dueDate: new Date('2026-04-05T00:00:00Z'),
    scheduledTime: '06:00',
    completedAt: null,
    assignedTo: USER_ID,
    createdBy: USER_ID,
    estimatedMinutes: 120,
    actualMinutes: null,
    completionNotes: null,
    evidence: null,
    createdAt: now,
    updatedAt: now,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Mock factories
// ---------------------------------------------------------------------------

function createMockPrisma() {
  return {
    task: {
      findMany: jest.fn(),
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
    },
  };
}

function createMockCache() {
  return {
    get: jest.fn().mockResolvedValue(null),
    set: jest.fn().mockResolvedValue(undefined),
    del: jest.fn().mockResolvedValue(undefined),
  };
}

// ---------------------------------------------------------------------------
// Test suite
// ---------------------------------------------------------------------------

describe('TasksService', () => {
  let service: TasksService;
  let prisma: ReturnType<typeof createMockPrisma>;
  let cache: ReturnType<typeof createMockCache>;

  beforeEach(async () => {
    prisma = createMockPrisma();
    cache = createMockCache();

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TasksService,
        { provide: PrismaService, useValue: prisma },
        { provide: CacheService, useValue: cache },
      ],
    }).compile();

    service = module.get<TasksService>(TasksService);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  // =========================================================================
  // getTasksForField()
  // =========================================================================
  describe('getTasksForField()', () => {
    it('should return tasks for a field scoped to tenant', async () => {
      const tasks = [makeTaskRow(), makeTaskRow({ id: 'task-2', title: 'Irrigate' })];
      prisma.task.findMany.mockResolvedValue(tasks);

      const result = await service.getTasksForField(FIELD_ID, TENANT_A);

      expect(result).toHaveLength(2);
      expect(prisma.task.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            fieldId: FIELD_ID,
            field: { tenantId: TENANT_A },
          }),
        }),
      );
    });

    it('should return empty array when field has no tasks', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      const result = await service.getTasksForField(FIELD_ID, TENANT_A);

      expect(result).toEqual([]);
    });

    it('should cache results when no status filter is applied', async () => {
      prisma.task.findMany.mockResolvedValue([makeTaskRow()]);

      await service.getTasksForField(FIELD_ID, TENANT_A);

      expect(cache.set).toHaveBeenCalledWith(
        CACHE_KEYS.TASK_LIST(FIELD_ID),
        expect.any(Array),
        CACHE_TTL.SHORT,
      );
    });

    it('should return cached tasks on cache hit when no status filter', async () => {
      const cached = [makeTaskRow()];
      cache.get.mockResolvedValue(cached);

      const result = await service.getTasksForField(FIELD_ID, TENANT_A);

      expect(result).toEqual(cached);
      expect(prisma.task.findMany).not.toHaveBeenCalled();
    });

    it('should bypass cache when status filter is provided', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      await service.getTasksForField(FIELD_ID, TENANT_A, TaskState.pending as any);

      expect(cache.get).not.toHaveBeenCalled();
      expect(cache.set).not.toHaveBeenCalled();
      const whereArg = prisma.task.findMany.mock.calls[0][0].where;
      expect(whereArg.status).toBe(TaskState.pending);
    });

    it('should order tasks by priority desc then dueDate asc', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      await service.getTasksForField(FIELD_ID, TENANT_A);

      const orderArg = prisma.task.findMany.mock.calls[0][0].orderBy;
      expect(orderArg).toEqual([{ priority: 'desc' }, { dueDate: 'asc' }]);
    });
  });

  // =========================================================================
  // createTask()
  // =========================================================================
  describe('createTask()', () => {
    it('should create a task with all fields', async () => {
      const input = {
        fieldId: FIELD_ID,
        tenantId: TENANT_A,
        title: 'Spray pesticide',
        titleAr: 'رش المبيد',
        description: 'Apply treatment',
        taskType: TaskType.spraying as any,
        priority: Priority.high as any,
        dueDate: new Date('2026-04-10T00:00:00Z'),
        assignedTo: USER_ID,
        createdBy: USER_ID,
        estimatedMinutes: 60,
      };
      prisma.task.create.mockResolvedValue(makeTaskRow({ ...input, id: 'new-task' }));

      const result = await service.createTask(input);

      expect(result.id).toBe('new-task');
      expect(prisma.task.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          title: 'Spray pesticide',
          status: TaskState.pending,
          priority: Priority.high,
        }),
      });
    });

    it('should default priority to medium when not provided', async () => {
      const input = {
        fieldId: FIELD_ID,
        tenantId: TENANT_A,
        title: 'Scout field',
        taskType: TaskType.scouting as any,
        createdBy: USER_ID,
      };
      prisma.task.create.mockResolvedValue(makeTaskRow(input));

      await service.createTask(input);

      expect(prisma.task.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          priority: Priority.medium,
        }),
      });
    });

    it('should invalidate task cache for the field', async () => {
      prisma.task.create.mockResolvedValue(makeTaskRow());

      await service.createTask({
        fieldId: FIELD_ID,
        tenantId: TENANT_A,
        title: 'Task',
        taskType: TaskType.other as any,
        createdBy: USER_ID,
      });

      expect(cache.del).toHaveBeenCalledWith(CACHE_KEYS.TASK_LIST(FIELD_ID));
    });

    it('should not invalidate cache when no fieldId is provided', async () => {
      prisma.task.create.mockResolvedValue(makeTaskRow({ fieldId: undefined }));

      await service.createTask({
        tenantId: TENANT_A,
        title: 'General task',
        taskType: TaskType.maintenance as any,
        createdBy: USER_ID,
      });

      expect(cache.del).not.toHaveBeenCalled();
    });
  });

  // =========================================================================
  // updateTaskStatus()
  // =========================================================================
  describe('updateTaskStatus()', () => {
    it('should update task status to completed and set completedAt', async () => {
      prisma.task.findUnique.mockResolvedValue(makeTaskRow());
      prisma.task.update.mockResolvedValue(
        makeTaskRow({ status: TaskState.completed, completedAt: now }),
      );

      const result = await service.updateTaskStatus(
        TASK_ID,
        TENANT_A,
        TaskState.completed as any,
        'Done successfully',
        90,
      );

      expect(result.status).toBe(TaskState.completed);
      expect(prisma.task.update).toHaveBeenCalledWith({
        where: { id: TASK_ID },
        data: expect.objectContaining({
          status: TaskState.completed,
          completionNotes: 'Done successfully',
          actualMinutes: 90,
        }),
      });
    });

    it('should set completedAt to null for non-completed statuses', async () => {
      prisma.task.findUnique.mockResolvedValue(makeTaskRow());
      prisma.task.update.mockResolvedValue(
        makeTaskRow({ status: TaskState.in_progress }),
      );

      await service.updateTaskStatus(TASK_ID, TENANT_A, TaskState.in_progress as any);

      expect(prisma.task.update).toHaveBeenCalledWith({
        where: { id: TASK_ID },
        data: expect.objectContaining({
          completedAt: null,
        }),
      });
    });

    it('should throw NotFoundException when task does not exist', async () => {
      prisma.task.findUnique.mockResolvedValue(null);

      await expect(
        service.updateTaskStatus('nonexistent', TENANT_A, TaskState.completed as any),
      ).rejects.toThrow(NotFoundException);
    });

    it('should throw ForbiddenException for cross-tenant status update', async () => {
      prisma.task.findUnique.mockResolvedValue(makeTaskRow({ tenantId: TENANT_A }));

      await expect(
        service.updateTaskStatus(TASK_ID, TENANT_B, TaskState.completed as any),
      ).rejects.toThrow(ForbiddenException);
    });

    it('should invalidate task cache after status update', async () => {
      prisma.task.findUnique.mockResolvedValue(makeTaskRow());
      prisma.task.update.mockResolvedValue(makeTaskRow({ status: TaskState.completed }));

      await service.updateTaskStatus(TASK_ID, TENANT_A, TaskState.completed as any);

      expect(cache.del).toHaveBeenCalledWith(CACHE_KEYS.TASK_LIST(FIELD_ID));
    });
  });

  // =========================================================================
  // getOverdueTasks()
  // =========================================================================
  describe('getOverdueTasks()', () => {
    it('should return overdue tasks scoped to tenant', async () => {
      const overdueTasks = [
        makeTaskRow({
          dueDate: new Date('2026-03-20T00:00:00Z'),
          field: { id: FIELD_ID, name: 'North Field', tenantId: TENANT_A },
        }),
      ];
      prisma.task.findMany.mockResolvedValue(overdueTasks);

      const result = await service.getOverdueTasks(TENANT_A);

      expect(result).toHaveLength(1);
      expect(prisma.task.findMany).toHaveBeenCalledWith(
        expect.objectContaining({
          where: expect.objectContaining({
            status: { in: [TaskState.pending, TaskState.in_progress] },
            dueDate: { lt: expect.any(Date) },
            field: { tenantId: TENANT_A },
          }),
        }),
      );
    });

    it('should return empty array when no tasks are overdue', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      const result = await service.getOverdueTasks(TENANT_A);

      expect(result).toEqual([]);
    });

    it('should include field data in overdue task results', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      await service.getOverdueTasks(TENANT_A);

      const callArgs = prisma.task.findMany.mock.calls[0][0];
      expect(callArgs.include).toEqual({
        field: { select: { id: true, name: true, tenantId: true } },
      });
    });

    it('should order overdue tasks by dueDate ascending', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      await service.getOverdueTasks(TENANT_A);

      const callArgs = prisma.task.findMany.mock.calls[0][0];
      expect(callArgs.orderBy).toEqual({ dueDate: 'asc' });
    });

    it('should limit results to 100', async () => {
      prisma.task.findMany.mockResolvedValue([]);

      await service.getOverdueTasks(TENANT_A);

      const callArgs = prisma.task.findMany.mock.calls[0][0];
      expect(callArgs.take).toBe(100);
    });
  });
});
