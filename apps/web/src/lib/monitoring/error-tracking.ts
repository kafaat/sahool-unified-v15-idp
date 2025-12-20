/**
 * SAHOOL Error Tracking & Monitoring
 * نظام تتبع الأخطاء والمراقبة
 *
 * Features:
 * - Error capturing and reporting
 * - Performance metrics (Web Vitals)
 * - Session tracking
 * - Error context enrichment
 */

import type { ErrorInfo } from 'react';

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

export interface ErrorEvent {
  id: string;
  timestamp: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  stack?: string;
  componentStack?: string;
  url: string;
  userAgent: string;
  userId?: string;
  sessionId: string;
  metadata?: Record<string, unknown>;
  breadcrumbs: Breadcrumb[];
}

export interface Breadcrumb {
  timestamp: string;
  type: 'navigation' | 'click' | 'xhr' | 'console' | 'error';
  category: string;
  message: string;
  data?: Record<string, unknown>;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Constants
// ═══════════════════════════════════════════════════════════════════════════

const MAX_BREADCRUMBS = 50;
const SESSION_ID_KEY = 'sahool_session_id';
const ERROR_ENDPOINT = '/api/log-error';

// ═══════════════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════════════

let breadcrumbs: Breadcrumb[] = [];
let sessionId: string | null = null;
let userId: string | null = null;
let isInitialized = false;

// ═══════════════════════════════════════════════════════════════════════════
// Session Management
// ═══════════════════════════════════════════════════════════════════════════

function getSessionId(): string {
  if (sessionId) return sessionId;

  if (typeof window !== 'undefined') {
    sessionId = sessionStorage.getItem(SESSION_ID_KEY);
    if (!sessionId) {
      sessionId = generateId();
      sessionStorage.setItem(SESSION_ID_KEY, sessionId);
    }
  } else {
    sessionId = generateId();
  }

  return sessionId;
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// Breadcrumbs
// ═══════════════════════════════════════════════════════════════════════════

export function addBreadcrumb(breadcrumb: Omit<Breadcrumb, 'timestamp'>): void {
  const entry: Breadcrumb = {
    ...breadcrumb,
    timestamp: new Date().toISOString(),
  };

  breadcrumbs.push(entry);

  // Keep only last N breadcrumbs
  if (breadcrumbs.length > MAX_BREADCRUMBS) {
    breadcrumbs = breadcrumbs.slice(-MAX_BREADCRUMBS);
  }
}

export function clearBreadcrumbs(): void {
  breadcrumbs = [];
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Capturing
// ═══════════════════════════════════════════════════════════════════════════

export function captureError(
  error: Error,
  errorInfo?: ErrorInfo,
  metadata?: Record<string, unknown>
): void {
  const event: ErrorEvent = {
    id: generateId(),
    timestamp: new Date().toISOString(),
    type: 'error',
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo?.componentStack,
    url: typeof window !== 'undefined' ? window.location.href : '',
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
    userId: userId ?? undefined,
    sessionId: getSessionId(),
    metadata,
    breadcrumbs: [...breadcrumbs],
  };

  sendError(event);
}

export function captureMessage(
  message: string,
  type: 'error' | 'warning' | 'info' = 'info',
  metadata?: Record<string, unknown>
): void {
  const event: ErrorEvent = {
    id: generateId(),
    timestamp: new Date().toISOString(),
    type,
    message,
    url: typeof window !== 'undefined' ? window.location.href : '',
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
    userId: userId ?? undefined,
    sessionId: getSessionId(),
    metadata,
    breadcrumbs: [...breadcrumbs],
  };

  sendError(event);
}

async function sendError(event: ErrorEvent): Promise<void> {
  try {
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group('🔴 Error Captured');
      console.error('Message:', event.message);
      console.error('Stack:', event.stack);
      if (event.componentStack) {
        console.error('Component Stack:', event.componentStack);
      }
      console.log('Breadcrumbs:', event.breadcrumbs);
      console.groupEnd();
    }

    // Send to error endpoint
    await fetch(ERROR_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event),
    });
  } catch (e) {
    // Silent fail - don't cause more errors
    console.warn('Failed to send error to server:', e);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Performance Monitoring (Web Vitals)
// ═══════════════════════════════════════════════════════════════════════════

export interface WebVitalsMetrics {
  CLS: number | null;  // Cumulative Layout Shift
  FID: number | null;  // First Input Delay
  FCP: number | null;  // First Contentful Paint
  LCP: number | null;  // Largest Contentful Paint
  TTFB: number | null; // Time to First Byte
  INP: number | null;  // Interaction to Next Paint
}

const vitalsThresholds = {
  CLS: { good: 0.1, poor: 0.25 },
  FID: { good: 100, poor: 300 },
  FCP: { good: 1800, poor: 3000 },
  LCP: { good: 2500, poor: 4000 },
  TTFB: { good: 800, poor: 1800 },
  INP: { good: 200, poor: 500 },
};

function getRating(name: keyof typeof vitalsThresholds, value: number): 'good' | 'needs-improvement' | 'poor' {
  const threshold = vitalsThresholds[name];
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

export function reportWebVitals(metric: { name: string; value: number; id: string }): void {
  const name = metric.name as keyof typeof vitalsThresholds;
  const rating = vitalsThresholds[name] ? getRating(name, metric.value) : 'good';

  const performanceMetric: PerformanceMetric = {
    name: metric.name,
    value: metric.value,
    rating,
    timestamp: new Date().toISOString(),
  };

  // Log in development
  if (process.env.NODE_ENV === 'development') {
    const emoji = rating === 'good' ? '🟢' : rating === 'needs-improvement' ? '🟡' : '🔴';
    console.log(`${emoji} ${metric.name}: ${metric.value.toFixed(2)} (${rating})`);
  }

  // Send to analytics endpoint
  sendPerformanceMetric(performanceMetric);
}

async function sendPerformanceMetric(metric: PerformanceMetric): Promise<void> {
  try {
    await fetch('/api/analytics/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...metric,
        sessionId: getSessionId(),
        userId,
        url: typeof window !== 'undefined' ? window.location.href : '',
      }),
    });
  } catch (e) {
    // Silent fail
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Global Error Handlers
// ═══════════════════════════════════════════════════════════════════════════

export function initializeErrorTracking(options?: { userId?: string }): void {
  if (isInitialized || typeof window === 'undefined') return;

  if (options?.userId) {
    userId = options.userId;
  }

  // Global error handler
  window.onerror = (message, source, lineno, colno, error) => {
    captureError(error || new Error(String(message)), undefined, {
      source,
      lineno,
      colno,
    });
    return false;
  };

  // Unhandled promise rejection handler
  window.onunhandledrejection = (event) => {
    const error = event.reason instanceof Error
      ? event.reason
      : new Error(String(event.reason));
    captureError(error, undefined, { type: 'unhandledrejection' });
  };

  // Track navigation
  const originalPushState = history.pushState;
  history.pushState = function (...args) {
    addBreadcrumb({
      type: 'navigation',
      category: 'history',
      message: `Navigate to ${args[2]}`,
      data: { from: window.location.href, to: args[2] as string },
    });
    return originalPushState.apply(this, args);
  };

  // Track clicks
  document.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    const text = target.innerText?.substring(0, 50) || target.className;
    addBreadcrumb({
      type: 'click',
      category: 'ui',
      message: `Click on ${target.tagName.toLowerCase()}`,
      data: { text, className: target.className },
    });
  }, { passive: true });

  // Track XHR/Fetch
  const originalFetch = window.fetch;
  window.fetch = async function (...args) {
    const url = typeof args[0] === 'string' ? args[0] : (args[0] as Request).url;
    const method = (args[1]?.method || 'GET').toUpperCase();

    addBreadcrumb({
      type: 'xhr',
      category: 'fetch',
      message: `${method} ${url}`,
    });

    try {
      const response = await originalFetch.apply(this, args);
      addBreadcrumb({
        type: 'xhr',
        category: 'fetch',
        message: `${method} ${url} - ${response.status}`,
        data: { status: response.status },
      });
      return response;
    } catch (error) {
      addBreadcrumb({
        type: 'error',
        category: 'fetch',
        message: `${method} ${url} - Failed`,
        data: { error: String(error) },
      });
      throw error;
    }
  };

  isInitialized = true;
  console.log('🔍 Error tracking initialized');
}

// ═══════════════════════════════════════════════════════════════════════════
// User Context
// ═══════════════════════════════════════════════════════════════════════════

export function setUser(user: { id: string; email?: string; name?: string } | null): void {
  userId = user?.id ?? null;
}

export function clearUser(): void {
  userId = null;
}

export function getBreadcrumbs(): Breadcrumb[] {
  return [...breadcrumbs];
}

export function getMonitoringContext() {
  return {
    sessionId: getSessionId(),
    userId,
    breadcrumbs: [...breadcrumbs],
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Export
// ═══════════════════════════════════════════════════════════════════════════

export const ErrorTracking = {
  initialize: initializeErrorTracking,
  captureError,
  captureMessage,
  addBreadcrumb,
  getBreadcrumbs,
  clearBreadcrumbs,
  setUser,
  clearUser,
  reportWebVitals,
  getContext: getMonitoringContext,
};

export default ErrorTracking;
