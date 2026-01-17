/**
 * Tasks Types Tests
 * اختبارات أنواع المهام
 */

import { describe, it, expect } from "vitest";
import type {
  Task,
  TaskFormData,
  TaskFilters,
  TaskBoardColumn,
  TaskEvidence,
  TaskAssignment,
  TaskStatistics,
  TaskUpdatePayload,
  TaskResponse,
} from "../types";

describe("Tasks Types", () => {
  describe("Task interface", () => {
    it("should create a valid task object", () => {
      const task: Task = {
        id: "task-001",
        title: "Apply Fertilizer",
        title_ar: "تطبيق الأسمدة",
        description: "Apply nitrogen fertilizer to field A",
        description_ar: "تطبيق سماد النيتروجين على الحقل أ",
        status: "pending",
        priority: "high",
        field_id: "field-123",
        created_at: "2026-01-06T08:00:00Z",
        updated_at: "2026-01-06T08:00:00Z",
        due_date: "2026-01-08T12:00:00Z",
      } as Task;

      expect(task.id).toBe("task-001");
      expect(task.title).toBe("Apply Fertilizer");
      expect(task.priority).toBe("high");
    });

    it("should support optional fields", () => {
      const task: Task = {
        id: "task-002",
        title: "Irrigation Check",
        title_ar: "فحص الري",
        status: "in_progress",
        priority: "medium",
        created_at: "2026-01-06T09:00:00Z",
        updated_at: "2026-01-06T10:00:00Z",
        completed_at: undefined,
        farm_id: "farm-456",
      } as Task;

      expect(task.farm_id).toBe("farm-456");
      expect(task.completed_at).toBeUndefined();
    });

    it("should support task completion", () => {
      const task: Task = {
        id: "task-003",
        title: "Pest Inspection",
        title_ar: "فحص الآفات",
        status: "completed",
        priority: "low",
        created_at: "2026-01-05T08:00:00Z",
        updated_at: "2026-01-06T14:00:00Z",
        completed_at: "2026-01-06T14:00:00Z",
      } as Task;

      expect(task.status).toBe("completed");
      expect(task.completed_at).toBeDefined();
    });
  });

  describe("TaskFormData interface", () => {
    it("should create valid form data", () => {
      const formData: TaskFormData = {
        title: "New Task",
        title_ar: "مهمة جديدة",
        description: "Task description",
        description_ar: "وصف المهمة",
        due_date: "2026-01-10T12:00:00Z",
        priority: "high",
        field_id: "field-123",
        assigned_to: "user-456",
      };

      expect(formData.title).toBe("New Task");
      expect(formData.priority).toBe("high");
      expect(formData.due_date).toBeDefined();
    });

    it("should require bilingual titles", () => {
      const formData: TaskFormData = {
        title: "Harvest Preparation",
        title_ar: "تحضير الحصاد",
        due_date: "2026-01-15T08:00:00Z",
        priority: "medium",
      };

      expect(formData.title).toBeDefined();
      expect(formData.title_ar).toBeDefined();
    });

    it("should support status in form", () => {
      const formData: TaskFormData = {
        title: "Equipment Maintenance",
        title_ar: "صيانة المعدات",
        due_date: "2026-01-12T10:00:00Z",
        priority: "low",
        status: "pending",
      };

      expect(formData.status).toBe("pending");
    });
  });

  describe("TaskFilters interface", () => {
    it("should create valid filters", () => {
      const filters: TaskFilters = {
        search: "irrigation",
        status: "pending",
        priority: "high",
        field_id: "field-123",
      };

      expect(filters.search).toBe("irrigation");
      expect(filters.status).toBe("pending");
    });

    it("should support date range filters", () => {
      const filters: TaskFilters = {
        due_date_from: "2026-01-01",
        due_date_to: "2026-01-31",
        assigned_to: "user-456",
      };

      expect(filters.due_date_from).toBe("2026-01-01");
      expect(filters.due_date_to).toBe("2026-01-31");
    });
  });

  describe("TaskBoardColumn interface", () => {
    it("should create valid Kanban column", () => {
      const column: TaskBoardColumn = {
        id: "pending",
        title: "Pending",
        title_ar: "قيد الانتظار",
        tasks: [],
        color: "#FFA500",
      };

      expect(column.id).toBe("pending");
      expect(column.title).toBe("Pending");
      expect(column.color).toBe("#FFA500");
    });

    it("should hold tasks array", () => {
      const mockTask: Task = {
        id: "task-001",
        title: "Test Task",
        title_ar: "مهمة اختبار",
        status: "pending",
        priority: "medium",
        created_at: "2026-01-06T08:00:00Z",
        updated_at: "2026-01-06T08:00:00Z",
      } as Task;

      const column: TaskBoardColumn = {
        id: "pending",
        title: "Pending",
        title_ar: "قيد الانتظار",
        tasks: [mockTask],
        color: "#FFA500",
      };

      expect(column.tasks).toHaveLength(1);
      expect(column.tasks[0].id).toBe("task-001");
    });

    it("should support different status columns", () => {
      const columns: TaskBoardColumn[] = [
        {
          id: "pending",
          title: "Pending",
          title_ar: "قيد الانتظار",
          tasks: [],
          color: "#FFA500",
        },
        {
          id: "in_progress",
          title: "In Progress",
          title_ar: "قيد التنفيذ",
          tasks: [],
          color: "#2196F3",
        },
        {
          id: "completed",
          title: "Completed",
          title_ar: "مكتمل",
          tasks: [],
          color: "#4CAF50",
        },
        {
          id: "cancelled",
          title: "Cancelled",
          title_ar: "ملغي",
          tasks: [],
          color: "#9E9E9E",
        },
      ];

      expect(columns).toHaveLength(4);
      expect(columns.map((c) => c.id)).toContain("in_progress");
    });
  });

  describe("TaskEvidence interface", () => {
    it("should create valid evidence object", () => {
      const evidence: TaskEvidence = {
        notes: "Task completed successfully. Applied 50kg of fertilizer.",
        photos: ["photo1.jpg", "photo2.jpg"],
      };

      expect(evidence.notes).toContain("successfully");
      expect(evidence.photos).toHaveLength(2);
    });

    it("should allow notes without photos", () => {
      const evidence: TaskEvidence = {
        notes: "Visual inspection completed. No issues found.",
      };

      expect(evidence.notes).toBeDefined();
      expect(evidence.photos).toBeUndefined();
    });

    it("should allow photos without notes", () => {
      const evidence: TaskEvidence = {
        photos: ["before.jpg", "after.jpg", "detail.jpg"],
      };

      expect(evidence.photos).toHaveLength(3);
      expect(evidence.notes).toBeUndefined();
    });
  });

  describe("TaskAssignment interface", () => {
    it("should create valid assignment", () => {
      const assignment: TaskAssignment = {
        task_id: "task-001",
        user_id: "user-456",
        assigned_at: "2026-01-06T09:00:00Z",
        assigned_by: "user-123",
      };

      expect(assignment.task_id).toBe("task-001");
      expect(assignment.user_id).toBe("user-456");
      expect(assignment.assigned_by).toBe("user-123");
    });

    it("should support self-assignment", () => {
      const assignment: TaskAssignment = {
        task_id: "task-002",
        user_id: "user-456",
        assigned_at: "2026-01-06T10:00:00Z",
        assigned_by: "user-456",
      };

      expect(assignment.user_id).toBe(assignment.assigned_by);
    });
  });

  describe("TaskStatistics interface", () => {
    it("should track comprehensive statistics", () => {
      const stats: TaskStatistics = {
        total: 100,
        open: 25,
        in_progress: 30,
        completed: 40,
        cancelled: 5,
        overdue: 8,
        by_priority: {
          high: 15,
          medium: 50,
          low: 35,
        },
      };

      expect(stats.total).toBe(100);
      expect(stats.overdue).toBe(8);
      expect(stats.by_priority.high).toBe(15);
    });

    it("should have consistent totals", () => {
      const stats: TaskStatistics = {
        total: 50,
        open: 10,
        in_progress: 15,
        completed: 20,
        cancelled: 5,
        overdue: 3,
        by_priority: {
          high: 10,
          medium: 25,
          low: 15,
        },
      };

      // Verify status totals
      const statusSum =
        stats.open + stats.in_progress + stats.completed + stats.cancelled;
      expect(statusSum).toBe(stats.total);

      // Verify priority totals
      const prioritySum =
        stats.by_priority.high +
        stats.by_priority.medium +
        stats.by_priority.low;
      expect(prioritySum).toBe(stats.total);
    });

    it("should track overdue separately", () => {
      const stats: TaskStatistics = {
        total: 30,
        open: 10,
        in_progress: 10,
        completed: 8,
        cancelled: 2,
        overdue: 5, // These overlap with open/in_progress
        by_priority: {
          high: 8,
          medium: 12,
          low: 10,
        },
      };

      // Overdue tasks are subset of open + in_progress
      expect(stats.overdue).toBeLessThanOrEqual(stats.open + stats.in_progress);
    });
  });

  describe("TaskUpdatePayload interface", () => {
    it("should support partial updates", () => {
      const payload: TaskUpdatePayload = {
        status: "in_progress",
      };

      expect(payload.status).toBe("in_progress");
      expect(payload.title).toBeUndefined();
    });

    it("should support multiple field updates", () => {
      const payload: TaskUpdatePayload = {
        title: "Updated Title",
        title_ar: "العنوان المحدث",
        description: "New description",
        description_ar: "وصف جديد",
        status: "completed",
        priority: "high",
        due_date: "2026-01-15T12:00:00Z",
      };

      expect(payload.title).toBe("Updated Title");
      expect(payload.status).toBe("completed");
      expect(payload.priority).toBe("high");
    });

    it("should support reassignment", () => {
      const payload: TaskUpdatePayload = {
        assigned_to: "user-789",
        field_id: "field-456",
      };

      expect(payload.assigned_to).toBe("user-789");
      expect(payload.field_id).toBe("field-456");
    });
  });

  describe("TaskResponse interface", () => {
    it("should handle successful response", () => {
      const response: TaskResponse = {
        success: true,
        data: {
          id: "task-new",
          title: "Created Task",
          title_ar: "مهمة مُنشأة",
          status: "pending",
          priority: "medium",
          created_at: "2026-01-06T12:00:00Z",
          updated_at: "2026-01-06T12:00:00Z",
        } as Task,
        message: "Task created successfully",
        message_ar: "تم إنشاء المهمة بنجاح",
      };

      expect(response.success).toBe(true);
      expect(response.data?.id).toBe("task-new");
    });

    it("should handle error response", () => {
      const response: TaskResponse = {
        success: false,
        error: "Task not found",
        message: "The requested task does not exist",
        message_ar: "المهمة المطلوبة غير موجودة",
      };

      expect(response.success).toBe(false);
      expect(response.error).toBe("Task not found");
      expect(response.data).toBeUndefined();
    });

    it("should support bilingual messages", () => {
      const response: TaskResponse = {
        success: true,
        message: "Task updated",
        message_ar: "تم تحديث المهمة",
      };

      expect(response.message).toBe("Task updated");
      expect(response.message_ar).toBe("تم تحديث المهمة");
    });
  });

  describe("Priority and Status values", () => {
    it("should have valid priority values", () => {
      const priorities = ["high", "medium", "low"];
      expect(priorities).toHaveLength(3);
    });

    it("should have valid status values", () => {
      const statuses = ["pending", "in_progress", "completed", "cancelled"];
      expect(statuses).toHaveLength(4);
    });

    it("should follow task lifecycle", () => {
      // Normal flow: pending -> in_progress -> completed
      const normalFlow = ["pending", "in_progress", "completed"];
      expect(normalFlow[0]).toBe("pending");
      expect(normalFlow[2]).toBe("completed");

      // Alternative flow: pending -> cancelled
      const cancelledFlow = ["pending", "cancelled"];
      expect(cancelledFlow[1]).toBe("cancelled");
    });
  });
});
