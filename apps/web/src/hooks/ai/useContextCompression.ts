/**
 * SAHOOL useContextCompression Hook
 * ضغط السياق لمعالجة الذكاء الاصطناعي
 */

"use client";

import { useCallback, useState } from "react";
import { logger } from "@/lib/logger";

/**
 * Compression level configuration
 */
export enum CompressionLevel {
  LOW = "low", // Minimal compression, preserve most details
  MEDIUM = "medium", // Balanced compression
  HIGH = "high", // Aggressive compression, preserve only essentials
}

/**
 * Context metadata structure
 */
export interface ContextMetadata {
  timestamp: number;
  fieldId?: string;
  tenantId?: string;
  dataType: string;
  originalSize: number;
  compressedSize: number;
  compressionRatio: number;
}

/**
 * Compression statistics
 */
export interface CompressionStats {
  totalOperations: number;
  totalOriginalSize: number;
  totalCompressedSize: number;
  averageCompressionRatio: number;
  lastCompressed: Date | null;
}

/**
 * Hook for compressing AI context data
 * خطاف لضغط بيانات سياق الذكاء الاصطناعي
 */
export function useContextCompression() {
  const [stats, setStats] = useState<CompressionStats>({
    totalOperations: 0,
    totalOriginalSize: 0,
    totalCompressedSize: 0,
    averageCompressionRatio: 0,
    lastCompressed: null,
  });

  /**
   * Compress context data based on level
   * ضغط بيانات السياق بناءً على المستوى
   */
  const compress = useCallback(
    (
      data: unknown,
      level: CompressionLevel = CompressionLevel.MEDIUM,
    ): {
      compressed: string;
      metadata: ContextMetadata;
    } => {
      try {
        const originalJson = JSON.stringify(data);
        const originalSize = new Blob([originalJson]).size;

        let compressed = originalJson;

        switch (level) {
          case CompressionLevel.HIGH:
            // Remove whitespace, nulls, and optional fields
            compressed = JSON.stringify(
              removeNullsAndEmpty(stripWhitespace(data)),
            );
            // Apply simple RLE for repeated patterns
            compressed = applySimpleRLE(compressed);
            break;

          case CompressionLevel.MEDIUM:
            // Remove unnecessary whitespace and null values
            compressed = JSON.stringify(removeNullsAndEmpty(data));
            break;

          case CompressionLevel.LOW:
            // Only remove extra whitespace
            compressed = JSON.stringify(data);
            break;
        }

        const compressedSize = new Blob([compressed]).size;
        const compressionRatio = originalSize / compressedSize;

        const metadata: ContextMetadata = {
          timestamp: Date.now(),
          dataType: Array.isArray(data) ? "array" : typeof data,
          originalSize,
          compressedSize,
          compressionRatio,
        };

        // Update statistics
        setStats((prev) => {
          const newTotal = prev.totalOperations + 1;
          const newOriginal = prev.totalOriginalSize + originalSize;
          const newCompressed = prev.totalCompressedSize + compressedSize;

          return {
            totalOperations: newTotal,
            totalOriginalSize: newOriginal,
            totalCompressedSize: newCompressed,
            averageCompressionRatio: newOriginal / newCompressed,
            lastCompressed: new Date(),
          };
        });

        logger.debug(
          `[useContextCompression] Compressed ${level}`,
          {
            originalSize,
            compressedSize,
            ratio: compressionRatio.toFixed(2),
          },
        );

        return { compressed, metadata };
      } catch (error) {
        logger.error("[useContextCompression] Compression failed:", error);
        throw new Error(
          `Compression failed: ${error instanceof Error ? error.message : "Unknown error"}`,
        );
      }
    },
    [],
  );

  /**
   * Decompress context data
   * فك ضغط بيانات السياق
   */
  const decompress = useCallback((compressed: string): unknown => {
    try {
      return JSON.parse(decompressRLE(compressed));
    } catch (error) {
      logger.error("[useContextCompression] Decompression failed:", error);
      throw new Error(
        `Decompression failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  }, []);

  /**
   * Get current statistics
   * الحصول على الإحصائيات الحالية
   */
  const getStats = useCallback(() => stats, [stats]);

  /**
   * Reset statistics
   * إعادة تعيين الإحصائيات
   */
  const resetStats = useCallback(() => {
    setStats({
      totalOperations: 0,
      totalOriginalSize: 0,
      totalCompressedSize: 0,
      averageCompressionRatio: 0,
      lastCompressed: null,
    });
  }, []);

  return {
    compress,
    decompress,
    getStats,
    resetStats,
    stats,
  };
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Remove null and empty values from object
 */
function removeNullsAndEmpty(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj
      .map((item) => removeNullsAndEmpty(item))
      .filter((item) => item !== null && item !== undefined && item !== "");
  }

  if (obj !== null && typeof obj === "object") {
    const cleaned: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      const cleaned_value = removeNullsAndEmpty(value);
      if (
        cleaned_value !== null &&
        cleaned_value !== undefined &&
        cleaned_value !== ""
      ) {
        cleaned[key] = cleaned_value;
      }
    }
    return cleaned;
  }

  return obj;
}

/**
 * Strip unnecessary whitespace
 */
function stripWhitespace(obj: unknown): unknown {
  if (typeof obj === "string") {
    return obj.trim();
  }

  if (Array.isArray(obj)) {
    return obj.map(stripWhitespace);
  }

  if (obj !== null && typeof obj === "object") {
    const stripped: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      stripped[key] = stripWhitespace(value);
    }
    return stripped;
  }

  return obj;
}

/**
 * Apply simple Run-Length Encoding for compression
 */
function applySimpleRLE(str: string): string {
  return str.replace(/(.)\1{2,}/g, (matchStr) => {
    return `_${matchStr.length}${matchStr[0]}`;
  });
}

/**
 * Decompress simple RLE
 */
function decompressRLE(str: string): string {
  return str.replace(/_(\d+)(.)/g, (_match, count, char) => {
    return char.repeat(parseInt(count, 10));
  });
}

export default useContextCompression;
