/**
 * AI Farm Memory Module
 * ======================
 * وحدة ذاكرة المزرعة للذكاء الاصطناعي
 *
 * Provides memory management for AI interactions with tenant isolation.
 * Implements sliding window for recent history and context retrieval.
 *
 * المميزات:
 * - عزل البيانات لكل مستأجر (Tenant Isolation)
 * - نافذة منزلقة للسجل الأخير
 * - استرجاع السياق ذي الصلة
 * - تخزين واسترجاع الذاكرة
 *
 * Author: SAHOOL Platform Team
 * Updated: January 2025
 */

import { estimateTokens } from "./context-compressor";

// ─────────────────────────────────────────────────────────────────────────────
// Constants & Configuration
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_WINDOW_SIZE = 20;
const DEFAULT_TTL_HOURS = 24;
const DEFAULT_MAX_ENTRIES = 1000;
const DEFAULT_RELEVANCE_THRESHOLD = 0.5;

// ─────────────────────────────────────────────────────────────────────────────
// Enums & Models
// ─────────────────────────────────────────────────────────────────────────────

export enum MemoryType {
  /** Chat/interaction history */
  CONVERSATION = "conversation",
  /** Field status snapshots */
  FIELD_STATE = "field_state",
  /** AI recommendations */
  RECOMMENDATION = "recommendation",
  /** Field observations */
  OBSERVATION = "observation",
  /** Weather data */
  WEATHER = "weather",
  /** User actions */
  ACTION = "action",
  /** System events */
  SYSTEM = "system",
}

export enum RelevanceScore {
  /** Always include */
  CRITICAL = "critical",
  /** Include if space */
  HIGH = "high",
  /** Include if relevant */
  MEDIUM = "medium",
  /** Only if specifically requested */
  LOW = "low",
}

export interface MemoryConfig {
  /** حجم النافذة - Number of recent entries to keep in sliding window */
  windowSize?: number;
  /** الحد الأقصى للإدخالات - Maximum total entries per tenant */
  maxEntries?: number;
  /** مدة الصلاحية - Time-to-live for entries in hours */
  ttlHours?: number;
  /** عتبة الصلة - Minimum relevance score for retrieval */
  relevanceThreshold?: number;
  /** تفعيل الضغط - Enable automatic compression */
  enableCompression?: boolean;
  /** الحفظ الدائم - Persist to external storage */
  persistToStorage?: boolean;
}

export interface MemoryEntry {
  /** المعرف - Unique identifier */
  id: string;
  /** معرف المستأجر - Tenant identifier for isolation */
  tenantId: string;
  /** معرف الحقل - Field identifier (optional) */
  fieldId: string | null;
  /** نوع الذاكرة - Type of memory entry */
  memoryType: MemoryType;
  /** المحتوى - The actual content/data */
  content: Record<string, unknown> | string;
  /** البيانات الوصفية - Additional metadata */
  metadata: Record<string, unknown>;
  /** الطابع الزمني - When entry was created */
  timestamp: Date;
  /** الصلة - Relevance score */
  relevance: RelevanceScore;
  /** التضمين - Vector embedding (optional) */
  embedding?: number[];
  /** تاريخ الانتهاء - Expiration timestamp */
  expiresAt?: Date;
}

export interface RecallResult {
  /** الإدخالات - Retrieved memory entries */
  entries: MemoryEntry[];
  /** إجمالي الموجود - Total matching entries */
  totalFound: number;
  /** وقت الاستعلام - Query execution time in ms */
  queryTimeMs: number;
  /** نص السياق - Formatted context text */
  contextText?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory & Helper Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create a new memory entry
 * إنشاء إدخال ذاكرة جديد
 */
export function createMemoryEntry(
  tenantId: string,
  memoryType: MemoryType,
  content: Record<string, unknown> | string,
  fieldId?: string | null,
  metadata?: Record<string, unknown>,
  relevance: RelevanceScore = RelevanceScore.MEDIUM,
  ttlHours: number = DEFAULT_TTL_HOURS,
): MemoryEntry {
  const now = new Date();
  const expiresAt = ttlHours > 0 ? new Date(now.getTime() + ttlHours * 3600000) : undefined;

  return {
    id: `${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
    tenantId,
    fieldId: fieldId ?? null,
    memoryType,
    content,
    metadata: metadata || {},
    timestamp: now,
    relevance,
    expiresAt,
  };
}

/**
 * Check if memory entry has expired
 * التحقق من انتهاء الصلاحية
 */
export function isMemoryEntryExpired(entry: MemoryEntry): boolean {
  if (!entry.expiresAt) {
    return false;
  }
  return new Date() > entry.expiresAt;
}

/**
 * Convert memory entry to dictionary
 * التحويل إلى قاموس
 */
export function memoryEntryToDict(entry: MemoryEntry): Record<string, unknown> {
  return {
    id: entry.id,
    tenantId: entry.tenantId,
    fieldId: entry.fieldId,
    memoryType: entry.memoryType,
    content: entry.content,
    metadata: entry.metadata,
    timestamp: entry.timestamp.toISOString(),
    relevance: entry.relevance,
    expiresAt: entry.expiresAt?.toISOString() || null,
  };
}

/**
 * Relevance score to integer mapping for sorting
 * تحويل درجة الصلة إلى رقم للفرز
 */
function relevanceToInt(relevance: RelevanceScore): number {
  const mapping: Record<RelevanceScore, number> = {
    [RelevanceScore.CRITICAL]: 4,
    [RelevanceScore.HIGH]: 3,
    [RelevanceScore.MEDIUM]: 2,
    [RelevanceScore.LOW]: 1,
  };
  return mapping[relevance] ?? 0;
}

// ─────────────────────────────────────────────────────────────────────────────
// Farm Memory Class
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Memory management for AI interactions with tenant isolation.
 * إدارة الذاكرة للتفاعلات مع الذكاء الاصطناعي مع عزل المستأجرين
 *
 * Implements a sliding window approach for recent history while
 * maintaining full history within configured limits.
 *
 * يُنفذ نهج النافذة المنزلقة للسجل الأخير مع الحفاظ على
 * السجل الكامل ضمن الحدود المُعدة.
 *
 * Features:
 * - Tenant isolation: Each tenant has separate memory space
 * - Sliding window: Recent entries always accessible
 * - TTL-based expiration: Automatic cleanup of old entries
 * - Relevance scoring: Prioritize important memories
 * - Context retrieval: Get relevant context for AI queries
 */
export class FarmMemory {
  private config: Required<MemoryConfig>;
  private memory: Map<string, MemoryEntry[]>;
  private fieldIndex: Map<string, Set<string>>;
  private stats: Record<string, number>;

  constructor(config?: MemoryConfig) {
    /**
     * Initialize farm memory.
     * تهيئة ذاكرة المزرعة
     *
     * @param config - الإعدادات - Memory configuration
     */
    this.config = {
      windowSize: config?.windowSize ?? DEFAULT_WINDOW_SIZE,
      maxEntries: config?.maxEntries ?? DEFAULT_MAX_ENTRIES,
      ttlHours: config?.ttlHours ?? DEFAULT_TTL_HOURS,
      relevanceThreshold: config?.relevanceThreshold ?? DEFAULT_RELEVANCE_THRESHOLD,
      enableCompression: config?.enableCompression ?? true,
      persistToStorage: config?.persistToStorage ?? false,
    };

    // In-memory storage: tenant_id -> list of entries
    this.memory = new Map();

    // Index for faster field lookups: `${tenant_id}:${field_id}` -> entry ids
    this.fieldIndex = new Map();

    // Statistics
    this.stats = {
      stores: 0,
      recalls: 0,
      forgets: 0,
      expirations: 0,
    };
  }

  /**
   * Store a new memory entry.
   * تخزين إدخال ذاكرة جديد
   *
   * @param tenantId - معرف المستأجر - Tenant identifier
   * @param content - المحتوى - Content to store
   * @param memoryType - نوع الذاكرة - Type of memory
   * @param fieldId - معرف الحقل - Optional field identifier
   * @param metadata - البيانات الوصفية - Optional metadata
   * @param relevance - الصلة - Relevance score
   * @param ttlHours - مدة الصلاحية - Override default TTL
   * @returns الإدخال المُخزن - The stored entry
   */
  store(
    tenantId: string,
    content: Record<string, unknown> | string,
    memoryType: MemoryType = MemoryType.OBSERVATION,
    fieldId?: string | null,
    metadata?: Record<string, unknown>,
    relevance: RelevanceScore = RelevanceScore.MEDIUM,
    ttlHours?: number,
  ): MemoryEntry {
    const ttl = ttlHours ?? this.config.ttlHours;

    const entry = createMemoryEntry(tenantId, memoryType, content, fieldId, metadata, relevance, ttl);

    // Add to memory
    if (!this.memory.has(tenantId)) {
      this.memory.set(tenantId, []);
    }
    this.memory.get(tenantId)!.push(entry);

    // Update field index
    const indexKey = `${tenantId}:${fieldId}`;
    if (!this.fieldIndex.has(indexKey)) {
      this.fieldIndex.set(indexKey, new Set());
    }
    this.fieldIndex.get(indexKey)!.add(entry.id);

    // Enforce limits
    this._enforceLimits(tenantId);

    // Clean expired entries periodically
    if (this.stats.stores % 100 === 0) {
      this._cleanupExpired(tenantId);
    }

    this.stats.stores += 1;

    return entry;
  }

  /**
   * Recall memory entries.
   * استرجاع إدخالات الذاكرة
   *
   * @param tenantId - معرف المستأجر - Tenant identifier
   * @param fieldId - معرف الحقل - Filter by field
   * @param memoryTypes - أنواع الذاكرة - Filter by memory types
   * @param minRelevance - الحد الأدنى للصلة - Minimum relevance score
   * @param limit - الحد الأقصى - Maximum entries to return
   * @param since - منذ - Only entries after this time
   * @param includeExpired - تضمين المنتهية - Include expired entries
   * @returns نتيجة الاسترجاع - Recall result with entries
   */
  recall(
    tenantId: string,
    fieldId?: string | null,
    memoryTypes?: MemoryType[],
    minRelevance?: RelevanceScore,
    limit?: number,
    since?: Date,
    includeExpired: boolean = false,
  ): RecallResult {
    const startTime = performance.now();

    const entries = this.memory.get(tenantId) ?? [];

    // Apply filters
    const filtered = this._filterEntries(
      entries,
      fieldId ?? null,
      memoryTypes,
      minRelevance,
      since,
      includeExpired,
    );

    const totalFound = filtered.length;

    // Sort by relevance and timestamp
    const sorted = [...filtered].sort((a, b) => {
      const relevanceDiff = relevanceToInt(b.relevance) - relevanceToInt(a.relevance);
      if (relevanceDiff !== 0) return relevanceDiff;
      return b.timestamp.getTime() - a.timestamp.getTime();
    });

    // Apply limit
    const resultLimit = limit ?? this.config.windowSize;
    const resultEntries = sorted.slice(0, resultLimit);

    const queryTime = performance.now() - startTime;

    this.stats.recalls += 1;

    return {
      entries: resultEntries,
      totalFound,
      queryTimeMs: queryTime,
      contextText: this._entriesToContext(resultEntries),
    };
  }

  /**
   * Forget (delete) memory entries.
   * نسيان (حذف) إدخالات الذاكرة
   *
   * @param tenantId - معرف المستأجر - Tenant identifier
   * @param entryId - معرف الإدخال - Specific entry to forget
   * @param fieldId - معرف الحقل - Forget all for field
   * @param memoryTypes - أنواع الذاكرة - Forget specific types
   * @param before - قبل - Forget entries before this time
   * @returns عدد الإدخالات المحذوفة - Number of entries forgotten
   */
  forget(
    tenantId: string,
    entryId?: string,
    fieldId?: string | null,
    memoryTypes?: MemoryType[],
    before?: Date,
  ): number {
    if (!this.memory.has(tenantId)) {
      return 0;
    }

    const entries = this.memory.get(tenantId)!;
    const originalCount = entries.length;
    let forgottenCount = 0;

    const entriesToKeep: MemoryEntry[] = [];
    for (const entry of entries) {
      let shouldForget = false;

      if ((entryId && entry.id === entryId) || (fieldId && entry.fieldId === fieldId)) {
        shouldForget = true;
      } else if (memoryTypes && memoryTypes.includes(entry.memoryType)) {
        if (!fieldId || entry.fieldId === fieldId) {
          shouldForget = true;
        }
      } else if (before && entry.timestamp < before) {
        shouldForget = true;
      }

      if (shouldForget) {
        // Remove from field index
        const indexKey = `${tenantId}:${entry.fieldId}`;
        this.fieldIndex.get(indexKey)?.delete(entry.id);
        forgottenCount += 1;
      } else {
        entriesToKeep.push(entry);
      }
    }

    this.memory.set(tenantId, entriesToKeep);
    this.stats.forgets += forgottenCount;

    return forgottenCount;
  }

  /**
   * Get relevant context for an AI query.
   * الحصول على السياق ذي الصلة لاستعلام الذكاء الاصطناعي
   *
   * Retrieves and formats memory entries most relevant to the given query.
   * Uses keyword matching and recency to determine relevance.
   *
   * @param tenantId - معرف المستأجر - Tenant identifier
   * @param query - الاستعلام - User query for relevance matching
   * @param fieldId - معرف الحقل - Filter by field
   * @param maxTokens - الحد الأقصى للرموز - Maximum tokens in context
   * @param memoryTypes - أنواع الذاكرة - Filter by memory types
   * @returns السياق المُنسق - Formatted context string
   */
  getRelevantContext(
    tenantId: string,
    query: string,
    fieldId?: string | null,
    maxTokens: number = 2000,
    memoryTypes?: MemoryType[],
  ): string {
    // Recall all relevant entries
    const result = this.recall(
      tenantId,
      fieldId,
      memoryTypes,
      undefined,
      this.config.windowSize * 2, // Get more for filtering
    );

    if (result.entries.length === 0) {
      return "";
    }

    // Score entries by relevance to query
    const scoredEntries = result.entries.map((entry) => ({
      entry,
      score: this._calculateRelevanceScore(entry, query),
    }));

    // Sort by relevance score
    scoredEntries.sort((a, b) => b.score - a.score);

    // Build context within token limit
    const contextParts: string[] = [];
    let currentTokens = 0;

    for (const { entry } of scoredEntries) {
      const entryText = this._formatEntryForContext(entry);
      const entryTokens = estimateTokens(entryText);

      if (currentTokens + entryTokens > maxTokens) {
        break;
      }

      contextParts.push(entryText);
      currentTokens += entryTokens;
    }

    return contextParts.join("\n---\n");
  }

  /**
   * Get the sliding window of recent entries.
   * الحصول على النافذة المنزلقة للإدخالات الأخيرة
   *
   * @param tenantId - معرف المستأجر - Tenant identifier
   * @param fieldId - معرف الحقل - Filter by field
   * @returns الإدخالات الأخيرة - Recent entries
   */
  getSlidingWindow(tenantId: string, fieldId?: string | null): MemoryEntry[] {
    const result = this.recall(tenantId, fieldId, undefined, undefined, this.config.windowSize);
    return result.entries;
  }

  /**
   * Get memory statistics.
   * الحصول على إحصائيات الذاكرة
   *
   * @returns الإحصائيات - Memory statistics
   */
  getStats(): Record<string, unknown> {
    let totalEntries = 0;
    for (const entries of this.memory.values()) {
      totalEntries += entries.length;
    }

    const tenantCount = this.memory.size;

    return {
      ...this.stats,
      totalEntries,
      tenantCount,
      avgEntriesPerTenant: tenantCount > 0 ? totalEntries / tenantCount : 0,
    };
  }

  /**
   * Clear all memory for a tenant.
   * مسح كل الذاكرة للمستأجر
   *
   * @param tenantId - معرف المستأجر - Tenant identifier
   * @returns عدد الإدخالات المحذوفة - Number of entries cleared
   */
  clearTenant(tenantId: string): number {
    if (!this.memory.has(tenantId)) {
      return 0;
    }

    const count = this.memory.get(tenantId)!.length;

    // Clear field index entries
    const keysToRemove: string[] = [];
    for (const key of this.fieldIndex.keys()) {
      if (key.startsWith(`${tenantId}:`)) {
        keysToRemove.push(key);
      }
    }
    for (const key of keysToRemove) {
      this.fieldIndex.delete(key);
    }

    this.memory.delete(tenantId);

    return count;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Private Helper Methods
  // ─────────────────────────────────────────────────────────────────────────

  private _filterEntries(
    entries: MemoryEntry[],
    fieldId: string | null,
    memoryTypes?: MemoryType[],
    minRelevance?: RelevanceScore,
    since?: Date,
    includeExpired: boolean = false,
  ): MemoryEntry[] {
    const result: MemoryEntry[] = [];

    for (const entry of entries) {
      // Skip expired unless requested
      if (!includeExpired && isMemoryEntryExpired(entry)) {
        continue;
      }

      // Filter by field_id
      if (fieldId !== null && entry.fieldId !== fieldId) {
        continue;
      }

      // Filter by memory type
      if (memoryTypes && !memoryTypes.includes(entry.memoryType)) {
        continue;
      }

      // Filter by relevance
      if (minRelevance) {
        if (relevanceToInt(entry.relevance) < relevanceToInt(minRelevance)) {
          continue;
        }
      }

      // Filter by time
      if (since && entry.timestamp < since) {
        continue;
      }

      result.push(entry);
    }

    return result;
  }

  private _enforceLimits(tenantId: string): void {
    const entries = this.memory.get(tenantId);
    if (!entries || entries.length <= this.config.maxEntries) {
      return;
    }

    // Remove oldest low-relevance entries first
    entries.sort(
      (a, b) =>
        relevanceToInt(a.relevance) - relevanceToInt(b.relevance) ||
        a.timestamp.getTime() - b.timestamp.getTime(),
    );

    // Keep the most relevant/recent entries
    const entriesToRemove = entries.slice(0, entries.length - this.config.maxEntries);
    const entriesToKeep = entries.slice(entries.length - this.config.maxEntries);

    // Update index
    for (const entry of entriesToRemove) {
      const indexKey = `${tenantId}:${entry.fieldId}`;
      this.fieldIndex.get(indexKey)?.delete(entry.id);
    }

    this.memory.set(tenantId, entriesToKeep);
  }

  private _cleanupExpired(tenantId: string): number {
    if (!this.memory.has(tenantId)) {
      return 0;
    }

    const entries = this.memory.get(tenantId)!;
    const originalCount = entries.length;

    const validEntries: MemoryEntry[] = [];
    for (const entry of entries) {
      if (isMemoryEntryExpired(entry)) {
        const indexKey = `${tenantId}:${entry.fieldId}`;
        this.fieldIndex.get(indexKey)?.delete(entry.id);
        this.stats.expirations += 1;
      } else {
        validEntries.push(entry);
      }
    }

    this.memory.set(tenantId, validEntries);
    return originalCount - validEntries.length;
  }

  private _calculateRelevanceScore(entry: MemoryEntry, query: string): number {
    let score = 0.0;

    // Base score from relevance level
    score += relevanceToInt(entry.relevance) * 0.25;

    // Recency bonus (entries from last 24h get bonus)
    const hoursOld = (new Date().getTime() - entry.timestamp.getTime()) / (3600 * 1000);
    const recencyBonus = Math.max(0, 1 - hoursOld / 24) * 0.3;
    score += recencyBonus;

    // Keyword matching
    const queryLower = query.toLowerCase();
    const contentStr = String(entry.content).toLowerCase();

    const keywords = new Set(
      queryLower
        .split(/\s+/)
        .filter((w) => w.length > 0),
    );

    if (keywords.size > 0) {
      let matches = 0;
      for (const kw of keywords) {
        if (contentStr.includes(kw)) {
          matches += 1;
        }
      }
      const keywordScore = (matches / keywords.size) * 0.45;
      score += keywordScore;
    }

    return Math.min(score, 1.0);
  }

  private _entriesToContext(entries: MemoryEntry[]): string {
    if (entries.length === 0) {
      return "";
    }

    const parts = entries.map((entry) => this._formatEntryForContext(entry));
    return parts.join("\n---\n");
  }

  private _formatEntryForContext(entry: MemoryEntry): string {
    const lines: string[] = [];

    // Header
    const timeStr = entry.timestamp.toLocaleString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
    lines.push(`[${entry.memoryType.toUpperCase()}] ${timeStr}`);

    // Field reference if present
    if (entry.fieldId) {
      lines.push(`Field: ${entry.fieldId}`);
    }

    // Content
    if (typeof entry.content === "object" && entry.content !== null) {
      for (const [key, value] of Object.entries(entry.content)) {
        lines.push(`  ${key}: ${value}`);
      }
    } else {
      lines.push(`  ${entry.content}`);
    }

    return lines.join("\n");
  }
}
