/**
 * SAHOOL AI Context Engineering Module
 * =====================================
 * وحدة هندسة السياق للذكاء الاصطناعي
 *
 * Comprehensive context engineering for AI interactions in the SAHOOL platform.
 * Implements context compression, farm memory management, and recommendation evaluation.
 *
 * Features:
 * - Context compression with Arabic text support
 * - Tenant-isolated farm memory with sliding window
 * - LLM-as-Judge recommendation evaluation
 * - Token estimation and optimization
 *
 * Based on modern context engineering best practices for agricultural AI systems.
 *
 * المميزات:
 * - ضغط السياق مع دعم النص العربي
 * - ذاكرة المزرعة المعزولة لكل مستأجر مع نافذة منزلقة
 * - تقييم التوصيات باستخدام نموذج اللغة كحكم
 * - تقدير وتحسين الرموز
 *
 * Author: SAHOOL Platform Team
 * Updated: January 2025
 */

// ─────────────────────────────────────────────────────────────────────────────
// Context Compression Exports
// ─────────────────────────────────────────────────────────────────────────────

export {
  CompressionStrategy,
  ContextCompressor,
  estimateTokens,
  detectPrimaryLanguage,
  type CompressionResult,
} from "./context-compressor";

// ─────────────────────────────────────────────────────────────────────────────
// Farm Memory Exports
// ─────────────────────────────────────────────────────────────────────────────

export {
  MemoryType,
  RelevanceScore,
  FarmMemory,
  createMemoryEntry,
  isMemoryEntryExpired,
  memoryEntryToDict,
  type MemoryConfig,
  type MemoryEntry,
  type RecallResult,
} from "./farm-memory";

// ─────────────────────────────────────────────────────────────────────────────
// Recommendation Evaluator Exports
// ─────────────────────────────────────────────────────────────────────────────

export {
  EvaluationCriteria,
  EvaluationGrade,
  RecommendationType,
  RecommendationEvaluator,
  createCriteriaScore,
  createEvaluationResult,
  scoreToGrade,
  generateFeedback,
  generateImprovements,
  type CriteriaScore,
  type EvaluationResult,
} from "./recommendation-evaluator";

// ─────────────────────────────────────────────────────────────────────────────
// Version
// ─────────────────────────────────────────────────────────────────────────────

export const AI_CONTEXT_ENGINEERING_VERSION = "1.0.0";
