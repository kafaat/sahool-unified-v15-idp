/**
 * SAHOOL Task Types
 * Domain types for agricultural task management
 *
 * Tasks represent actionable items such as irrigation, fertilization,
 * pest control, harvesting, and other field operations.
 */

import type {
  TenantEntity,
  BilingualName,
  BilingualDescription,
  Priority,
  ISODateString,
  ISODateTimeString,
} from "./common";

// ═══════════════════════════════════════════════════════════════════════════════
// Task Status Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Task lifecycle status
 */
export type TaskStatus =
  | "open"        // Created but not started
  | "pending"     // Awaiting prerequisites or approval
  | "in_progress" // Currently being executed
  | "completed"   // Successfully finished
  | "cancelled"   // Cancelled before completion
  | "on_hold"     // Temporarily paused
  | "overdue";    // Past due date without completion

/**
 * Task type categories
 */
export type TaskType =
  | "irrigation"
  | "fertilization"
  | "pesticide"
  | "herbicide"
  | "planting"
  | "harvesting"
  | "soil_preparation"
  | "pruning"
  | "scouting"
  | "maintenance"
  | "inspection"
  | "sampling"
  | "transport"
  | "storage"
  | "general";

/**
 * Task recurrence patterns
 */
export type RecurrencePattern =
  | "none"
  | "daily"
  | "weekly"
  | "biweekly"
  | "monthly"
  | "custom";

// ═══════════════════════════════════════════════════════════════════════════════
// Task Entity Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Core task entity
 */
export interface Task extends TenantEntity, BilingualName, BilingualDescription {
  /** Associated field ID */
  fieldId: string;

  /** Associated farm ID */
  farmId?: string;

  /** Task type/category */
  type: TaskType;

  /** Current status */
  status: TaskStatus;

  /** Priority level */
  priority: Priority;

  /** Due date */
  dueDate?: ISODateString;

  /** Due datetime (more precise) */
  dueDateTime?: ISODateTimeString;

  /** Scheduled start time */
  scheduledStart?: ISODateTimeString;

  /** Scheduled end time */
  scheduledEnd?: ISODateTimeString;

  /** Actual start time */
  actualStart?: ISODateTimeString;

  /** Actual completion time */
  completedAt?: ISODateTimeString;

  /** Assigned user ID */
  assignedTo?: string;

  /** Assigned user name */
  assigneeName?: string;

  /** Created by user ID */
  createdBy: string;

  /** Estimated duration in minutes */
  estimatedDurationMin?: number;

  /** Actual duration in minutes */
  actualDurationMin?: number;

  /** Estimated cost */
  estimatedCost?: number;

  /** Actual cost */
  actualCost?: number;

  /** Currency for costs */
  currency?: string;

  /** Parent task ID (for subtasks) */
  parentTaskId?: string;

  /** Subtask IDs */
  subtaskIds?: string[];

  /** Dependent task IDs (must be completed first) */
  dependsOn?: string[];

  /** Tags for filtering */
  tags?: string[];

  /** Evidence/completion photos */
  evidencePhotos?: string[];

  /** Evidence notes */
  evidenceNotes?: string;

  /** Recurrence pattern */
  recurrence?: RecurrencePattern;

  /** Recurrence interval (for custom) */
  recurrenceInterval?: number;

  /** Next occurrence date */
  nextOccurrence?: ISODateString;

  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Task with snake_case properties (API compatibility)
 */
export interface TaskSnakeCase {
  id: string;
  tenant_id: string;
  field_id: string;
  farm_id?: string;
  title: string;
  title_ar?: string;
  description?: string;
  description_ar?: string;
  type?: string;
  status: string;
  priority: string;
  due_date?: string;
  assigned_to?: string;
  evidence_photos?: string[];
  evidence_notes?: string;
  created_at: string;
  updated_at: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task Evidence Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Evidence attached to a completed task
 */
export interface TaskEvidence {
  /** Evidence ID */
  id: string;
  /** Task ID */
  taskId: string;
  /** Evidence type */
  type: "photo" | "document" | "video" | "audio" | "note";
  /** File URL (for media types) */
  fileUrl?: string;
  /** Thumbnail URL */
  thumbnailUrl?: string;
  /** Text content (for notes) */
  content?: string;
  /** Content in Arabic */
  contentAr?: string;
  /** File size in bytes */
  fileSizeBytes?: number;
  /** MIME type */
  mimeType?: string;
  /** Captured/created timestamp */
  capturedAt: string;
  /** GPS coordinates where captured */
  capturedLocation?: {
    lat: number;
    lng: number;
  };
  /** Who uploaded/created */
  uploadedBy: string;
}

/**
 * Task completion data
 */
export interface TaskCompletion {
  /** Task ID */
  taskId: string;
  /** Completion status */
  status: "completed" | "partially_completed" | "failed";
  /** Completion notes */
  notes?: string;
  /** Notes in Arabic */
  notesAr?: string;
  /** Completion percentage (0-100) */
  completionPercent?: number;
  /** Evidence items */
  evidence?: TaskEvidence[];
  /** Actual duration in minutes */
  actualDurationMin?: number;
  /** Actual cost */
  actualCost?: number;
  /** Materials used */
  materialsUsed?: TaskMaterial[];
  /** Completed by user ID */
  completedBy: string;
  /** Completion timestamp */
  completedAt: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task Material Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Material/input used in a task
 */
export interface TaskMaterial {
  /** Material ID */
  id?: string;
  /** Material name */
  name: string;
  /** Material name in Arabic */
  nameAr?: string;
  /** Material type */
  type: "fertilizer" | "pesticide" | "herbicide" | "seed" | "water" | "fuel" | "other";
  /** Quantity used */
  quantity: number;
  /** Unit of measurement */
  unit: string;
  /** Unit cost */
  unitCost?: number;
  /** Total cost */
  totalCost?: number;
  /** Batch/lot number */
  batchNumber?: string;
  /** Application rate */
  applicationRate?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task Assignment Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Task assignment details
 */
export interface TaskAssignment {
  /** Assignment ID */
  id: string;
  /** Task ID */
  taskId: string;
  /** Assigned user ID */
  assigneeId: string;
  /** Assignee name */
  assigneeName?: string;
  /** Assignee role */
  assigneeRole?: string;
  /** Assignment date */
  assignedAt: string;
  /** Assigned by user ID */
  assignedBy: string;
  /** Assignment notes */
  notes?: string;
  /** Notification sent */
  notificationSent: boolean;
  /** Acknowledgment status */
  acknowledged: boolean;
  /** Acknowledgment timestamp */
  acknowledgedAt?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task Board Types (Kanban)
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Kanban board column
 */
export interface TaskBoardColumn {
  /** Column ID (matches status) */
  id: TaskStatus;
  /** Column title */
  title: string;
  /** Title in Arabic */
  titleAr: string;
  /** Tasks in this column */
  tasks: Task[];
  /** Task count */
  count: number;
  /** Column color */
  color?: string;
  /** WIP limit */
  wipLimit?: number;
}

/**
 * Task board configuration
 */
export interface TaskBoard {
  /** Board ID */
  id: string;
  /** Board name */
  name: string;
  /** Columns */
  columns: TaskBoardColumn[];
  /** Total tasks */
  totalTasks: number;
  /** Last updated */
  lastUpdated: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task Statistics Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Task statistics
 */
export interface TaskStatistics {
  /** Total tasks */
  total: number;
  /** Open tasks */
  open: number;
  /** In progress tasks */
  inProgress: number;
  /** Completed tasks */
  completed: number;
  /** Overdue tasks */
  overdue: number;
  /** Cancelled tasks */
  cancelled: number;
  /** Tasks by type */
  byType: Record<TaskType, number>;
  /** Tasks by priority */
  byPriority: Record<Priority, number>;
  /** Average completion time in minutes */
  avgCompletionTimeMin?: number;
  /** Completion rate (percentage) */
  completionRate: number;
  /** On-time completion rate */
  onTimeRate: number;
  /** Tasks due today */
  dueToday: number;
  /** Tasks due this week */
  dueThisWeek: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Task Request/Response Types
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Request to create a task
 */
export interface CreateTaskRequest {
  /** Tenant ID */
  tenantId: string;
  /** Field ID */
  fieldId: string;
  /** Farm ID */
  farmId?: string;
  /** Task title */
  name: string;
  /** Title in Arabic */
  nameAr?: string;
  /** Description */
  description?: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Task type */
  type?: TaskType;
  /** Priority */
  priority?: Priority;
  /** Due date */
  dueDate?: ISODateString;
  /** Scheduled start */
  scheduledStart?: ISODateTimeString;
  /** Scheduled end */
  scheduledEnd?: ISODateTimeString;
  /** Assign to user ID */
  assignedTo?: string;
  /** Estimated duration in minutes */
  estimatedDurationMin?: number;
  /** Estimated cost */
  estimatedCost?: number;
  /** Parent task ID */
  parentTaskId?: string;
  /** Dependent task IDs */
  dependsOn?: string[];
  /** Tags */
  tags?: string[];
  /** Recurrence */
  recurrence?: RecurrencePattern;
  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Request to update a task
 */
export interface UpdateTaskRequest {
  /** Task title */
  name?: string;
  /** Title in Arabic */
  nameAr?: string;
  /** Description */
  description?: string;
  /** Description in Arabic */
  descriptionAr?: string;
  /** Task type */
  type?: TaskType;
  /** Status */
  status?: TaskStatus;
  /** Priority */
  priority?: Priority;
  /** Due date */
  dueDate?: ISODateString;
  /** Scheduled start */
  scheduledStart?: ISODateTimeString;
  /** Scheduled end */
  scheduledEnd?: ISODateTimeString;
  /** Assign to user ID */
  assignedTo?: string;
  /** Estimated duration */
  estimatedDurationMin?: number;
  /** Estimated cost */
  estimatedCost?: number;
  /** Tags */
  tags?: string[];
  /** Evidence photos */
  evidencePhotos?: string[];
  /** Evidence notes */
  evidenceNotes?: string;
}

/**
 * Filters for querying tasks
 */
export interface TaskFilters {
  /** Filter by field */
  fieldId?: string;
  /** Filter by farm */
  farmId?: string;
  /** Filter by assignee */
  assignedTo?: string;
  /** Filter by status */
  status?: TaskStatus | TaskStatus[];
  /** Filter by type */
  type?: TaskType | TaskType[];
  /** Filter by priority */
  priority?: Priority | Priority[];
  /** Filter by due date range start */
  dueDateFrom?: ISODateString;
  /** Filter by due date range end */
  dueDateTo?: ISODateString;
  /** Include overdue only */
  overdueOnly?: boolean;
  /** Filter by tags */
  tags?: string[];
  /** Search by title/description */
  search?: string;
}

/**
 * Task response with additional computed fields
 */
export interface TaskResponse extends Task {
  /** Field name */
  fieldName?: string;
  /** Farm name */
  farmName?: string;
  /** Is overdue */
  isOverdue?: boolean;
  /** Days until due (negative if overdue) */
  daysUntilDue?: number;
  /** Subtasks */
  subtasks?: Task[];
  /** Dependent tasks */
  dependencies?: Task[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Type Guards
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Type guard for Task
 */
export function isTask(obj: unknown): obj is Task {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "id" in obj &&
    "fieldId" in obj &&
    "status" in obj &&
    "priority" in obj
  );
}

/**
 * Type guard for valid TaskStatus
 */
export function isTaskStatus(value: unknown): value is TaskStatus {
  const validStatuses: TaskStatus[] = [
    "open",
    "pending",
    "in_progress",
    "completed",
    "cancelled",
    "on_hold",
    "overdue",
  ];
  return typeof value === "string" && validStatuses.includes(value as TaskStatus);
}

/**
 * Type guard for valid TaskType
 */
export function isTaskType(value: unknown): value is TaskType {
  const validTypes: TaskType[] = [
    "irrigation",
    "fertilization",
    "pesticide",
    "herbicide",
    "planting",
    "harvesting",
    "soil_preparation",
    "pruning",
    "scouting",
    "maintenance",
    "inspection",
    "sampling",
    "transport",
    "storage",
    "general",
  ];
  return typeof value === "string" && validTypes.includes(value as TaskType);
}

/**
 * Check if a task is overdue
 */
export function isTaskOverdue(task: Task): boolean {
  if (!task.dueDate || task.status === "completed" || task.status === "cancelled") {
    return false;
  }
  return new Date(task.dueDate) < new Date();
}
