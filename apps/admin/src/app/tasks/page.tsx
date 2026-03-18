"use client";

// Tasks Management Page - Full CRUD
// صفحة إدارة المهام - عمليات كاملة

import { useEffect, useState, useMemo, useCallback } from "react";
import Header from "@/components/layout/Header";
import DataTable from "@/components/ui/DataTable";
import { formatDate, cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import { API_URLS } from "@/config/api";
import { logger } from "@/lib/logger";
import type { Task, TaskStatus, Priority } from "@/types";
import {
  Search,
  Plus,
  RefreshCw,
  Download,
  CheckSquare,
  Clock,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  ArrowUpCircle,
  ArrowDownCircle,
  MinusCircle,
  X,
  Pencil,
  Trash2,
  Calendar,
} from "lucide-react";

// ═══════════════════════════════════════════════════════════════════════════
// Types
// أنواع البيانات
// ═══════════════════════════════════════════════════════════════════════════

interface TaskFormData {
  title: string;
  title_ar: string;
  description: string;
  description_ar: string;
  assigned_to: string;
  priority: Priority;
  status: TaskStatus;
  due_date: string;
  field_id: string;
}

const INITIAL_FORM_DATA: TaskFormData = {
  title: "",
  title_ar: "",
  description: "",
  description_ar: "",
  assigned_to: "",
  priority: "medium",
  status: "pending",
  due_date: "",
  field_id: "",
};

// ═══════════════════════════════════════════════════════════════════════════
// Mock Data - dynamic import for dead-code elimination in production builds.
// بيانات وهمية - استيراد ديناميكي لإزالة الكود الميت في بيئة الإنتاج
// In production, the .mock module is never bundled because the import() is unreachable.
// ═══════════════════════════════════════════════════════════════════════════

async function getMockTasks(): Promise<Task[]> {
  if (process.env.NODE_ENV !== "production") {
    const { MOCK_TASKS } = await import("./tasks.mock");
    return MOCK_TASKS;
  }
  return [];
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// دوال مساعدة
// ═══════════════════════════════════════════════════════════════════════════

function getTaskStatusColor(status: string): string {
  switch (status) {
    case "pending":
    case "open":
      return "text-yellow-600 bg-yellow-100";
    case "in_progress":
      return "text-blue-600 bg-blue-100";
    case "completed":
      return "text-green-600 bg-green-100";
    case "cancelled":
      return "text-gray-600 bg-gray-100";
    default:
      return "text-gray-600 bg-gray-100";
  }
}

function getTaskStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    open: "مفتوح",
    pending: "قيد الانتظار",
    in_progress: "قيد التنفيذ",
    completed: "مكتمل",
    cancelled: "ملغي",
  };
  return labels[status] || status;
}

function getPriorityColor(priority: string): string {
  switch (priority) {
    case "urgent":
      return "text-red-600 bg-red-100";
    case "high":
      return "text-orange-600 bg-orange-100";
    case "medium":
      return "text-yellow-600 bg-yellow-100";
    case "low":
      return "text-green-600 bg-green-100";
    default:
      return "text-gray-600 bg-gray-100";
  }
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    urgent: "عاجل",
    high: "مرتفع",
    medium: "متوسط",
    low: "منخفض",
  };
  return labels[priority] || priority;
}

function getPriorityIcon(priority: string) {
  switch (priority) {
    case "urgent":
      return <AlertTriangle className="w-4 h-4 text-red-600" />;
    case "high":
      return <ArrowUpCircle className="w-4 h-4 text-orange-600" />;
    case "medium":
      return <MinusCircle className="w-4 h-4 text-yellow-600" />;
    case "low":
      return <ArrowDownCircle className="w-4 h-4 text-green-600" />;
    default:
      return <MinusCircle className="w-4 h-4 text-gray-400" />;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Component
// المكون الرئيسي
// ═══════════════════════════════════════════════════════════════════════════

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [assigneeFilter, setAssigneeFilter] = useState("");

  // Modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [formData, setFormData] = useState<TaskFormData>(INITIAL_FORM_DATA);
  const [isSaving, setIsSaving] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // API Functions
  // دوال الاتصال بالخادم
  // ─────────────────────────────────────────────────────────────────────────

  async function loadTasks() {
    setIsLoading(true);
    try {
      const response = await apiClient.get(API_URLS.taskEndpoints.list);
      setTasks(response.data);
    } catch {
      logger.log("Falling back to static mock tasks data");
      const mockTasks = await getMockTasks();
      setTasks(mockTasks);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCreateTask() {
    setIsSaving(true);
    try {
      const payload = {
        tenant_id: "default",
        field_id: formData.field_id || "field-1",
        title: formData.title,
        title_ar: formData.title_ar,
        description: formData.description,
        description_ar: formData.description_ar,
        assigned_to: formData.assigned_to,
        priority: formData.priority,
        status: formData.status,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : undefined,
      };
      const response = await apiClient.post(API_URLS.taskEndpoints.create, payload);
      setTasks((prev) => [response.data, ...prev]);
    } catch {
      // Fallback: create task locally with generated ID
      logger.log("API unavailable, creating task locally");
      const newTask: Task = {
        id: `task-local-${Date.now()}`,
        tenant_id: "default",
        field_id: formData.field_id || "field-1",
        title: formData.title,
        title_ar: formData.title_ar,
        description: formData.description,
        description_ar: formData.description_ar,
        assigned_to: formData.assigned_to,
        priority: formData.priority,
        status: formData.status,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : undefined,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setTasks((prev) => [newTask, ...prev]);
    } finally {
      setIsSaving(false);
      setShowCreateModal(false);
      setFormData(INITIAL_FORM_DATA);
    }
  }

  async function handleUpdateTask() {
    if (!editingTask) return;
    setIsSaving(true);
    try {
      const payload = {
        title: formData.title,
        title_ar: formData.title_ar,
        description: formData.description,
        description_ar: formData.description_ar,
        assigned_to: formData.assigned_to,
        priority: formData.priority,
        status: formData.status,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : undefined,
      };
      const response = await apiClient.put(
        API_URLS.taskEndpoints.byId(editingTask.id),
        payload,
      );
      setTasks((prev) =>
        prev.map((t) => (t.id === editingTask.id ? response.data : t)),
      );
    } catch {
      // Fallback: update task locally
      logger.log("API unavailable, updating task locally");
      setTasks((prev) =>
        prev.map((t) =>
          t.id === editingTask.id
            ? {
                ...t,
                title: formData.title,
                title_ar: formData.title_ar,
                description: formData.description,
                description_ar: formData.description_ar,
                assigned_to: formData.assigned_to,
                priority: formData.priority,
                status: formData.status,
                due_date: formData.due_date
                  ? new Date(formData.due_date).toISOString()
                  : t.due_date,
                updated_at: new Date().toISOString(),
              }
            : t,
        ),
      );
    } finally {
      setIsSaving(false);
      setEditingTask(null);
      setFormData(INITIAL_FORM_DATA);
    }
  }

  async function handleDeleteTask(id: string) {
    try {
      await apiClient.delete(API_URLS.taskEndpoints.byId(id));
    } catch {
      logger.log("API unavailable, deleting task locally");
    }
    setTasks((prev) => prev.filter((t) => t.id !== id));
    setDeleteConfirmId(null);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Open edit modal
  // فتح نافذة التعديل
  // ─────────────────────────────────────────────────────────────────────────

  const openEditModal = useCallback((task: Task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      title_ar: task.title_ar || "",
      description: task.description || "",
      description_ar: task.description_ar || "",
      assigned_to: task.assigned_to || "",
      priority: task.priority,
      status: task.status,
      due_date: task.due_date?.split("T")[0] ?? "",
      field_id: task.field_id,
    });
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Filtered data
  // البيانات المفلترة
  // ─────────────────────────────────────────────────────────────────────────

  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !(t.title_ar || "").toLowerCase().includes(query) &&
          !t.title.toLowerCase().includes(query) &&
          !(t.assigned_to || "").toLowerCase().includes(query) &&
          !(t.description || "").toLowerCase().includes(query)
        ) {
          return false;
        }
      }
      if (statusFilter && t.status !== statusFilter) return false;
      if (priorityFilter && t.priority !== priorityFilter) return false;
      if (assigneeFilter && t.assigned_to !== assigneeFilter) return false;
      return true;
    });
  }, [tasks, searchQuery, statusFilter, priorityFilter, assigneeFilter]);

  // Stats
  const stats = useMemo(() => {
    const total = tasks.length;
    const pending = tasks.filter((t) => t.status === "pending" || t.status === "open").length;
    const inProgress = tasks.filter((t) => t.status === "in_progress").length;
    const completed = tasks.filter((t) => t.status === "completed").length;
    return { total, pending, inProgress, completed };
  }, [tasks]);

  // Unique assignees for filter
  const assignees = useMemo(() => {
    const set = new Set<string>();
    tasks.forEach((t) => {
      if (t.assigned_to) set.add(t.assigned_to);
    });
    return Array.from(set);
  }, [tasks]);

  // ─────────────────────────────────────────────────────────────────────────
  // Table columns
  // أعمدة الجدول
  // ─────────────────────────────────────────────────────────────────────────

  const columns = [
    {
      key: "title",
      header: "عنوان المهمة",
      render: (task: Task) => (
        <div>
          <p className="font-medium text-gray-900">{task.title_ar || task.title}</p>
          {task.title_ar && (
            <p className="text-xs text-gray-500">{task.title}</p>
          )}
        </div>
      ),
    },
    {
      key: "assigned_to",
      header: "المسؤول",
      render: (task: Task) => (
        <span className="text-gray-700">{task.assigned_to || "غير معيّن"}</span>
      ),
    },
    {
      key: "priority",
      header: "الأولوية",
      render: (task: Task) => (
        <div className="flex items-center gap-1.5">
          {getPriorityIcon(task.priority)}
          <span
            className={cn(
              "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
              getPriorityColor(task.priority),
            )}
          >
            {getPriorityLabel(task.priority)}
          </span>
        </div>
      ),
    },
    {
      key: "status",
      header: "الحالة",
      render: (task: Task) => (
        <span
          className={cn(
            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
            getTaskStatusColor(task.status),
          )}
        >
          {getTaskStatusLabel(task.status)}
        </span>
      ),
    },
    {
      key: "due_date",
      header: "تاريخ الاستحقاق",
      render: (task: Task) => (
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-gray-400" />
          <span className="text-gray-700 text-sm">
            {task.due_date ? formatDate(task.due_date) : "غير محدد"}
          </span>
        </div>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (task: Task) => (
        <div className="flex items-center gap-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              openEditModal(task);
            }}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="تعديل"
          >
            <Pencil className="w-4 h-4 text-gray-500" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setDeleteConfirmId(task.id);
            }}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
            title="حذف"
          >
            <Trash2 className="w-4 h-4 text-red-500" />
          </button>
        </div>
      ),
      className: "w-24",
    },
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Render
  // العرض
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div className="p-6">
      <Header title="إدارة المهام" subtitle={`${tasks.length} مهمة مسجلة`} />

      {/* Stats Cards - بطاقات الإحصائيات */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "" && "ring-2 ring-sahool-500 border-sahool-500",
          )}
          onClick={() => setStatusFilter("")}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sahool-100 rounded-lg flex items-center justify-center">
              <CheckSquare className="w-5 h-5 text-sahool-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-500">إجمالي المهام</p>
            </div>
          </div>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "pending" && "ring-2 ring-yellow-500 border-yellow-500",
          )}
          onClick={() => setStatusFilter(statusFilter === "pending" ? "" : "pending")}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
              <p className="text-sm text-gray-500">قيد الانتظار</p>
            </div>
          </div>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "in_progress" && "ring-2 ring-blue-500 border-blue-500",
          )}
          onClick={() => setStatusFilter(statusFilter === "in_progress" ? "" : "in_progress")}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.inProgress}</p>
              <p className="text-sm text-gray-500">قيد التنفيذ</p>
            </div>
          </div>
        </div>

        <div
          className={cn(
            "bg-white rounded-xl p-4 border border-gray-100 cursor-pointer transition-all",
            statusFilter === "completed" && "ring-2 ring-green-500 border-green-500",
          )}
          onClick={() => setStatusFilter(statusFilter === "completed" ? "" : "completed")}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
              <p className="text-sm text-gray-500">مكتملة</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Actions - شريط البحث والفلاتر */}
      <div className="mt-6 bg-white rounded-xl p-4 border border-gray-100">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="بحث بالعنوان أو المسؤول..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
            />
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الحالات</option>
            <option value="pending">قيد الانتظار</option>
            <option value="in_progress">قيد التنفيذ</option>
            <option value="completed">مكتمل</option>
            <option value="cancelled">ملغي</option>
          </select>

          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل الأولويات</option>
            <option value="urgent">عاجل</option>
            <option value="high">مرتفع</option>
            <option value="medium">متوسط</option>
            <option value="low">منخفض</option>
          </select>

          {/* Assignee Filter */}
          <select
            value={assigneeFilter}
            onChange={(e) => setAssigneeFilter(e.target.value)}
            className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
          >
            <option value="">كل المسؤولين</option>
            {assignees.map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>

          {/* Actions */}
          <button
            onClick={loadTasks}
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="تحديث"
          >
            <RefreshCw
              className={cn(
                "w-5 h-5 text-gray-600",
                isLoading && "animate-spin",
              )}
            />
          </button>
          <button
            disabled
            className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            title="تصدير (قريبًا)"
          >
            <Download className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={() => {
              setFormData(INITIAL_FORM_DATA);
              setEditingTask(null);
              setShowCreateModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-sahool-600 text-white rounded-lg hover:bg-sahool-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            إضافة مهمة
          </button>
        </div>
      </div>

      {/* Data Table - جدول البيانات */}
      <div className="mt-6">
        <DataTable
          columns={columns}
          data={filteredTasks}
          keyExtractor={(task) => task.id}
          emptyMessage="لا توجد مهام مطابقة للبحث"
          isLoading={isLoading}
        />
      </div>

      {/* Create / Edit Modal - نافذة الإنشاء / التعديل */}
      {(showCreateModal || editingTask) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">
                {editingTask ? "تعديل المهمة" : "إضافة مهمة جديدة"}
              </h2>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setEditingTask(null);
                  setFormData(INITIAL_FORM_DATA);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="px-6 py-4 space-y-4">
              {/* Title AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  العنوان (عربي) <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.title_ar}
                  onChange={(e) => setFormData({ ...formData, title_ar: e.target.value })}
                  placeholder="عنوان المهمة بالعربية"
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                />
              </div>

              {/* Title EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  العنوان (إنجليزي)
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Task title in English"
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  dir="ltr"
                />
              </div>

              {/* Description AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الوصف (عربي)
                </label>
                <textarea
                  value={formData.description_ar}
                  onChange={(e) => setFormData({ ...formData, description_ar: e.target.value })}
                  placeholder="وصف المهمة بالعربية"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 resize-none"
                />
              </div>

              {/* Description EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الوصف (إنجليزي)
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Task description in English"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500 resize-none"
                  dir="ltr"
                />
              </div>

              {/* Row: Assigned To + Field ID */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    المسؤول
                  </label>
                  <input
                    type="text"
                    value={formData.assigned_to}
                    onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                    placeholder="اسم المسؤول"
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    معرف الحقل
                  </label>
                  <input
                    type="text"
                    value={formData.field_id}
                    onChange={(e) => setFormData({ ...formData, field_id: e.target.value })}
                    placeholder="field-1"
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Row: Priority + Status + Due Date */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الأولوية
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value as Priority })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  >
                    <option value="urgent">عاجل</option>
                    <option value="high">مرتفع</option>
                    <option value="medium">متوسط</option>
                    <option value="low">منخفض</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    الحالة
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as TaskStatus })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                  >
                    <option value="pending">قيد الانتظار</option>
                    <option value="in_progress">قيد التنفيذ</option>
                    <option value="completed">مكتمل</option>
                    <option value="cancelled">ملغي</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    تاريخ الاستحقاق
                  </label>
                  <input
                    type="date"
                    value={formData.due_date}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sahool-500"
                    dir="ltr"
                  />
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setEditingTask(null);
                  setFormData(INITIAL_FORM_DATA);
                }}
                className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                إلغاء
              </button>
              <button
                onClick={editingTask ? handleUpdateTask : handleCreateTask}
                disabled={isSaving || (!formData.title_ar && !formData.title)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors",
                  isSaving || (!formData.title_ar && !formData.title)
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-sahool-600 hover:bg-sahool-700",
                )}
              >
                {isSaving && <Loader2 className="w-4 h-4 animate-spin" />}
                {editingTask ? "حفظ التعديلات" : "إنشاء المهمة"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal - نافذة تأكيد الحذف */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">تأكيد الحذف</h3>
            </div>
            <p className="text-gray-600 mb-6">
              هل أنت متأكد من حذف هذه المهمة؟ لا يمكن التراجع عن هذا الإجراء.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-4 py-2 border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                إلغاء
              </button>
              <button
                onClick={() => handleDeleteTask(deleteConfirmId)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
              >
                حذف المهمة
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
