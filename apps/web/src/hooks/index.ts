/**
 * SAHOOL Hooks Index
 * فهرس الخطافات
 */

export { useKPIs } from './useKPIs';
export { useAlerts } from './useAlerts';
export {
  useWebSocket,
  useWebSocketEvent,
  useWebSocketEvents,
  useWebSocketQueryInvalidation,
  useWebSocketRoom,
} from './useWebSocket';
export {
  useFormValidation,
  validationPatterns,
  type ValidationRule,
  type FieldConfig,
  type FieldState,
  type FormState,
} from './useFormValidation';

// AI Skills Hooks
export * from './ai';
