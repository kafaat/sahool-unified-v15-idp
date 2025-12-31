/**
 * SAHOOL CSP Nonce Utilities
 * أدوات nonce لـ CSP
 *
 * Utilities for working with CSP nonces in React components
 * أدوات للعمل مع nonces في مكونات React
 */

import { headers } from 'next/headers';

// ═══════════════════════════════════════════════════════════════════════════
// Server-side Nonce Retrieval
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get the current CSP nonce from headers (server-side only)
 * الحصول على nonce الحالي من headers (من جانب الخادم فقط)
 *
 * Usage in Server Components:
 * const nonce = await getNonce();
 */
export async function getNonce(): Promise<string | null> {
  try {
    const headersList = await headers();
    return headersList.get('x-nonce');
  } catch {
    // Headers not available (e.g., in static generation)
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Nonce Props for Components
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get nonce props for script tags
 * الحصول على خصائص nonce لوسوم script
 *
 * Usage:
 * <script {...getNonceProps(nonce)}>...</script>
 */
export function getNonceProps(nonce: string | null): { nonce?: string } {
  if (!nonce) return {};
  return { nonce };
}

/**
 * Get nonce style attribute
 * الحصول على خاصية nonce للأنماط
 *
 * Usage:
 * <style {...getStyleNonceProps(nonce)}>...</style>
 */
export function getStyleNonceProps(nonce: string | null): { nonce?: string } {
  if (!nonce) return {};
  return { nonce };
}

// ═══════════════════════════════════════════════════════════════════════════
// CSP-Safe Inline Styles
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create CSP-safe inline styles using CSS variables
 * إنشاء أنماط مضمنة آمنة لـ CSP باستخدام متغيرات CSS
 *
 * Instead of inline styles, use CSS custom properties:
 *
 * Bad (blocked by CSP):
 * <div style={{ color: 'red' }}>...</div>
 *
 * Good (CSP-safe):
 * <div className="custom-color" style={cssVars({ '--color': 'red' })}>
 *   <style {...getStyleNonceProps(nonce)}>{`.custom-color { color: var(--color); }`}</style>
 * </div>
 */
export function cssVars(vars: Record<string, string>): Record<string, string> {
  return vars;
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Check if code is running on server
 * التحقق مما إذا كان الكود يعمل على الخادم
 */
export function isServer(): boolean {
  return typeof window === 'undefined';
}

/**
 * Safe way to add inline script with nonce
 * طريقة آمنة لإضافة script مضمن مع nonce
 *
 * Usage in Server Components:
 * const nonce = await getNonce();
 * <script {...getNonceProps(nonce)} dangerouslySetInnerHTML={{ __html: code }} />
 */
export function createInlineScript(code: string, nonce: string | null) {
  return {
    ...getNonceProps(nonce),
    dangerouslySetInnerHTML: { __html: code },
  };
}

/**
 * Safe way to add inline style with nonce
 * طريقة آمنة لإضافة style مضمن مع nonce
 *
 * Usage in Server Components:
 * const nonce = await getNonce();
 * <style {...createInlineStyle(css, nonce)} />
 */
export function createInlineStyle(css: string, nonce: string | null) {
  return {
    ...getStyleNonceProps(nonce),
    dangerouslySetInnerHTML: { __html: css },
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const Nonce = {
  get: getNonce,
  getProps: getNonceProps,
  getStyleProps: getStyleNonceProps,
  cssVars,
  isServer,
  createInlineScript,
  createInlineStyle,
};

export default Nonce;
