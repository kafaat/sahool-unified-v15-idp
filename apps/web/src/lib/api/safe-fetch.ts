/**
 * Safe Fetch Utilities - أدوات الجلب الآمن
 *
 * Provides ContractError for API format/contract violations and a
 * SafeFetchResult discriminated-union type so callers can handle
 * unexpected shapes without silent data loss.
 */

// ═══════════════════════════════════════════════════════════════════════════
// Bilingual contract error messages
// ═══════════════════════════════════════════════════════════════════════════

const messages: Record<string, { en: string; ar: string }> = {
  UNEXPECTED_FORMAT: {
    en: 'Unexpected API response format. Please contact support if this persists.',
    ar: 'تنسيق استجابة API غير متوقع. تواصل مع الدعم إذا استمرت المشكلة.',
  },
  MISSING_FIELD: {
    en: 'Required field missing in API response.',
    ar: 'حقل مطلوب مفقود في استجابة API.',
  },
  SCHEMA_MISMATCH: {
    en: 'API response does not match expected schema.',
    ar: 'استجابة API لا تطابق المخطط المتوقع.',
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// ContractError class
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Thrown when an API response does not match the expected contract/format.
 *
 * Distinct from network/HTTP errors so React Query error boundaries and
 * `onError` handlers can differentiate format bugs from connectivity issues.
 *
 * يُطرح عند عدم تطابق استجابة API مع العقد/التنسيق المتوقع.
 */
export class ContractError extends Error {
  /** Machine-readable code for programmatic handling */
  readonly code: string;
  /** Arabic error message */
  readonly messageAr: string;

  constructor(
    code: keyof typeof messages = 'UNEXPECTED_FORMAT',
    /** Optional detail appended to the message (e.g. field name, received type) */
    detail?: string
  ) {
    const entry = messages[code] ?? messages['UNEXPECTED_FORMAT'];
    const full = detail ? `${entry.en} (${detail})` : entry.en;
    super(full);
    this.name = 'ContractError';
    this.code = code;
    this.messageAr = detail ? `${entry.ar} (${detail})` : entry.ar;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SafeFetchResult discriminated union
// ═══════════════════════════════════════════════════════════════════════════

/** Successful result wrapping the parsed payload. */
export interface SafeFetchSuccess<T> {
  ok: true;
  data: T;
}

/** Failed result carrying the error so the caller can surface it explicitly. */
export interface SafeFetchFailure {
  ok: false;
  error: Error;
}

/**
 * Discriminated union returned by fetch helpers that prefer not to throw.
 *
 * Usage:
 * ```ts
 * const result = await safeFetch(...);
 * if (!result.ok) throw result.error; // let React Query handle it
 * return result.data;
 * ```
 */
export type SafeFetchResult<T> = SafeFetchSuccess<T> | SafeFetchFailure;

/**
 * Wraps a value in a successful SafeFetchResult.
 *
 * Intended for feature API modules that prefer the Result style over throwing.
 * Example:
 * ```ts
 * async function getItems(): Promise<SafeFetchResult<Item[]>> {
 *   try {
 *     const data = await api.get('/items');
 *     return safeFetchOk(data);
 *   } catch (error) {
 *     return safeFetchErr(error instanceof Error ? error : new Error(String(error)));
 *   }
 * }
 * ```
 */
export function safeFetchOk<T>(data: T): SafeFetchSuccess<T> {
  return { ok: true, data };
}

/**
 * Wraps an error in a failed SafeFetchResult.
 *
 * @see safeFetchOk
 */
export function safeFetchErr(error: Error): SafeFetchFailure {
  return { ok: false, error };
}
