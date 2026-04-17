/**
 * Field Audit History — public surface of the feature module.
 * السطح العام لوحدة سجل تدقيق الحقل
 */

export { fieldAuditHistoryApi, RESOURCE_TYPE_FIELD, mapBackendPage, buildTrailQuery } from './api';
export { useFieldAuditTrail, useReplayedState } from './hooks';
export type { UseFieldAuditTrailResult } from './hooks';
export { default as Timeline } from './components/Timeline';
export { default as TimelineEntry } from './components/TimelineEntry';
export { default as DiffViewer, computeDiff } from './components/DiffViewer';
export { default as HistoryFilters } from './components/HistoryFilters';
export { default as ReplayView } from './components/ReplayView';
export type {
  FieldAuditEvent,
  FieldAuditFilters,
  FieldAuditTrailPage,
  PaginationState,
  ReplayedState,
} from './types';
