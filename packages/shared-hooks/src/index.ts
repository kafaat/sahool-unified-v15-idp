// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Shared Hooks
// خطافات React الموحدة لمنصة سهول
// ═══════════════════════════════════════════════════════════════════════════════

// WebSocket
export { useWebSocket, type UseWebSocketOptions, type UseWebSocketReturn, type WSMessage } from './useWebSocket';

// Authentication
export {
  useAuth,
  useCan,
  useCanAny,
  useCanAll,
  useHasRole,
  AuthContext,
  createAuthContextValue,
  type User,
  type AuthState,
  type AuthContextValue,
  type AuthProviderProps,
  type Permission,
  type Role,
  PERMISSIONS,
  ROLES,
  ROLE_PERMISSIONS,
  roleHasPermission,
  getRolePermissions,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  getPermissionsForRoles,
} from './auth';

// Storage
export { useLocalStorage } from './useLocalStorage';

// Utilities
export { useDebounce, useDebouncedCallback } from './useDebounce';

// API
export { useApi, usePaginatedApi, type UseApiOptions, type UseApiReturn, type UsePaginatedApiOptions, type UsePaginatedApiReturn } from './useApi';
