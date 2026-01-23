// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Shared Utilities
// Unified utility functions for all frontend applications
// ═══════════════════════════════════════════════════════════════════════════════

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// ─────────────────────────────────────────────────────────────────────────────
// Class Name Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Merge Tailwind CSS classes with clsx
 * دمج أصناف CSS مع clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ─────────────────────────────────────────────────────────────────────────────
// Date Formatting
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Format date for Arabic/English display
 * تنسيق التاريخ للعرض بالعربية/الإنجليزية
 */
export function formatDate(date: string | Date, locale: string = "ar"): string {
  const d = new Date(date);
  return d.toLocaleDateString(locale === "ar" ? "ar-YE" : "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format date with time
 * تنسيق التاريخ مع الوقت
 */
export function formatDateTime(
  date: string | Date,
  locale: string = "ar",
): string {
  const d = new Date(date);
  return d.toLocaleString(locale === "ar" ? "ar-YE" : "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Number Formatting
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Format number for Arabic/English display
 * تنسيق الأرقام للعرض بالعربية/الإنجليزية
 */
export function formatNumber(num: number, locale: string = "ar"): string {
  return num.toLocaleString(locale === "ar" ? "ar-YE" : "en-US");
}

/**
 * Format area in hectares
 * تنسيق المساحة بالهكتار
 */
export function formatArea(hectares: number, locale: string = "ar"): string {
  return `${formatNumber(hectares, locale)} ${locale === "ar" ? "هكتار" : "ha"}`;
}

/**
 * Format currency
 * تنسيق العملة
 */
export function formatCurrency(
  amount: number,
  locale: string = "ar",
  currency: string = "YER",
): string {
  return new Intl.NumberFormat(locale === "ar" ? "ar-YE" : "en-US", {
    style: "currency",
    currency,
  }).format(amount);
}

/**
 * Format percentage
 * تنسيق النسبة المئوية
 */
export function formatPercentage(value: number, locale: string = "ar"): string {
  return `${formatNumber(Math.round(value * 100) / 100, locale)}%`;
}

// ─────────────────────────────────────────────────────────────────────────────
// Color Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get health score color classes
 * الحصول على أصناف ألوان درجة الصحة
 */
export function getHealthScoreColor(score: number): string {
  if (score >= 80) return "text-green-600 bg-green-100";
  if (score >= 60) return "text-yellow-600 bg-yellow-100";
  if (score >= 40) return "text-orange-600 bg-orange-100";
  return "text-red-600 bg-red-100";
}

/**
 * Get severity color classes
 * الحصول على أصناف ألوان الخطورة
 */
export function getSeverityColor(severity: string): string {
  const colors: Record<string, string> = {
    low: "text-green-600 bg-green-100",
    medium: "text-yellow-600 bg-yellow-100",
    high: "text-orange-600 bg-orange-100",
    critical: "text-red-600 bg-red-100",
  };
  return colors[severity] || "text-gray-600 bg-gray-100";
}

/**
 * Get status color classes
 * الحصول على أصناف ألوان الحالة
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: "text-yellow-600 bg-yellow-100",
    confirmed: "text-blue-600 bg-blue-100",
    rejected: "text-gray-600 bg-gray-100",
    treated: "text-green-600 bg-green-100",
    active: "text-green-600 bg-green-100",
    inactive: "text-red-600 bg-red-100",
    success: "text-green-600 bg-green-100",
    error: "text-red-600 bg-red-100",
    warning: "text-yellow-600 bg-yellow-100",
    info: "text-blue-600 bg-blue-100",
  };
  return colors[status] || "text-gray-600 bg-gray-100";
}

// ─────────────────────────────────────────────────────────────────────────────
// Label Utilities (Arabic/English)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Get severity label in Arabic/English
 * الحصول على تسمية الخطورة بالعربية/الإنجليزية
 */
export function getSeverityLabel(
  severity: string,
  locale: string = "ar",
): string {
  const labels: Record<string, Record<string, string>> = {
    ar: {
      low: "منخفض",
      medium: "متوسط",
      high: "مرتفع",
      critical: "حرج",
    },
    en: {
      low: "Low",
      medium: "Medium",
      high: "High",
      critical: "Critical",
    },
  };
  return labels[locale]?.[severity] || severity;
}

/**
 * Get status label in Arabic/English
 * الحصول على تسمية الحالة بالعربية/الإنجليزية
 */
export function getStatusLabel(status: string, locale: string = "ar"): string {
  const labels: Record<string, Record<string, string>> = {
    ar: {
      pending: "قيد المراجعة",
      confirmed: "مؤكد",
      rejected: "مرفوض",
      treated: "تم العلاج",
      active: "نشط",
      inactive: "غير نشط",
      success: "نجاح",
      error: "خطأ",
      warning: "تحذير",
      info: "معلومات",
    },
    en: {
      pending: "Pending",
      confirmed: "Confirmed",
      rejected: "Rejected",
      treated: "Treated",
      active: "Active",
      inactive: "Inactive",
      success: "Success",
      error: "Error",
      warning: "Warning",
      info: "Info",
    },
  };
  return labels[locale]?.[status] || status;
}

// ─────────────────────────────────────────────────────────────────────────────
// Validation Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Check if value is empty (null, undefined, empty string, empty array)
 */
export function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === "string") return value.trim() === "";
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value).length === 0;
  return false;
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate phone number (Yemen format)
 */
export function isValidYemenPhone(phone: string): boolean {
  const yemenPhoneRegex = /^(\+967|00967|967)?[1-9]\d{8}$/;
  return yemenPhoneRegex.test(phone.replace(/\s/g, ""));
}

// ─────────────────────────────────────────────────────────────────────────────
// String Utilities
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Truncate string to specified length
 * قص النص إلى طول محدد
 *
 * @param str - النص - String to truncate
 * @param length - الطول - Maximum length
 * @param suffix - اللاحقة - Suffix to add (default: "...")
 * @returns النص المقصوص - Truncated string
 */
export function truncate(str: string, length: number, suffix: string = "..."): string {
  if (str.length <= length) return str;
  return str.slice(0, length - suffix.length) + suffix;
}

/**
 * Capitalize first letter
 * جعل الحرف الأول كبيراً
 */
export function capitalize(str: string): string {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Capitalize all words (title case)
 * جعل أول حرف من كل كلمة كبيراً
 */
export function titleCase(str: string): string {
  return str
    .toLowerCase()
    .split(" ")
    .map((word) => capitalize(word))
    .join(" ");
}

/**
 * Convert string to kebab-case
 * تحويل النص إلى kebab-case
 */
export function kebabCase(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, "$1-$2")
    .replace(/[\s_]+/g, "-")
    .toLowerCase();
}

/**
 * Convert string to camelCase
 * تحويل النص إلى camelCase
 */
export function camelCase(str: string): string {
  return str
    .replace(/[-_\s]+(.)?/g, (_, c) => (c ? c.toUpperCase() : ""))
    .replace(/^./, (c) => c.toLowerCase());
}

/**
 * Convert string to snake_case
 * تحويل النص إلى snake_case
 */
export function snakeCase(str: string): string {
  return str
    .replace(/([a-z])([A-Z])/g, "$1_$2")
    .replace(/[\s-]+/g, "_")
    .toLowerCase();
}

/**
 * Generate random ID with crypto (if available) or fallback
 * توليد معرف عشوائي آمن
 */
export function generateId(prefix: string = "id"): string {
  let randomPart: string;

  // Use crypto if available for better randomness
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    randomPart = crypto.randomUUID().slice(0, 12);
  } else {
    randomPart = `${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 11)}`;
  }

  return `${prefix}_${randomPart}`;
}

/**
 * Generate UUID v4
 * توليد UUID v4
 */
export function generateUUID(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }

  // Fallback implementation
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Slugify a string (URL-safe)
 * تحويل النص إلى slug آمن للروابط
 */
export function slugify(str: string): string {
  return str
    .toLowerCase()
    .trim()
    .replace(/[\u0600-\u06FF]/g, "") // Remove Arabic characters
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Escape HTML special characters
 * تهريب أحرف HTML الخاصة
 */
export function escapeHtml(str: string): string {
  const htmlEntities: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return str.replace(/[&<>"']/g, (char) => htmlEntities[char]);
}

/**
 * Pad string to specified length
 * إضافة حشو للنص
 */
export function padStart(str: string, length: number, char: string = " "): string {
  return str.padStart(length, char);
}

export function padEnd(str: string, length: number, char: string = " "): string {
  return str.padEnd(length, char);
}

// ─────────────────────────────────────────────────────────────────────────────
// Export Types
// ─────────────────────────────────────────────────────────────────────────────

export type Locale = "ar" | "en";
export type Severity = "low" | "medium" | "high" | "critical";
export type Status =
  | "pending"
  | "confirmed"
  | "rejected"
  | "treated"
  | "active"
  | "inactive";

// ─────────────────────────────────────────────────────────────────────────────
// Performance Utilities
// ─────────────────────────────────────────────────────────────────────────────

export {
  debounce,
  throttle,
  memoize,
  batchCalls,
  requestIdleCallback,
  cancelIdleCallback,
  measureTime,
  createLRUCache,
} from "./performance";

// ─────────────────────────────────────────────────────────────────────────────
// AI Context Engineering
// ─────────────────────────────────────────────────────────────────────────────

export * from "./ai";
