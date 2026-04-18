/**
 * Formatting helpers
 * مساعدات التنسيق
 */

/**
 * Format a currency amount using Intl.NumberFormat.
 * Falls back to a simple string if the locale/currency is unsupported.
 */
export function formatCurrency(amount: number, currency: string, locale?: string): string {
  const effectiveLocale =
    locale ||
    (typeof document !== 'undefined' && document.documentElement.lang) ||
    'ar-SA';
  try {
    return new Intl.NumberFormat(effectiveLocale, {
      style: 'currency',
      currency,
    }).format(amount);
  } catch {
    return `${amount.toFixed(2)} ${currency}`;
  }
}
