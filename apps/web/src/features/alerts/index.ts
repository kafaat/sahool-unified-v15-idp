/**
 * Alerts Feature - Main Exports
 * ميزة التنبيهات - الصادرات الرئيسية
 *
 * This feature handles:
 * - Alert display and management
 * - Real-time alert streaming
 * - Alert acknowledgment, resolution, and dismissal
 * - Alert statistics and analytics
 * - Bulk alert operations
 */

// ═══════════════════════════════════════════════════════════════════════════
// API Layer
// ═══════════════════════════════════════════════════════════════════════════

export { alertsApi, ERROR_MESSAGES } from './api';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Core Alert Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  Alert,
  AlertSeverity,
  AlertCategory,
  AlertStatus,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Filter and Query Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  AlertFilters,
  AlertListParams,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Statistics Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  AlertStats,
  AlertCount,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - API Response Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  AlertListResponse,
  AlertResponse,
  AlertStatsResponse,
  AlertCountResponse,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Mutation Payload Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  CreateAlertPayload,
  UpdateAlertPayload,
  AcknowledgeAlertPayload,
  ResolveAlertPayload,
  DismissAlertPayload,
  BulkAlertActionPayload,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Stream Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  AlertStreamEvent,
  AlertStreamOptions,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Hook Return Types
// ═══════════════════════════════════════════════════════════════════════════

export type {
  UseAlertsReturn,
  UseAlertReturn,
  UseAlertStatsReturn,
  UseAlertStreamReturn,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Types - Error Messages
// ═══════════════════════════════════════════════════════════════════════════

export type {
  BilingualMessage,
  AlertErrorMessages,
} from './types';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks - Query Keys
// ═══════════════════════════════════════════════════════════════════════════

export { alertKeys } from './hooks/useAlerts';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks - Query Hooks (Read Operations)
// ═══════════════════════════════════════════════════════════════════════════

export {
  useAlerts,
  useAlert,
  useActiveAlertsCount,
  useAlertStats,
} from './hooks/useAlerts';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks - Mutation Hooks (Write Operations)
// ═══════════════════════════════════════════════════════════════════════════

export {
  useCreateAlert,
  useUpdateAlert,
  useAcknowledgeAlert,
  useResolveAlert,
  useDismissAlert,
  useDeleteAlert,
  useBulkAcknowledgeAlerts,
  useBulkDismissAlerts,
} from './hooks/useAlerts';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks - Real-time Stream Hook
// ═══════════════════════════════════════════════════════════════════════════

export { useAlertStream } from './hooks/useAlerts';

// ═══════════════════════════════════════════════════════════════════════════
// Hooks - Composite Hooks
// ═══════════════════════════════════════════════════════════════════════════

export { useAlertMutations } from './hooks/useAlerts';
