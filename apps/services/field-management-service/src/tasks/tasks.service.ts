/**
 * Tasks Service - Agricultural Task Operations
 */

import { Injectable, NotFoundException, Logger } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService, CACHE_KEYS, CACHE_TTL } from "../cache/cache.service";
import { TaskType, Priority, TaskState, Prisma } from "../../prisma/generated/client";
import { assertTenantOwnership } from "../auth/tenant.utils";

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name);

  constructor(
    private prisma: PrismaService,
    private cacheService: CacheService,
  ) {}

  /**
   * Get tasks for a field with tenant isolation
   */
  async getTasksForField(fieldId: string, tenantId: string, status?: TaskState) {
    const cacheKey = CACHE_KEYS.TASK_LIST(fieldId);

    // Try cache if no status filter
    if (!status) {
      const cached = await this.cacheService.get<any[]>(cacheKey);
      if (cached) return cached;
    }

    // Scope tasks to tenant via field relationship
    const where: Prisma.TaskWhereInput = {
      fieldId,
      field: { tenantId },
    };
    if (status) where.status = status;

    const tasks = await this.prisma.task.findMany({
      where,
      orderBy: [{ priority: "desc" }, { dueDate: "asc" }],
      select: {
        id: true,
        title: true,
        titleAr: true,
        description: true,
        taskType: true,
        priority: true,
        status: true,
        dueDate: true,
        scheduledTime: true,
        completedAt: true,
        assignedTo: true,
        createdBy: true,
        estimatedMinutes: true,
        actualMinutes: true,
        completionNotes: true,
        evidence: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    // Cache if no filter
    if (!status) {
      await this.cacheService.set(cacheKey, tasks, CACHE_TTL.SHORT);
    }

    return tasks;
  }

  /**
   * Create a new task
   */
  async createTask(data: {
    fieldId?: string;
    tenantId?: string;
    title: string;
    titleAr?: string;
    description?: string;
    taskType: TaskType;
    priority?: Priority;
    dueDate?: Date;
    scheduledTime?: string;
    assignedTo?: string;
    createdBy: string;
    estimatedMinutes?: number;
  }) {
    const task = await this.prisma.task.create({
      data: {
        tenantId: data.tenantId,
        fieldId: data.fieldId,
        title: data.title,
        titleAr: data.titleAr,
        description: data.description,
        taskType: data.taskType,
        priority: data.priority || Priority.medium,
        status: TaskState.pending,
        dueDate: data.dueDate,
        scheduledTime: data.scheduledTime,
        assignedTo: data.assignedTo,
        createdBy: data.createdBy,
        estimatedMinutes: data.estimatedMinutes,
      },
    });

    // Invalidate cache
    if (data.fieldId) {
      await this.cacheService.del(CACHE_KEYS.TASK_LIST(data.fieldId));
    }

    return task;
  }

  /**
   * Update task status with tenant isolation
   */
  async updateTaskStatus(
    id: string,
    tenantId: string,
    status: TaskState,
    completionNotes?: string,
    actualMinutes?: number,
  ) {
    const task = await this.prisma.task.findUnique({
      where: { id },
      select: { fieldId: true, tenantId: true },
    });

    if (!task) {
      throw new NotFoundException("Task not found - المهمة غير موجودة");
    }

    // Enforce tenant isolation
    if (task.tenantId) {
      assertTenantOwnership(task.tenantId, tenantId, "task");
    }

    const updated = await this.prisma.task.update({
      where: { id },
      data: {
        status,
        completedAt: status === TaskState.completed ? new Date() : null,
        completionNotes,
        actualMinutes,
      },
    });

    // Invalidate cache
    if (task.fieldId) {
      await this.cacheService.del(CACHE_KEYS.TASK_LIST(task.fieldId));
    }

    return updated;
  }

  /**
   * Get overdue tasks - always scoped to tenant
   */
  async getOverdueTasks(tenantId: string) {
    const now = new Date();

    const where: Prisma.TaskWhereInput = {
      status: { in: [TaskState.pending, TaskState.in_progress] },
      dueDate: { lt: now },
      // Always filter by tenant for isolation
      field: { tenantId },
    };

    return this.prisma.task.findMany({
      where,
      include: {
        field: {
          select: {
            id: true,
            name: true,
            tenantId: true,
          },
        },
      },
      orderBy: { dueDate: "asc" },
    });
  }
}
