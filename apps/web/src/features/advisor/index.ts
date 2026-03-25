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

export const ADVISOR_FEATURE = 'advisor' as const;
