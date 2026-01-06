/**
 * SAHOOL Action Windows Feature
 * ميزة نوافذ العمل
 *
 * Main export file for action windows feature
 */

// Types
export type {
  WindowStatus,
  ActionType,
  WeatherCondition,
  SprayWindow,
  SprayWindowCriteria,
  IrrigationWindow,
  IrrigationNeed,
  ActionRecommendation as ActionRecommendationType,
  Timeline,
  TimelineBlock,
  ThresholdIndicator,
  GetSprayWindowsRequest,
  GetIrrigationWindowsRequest,
  GetActionRecommendationsRequest,
  ActionWindowsResponse,
  WindowCalculationResult,
  SoilMoistureData,
  ETData,
} from './types/action-windows';

// API
export {
  getSprayWindows,
  getIrrigationWindows,
  getActionRecommendations,
  actionWindowsKeys,
  ERROR_MESSAGES,
} from './api/action-windows-api';

// Hooks
export {
  useSprayWindows,
  useOptimalSprayWindows,
  useNextSprayWindow,
  useIrrigationWindows,
  useUrgentIrrigationWindows,
  useNextIrrigationWindow,
  useActionRecommendations,
  useHighPriorityRecommendations,
  useRecommendationsByType,
  useAllActionWindows,
} from './hooks/useActionWindows';

export type {
  ActionWindowsHookOptions,
  SprayWindowsOptions,
  ActionRecommendationsOptions,
} from './hooks/useActionWindows';

// Components
export {
  SprayWindowsPanel,
  IrrigationWindowsPanel,
  WindowTimeline,
  WeatherConditions,
  ActionRecommendation,
  ActionWindowsDemo,
} from './components';

// Utils
export {
  calculateSprayWindow,
  calculateIrrigationNeed,
  getOptimalWindow,
  calculateET0,
  groupIntoWindows,
  DEFAULT_SPRAY_CRITERIA,
} from './utils/window-calculator';
