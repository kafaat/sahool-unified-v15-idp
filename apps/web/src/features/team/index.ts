/**
 * SAHOOL Team Management Feature
 * Export all team management components, hooks, and utilities
 */

// Components
export { TeamManagement } from './components/TeamManagement';
export { MemberCard } from './components/MemberCard';
export { InviteMemberDialog } from './components/InviteMemberDialog';
export { RoleSelector } from './components/RoleSelector';
export { PermissionsMatrix } from './components/PermissionsMatrix';

// Hooks
export {
  useTeamMembers,
  useTeamMember,
  useRoles,
  usePermissions,
  useTeamStats,
  useInviteMember,
  useUpdateRole,
  useRemoveMember,
} from './hooks/useTeam';

// API
export { teamApi } from './api/team-api';

// Types
export type {
  TeamMember,
  Role,
  UserStatus,
  Permission,
  PermissionCategory,
  PermissionAction,
  RoleConfig,
  InviteRequest,
  RoleUpdate,
  TeamStats,
  TeamFilters,
  ApiResponse,
} from './types/team';

export { ROLE_CONFIGS } from './types/team';
