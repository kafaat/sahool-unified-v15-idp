/**
 * Advisor Feature
 * ميزة المستشار الزراعي
 *
 * This feature handles:
 * - AI-powered agricultural recommendations
 * - Crop advice and guidance
 * - Irrigation recommendations
 * - Fertilizer suggestions
 * - Pest and disease identification
 */

// API exports
export { advisorApi } from './api';
export type {
  Recommendation,
  RecommendationType,
  RecommendationPriority,
  RecommendationStatus,
  ActionItem,
  AdvisorQuery,
  AdvisorResponse,
  AdvisorFilters,
} from './api';

// Hooks exports
export {
  useRecommendations,
  useRecommendation,
  useAskAdvisor,
  useApplyRecommendation,
  useDismissRecommendation,
  useCompleteAction,
  useAdvisorHistory,
  useAdvisorStats,
} from './hooks/useAdvisor';

// Explainability types
export type {
  Explanation,
  ContributingFactor,
  AlternativeRecommendation,
  RuleExplanation,
  ExplainIrrigationParams,
  ExplainFertilizerParams,
} from './types/explainability';
export {
  ExplanationType,
  FactorType,
  ImpactLevel,
} from './types/explainability';

// Explainability component
export { ExplanationPanel } from './components/ExplanationPanel';
export type { ExplanationPanelProps } from './components/ExplanationPanel';

export const ADVISOR_FEATURE = 'advisor' as const;
