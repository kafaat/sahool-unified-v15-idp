/**
 * Tasks Service - Agricultural Task Operations
 */

import { Injectable, NotFoundException, Logger } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService, CACHE_KEYS, CACHE_TTL } from "../cache/cache.service";

@Injectable()
export class TasksService {
  private readonly logger = new Logger(TasksService.name);

  constructor(
    private prisma: PrismaService,
    private cacheService: CacheService,
  ) {}

  /**
   * Get tasks for a field
   */
  async getTasksForField(fieldId: string, status?: string) {
    const cacheKey = CACHE_KEYS.TASK_LIST(fieldId);

    // Try cache if no status filter
    if (!status) {
      const cached = await this.cacheService.get<any[]>(cacheKey);
      if (cached) return cached;
    }

    const where: any = { fieldId };
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
    title: string;
    titleAr?: string;
    description?: string;
    taskType: string;
    priority?: string;
    dueDate?: Date;
    scheduledTime?: string;
    assignedTo?: string;
    createdBy: string;
    estimatedMinutes?: number;
  }) {
    const task = await this.prisma.task.create({
      data: {
        fieldId: data.fieldId,
        title: data.title,
        titleAr: data.titleAr,
        description: data.description,
        taskType: data.taskType as any,
        priority: (data.priority as any) || "medium",
        status: "pending",
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
   * Update task status
   */
  async updateTaskStatus(
    id: string,
    status: string,
    completionNotes?: string,
    actualMinutes?: number,
  ) {
    const task = await this.prisma.task.findUnique({
      where: { id },
      select: { fieldId: true },
    });

    if (!task) {
      throw new NotFoundException("Task not found - المهمة غير موجودة");
    }

    const updated = await this.prisma.task.update({
      where: { id },
      data: {
        status: status as any,
        completedAt: status === "completed" ? new Date() : null,
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
   * Get overdue tasks
   */
  async getOverdueTasks(tenantId?: string) {
    const now = new Date();

    const where: any = {
      status: { in: ["pending", "in_progress"] },
      dueDate: { lt: now },
    };

    if (tenantId) {
      where.field = { tenantId };
    }

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
