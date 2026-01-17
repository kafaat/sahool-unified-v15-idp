/**
 * SAHOOL AI Skills Hooks
 * خطافات مهارات الذكاء الاصطناعي
 */

export { useContextCompression, CompressionLevel } from "./useContextCompression";
export type {
  ContextMetadata,
  CompressionStats,
} from "./useContextCompression";

export { useFarmMemory, MemoryEntryType } from "./useFarmMemory";
export type {
  MemoryEntry,
  MemoryStatistics,
  MemoryQueryOptions,
} from "./useFarmMemory";

export {
  useRecommendationEvaluation,
  EvaluationStatus,
  FeedbackType,
} from "./useRecommendationEvaluation";
export type {
  EvaluationScore,
  RecommendationEvaluation,
  EvaluationStatistics,
  EvaluationFilterOptions,
} from "./useRecommendationEvaluation";
