/**
 * Alerts Feature
 * ميزة التنبيهات
 *
 * This feature handles:
 * - Alert display and management
 * - Real-time alert streaming
 * - Alert acknowledgment and resolution
 * - Alert statistics
 */

// API
export { alertsApi } from './api';
export type {
  Alert,
  AlertSeverity,
  AlertCategory,
  AlertStatus,
  AlertFilters,
  AlertStats,
} from './api';

// Hooks
export {
  useAlerts,
  useAlert,
  useActiveAlertsCount,
  useAlertStats,
  useAcknowledgeAlert,
  useResolveAlert,
  useDismissAlert,
  useAlertStream,
  alertKeys,
} from './hooks/useAlerts';
