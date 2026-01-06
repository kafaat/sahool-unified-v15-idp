/**
 * SAHOOL Team Management Hooks
 * خطافات إدارة الفريق
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { teamApi } from '../api/team-api';
import type { InviteRequest, Role, TeamFilters } from '../types/team';

/**
 * Query Hooks - For reading data
 * خطافات الاستعلام - لقراءة البيانات
 */

/**
 * Get all team members with optional filters
 * جلب جميع أعضاء الفريق مع فلاتر اختيارية
 */
export function useTeamMembers(filters?: TeamFilters) {
  return useQuery({
    queryKey: ['team', 'members', filters],
    queryFn: () => teamApi.getTeamMembers(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Get a single team member by ID
 * جلب عضو فريق واحد بواسطة المعرف
 */
export function useTeamMember(id: string) {
  return useQuery({
    queryKey: ['team', 'member', id],
    queryFn: () => teamApi.getMember(id),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

/**
 * Get available roles
 * جلب الأدوار المتاحة
 */
export function useRoles() {
  return useQuery({
    queryKey: ['team', 'roles'],
    queryFn: () => teamApi.getRoles(),
    staleTime: 10 * 60 * 1000, // 10 minutes - roles don't change often
  });
}

/**
 * Get permissions for a specific role
 * جلب الصلاحيات لدور معين
 */
export function usePermissions(role: Role) {
  return useQuery({
    queryKey: ['team', 'permissions', role],
    queryFn: () => teamApi.getPermissions(role),
    enabled: !!role,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Get team statistics
 * جلب إحصائيات الفريق
 */
export function useTeamStats() {
  return useQuery({
    queryKey: ['team', 'stats'],
    queryFn: () => teamApi.getStats(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Mutation Hooks - For writing/updating data
 * خطافات الطفرة - لكتابة/تحديث البيانات
 */

/**
 * Invite a new team member
 * دعوة عضو فريق جديد
 */
export function useInviteMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: InviteRequest) => teamApi.inviteMember(data),
    onSuccess: () => {
      // Invalidate and refetch team data
      queryClient.invalidateQueries({ queryKey: ['team', 'members'] });
      queryClient.invalidateQueries({ queryKey: ['team', 'stats'] });
    },
  });
}

/**
 * Update a team member's role
 * تحديث دور عضو الفريق
 */
export function useUpdateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: Role }) =>
      teamApi.updateMemberRole(userId, role),
    onSuccess: (_, variables) => {
      // Invalidate specific member and list
      queryClient.invalidateQueries({ queryKey: ['team', 'members'] });
      queryClient.invalidateQueries({ queryKey: ['team', 'member', variables.userId] });
      queryClient.invalidateQueries({ queryKey: ['team', 'stats'] });
    },
  });
}

/**
 * Remove a team member
 * إزالة عضو فريق
 */
export function useRemoveMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => teamApi.removeMember(userId),
    onSuccess: () => {
      // Invalidate team data
      queryClient.invalidateQueries({ queryKey: ['team', 'members'] });
      queryClient.invalidateQueries({ queryKey: ['team', 'stats'] });
    },
  });
}
