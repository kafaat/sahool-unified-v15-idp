/**
 * SAHOOL useRecommendationEvaluation Hook
 * تقييم توصيات الذكاء الاصطناعي
 */

"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { logger } from "@/lib/logger";

/**
 * Recommendation evaluation status
 */
export enum EvaluationStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
}

/**
 * Recommendation feedback type
 */
export enum FeedbackType {
  HELPFUL = "helpful",
  NOT_HELPFUL = "not_helpful",
  PARTIALLY_HELPFUL = "partially_helpful",
  UNCLEAR = "unclear",
}

/**
 * Recommendation evaluation score
 */
export interface EvaluationScore {
  accuracy: number; // 0-1: How accurate was the recommendation?
  timeliness: number; // 0-1: Was it timely and actionable?
  impact: number; // 0-1: What was the actual impact?
  relevance: number; // 0-1: How relevant was it to the farm?
  overall: number; // 0-1: Overall recommendation quality
}

/**
 * Recommendation evaluation data
 */
export interface RecommendationEvaluation {
  id: string;
  recommendationId: string;
  fieldId?: string;
  tenantId?: string;
  status: EvaluationStatus;
  feedback?: FeedbackType;
  scores?: EvaluationScore;
  notes?: string;
  appliedAt?: number;
  evaluatedAt?: number;
  createdAt: number;
  updatedAt: number;
}

/**
 * Evaluation statistics
 */
export interface EvaluationStatistics {
  totalEvaluations: number;
  evaluationsByStatus: Record<EvaluationStatus, number>;
  feedbackDistribution: Record<FeedbackType, number>;
  averageScores: EvaluationScore;
  successRate: number; // Percentage of helpful recommendations
  avgTimeToEvaluate: number; // in milliseconds
}

/**
 * Evaluation filter options
 */
export interface EvaluationFilterOptions {
  recommendationId?: string;
  fieldId?: string;
  tenantId?: string;
  status?: EvaluationStatus;
  feedback?: FeedbackType;
  startTime?: number;
  endTime?: number;
  limit?: number;
}

/**
 * Hook for evaluating AI recommendations
 * خطاف لتقييم توصيات الذكاء الاصطناعي
 */
export function useRecommendationEvaluation() {
  const [evaluations, setEvaluations] = useState<RecommendationEvaluation[]>([]);
  const evaluationsRef = useRef<RecommendationEvaluation[]>([]);

  // Sync ref with state
  useEffect(() => {
    evaluationsRef.current = evaluations;
  }, [evaluations]);

  /**
   * Create new evaluation for a recommendation
   * إنشاء تقييم جديد لتوصية
   */
  const createEvaluation = useCallback(
    (
      recommendationId: string,
      options?: {
        fieldId?: string;
        tenantId?: string;
      },
    ): RecommendationEvaluation => {
      const evaluation: RecommendationEvaluation = {
        id: generateEvaluationId(),
        recommendationId,
        status: EvaluationStatus.PENDING,
        createdAt: Date.now(),
        updatedAt: Date.now(),
        ...options,
      };

      setEvaluations((prev) => [evaluation, ...prev]);

      logger.debug(`[useRecommendationEvaluation] Created evaluation:`, {
        id: evaluation.id,
        recommendationId,
      });

      return evaluation;
    },
    [],
  );

  /**
   * Submit feedback for an evaluation
   * تقديم تعليقات لتقييم
   */
  const submitFeedback = useCallback(
    (
      evaluationId: string,
      feedback: FeedbackType,
      notes?: string,
    ): RecommendationEvaluation | null => {
      let updated: RecommendationEvaluation | null = null;

      setEvaluations((prev) =>
        prev.map((evaluation) => {
          if (evaluation.id === evaluationId) {
            updated = {
              ...evaluation,
              feedback,
              notes,
              updatedAt: Date.now(),
            };
            return updated;
          }
          return evaluation;
        }),
      );

      if (updated) {
        logger.debug(
          `[useRecommendationEvaluation] Submitted feedback:`,
          { evaluationId, feedback },
        );
      }

      return updated;
    },
    [],
  );

  /**
   * Submit detailed evaluation scores
   * تقديم درجات التقييم المفصلة
   */
  const submitScores = useCallback(
    (
      evaluationId: string,
      scores: Partial<EvaluationScore>,
    ): RecommendationEvaluation | null => {
      let updated: RecommendationEvaluation | null = null;

      setEvaluations((prev) =>
        prev.map((evaluation) => {
          if (evaluation.id === evaluationId) {
            const existing = evaluation.scores || {
              accuracy: 0,
              timeliness: 0,
              impact: 0,
              relevance: 0,
              overall: 0,
            };

            const merged = {
              ...existing,
              ...scores,
            };

            // Calculate overall score if not provided
            if (!scores.overall) {
              merged.overall =
                (merged.accuracy +
                  merged.timeliness +
                  merged.impact +
                  merged.relevance) /
                4;
            }

            updated = {
              ...evaluation,
              scores: merged,
              status: EvaluationStatus.COMPLETED,
              evaluatedAt: Date.now(),
              updatedAt: Date.now(),
            };
            return updated;
          }
          return evaluation;
        }),
      );

      if (updated != null) {
        logger.debug(
          `[useRecommendationEvaluation] Submitted scores:`,
          { evaluationId, scores: (updated as RecommendationEvaluation).scores },
        );
      }

      return updated;
    },
    [],
  );

  /**
   * Mark recommendation as applied
   * وضع علامة على التوصية كمطبقة
   */
  const markApplied = useCallback(
    (evaluationId: string): RecommendationEvaluation | null => {
      let updated: RecommendationEvaluation | null = null;

      setEvaluations((prev) =>
        prev.map((evaluation) => {
          if (evaluation.id === evaluationId) {
            updated = {
              ...evaluation,
              appliedAt: Date.now(),
              status: EvaluationStatus.IN_PROGRESS,
              updatedAt: Date.now(),
            };
            return updated;
          }
          return evaluation;
        }),
      );

      return updated;
    },
    [],
  );

  /**
   * Get evaluations by filters
   * الحصول على التقييمات حسب المرشحات
   */
  const getEvaluations = useCallback(
    (options?: EvaluationFilterOptions): RecommendationEvaluation[] => {
      let results = [...evaluationsRef.current];

      if (options?.recommendationId) {
        results = results.filter(
          (evaluation) => evaluation.recommendationId === options.recommendationId,
        );
      }

      if (options?.fieldId) {
        results = results.filter((evaluation) => evaluation.fieldId === options.fieldId);
      }

      if (options?.tenantId) {
        results = results.filter((evaluation) => evaluation.tenantId === options.tenantId);
      }

      if (options?.status) {
        results = results.filter((evaluation) => evaluation.status === options.status);
      }

      if (options?.feedback) {
        results = results.filter((evaluation) => evaluation.feedback === options.feedback);
      }

      if (options?.startTime) {
        results = results.filter((evaluation) => evaluation.createdAt >= options.startTime!);
      }

      if (options?.endTime) {
        results = results.filter((evaluation) => evaluation.createdAt <= options.endTime!);
      }

      if (options?.limit && options.limit > 0) {
        results = results.slice(0, options.limit);
      }

      return results;
    },
    [],
  );

  /**
   * Get evaluation statistics
   * الحصول على إحصائيات التقييم
   */
  const getStatistics = useCallback((): EvaluationStatistics => {
    const currentEvals = evaluationsRef.current;

    const statusCounts: Record<EvaluationStatus, number> = {
      [EvaluationStatus.PENDING]: 0,
      [EvaluationStatus.IN_PROGRESS]: 0,
      [EvaluationStatus.COMPLETED]: 0,
      [EvaluationStatus.FAILED]: 0,
    };

    const feedbackCounts: Record<FeedbackType, number> = {
      [FeedbackType.HELPFUL]: 0,
      [FeedbackType.NOT_HELPFUL]: 0,
      [FeedbackType.PARTIALLY_HELPFUL]: 0,
      [FeedbackType.UNCLEAR]: 0,
    };

    const totalScores: EvaluationScore = {
      accuracy: 0,
      timeliness: 0,
      impact: 0,
      relevance: 0,
      overall: 0,
    };

    let scoredCount = 0;
    let totalTimeToEvaluate = 0;
    let evaluatedCount = 0;

    currentEvals.forEach((evaluation) => {
      statusCounts[evaluation.status]++;

      if (evaluation.feedback) {
        feedbackCounts[evaluation.feedback]++;
      }

      if (evaluation.scores) {
        totalScores.accuracy += evaluation.scores.accuracy;
        totalScores.timeliness += evaluation.scores.timeliness;
        totalScores.impact += evaluation.scores.impact;
        totalScores.relevance += evaluation.scores.relevance;
        totalScores.overall += evaluation.scores.overall;
        scoredCount++;
      }

      if (evaluation.evaluatedAt) {
        totalTimeToEvaluate += evaluation.evaluatedAt - evaluation.createdAt;
        evaluatedCount++;
      }
    });

    const averageScores: EvaluationScore = scoredCount
      ? {
          accuracy: totalScores.accuracy / scoredCount,
          timeliness: totalScores.timeliness / scoredCount,
          impact: totalScores.impact / scoredCount,
          relevance: totalScores.relevance / scoredCount,
          overall: totalScores.overall / scoredCount,
        }
      : {
          accuracy: 0,
          timeliness: 0,
          impact: 0,
          relevance: 0,
          overall: 0,
        };

    const helpfulCount =
      feedbackCounts[FeedbackType.HELPFUL] +
      feedbackCounts[FeedbackType.PARTIALLY_HELPFUL];
    const totalFeedback = Object.values(feedbackCounts).reduce(
      (a, b) => a + b,
      0,
    );
    const successRate = totalFeedback > 0 ? helpfulCount / totalFeedback : 0;

    return {
      totalEvaluations: currentEvals.length,
      evaluationsByStatus: statusCounts,
      feedbackDistribution: feedbackCounts,
      averageScores,
      successRate,
      avgTimeToEvaluate: evaluatedCount > 0 ? totalTimeToEvaluate / evaluatedCount : 0,
    };
  }, []);

  /**
   * Get trending insights from evaluations
   * الحصول على الرؤى الاتجاهية من التقييمات
   */
  const getTrendingInsights = useCallback(
    (timeWindowMs: number = 7 * 24 * 60 * 60 * 1000) => {
      const now = Date.now();
      const recentEvals = evaluationsRef.current.filter(
        (evaluation) => evaluation.createdAt > now - timeWindowMs,
      );

      const stats = {
        totalRecent: recentEvals.length,
        avgOverallScore:
          recentEvals
            .filter((evaluation) => evaluation.scores?.overall)
            .reduce((sum, evaluation) => sum + (evaluation.scores?.overall || 0), 0) /
            Math.max(recentEvals.filter((evaluation) => evaluation.scores?.overall).length, 1) ||
          0,
        mostCommonFeedback:
          getMostCommon(recentEvals.map((evaluation) => evaluation.feedback)) || "no_data",
        improvementAreas: getLowestScoringAreas(recentEvals),
      };

      return stats;
    },
    [],
  );

  /**
   * Clear evaluations
   * مسح التقييمات
   */
  const clearEvaluations = useCallback(
    (options?: {
      olderThan?: number; // Timestamp
      all?: boolean;
    }): number => {
      let deletedCount = 0;

      setEvaluations((prev) =>
        prev.filter((evaluation) => {
          let shouldDelete = false;

          if (options?.all) {
            shouldDelete = true;
          } else if (
            options?.olderThan &&
            evaluation.createdAt < options.olderThan
          ) {
            shouldDelete = true;
          }

          if (shouldDelete) {
            deletedCount++;
          }

          return !shouldDelete;
        }),
      );

      logger.info(
        `[useRecommendationEvaluation] Cleared ${deletedCount} evaluations`,
      );
      return deletedCount;
    },
    [],
  );

  return {
    evaluations,
    createEvaluation,
    submitFeedback,
    submitScores,
    markApplied,
    getEvaluations,
    getStatistics,
    getTrendingInsights,
    clearEvaluations,
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generate unique ID for evaluation
 */
function generateEvaluationId(): string {
  return `eval_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Get most common item from array
 */
function getMostCommon<T>(arr: (T | undefined)[]): T | null {
  const counts = new Map<T, number>();

  arr.forEach((item) => {
    if (item !== undefined) {
      counts.set(item, (counts.get(item) || 0) + 1);
    }
  });

  let max = 0;
  let mostCommon: T | null = null;

  counts.forEach((count, item) => {
    if (count > max) {
      max = count;
      mostCommon = item;
    }
  });

  return mostCommon;
}

/**
 * Get lowest scoring areas from evaluations
 */
function getLowestScoringAreas(
  evaluations: RecommendationEvaluation[],
): string[] {
  const areas = {
    accuracy: 0,
    timeliness: 0,
    impact: 0,
    relevance: 0,
  };

  let count = 0;

  evaluations.forEach((evaluation) => {
    if (evaluation.scores) {
      areas.accuracy += evaluation.scores.accuracy;
      areas.timeliness += evaluation.scores.timeliness;
      areas.impact += evaluation.scores.impact;
      areas.relevance += evaluation.scores.relevance;
      count++;
    }
  });

  if (count === 0) {
    return [];
  }

  const averages = Object.entries(areas).map(([key, value]) => ({
    area: key,
    score: value / count,
  }));

  return averages
    .sort((a, b) => a.score - b.score)
    .slice(0, 3)
    .map((item) => item.area);
}

export default useRecommendationEvaluation;
