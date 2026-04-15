/**
 * Labor Management Feature - API Layer
 * طبقة API لميزة إدارة العمالة
 */

import { API_PREFIX } from '@sahool/shared-types/contracts';
import { createApiClient, extractData } from '@/lib/api/factory';
import { safeFetch } from '@/lib/api/safe-fetch';
import type {
  Worker,
  WorkerFilters,
  WorkerFormData,
  FarmTask,
  TaskFilters,
  TaskFormData,
  AttendanceRecord,
  AttendanceFilters,
  LeaveRequest,
  Timesheet,
  SafetyViolation,
  REIZone,
  LaborStats,
} from './types';

const api = createApiClient();
const BASE = `${API_PREFIX}/labor`;

export const laborApi = {
  // ── Workers ──────────────────────────────────────────────

  getWorkers: async (filters?: WorkerFilters): Promise<Worker[]> => {
    return safeFetch(`${BASE}/workers`, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.workerType) params.set('worker_type', filters.workerType);
      if (filters?.farmId) params.set('farm_id', filters.farmId);
      if (filters?.department) params.set('department', filters.department);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${BASE}/workers?${params.toString()}`);
      const data = extractData<Worker[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getWorker: async (id: string): Promise<Worker> => {
    return safeFetch(`${BASE}/workers/${id}`, async () => {
      const response = await api.get(`${BASE}/workers/${encodeURIComponent(id)}`);
      return extractData<Worker>(response);
    });
  },

  createWorker: async (data: WorkerFormData): Promise<Worker> => {
    return safeFetch(`${BASE}/workers`, async () => {
      const response = await api.post(`${BASE}/workers`, data);
      return extractData<Worker>(response);
    });
  },

  updateWorker: async (id: string, data: Partial<WorkerFormData>): Promise<Worker> => {
    return safeFetch(`${BASE}/workers/${id}`, async () => {
      const response = await api.put(`${BASE}/workers/${encodeURIComponent(id)}`, data);
      return extractData<Worker>(response);
    });
  },

  deleteWorker: async (id: string): Promise<void> => {
    return safeFetch(`${BASE}/workers/${id}`, async () => {
      await api.delete(`${BASE}/workers/${encodeURIComponent(id)}`);
    });
  },

  // ── Tasks ────────────────────────────────────────────────

  getTasks: async (filters?: TaskFilters): Promise<FarmTask[]> => {
    return safeFetch(`${BASE}/tasks`, async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status', filters.status);
      if (filters?.priority) params.set('priority', filters.priority);
      if (filters?.category) params.set('category', filters.category);
      if (filters?.fieldId) params.set('field_id', filters.fieldId);
      if (filters?.assignedWorkerId) params.set('assigned_worker_id', filters.assignedWorkerId);
      if (filters?.search) params.set('search', filters.search);
      const response = await api.get(`${BASE}/tasks?${params.toString()}`);
      const data = extractData<FarmTask[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getTask: async (id: string): Promise<FarmTask> => {
    return safeFetch(`${BASE}/tasks/${id}`, async () => {
      const response = await api.get(`${BASE}/tasks/${encodeURIComponent(id)}`);
      return extractData<FarmTask>(response);
    });
  },

  createTask: async (data: TaskFormData): Promise<FarmTask> => {
    return safeFetch(`${BASE}/tasks`, async () => {
      const response = await api.post(`${BASE}/tasks`, data);
      return extractData<FarmTask>(response);
    });
  },

  updateTask: async (id: string, data: Partial<TaskFormData>): Promise<FarmTask> => {
    return safeFetch(`${BASE}/tasks/${id}`, async () => {
      const response = await api.put(`${BASE}/tasks/${encodeURIComponent(id)}`, data);
      return extractData<FarmTask>(response);
    });
  },

  assignTask: async (taskId: string, workerIds: string[]): Promise<FarmTask> => {
    return safeFetch(`${BASE}/tasks/${taskId}/assign`, async () => {
      const response = await api.post(
        `${BASE}/tasks/${encodeURIComponent(taskId)}/assign`,
        { workerIds },
      );
      return extractData<FarmTask>(response);
    });
  },

  // ── Attendance ───────────────────────────────────────────

  getAttendance: async (filters?: AttendanceFilters): Promise<AttendanceRecord[]> => {
    return safeFetch(`${BASE}/attendance`, async () => {
      const params = new URLSearchParams();
      if (filters?.workerId) params.set('worker_id', filters.workerId);
      if (filters?.date) params.set('date', filters.date);
      if (filters?.dateFrom) params.set('date_from', filters.dateFrom);
      if (filters?.dateTo) params.set('date_to', filters.dateTo);
      if (filters?.status) params.set('status', filters.status);
      const response = await api.get(`${BASE}/attendance?${params.toString()}`);
      const data = extractData<AttendanceRecord[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  recordAttendance: async (data: Omit<AttendanceRecord, 'id'>): Promise<AttendanceRecord> => {
    return safeFetch(`${BASE}/attendance`, async () => {
      const response = await api.post(`${BASE}/attendance`, data);
      return extractData<AttendanceRecord>(response);
    });
  },

  clockIn: async (workerId: string): Promise<AttendanceRecord> => {
    return safeFetch(`${BASE}/attendance/clock-in`, async () => {
      const response = await api.post(`${BASE}/attendance/clock-in`, { workerId });
      return extractData<AttendanceRecord>(response);
    });
  },

  clockOut: async (workerId: string): Promise<AttendanceRecord> => {
    return safeFetch(`${BASE}/attendance/clock-out`, async () => {
      const response = await api.post(`${BASE}/attendance/clock-out`, { workerId });
      return extractData<AttendanceRecord>(response);
    });
  },

  // ── Leave ────────────────────────────────────────────────

  getLeaveRequests: async (workerId?: string): Promise<LeaveRequest[]> => {
    return safeFetch(`${BASE}/leave`, async () => {
      const params = new URLSearchParams();
      if (workerId) params.set('worker_id', workerId);
      const response = await api.get(`${BASE}/leave?${params.toString()}`);
      const data = extractData<LeaveRequest[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  submitLeaveRequest: async (data: Omit<LeaveRequest, 'id' | 'status' | 'approvedBy' | 'approvalDate'>): Promise<LeaveRequest> => {
    return safeFetch(`${BASE}/leave`, async () => {
      const response = await api.post(`${BASE}/leave`, data);
      return extractData<LeaveRequest>(response);
    });
  },

  approveLeave: async (id: string): Promise<LeaveRequest> => {
    return safeFetch(`${BASE}/leave/${id}/approve`, async () => {
      const response = await api.post(
        `${BASE}/leave/${encodeURIComponent(id)}/approve`,
      );
      return extractData<LeaveRequest>(response);
    });
  },

  rejectLeave: async (id: string, reason: string): Promise<LeaveRequest> => {
    return safeFetch(`${BASE}/leave/${id}/reject`, async () => {
      const response = await api.post(
        `${BASE}/leave/${encodeURIComponent(id)}/reject`,
        { reason },
      );
      return extractData<LeaveRequest>(response);
    });
  },

  // ── Timesheets ───────────────────────────────────────────

  getTimesheets: async (filters?: { workerId?: string; periodStart?: string; periodEnd?: string }): Promise<Timesheet[]> => {
    return safeFetch(`${BASE}/timesheets`, async () => {
      const params = new URLSearchParams();
      if (filters?.workerId) params.set('worker_id', filters.workerId);
      if (filters?.periodStart) params.set('period_start', filters.periodStart);
      if (filters?.periodEnd) params.set('period_end', filters.periodEnd);
      const response = await api.get(`${BASE}/timesheets?${params.toString()}`);
      const data = extractData<Timesheet[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  generateTimesheet: async (
    workerId: string,
    periodStart: string,
    periodEnd: string,
  ): Promise<Timesheet> => {
    return safeFetch(`${BASE}/timesheets/generate`, async () => {
      const response = await api.post(`${BASE}/timesheets/generate`, {
        workerId,
        periodStart,
        periodEnd,
      });
      return extractData<Timesheet>(response);
    });
  },

  // ── Safety ───────────────────────────────────────────────

  getSafetyViolations: async (workerId?: string): Promise<SafetyViolation[]> => {
    return safeFetch(`${BASE}/safety/violations`, async () => {
      const params = new URLSearchParams();
      if (workerId) params.set('worker_id', workerId);
      const response = await api.get(`${BASE}/safety/violations?${params.toString()}`);
      const data = extractData<SafetyViolation[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  getREIZones: async (fieldId?: string): Promise<REIZone[]> => {
    return safeFetch(`${BASE}/safety/rei-zones`, async () => {
      const params = new URLSearchParams();
      if (fieldId) params.set('field_id', fieldId);
      const response = await api.get(`${BASE}/safety/rei-zones?${params.toString()}`);
      const data = extractData<REIZone[]>(response);
      if (Array.isArray(data)) return data;
      return [];
    });
  },

  // ── Stats ────────────────────────────────────────────────

  getStats: async (): Promise<LaborStats> => {
    return safeFetch(`${BASE}/stats`, async () => {
      const response = await api.get(`${BASE}/stats`);
      return extractData<LaborStats>(response);
    });
  },
};
