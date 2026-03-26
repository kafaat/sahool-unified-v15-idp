/**
 * Audit Feature - React Hooks
 * خطافات React لميزة سجل التدقيق
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { auditApi } from '../api';
import type { AuditFilters } from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export const auditKeys = {
  all: ['audit'] as const,
  lists: () => [...auditKeys.all, 'list'] as const,
  list: (filters?: AuditFilters) => [...auditKeys.lists(), filters] as const,
  detail: (id: string) => [...auditKeys.all, 'detail', id] as const,
  stats: () => [...auditKeys.all, 'stats'] as const,
};

// ═══════════════════════════════════════════════════════════════════════════
// Query Hooks (Read Operations)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to fetch audit logs with optional filters
 * خطاف لجلب سجلات التدقيق مع فلاتر اختيارية
 */
export function useAuditLogs(filters?: AuditFilters) {
  return useQuery({
    queryKey: auditKeys.list(filters),
    queryFn: () => auditApi.getLogs(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch a single audit log by ID
 * خطاف لجلب سجل تدقيق واحد بواسطة المعرف
 */
export function useAuditLog(id: string) {
  return useQuery({
    queryKey: auditKeys.detail(id),
    queryFn: () => auditApi.getLogById(id),
    enabled: !!id,
  });
}

/**
 * Hook to fetch audit statistics
 * خطاف لجلب إحصائيات التدقيق
 */
export function useAuditStats() {
  return useQuery({
    queryKey: auditKeys.stats(),
    queryFn: () => auditApi.getStats(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
