/**
 * Core Web Vitals Monitoring
 * مراقبة مؤشرات أداء الويب الأساسية
 *
 * Tracks LCP, FID, CLS, FCP, TTFB and reports to analytics endpoint.
 * Uses the web-vitals library for accurate measurements.
 */

import type { Metric } from 'web-vitals';

const VITALS_ENDPOINT = '/api/log-error'; // Reuse existing logging endpoint

/**
 * Report a single web vital metric.
 * Uses `navigator.sendBeacon` for reliable delivery even during page unload.
 */
function sendMetric(metric: Metric): void {
  const payload = {
    type: 'web-vital',
    name: metric.name,
    value: metric.value,
    rating: metric.rating, // "good" | "needs-improvement" | "poor"
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
    url: typeof window !== 'undefined' ? window.location.pathname : '',
    timestamp: new Date().toISOString(),
  };

  const payloadJson = JSON.stringify(payload);

  // Use sendBeacon for reliable delivery during page transitions
  if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
    const beaconBody = new Blob([payloadJson], { type: 'application/json' });
    navigator.sendBeacon(VITALS_ENDPOINT, beaconBody);
  } else {
    fetch(VITALS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: payloadJson,
      keepalive: true,
    }).catch(() => {
      // Silently fail - vitals reporting is best-effort
    });
  }

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    const color =
      metric.rating === 'good'
        ? 'color: green'
        : metric.rating === 'needs-improvement'
          ? 'color: orange'
          : 'color: red';
    console.log(`%c[Web Vital] ${metric.name}: ${metric.value.toFixed(1)} (${metric.rating})`, color);
  }
}

/**
 * Initialize Core Web Vitals reporting.
 * Dynamically imports web-vitals to avoid impacting bundle size.
 *
 * Call this once from a client component (e.g., in providers or layout).
 */
export function reportWebVitals(): void {
  import('web-vitals').then(({ onCLS, onFID, onLCP, onFCP, onTTFB, onINP }) => {
    onCLS(sendMetric);
    onFID(sendMetric);
    onLCP(sendMetric);
    onFCP(sendMetric);
    onTTFB(sendMetric);
    onINP(sendMetric);
  });
}
