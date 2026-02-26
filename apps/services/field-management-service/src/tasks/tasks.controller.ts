/**
 * Tasks Controller - Task Management Endpoints
 */

import {
  Controller,
  Get,
  Post,
  Patch,
  Body,
  Param,
  Query,
  ParseUUIDPipe,
  ValidationPipe,
  HttpCode,
  HttpStatus,
  Req,
} from "@nestjs/common";
import { ApiTags, ApiOperation, ApiResponse, ApiParam, ApiQuery } from "@nestjs/swagger";
import { TasksService } from "./tasks.service";
import { TaskType, Priority, TaskState } from "@prisma/client";
import {
  IsString,
  IsOptional,
  IsEnum,
  IsNumber,
  IsDateString,
  IsUUID,
  Min,
} from "class-validator";

// Task DTOs
class CreateTaskDto {
  @IsOptional()
  @IsUUID()
  fieldId?: string;

  @IsString()
  title: string;

  @IsOptional()
  @IsString()
  titleAr?: string;

  @IsOptional()
  @IsString()
  description?: string;

  @IsEnum(TaskType)
  taskType: TaskType;

  @IsOptional()
  @IsEnum(Priority)
  priority?: Priority;

  @IsOptional()
  @IsDateString()
  dueDate?: string;

  @IsOptional()
  @IsString()
  scheduledTime?: string;

  @IsOptional()
  @IsString()
  assignedTo?: string;

  @IsString()
  createdBy: string;

  @IsOptional()
  @IsNumber()
  @Min(1)
  estimatedMinutes?: number;
}

class UpdateTaskStatusDto {
  @IsEnum(TaskState)
  status: TaskState;

  @IsOptional()
  @IsString()
  completionNotes?: string;

  @IsOptional()
  @IsNumber()
  @Min(1)
  actualMinutes?: number;
}

@ApiTags("Tasks - المهام")
@Controller("api/v1/tasks")
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}

  /**
   * Get tasks for a field
   */
  @Get("field/:fieldId")
  @ApiOperation({ summary: "Get tasks for a field" })
  @ApiParam({ name: "fieldId", type: String })
  @ApiQuery({ name: "status", required: false })
  @ApiResponse({ status: 200, description: "Tasks retrieved" })
  async getTasksForField(
    @Param("fieldId", ParseUUIDPipe) fieldId: string,
    @Query("status") status?: TaskState,
  ) {
    const tasks = await this.tasksService.getTasksForField(fieldId, status as TaskState | undefined);
    return {
      success: true,
      data: tasks,
      count: tasks.length,
    };
  }

  /**
   * Create a new task
   */
  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: "Create a new task" })
  @ApiResponse({ status: 201, description: "Task created" })
  async createTask(
    @Body(new ValidationPipe({ transform: true })) dto: CreateTaskDto,
  ) {
    const task = await this.tasksService.createTask({
      ...dto,
      taskType: dto.taskType as TaskType,
      priority: dto.priority as Priority | undefined,
      dueDate: dto.dueDate ? new Date(dto.dueDate) : undefined,
    });
    return {
      success: true,
      data: task,
      message: "تم إنشاء المهمة بنجاح",
    };
  }

  /**
   * Update task status
   */
  @Patch(":id/status")
  @ApiOperation({ summary: "Update task status" })
  @ApiParam({ name: "id", type: String })
  @ApiResponse({ status: 200, description: "Task status updated" })
  async updateTaskStatus(
    @Param("id", ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true })) dto: UpdateTaskStatusDto,
  ) {
    const task = await this.tasksService.updateTaskStatus(
      id,
      dto.status as TaskState,
      dto.completionNotes,
      dto.actualMinutes,
    );
    return {
      success: true,
      data: task,
      message: "تم تحديث حالة المهمة",
    };
  }

  /**
   * Get overdue tasks
   */
  @Get("overdue")
  @ApiOperation({ summary: "Get overdue tasks" })
  @ApiQuery({ name: "tenantId", required: false })
  @ApiResponse({ status: 200, description: "Overdue tasks retrieved" })
  async getOverdueTasks(
    @Req() req: any,
    @Query("tenantId") queryTenantId?: string,
  ) {
    const tenantId = req.user?.tenantId || req.headers['x-tenant-id'] || queryTenantId;
    const tasks = await this.tasksService.getOverdueTasks(tenantId);
    return {
      success: true,
      data: tasks,
      count: tasks.length,
    };
  }
}
