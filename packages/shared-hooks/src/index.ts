// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Shared Hooks
// خطافات React الموحدة لمنصة سهول
// ═══════════════════════════════════════════════════════════════════════════════

// WebSocket
export { useWebSocket, type UseWebSocketOptions, type UseWebSocketReturn, type WSMessage } from './useWebSocket';

// Authentication
export { useAuth, type UseAuthOptions, type UseAuthReturn, type User, type UserRole, type LoginCredentials, type AuthResponse } from './useAuth';

// Storage
export { useLocalStorage } from './useLocalStorage';

// Utilities
export { useDebounce, useDebouncedCallback } from './useDebounce';

// API
export { useApi, usePaginatedApi, type UseApiOptions, type UseApiReturn, type UsePaginatedApiOptions, type UsePaginatedApiReturn } from './useApi';
