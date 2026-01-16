/**
 * AI Recommendation Evaluation Module
 * =====================================
 * وحدة تقييم توصيات الذكاء الاصطناعي
 *
 * Implements LLM-as-Judge pattern for evaluating AI recommendations.
 * Provides structured evaluation across multiple criteria for agricultural advice.
 *
 * المميزات:
 * - تقييم الدقة والموثوقية
 * - تقييم قابلية التنفيذ
 * - تقييم السلامة
 * - تقييم الصلة بالسياق الزراعي
 *
 * Based on LLM-as-Judge best practices for agricultural domain.
 *
 * Author: SAHOOL Platform Team
 * Updated: January 2025
 */

// ─────────────────────────────────────────────────────────────────────────────
// Constants & Configuration
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_PASSING_THRESHOLD = 0.7;
const MIN_SCORE = 0.0;
const MAX_SCORE = 1.0;

// ─────────────────────────────────────────────────────────────────────────────
// Enums & Models
// ─────────────────────────────────────────────────────────────────────────────

export enum EvaluationCriteria {
  /** الدقة - Technical correctness */
  ACCURACY = "accuracy",
  /** قابلية التنفيذ - Can be acted upon */
  ACTIONABILITY = "actionability",
  /** السلامة - Safe for implementation */
  SAFETY = "safety",
  /** الصلة - Relevant to context */
  RELEVANCE = "relevance",
  /** الاكتمال - Covers all aspects */
  COMPLETENESS = "completeness",
  /** الوضوح - Clear and understandable */
  CLARITY = "clarity",
}

export enum EvaluationGrade {
  /** ممتاز (>= 0.9) */
  EXCELLENT = "excellent",
  /** جيد (>= 0.75) */
  GOOD = "good",
  /** مقبول (>= 0.6) */
  ACCEPTABLE = "acceptable",
  /** يحتاج تحسين (>= 0.4) */
  NEEDS_IMPROVEMENT = "needs_improvement",
  /** ضعيف (< 0.4) */
  POOR = "poor",
}

export enum RecommendationType {
  /** الري */
  IRRIGATION = "irrigation",
  /** التسميد */
  FERTILIZATION = "fertilization",
  /** مكافحة الآفات */
  PEST_CONTROL = "pest_control",
  /** الأمراض */
  DISEASE = "disease",
  /** الحصاد */
  HARVEST = "harvest",
  /** الزراعة */
  PLANTING = "planting",
  /** الطقس */
  WEATHER = "weather",
  /** عام */
  GENERAL = "general",
}

export interface CriteriaScore {
  /** المعيار - The evaluation criterion */
  criteria: EvaluationCriteria;
  /** الدرجة - Score from 0.0 to 1.0 */
  score: number;
  /** التفسير - Explanation for the score */
  explanation: string;
  /** التفسير بالعربية - Arabic explanation */
  explanationAr?: string;
  /** الأدلة - Evidence supporting the score */
  evidence: string[];
  /** اجتياز العتبة */
  isPassing?: boolean;
}

export interface EvaluationResult {
  /** المعرف - Unique evaluation identifier */
  id: string;
  /** معرف التوصية - ID of evaluated recommendation */
  recommendationId?: string;
  /** نوع التوصية - Type of recommendation */
  recommendationType: RecommendationType;
  /** الدرجات - Individual criteria scores */
  scores: Record<EvaluationCriteria, CriteriaScore>;
  /** الدرجة الإجمالية - Weighted overall score */
  overallScore: number;
  /** الدرجة - Letter grade */
  grade: EvaluationGrade;
  /** موافق عليها - Whether recommendation is approved */
  isApproved: boolean;
  /** الملاحظات - General feedback */
  feedback: string;
  /** الملاحظات بالعربية - Arabic feedback */
  feedbackAr?: string;
  /** التحسينات المقترحة - Suggested improvements */
  improvements: string[];
  /** تاريخ التقييم - Evaluation timestamp */
  evaluatedAt: Date;
  /** البيانات الوصفية - Additional metadata */
  metadata?: Record<string, unknown>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create a criteria score
 * إنشاء درجة معيار
 */
export function createCriteriaScore(
  criteria: EvaluationCriteria,
  score: number,
  explanation: string,
  explanationAr?: string,
  evidence?: string[],
): CriteriaScore {
  // Clamp score to valid range
  const clampedScore = Math.max(MIN_SCORE, Math.min(MAX_SCORE, score));

  return {
    criteria,
    score: clampedScore,
    explanation,
    explanationAr,
    evidence: evidence || [],
    isPassing: clampedScore >= DEFAULT_PASSING_THRESHOLD,
  };
}

/**
 * Convert score to grade
 * تحويل الدرجة إلى تقدير
 */
export function scoreToGrade(score: number): EvaluationGrade {
  if (score >= 0.9) {
    return EvaluationGrade.EXCELLENT;
  } else if (score >= 0.75) {
    return EvaluationGrade.GOOD;
  } else if (score >= 0.6) {
    return EvaluationGrade.ACCEPTABLE;
  } else if (score >= 0.4) {
    return EvaluationGrade.NEEDS_IMPROVEMENT;
  } else {
    return EvaluationGrade.POOR;
  }
}

/**
 * Create evaluation result
 * إنشاء نتيجة التقييم
 */
export function createEvaluationResult(
  recommendationType: RecommendationType,
  scores: Record<EvaluationCriteria, CriteriaScore>,
  weights?: Record<EvaluationCriteria, number>,
  recommendationId?: string,
  passingThreshold: number = DEFAULT_PASSING_THRESHOLD,
): EvaluationResult {
  // Default weights for agricultural recommendations
  const defaultWeights: Record<EvaluationCriteria, number> = {
    [EvaluationCriteria.ACCURACY]: 0.25,
    [EvaluationCriteria.ACTIONABILITY]: 0.2,
    [EvaluationCriteria.SAFETY]: 0.25,
    [EvaluationCriteria.RELEVANCE]: 0.15,
    [EvaluationCriteria.COMPLETENESS]: 0.1,
    [EvaluationCriteria.CLARITY]: 0.05,
  };

  const finalWeights = weights || defaultWeights;

  // Calculate weighted overall score
  let totalWeight = 0.0;
  let weightedSum = 0.0;

  for (const [criteria, score] of Object.entries(scores)) {
    const weight = finalWeights[criteria as EvaluationCriteria] || 0.1;
    weightedSum += score.score * weight;
    totalWeight += weight;
  }

  const overallScore = weightedSum / Math.max(totalWeight, 0.01);

  // Determine grade
  const grade = scoreToGrade(overallScore);

  // Check safety - if safety score is low, do not approve
  const safetyScore = scores[EvaluationCriteria.SAFETY];
  const safetyFailed = safetyScore && safetyScore.score < 0.5;

  const isApproved = overallScore >= passingThreshold && !safetyFailed;

  // Generate feedback
  const { feedback, feedbackAr } = generateFeedback(scores, grade, isApproved);

  // Generate improvements
  const improvements = generateImprovements(scores);

  return {
    id: `${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
    recommendationId,
    recommendationType,
    scores,
    overallScore,
    grade,
    isApproved,
    feedback,
    feedbackAr,
    improvements,
    evaluatedAt: new Date(),
  };
}

/**
 * Generate feedback text in English and Arabic
 * إنشاء نص الملاحظات بالإنجليزية والعربية
 */
export function generateFeedback(
  scores: Record<EvaluationCriteria, CriteriaScore>,
  grade: EvaluationGrade,
  isApproved: boolean,
): { feedback: string; feedbackAr: string } {
  if (isApproved) {
    if (grade === EvaluationGrade.EXCELLENT) {
      return {
        feedback: "Excellent recommendation. Ready for implementation.",
        feedbackAr: "توصية ممتازة. جاهزة للتنفيذ.",
      };
    } else if (grade === EvaluationGrade.GOOD) {
      return {
        feedback: "Good recommendation with minor areas for improvement.",
        feedbackAr: "توصية جيدة مع بعض المجالات للتحسين.",
      };
    } else {
      return {
        feedback: "Acceptable recommendation. Consider the suggested improvements.",
        feedbackAr: "توصية مقبولة. يُرجى النظر في التحسينات المقترحة.",
      };
    }
  } else {
    const safetyScore = scores[EvaluationCriteria.SAFETY];
    if (safetyScore && safetyScore.score < 0.5) {
      return {
        feedback:
          "Recommendation not approved due to safety concerns. Please review safety guidelines.",
        feedbackAr:
          "لم تتم الموافقة على التوصية بسبب مخاوف تتعلق بالسلامة. يرجى مراجعة إرشادات السلامة.",
      };
    } else {
      return {
        feedback:
          "Recommendation needs improvement before implementation. Please address the noted concerns.",
        feedbackAr:
          "التوصية تحتاج إلى تحسين قبل التنفيذ. يرجى معالجة الملاحظات المذكورة.",
      };
    }
  }
}

/**
 * Generate list of suggested improvements
 * إنشاء قائمة بالتحسينات المقترحة
 */
export function generateImprovements(
  scores: Record<EvaluationCriteria, CriteriaScore>,
): string[] {
  const improvements: string[] = [];

  const improvementMap: Record<EvaluationCriteria, string> = {
    [EvaluationCriteria.ACCURACY]: "Verify technical accuracy with domain experts",
    [EvaluationCriteria.ACTIONABILITY]: "Provide more specific, actionable steps",
    [EvaluationCriteria.SAFETY]: "Review safety implications and add precautions",
    [EvaluationCriteria.RELEVANCE]: "Ensure recommendation addresses the specific context",
    [EvaluationCriteria.COMPLETENESS]: "Add missing details or considerations",
    [EvaluationCriteria.CLARITY]: "Simplify language and improve structure",
  };

  for (const [criteria, score] of Object.entries(scores)) {
    if (score.score < DEFAULT_PASSING_THRESHOLD) {
      const improvement = improvementMap[criteria as EvaluationCriteria];
      if (improvement) {
        improvements.push(improvement);
      }
    }
  }

  return improvements;
}

// ─────────────────────────────────────────────────────────────────────────────
// Recommendation Evaluator
// ─────────────────────────────────────────────────────────────────────────────

/**
 * LLM-as-Judge evaluator for agricultural recommendations.
 * مُقيّم التوصيات الزراعية باستخدام نموذج اللغة كحكم
 *
 * Evaluates AI-generated recommendations for farmers using multiple criteria:
 * - Accuracy: Technical correctness
 * - Actionability: Practical implementation feasibility
 * - Safety: Risk assessment for crops, environment, health
 * - Relevance: Context appropriateness
 * - Completeness: Coverage of necessary information
 * - Clarity: Understandability
 */
export class RecommendationEvaluator {
  private criteriaWeights: Record<EvaluationCriteria, number>;
  private passingThreshold: number;
  private useHeuristicsFallback: boolean;
  private stats: Record<string, number>;

  constructor(
    criteriaWeights?: Record<EvaluationCriteria, number>,
    passingThreshold: number = DEFAULT_PASSING_THRESHOLD,
    useHeuristicsFallback: boolean = true,
  ) {
    /**
     * Initialize the evaluator.
     * تهيئة المُقيّم
     *
     * @param criteriaWeights - أوزان المعايير - Custom weights for criteria
     * @param passingThreshold - عتبة النجاح - Threshold for approval
     * @param useHeuristicsFallback - استخدام القواعس الاحتياطية - Use heuristics fallback
     */
    // Default weights optimized for agricultural recommendations
    this.criteriaWeights = criteriaWeights || {
      [EvaluationCriteria.ACCURACY]: 0.25,
      [EvaluationCriteria.ACTIONABILITY]: 0.2,
      [EvaluationCriteria.SAFETY]: 0.25,
      [EvaluationCriteria.RELEVANCE]: 0.15,
      [EvaluationCriteria.COMPLETENESS]: 0.1,
      [EvaluationCriteria.CLARITY]: 0.05,
    };

    this.passingThreshold = passingThreshold;
    this.useHeuristicsFallback = useHeuristicsFallback;

    // Statistics
    this.stats = {
      evaluations: 0,
      approved: 0,
      rejected: 0,
      heuristicEvaluations: 0,
    };
  }

  /**
   * Evaluate a recommendation using heuristics.
   * تقييم توصية باستخدام القواعد
   *
   * @param recommendation - التوصية - The recommendation text to evaluate
   * @param context - السياق - Contextual information
   * @param query - الاستعلام - Original user query
   * @param recommendationType - نوع التوصية - Type of recommendation
   * @param recommendationId - معرف التوصية - Optional ID for tracking
   * @returns نتيجة التقييم - Complete evaluation result
   */
  evaluate(
    recommendation: string,
    context?: Record<string, unknown>,
    query?: string,
    recommendationType?: RecommendationType,
    recommendationId?: string,
  ): EvaluationResult {
    context = context || {};
    query = query || "";
    recommendationType = recommendationType || this._detectRecommendationType(recommendation);

    this.stats.evaluations += 1;

    // Evaluate using heuristics
    const scores = this._evaluateWithHeuristics(recommendation, context, query, recommendationType);
    this.stats.heuristicEvaluations += 1;

    // Create evaluation result
    const result = createEvaluationResult(
      recommendationType,
      scores,
      this.criteriaWeights,
      recommendationId,
      this.passingThreshold,
    );

    // Update stats
    if (result.isApproved) {
      this.stats.approved += 1;
    } else {
      this.stats.rejected += 1;
    }

    return result;
  }

  /**
   * Evaluate multiple recommendations.
   * تقييم توصيات متعددة
   *
   * @param recommendations - قائمة التوصيات - List of recommendation objects
   * @returns قائمة نتائج التقييم - List of evaluation results
   */
  evaluateBatch(
    recommendations: Array<{
      recommendation: string;
      context?: Record<string, unknown>;
      query?: string;
      type?: RecommendationType;
      id?: string;
    }>,
  ): EvaluationResult[] {
    return recommendations.map((rec) =>
      this.evaluate(
        rec.recommendation,
        rec.context,
        rec.query,
        rec.type,
        rec.id,
      ),
    );
  }

  /**
   * Get evaluation statistics.
   * الحصول على إحصائيات التقييم
   *
   * @returns الإحصائيات - Evaluation statistics
   */
  getStats(): Record<string, unknown> {
    const total = this.stats.evaluations;
    return {
      ...this.stats,
      approvalRate: this.stats.approved / Math.max(total, 1),
      rejectionRate: this.stats.rejected / Math.max(total, 1),
    };
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Heuristic-based Evaluation
  // ─────────────────────────────────────────────────────────────────────────

  private _evaluateWithHeuristics(
    recommendation: string,
    context: Record<string, unknown>,
    query: string,
    recommendationType: RecommendationType,
  ): Record<EvaluationCriteria, CriteriaScore> {
    const scores: Record<EvaluationCriteria, CriteriaScore> = {
      [EvaluationCriteria.ACCURACY]: this._evaluateAccuracyHeuristic(
        recommendation,
        context,
        recommendationType,
      ),
      [EvaluationCriteria.ACTIONABILITY]: this._evaluateActionabilityHeuristic(recommendation),
      [EvaluationCriteria.SAFETY]: this._evaluateSafetyHeuristic(recommendation, recommendationType),
      [EvaluationCriteria.RELEVANCE]: this._evaluateRelevanceHeuristic(
        recommendation,
        query,
        context,
      ),
      [EvaluationCriteria.COMPLETENESS]: this._evaluateCompletenessHeuristic(
        recommendation,
        recommendationType,
      ),
      [EvaluationCriteria.CLARITY]: this._evaluateClarityHeuristic(recommendation),
    };

    return scores;
  }

  private _evaluateAccuracyHeuristic(
    recommendation: string,
    context: Record<string, unknown>,
    recommendationType: RecommendationType,
  ): CriteriaScore {
    let score = 0.7; // Base score
    const evidence: string[] = [];

    const recLower = recommendation.toLowerCase();

    // Check for specific numbers/quantities
    const numbers = recommendation.match(/\d+(?:\.\d+)?/g) || [];
    if (numbers.length > 0) {
      score += 0.1;
      evidence.push(`Contains specific quantities: ${numbers.slice(0, 3).join(", ")}`);
    }

    // Check for units
    const units = recLower.match(
      /\b(kg|كجم|liter|لتر|mm|مم|hectare|هكتار|m2|متر|hour|ساعة)\b/g,
    ) || [];
    if (units.length > 0) {
      score += 0.1;
      evidence.push(`Contains measurement units: ${Array.from(new Set(units)).join(", ")}`);
    }

    // Check context alignment
    const crop = ((context.crop as string) || (context.المحصول as string) || "").toLowerCase();
    if (crop && recLower.includes(crop)) {
      score += 0.1;
      evidence.push(`Mentions relevant crop: ${crop}`);
    }

    return createCriteriaScore(
      EvaluationCriteria.ACCURACY,
      Math.min(score, 1.0),
      "Accuracy evaluated based on specificity and context alignment",
      "تم تقييم الدقة بناءً على التحديد والتوافق مع السياق",
      evidence,
    );
  }

  private _evaluateActionabilityHeuristic(recommendation: string): CriteriaScore {
    let score = 0.6; // Base score
    const evidence: string[] = [];

    const recLower = recommendation.toLowerCase();

    // Check for action verbs
    const actionVerbs = [
      "apply",
      "water",
      "spray",
      "add",
      "remove",
      "harvest",
      "plant",
      "irrigate",
      "fertilize",
      "prune",
      // Arabic
      "ضع",
      "اسقِ",
      "رش",
      "أضف",
      "أزل",
      "احصد",
      "ازرع",
      "سمّد",
    ];
    const foundVerbs = actionVerbs.filter((v) => recLower.includes(v));
    if (foundVerbs.length > 0) {
      score += 0.15;
      evidence.push(`Contains action verbs: ${foundVerbs.slice(0, 3).join(", ")}`);
    }

    // Check for time references
    const timeRefs = [
      "morning",
      "evening",
      "daily",
      "weekly",
      "hours",
      "days",
      "صباحاً",
      "مساءً",
      "يومياً",
      "أسبوعياً",
    ];
    const foundTimes = timeRefs.filter((t) => recLower.includes(t));
    if (foundTimes.length > 0) {
      score += 0.15;
      evidence.push(`Contains timing guidance: ${foundTimes.slice(0, 3).join(", ")}`);
    }

    // Check for step-by-step indicators
    const stepIndicators = recommendation.match(/(\d+\.\s|\bstep\s+\d|\bأولاً|\bثانياً|\bثالثاً)/gi) || [];
    if (stepIndicators.length > 0) {
      score += 0.1;
      evidence.push("Contains step-by-step instructions");
    }

    return createCriteriaScore(
      EvaluationCriteria.ACTIONABILITY,
      Math.min(score, 1.0),
      "Actionability evaluated based on action verbs and timing guidance",
      "تم تقييم قابلية التنفيذ بناءً على أفعال العمل وإرشادات التوقيت",
      evidence,
    );
  }

  private _evaluateSafetyHeuristic(
    recommendation: string,
    recommendationType: RecommendationType,
  ): CriteriaScore {
    let score = 0.8; // Start optimistic
    const evidence: string[] = [];

    const recLower = recommendation.toLowerCase();

    // Check for safety warnings
    const safetyTerms = [
      "caution",
      "warning",
      "careful",
      "avoid",
      "do not",
      "تحذير",
      "احذر",
      "تجنب",
      "لا تفعل",
    ];
    const foundWarnings = safetyTerms.filter((t) => recLower.includes(t));
    if (foundWarnings.length > 0) {
      score += 0.1;
      evidence.push(`Contains safety guidance: ${foundWarnings.slice(0, 3).join(", ")}`);
    }

    // Check for protective equipment mentions
    const ppeTerms = [
      "gloves",
      "mask",
      "goggles",
      "protective",
      "قفازات",
      "كمامة",
      "نظارات",
      "حماية",
    ];
    const foundPpe = ppeTerms.filter((t) => recLower.includes(t));
    if (foundPpe.length > 0) {
      score += 0.1;
      evidence.push(`Mentions protective equipment: ${foundPpe.join(", ")}`);
    }

    // Check for dangerous chemicals without warnings
    const dangerousTerms = [
      "pesticide",
      "herbicide",
      "fungicide",
      "chemical",
      "مبيد",
      "كيميائي",
    ];
    const hasChemicals = dangerousTerms.some((t) => recLower.includes(t));
    const hasWarnings = safetyTerms.some((t) => recLower.includes(t));

    if (hasChemicals && !hasWarnings) {
      score -= 0.2;
      evidence.push("Contains chemical references without safety warnings");
    }

    // Penalize for excessive quantities
    const quantities = recommendation.match(/(\d+)\s*(kg|liter|كجم|لتر)/gi) || [];
    for (const qty of quantities) {
      const match = qty.match(/(\d+)/);
      if (match && parseInt(match[1]) > 100) {
        score -= 0.1;
        evidence.push(`Large quantity mentioned: ${qty}`);
        break;
      }
    }

    return createCriteriaScore(
      EvaluationCriteria.SAFETY,
      Math.max(score, 0.0),
      "Safety evaluated based on warnings and chemical handling guidance",
      "تم تقييم السلامة بناءً على التحذيرات وإرشادات التعامل مع المواد الكيميائية",
      evidence,
    );
  }

  private _evaluateRelevanceHeuristic(
    recommendation: string,
    query: string,
    context: Record<string, unknown>,
  ): CriteriaScore {
    let score = 0.5; // Base score
    const evidence: string[] = [];

    const recLower = recommendation.toLowerCase();
    const queryLower = query.toLowerCase();

    // Check keyword overlap with query
    const queryWords = new Set(
      queryLower
        .split(/\s+/)
        .filter((w) => w.length > 0),
    );
    const recWords = new Set(
      recLower
        .split(/\s+/)
        .filter((w) => w.length > 0),
    );
    const overlap = Array.from(queryWords).filter((w) => recWords.has(w));

    if (overlap.length > 0) {
      const overlapRatio = overlap.length / Math.max(queryWords.size, 1);
      score += overlapRatio * 0.3;
      evidence.push(`Query keyword overlap: ${overlap.slice(0, 5).join(", ")}`);
    }

    // Check context field mentions
    const contextValues = Object.values(context)
      .filter((v) => v)
      .map((v) => String(v).toLowerCase());
    for (const val of contextValues) {
      if (val.length > 2 && recLower.includes(val)) {
        score += 0.1;
        evidence.push(`Mentions context value: ${val}`);
      }
    }

    // Agricultural relevance
    const agriTerms = [
      "crop",
      "field",
      "soil",
      "water",
      "irrigation",
      "fertilizer",
      "harvest",
      "محصول",
      "حقل",
      "تربة",
      "ماء",
      "ري",
      "سماد",
      "حصاد",
    ];
    const foundAgri = agriTerms.filter((t) => recLower.includes(t));
    if (foundAgri.length > 0) {
      score += 0.2;
      evidence.push(`Agricultural relevance: ${foundAgri.slice(0, 3).join(", ")}`);
    }

    return createCriteriaScore(
      EvaluationCriteria.RELEVANCE,
      Math.min(score, 1.0),
      "Relevance evaluated based on query and context alignment",
      "تم تقييم الصلة بناءً على التوافق مع الاستعلام والسياق",
      evidence,
    );
  }

  private _evaluateCompletenessHeuristic(
    recommendation: string,
    recommendationType: RecommendationType,
  ): CriteriaScore {
    let score = 0.5; // Base score
    const evidence: string[] = [];

    // Check for expected components based on recommendation type
    const expectedComponents: Record<RecommendationType, Array<[string, string[]]>> = {
      [RecommendationType.IRRIGATION]: [
        ["quantity", ["liter", "mm", "لتر", "مم"]],
        ["timing", ["morning", "evening", "صباحاً", "مساءً"]],
        ["frequency", ["daily", "weekly", "يومياً", "أسبوعياً"]],
      ],
      [RecommendationType.FERTILIZATION]: [
        ["type", ["nitrogen", "phosphorus", "potassium", "نيتروجين", "فوسفور"]],
        ["quantity", ["kg", "gram", "كجم", "غرام"]],
        ["application", ["apply", "spread", "ضع", "انشر"]],
      ],
      [RecommendationType.PEST_CONTROL]: [
        ["identification", ["pest", "insect", "آفة", "حشرة"]],
        ["treatment", ["spray", "apply", "رش", "ضع"]],
        ["prevention", ["prevent", "avoid", "تجنب", "منع"]],
      ],
      [RecommendationType.GENERAL]: [],
      [RecommendationType.DISEASE]: [],
      [RecommendationType.HARVEST]: [],
      [RecommendationType.PLANTING]: [],
      [RecommendationType.WEATHER]: [],
    };

    const recLower = recommendation.toLowerCase();
    const components = expectedComponents[recommendationType] || [];

    for (const [componentName, keywords] of components) {
      if (keywords.some((kw) => recLower.includes(kw))) {
        score += 0.15;
        evidence.push(`Contains ${componentName} information`);
      }
    }

    // Length-based completeness
    const wordCount = recommendation.split(/\s+/).length;
    if (wordCount >= 50) {
      score += 0.1;
      evidence.push(`Detailed response (${wordCount} words)`);
    } else if (wordCount < 20) {
      score -= 0.1;
      evidence.push(`Brief response (${wordCount} words)`);
    }

    return createCriteriaScore(
      EvaluationCriteria.COMPLETENESS,
      Math.min(Math.max(score, 0.0), 1.0),
      "Completeness evaluated based on expected components",
      "تم تقييم الاكتمال بناءً على المكونات المتوقعة",
      evidence,
    );
  }

  private _evaluateClarityHeuristic(recommendation: string): CriteriaScore {
    let score = 0.7; // Base score
    const evidence: string[] = [];

    // Check sentence structure
    const sentences = recommendation
      .split(/[.!?،؟]/)
      .map((s) => s.trim())
      .filter((s) => s.length > 0);

    if (sentences.length > 0) {
      const avgSentenceLength =
        sentences.reduce((sum, s) => sum + s.split(/\s+/).length, 0) / sentences.length;

      if (avgSentenceLength >= 10 && avgSentenceLength <= 25) {
        score += 0.15;
        evidence.push(`Good sentence length (avg: ${avgSentenceLength.toFixed(1)} words)`);
      } else if (avgSentenceLength > 40) {
        score -= 0.2;
        evidence.push(`Sentences too long (avg: ${avgSentenceLength.toFixed(1)} words)`);
      }
    }

    // Check for clear structure markers
    const structureMarkers = [
      "first",
      "second",
      "then",
      "finally",
      "أولاً",
      "ثانياً",
      "ثم",
      "أخيراً",
    ];
    const foundMarkers = structureMarkers.filter((m) =>
      recommendation.toLowerCase().includes(m.toLowerCase()),
    );
    if (foundMarkers.length > 0) {
      score += 0.1;
      evidence.push("Contains structural markers");
    }

    // Check for bullet points or numbered lists
    if (/[\-\•\*]\s|^\d+\./m.test(recommendation)) {
      score += 0.1;
      evidence.push("Uses list formatting");
    }

    return createCriteriaScore(
      EvaluationCriteria.CLARITY,
      Math.min(score, 1.0),
      "Clarity evaluated based on sentence structure and formatting",
      "تم تقييم الوضوح بناءً على بنية الجملة والتنسيق",
      evidence,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Helper Methods
  // ─────────────────────────────────────────────────────────────────────────

  private _detectRecommendationType(recommendation: string): RecommendationType {
    const recLower = recommendation.toLowerCase();

    const typeKeywords: Record<RecommendationType, string[]> = {
      [RecommendationType.IRRIGATION]: [
        "water",
        "irrigat",
        "drip",
        "ري",
        "ماء",
        "رطوبة",
      ],
      [RecommendationType.FERTILIZATION]: [
        "fertiliz",
        "nutrient",
        "nitrogen",
        "سماد",
        "تسميد",
        "نيتروجين",
      ],
      [RecommendationType.PEST_CONTROL]: [
        "pest",
        "insect",
        "spray",
        "آفة",
        "حشرة",
        "مبيد",
      ],
      [RecommendationType.DISEASE]: [
        "disease",
        "fungus",
        "virus",
        "infection",
        "مرض",
        "فطر",
        "عدوى",
      ],
      [RecommendationType.HARVEST]: [
        "harvest",
        "pick",
        "collect",
        "حصاد",
        "قطف",
        "جمع",
      ],
      [RecommendationType.PLANTING]: [
        "plant",
        "seed",
        "sow",
        "زراعة",
        "بذور",
        "غرس",
      ],
      [RecommendationType.WEATHER]: [
        "weather",
        "rain",
        "temperature",
        "طقس",
        "مطر",
        "حرارة",
      ],
      [RecommendationType.GENERAL]: [],
    };

    for (const [recType, keywords] of Object.entries(typeKeywords)) {
      if (keywords.some((kw) => recLower.includes(kw))) {
        return recType as RecommendationType;
      }
    }

    return RecommendationType.GENERAL;
  }
}
