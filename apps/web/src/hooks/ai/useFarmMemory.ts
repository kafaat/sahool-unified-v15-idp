/**
 * SAHOOL useFarmMemory Hook
 * إدارة ذاكرة المزرعة للذكاء الاصطناعي
 */

"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { logger } from "@/lib/logger";

/**
 * Memory entry types
 */
export enum MemoryEntryType {
  OBSERVATION = "observation",
  RECOMMENDATION = "recommendation",
  ACTION = "action",
  OUTCOME = "outcome",
  METRIC = "metric",
}

/**
 * Memory entry structure
 */
export interface MemoryEntry {
  id: string;
  type: MemoryEntryType;
  timestamp: number;
  fieldId?: string;
  tenantId?: string;
  title: string;
  content: string;
  metadata?: Record<string, unknown>;
  confidence?: number; // 0-1 confidence score
  tags?: string[];
}

/**
 * Memory statistics
 */
export interface MemoryStatistics {
  totalEntries: number;
  entriesByType: Record<MemoryEntryType, number>;
  oldestEntry: number | null;
  newestEntry: number | null;
  averageConfidence: number;
  memorySize: number; // in bytes
}

/**
 * Memory query options
 */
export interface MemoryQueryOptions {
  fieldId?: string;
  tenantId?: string;
  type?: MemoryEntryType;
  tags?: string[];
  startTime?: number;
  endTime?: number;
  limit?: number;
}

/**
 * Hook for managing farm memory with retention policies
 * خطاف لإدارة ذاكرة المزرعة مع سياسات الاحتفاظ
 */
export function useFarmMemory(maxEntries: number = 1000) {
  const [entries, setEntries] = useState<MemoryEntry[]>([]);
  const entriesRef = useRef<MemoryEntry[]>([]);

  // Sync ref with state
  useEffect(() => {
    entriesRef.current = entries;
  }, [entries]);

  /**
   * Add memory entry
   * إضافة إدخال ذاكرة
   */
  const addEntry = useCallback(
    (
      type: MemoryEntryType,
      title: string,
      content: string,
      options?: {
        fieldId?: string;
        tenantId?: string;
        confidence?: number;
        tags?: string[];
        metadata?: Record<string, unknown>;
      },
    ): MemoryEntry => {
      const entry: MemoryEntry = {
        id: generateId(),
        type,
        timestamp: Date.now(),
        title,
        content,
        confidence: options?.confidence ?? 0.8,
        ...options,
      };

      setEntries((prev) => {
        const updated = [entry, ...prev];

        // Enforce max entries limit (keep most recent)
        if (updated.length > maxEntries) {
          const trimmed = updated.slice(0, maxEntries);
          logger.warn(
            `[useFarmMemory] Trimmed memory from ${updated.length} to ${maxEntries} entries`,
          );
          return trimmed;
        }

        return updated;
      });

      logger.debug(`[useFarmMemory] Added ${type} entry:`, { id: entry.id });
      return entry;
    },
    [maxEntries],
  );

  /**
   * Update memory entry
   * تحديث إدخال الذاكرة
   */
  const updateEntry = useCallback(
    (id: string, updates: Partial<MemoryEntry>): MemoryEntry | null => {
      let updated: MemoryEntry | null = null;

      setEntries((prev) =>
        prev.map((entry) => {
          if (entry.id === id) {
            updated = { ...entry, ...updates, id: entry.id };
            return updated;
          }
          return entry;
        }),
      );

      if (updated) {
        logger.debug(`[useFarmMemory] Updated entry:`, { id });
      }

      return updated;
    },
    [],
  );

  /**
   * Delete memory entry
   * حذف إدخال الذاكرة
   */
  const deleteEntry = useCallback((id: string): boolean => {
    let deleted = false;

    setEntries((prev) =>
      prev.filter((entry) => {
        if (entry.id === id) {
          deleted = true;
          return false;
        }
        return true;
      }),
    );

    if (deleted) {
      logger.debug(`[useFarmMemory] Deleted entry:`, { id });
    }

    return deleted;
  }, []);

  /**
   * Query memory entries
   * الاستعلام عن إدخالات الذاكرة
   */
  const queryEntries = useCallback(
    (options?: MemoryQueryOptions): MemoryEntry[] => {
      let results = [...entriesRef.current];

      if (options?.fieldId) {
        results = results.filter((e) => e.fieldId === options.fieldId);
      }

      if (options?.tenantId) {
        results = results.filter((e) => e.tenantId === options.tenantId);
      }

      if (options?.type) {
        results = results.filter((e) => e.type === options.type);
      }

      if (options?.tags && options.tags.length > 0) {
        results = results.filter((e) =>
          options.tags?.some((tag) => e.tags && e.tags.includes(tag)),
        );
      }

      if (options?.startTime) {
        results = results.filter((e) => e.timestamp >= options.startTime!);
      }

      if (options?.endTime) {
        results = results.filter((e) => e.timestamp <= options.endTime!);
      }

      if (options?.limit && options.limit > 0) {
        results = results.slice(0, options.limit);
      }

      logger.debug(`[useFarmMemory] Query returned ${results.length} entries`);
      return results;
    },
    [],
  );

  /**
   * Search memory by content
   * البحث في الذاكرة حسب المحتوى
   */
  const searchEntries = useCallback(
    (query: string, options?: Partial<MemoryQueryOptions>): MemoryEntry[] => {
      const lowerQuery = query.toLowerCase();
      const filtered = queryEntries(options);

      return filtered.filter(
        (e) =>
          e.title.toLowerCase().includes(lowerQuery) ||
          e.content.toLowerCase().includes(lowerQuery) ||
          e.tags?.some((tag) => tag.toLowerCase().includes(lowerQuery)),
      );
    },
    [queryEntries],
  );

  /**
   * Get memory statistics
   * الحصول على إحصائيات الذاكرة
   */
  const getStatistics = useCallback((): MemoryStatistics => {
    const currentEntries = entriesRef.current;

    const entriesByType: Record<MemoryEntryType, number> = {
      [MemoryEntryType.OBSERVATION]: 0,
      [MemoryEntryType.RECOMMENDATION]: 0,
      [MemoryEntryType.ACTION]: 0,
      [MemoryEntryType.OUTCOME]: 0,
      [MemoryEntryType.METRIC]: 0,
    };

    let totalConfidence = 0;
    let memorySize = 0;

    currentEntries.forEach((entry) => {
      entriesByType[entry.type]++;
      totalConfidence += entry.confidence ?? 0;
      memorySize += JSON.stringify(entry).length;
    });

    return {
      totalEntries: currentEntries.length,
      entriesByType,
      oldestEntry:
        currentEntries.length > 0
          ? currentEntries[currentEntries.length - 1]!.timestamp
          : null,
      newestEntry:
        currentEntries.length > 0 ? currentEntries[0]!.timestamp : null,
      averageConfidence:
        currentEntries.length > 0
          ? totalConfidence / currentEntries.length
          : 0,
      memorySize,
    };
  }, []);

  /**
   * Clear memory with retention policy
   * مسح الذاكرة مع سياسة الاحتفاظ
   */
  const clearMemory = useCallback(
    (options?: {
      olderThan?: number; // Timestamp - delete entries older than this
      type?: MemoryEntryType; // Only clear specific type
      fieldId?: string; // Only clear specific field
      all?: boolean; // Clear everything
    }): number => {
      let deletedCount = 0;

      setEntries((prev) =>
        prev.filter((entry) => {
          let shouldDelete = false;

          if (options?.all) {
            shouldDelete = true;
          } else if (options?.olderThan && entry.timestamp < options.olderThan) {
            shouldDelete = true;
          } else if (options?.type && entry.type === options.type) {
            shouldDelete = true;
          } else if (
            options?.fieldId &&
            entry.fieldId === options.fieldId
          ) {
            shouldDelete = true;
          }

          if (shouldDelete) {
            deletedCount++;
          }

          return !shouldDelete;
        }),
      );

      logger.info(`[useFarmMemory] Cleared ${deletedCount} entries`);
      return deletedCount;
    },
    [],
  );

  /**
   * Export memory for backup
   * تصدير الذاكرة للنسخ الاحتياطية
   */
  const exportMemory = useCallback((): string => {
    return JSON.stringify(entriesRef.current);
  }, []);

  /**
   * Import memory from backup
   * استيراد الذاكرة من النسخة الاحتياطية
   */
  const importMemory = useCallback((data: string): boolean => {
    try {
      const imported = JSON.parse(data) as MemoryEntry[];

      if (!Array.isArray(imported)) {
        throw new Error("Invalid memory format");
      }

      setEntries(imported);
      logger.info(
        `[useFarmMemory] Imported ${imported.length} memory entries`,
      );
      return true;
    } catch (error) {
      logger.error("[useFarmMemory] Import failed:", error);
      return false;
    }
  }, []);

  return {
    entries,
    addEntry,
    updateEntry,
    deleteEntry,
    queryEntries,
    searchEntries,
    getStatistics,
    clearMemory,
    exportMemory,
    importMemory,
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generate unique ID for memory entry
 */
function generateId(): string {
  return `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

export default useFarmMemory;
