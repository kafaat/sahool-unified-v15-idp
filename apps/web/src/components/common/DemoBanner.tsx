'use client';

/**
 * DemoBanner — honesty indicator for pages showing illustrative sample data
 * لافتة "وضع العرض التوضيحي" - إشعار بأن البيانات المعروضة توضيحية وليست حقيقية
 *
 * Rendered when the page has no live backend data available. The default is
 * ON; set NEXT_PUBLIC_ANALYTICS_DEMO_MODE=false in the environment to hide it
 * once real analytics endpoints are wired up.
 */

import { AlertTriangle } from 'lucide-react';

export function isDemoModeEnabled(): boolean {
  return process.env.NEXT_PUBLIC_ANALYTICS_DEMO_MODE !== 'false';
}

export default function DemoBanner() {
  if (!isDemoModeEnabled()) return null;

  return (
    <div
      className="flex items-start gap-3 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-amber-900"
      role="note"
      aria-label="Demo Mode"
      dir="rtl"
    >
      <AlertTriangle className="mt-0.5 h-5 w-5 flex-shrink-0 text-amber-600" aria-hidden="true" />
      <div className="text-sm leading-relaxed">
        <span className="font-semibold">وضع العرض التوضيحي:</span>{' '}
        البيانات المعروضة توضيحية وليست بيانات فعلية من الحقول.
        <span className="mx-1">|</span>
        <span className="font-semibold">Demo Mode:</span>{' '}
        The data shown here is illustrative and not live field data.
      </div>
    </div>
  );
}
