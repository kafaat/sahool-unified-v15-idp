/**
 * Labor Management Feature - React Hooks
 * خطافات React لميزة إدارة العمالة
 */

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { laborApi } from '../api';
import type {
  WorkerFilters,
  WorkerFormData,
  TaskFilters,
  TaskFormData,
  AttendanceFilters,
} from '../types';

// ── Query Keys ─────────────────────────────────────────────

export const laborKeys = {
  all: ['labor'] as const,

  workers: () => [...laborKeys.all, 'workers'] as const,
  workerLists: () => [...laborKeys.workers(), 'list'] as const,
  workerList: (filters?: WorkerFilters) => [...laborKeys.workerLists(), filters] as const,
  workerDetail: (id: string) => [...laborKeys.workers(), 'detail', id] as const,

  tasks: () => [...laborKeys.all, 'tasks'] as const,
  taskLists: () => [...laborKeys.tasks(), 'list'] as const,
  taskList: (filters?: TaskFilters) => [...laborKeys.taskLists(), filters] as const,
  taskDetail: (id: string) => [...laborKeys.tasks(), 'detail', id] as const,

  attendance: () => [...laborKeys.all, 'attendance'] as const,
  attendanceList: (filters?: AttendanceFilters) => [...laborKeys.attendance(), 'list', filters] as const,

  leave: () => [...laborKeys.all, 'leave'] as const,
  leaveList: (workerId?: string) => [...laborKeys.leave(), 'list', workerId] as const,

  timesheets: () => [...laborKeys.all, 'timesheets'] as const,
  timesheetList: (filters?: { workerId?: string; periodStart?: string; periodEnd?: string }) =>
    [...laborKeys.timesheets(), 'list', filters] as const,

  safety: () => [...laborKeys.all, 'safety'] as const,
  safetyViolations: (workerId?: string) => [...laborKeys.safety(), 'violations', workerId] as const,
  reiZones: (fieldId?: string) => [...laborKeys.safety(), 'rei-zones', fieldId] as const,

  stats: () => [...laborKeys.all, 'stats'] as const,
};

// ── Workers ────────────────────────────────────────────────

export function useWorkers(filters?: WorkerFilters) {
  return useQuery({
    queryKey: laborKeys.workerList(filters),
    queryFn: () => laborApi.getWorkers(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useWorker(id: string) {
  return useQuery({
    queryKey: laborKeys.workerDetail(id),
    queryFn: () => laborApi.getWorker(id),
    enabled: !!id,
  });
}

export function useCreateWorker() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: WorkerFormData) => laborApi.createWorker(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.workerLists() });
      qc.invalidateQueries({ queryKey: laborKeys.stats() });
    },
  });
}

export function useUpdateWorker() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<WorkerFormData> }) =>
      laborApi.updateWorker(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: laborKeys.workerLists() });
      qc.invalidateQueries({ queryKey: laborKeys.workerDetail(id) });
    },
  });
}

export function useDeleteWorker() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => laborApi.deleteWorker(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: laborKeys.workerLists() });
      qc.removeQueries({ queryKey: laborKeys.workerDetail(id) });
      qc.invalidateQueries({ queryKey: laborKeys.stats() });
    },
  });
}

// ── Tasks ──────────────────────────────────────────────────

export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: laborKeys.taskList(filters),
    queryFn: () => laborApi.getTasks(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useTask(id: string) {
  return useQuery({
    queryKey: laborKeys.taskDetail(id),
    queryFn: () => laborApi.getTask(id),
    enabled: !!id,
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: TaskFormData) => laborApi.createTask(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.taskLists() });
      qc.invalidateQueries({ queryKey: laborKeys.stats() });
    },
  });
}

export function useUpdateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<TaskFormData> }) =>
      laborApi.updateTask(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: laborKeys.taskLists() });
      qc.invalidateQueries({ queryKey: laborKeys.taskDetail(id) });
    },
  });
}

export function useAssignTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ taskId, workerIds }: { taskId: string; workerIds: string[] }) =>
      laborApi.assignTask(taskId, workerIds),
    onSuccess: (_, { taskId }) => {
      qc.invalidateQueries({ queryKey: laborKeys.taskLists() });
      qc.invalidateQueries({ queryKey: laborKeys.taskDetail(taskId) });
    },
  });
}

// ── Attendance ─────────────────────────────────────────────

export function useAttendance(filters?: AttendanceFilters) {
  return useQuery({
    queryKey: laborKeys.attendanceList(filters),
    queryFn: () => laborApi.getAttendance(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useRecordAttendance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: laborApi.recordAttendance,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.attendance() });
      qc.invalidateQueries({ queryKey: laborKeys.stats() });
    },
  });
}

export function useClockIn() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (workerId: string) => laborApi.clockIn(workerId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.attendance() });
    },
  });
}

export function useClockOut() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (workerId: string) => laborApi.clockOut(workerId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.attendance() });
      qc.invalidateQueries({ queryKey: laborKeys.stats() });
    },
  });
}

// ── Leave ──────────────────────────────────────────────────

export function useLeaveRequests(workerId?: string) {
  return useQuery({
    queryKey: laborKeys.leaveList(workerId),
    queryFn: () => laborApi.getLeaveRequests(workerId),
    staleTime: 1000 * 60 * 5,
  });
}

export function useSubmitLeaveRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: laborApi.submitLeaveRequest,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.leave() });
    },
  });
}

export function useApproveLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => laborApi.approveLeave(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.leave() });
      qc.invalidateQueries({ queryKey: laborKeys.stats() });
    },
  });
}

export function useRejectLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      laborApi.rejectLeave(id, reason),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.leave() });
    },
  });
}

// ── Timesheets ─────────────────────────────────────────────

export function useTimesheets(filters?: { workerId?: string; periodStart?: string; periodEnd?: string }) {
  return useQuery({
    queryKey: laborKeys.timesheetList(filters),
    queryFn: () => laborApi.getTimesheets(filters),
    staleTime: 1000 * 60 * 5,
  });
}

export function useGenerateTimesheet() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ workerId, periodStart, periodEnd }: { workerId: string; periodStart: string; periodEnd: string }) =>
      laborApi.generateTimesheet(workerId, periodStart, periodEnd),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: laborKeys.timesheets() });
    },
  });
}

// ── Safety ─────────────────────────────────────────────────

export function useSafetyViolations(workerId?: string) {
  return useQuery({
    queryKey: laborKeys.safetyViolations(workerId),
    queryFn: () => laborApi.getSafetyViolations(workerId),
    staleTime: 1000 * 60 * 5,
  });
}

export function useREIZones(fieldId?: string) {
  return useQuery({
    queryKey: laborKeys.reiZones(fieldId),
    queryFn: () => laborApi.getREIZones(fieldId),
    staleTime: 1000 * 60 * 5,
  });
}

// ── Stats ──────────────────────────────────────────────────

export function useLaborStats() {
  return useQuery({
    queryKey: laborKeys.stats(),
    queryFn: () => laborApi.getStats(),
    staleTime: 1000 * 60 * 5,
  });
}
