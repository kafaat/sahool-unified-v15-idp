/**
 * SAHOOL Web Test Setup
 * إعداد الاختبارات
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Mock error-tracking module globally to prevent import resolution issues
vi.mock('@/lib/monitoring/error-tracking', () => ({
  ErrorTracking: {
    initialize: vi.fn(),
    cleanup: vi.fn(),
    captureError: vi.fn(),
    captureMessage: vi.fn(),
    addBreadcrumb: vi.fn(),
    getBreadcrumbs: vi.fn(() => []),
    clearBreadcrumbs: vi.fn(),
    setUser: vi.fn(),
    clearUser: vi.fn(),
    reportWebVitals: vi.fn(),
    getContext: vi.fn(() => ({
      sessionId: 'test-session-id',
      userId: null,
      breadcrumbs: [],
    })),
  },
  default: {
    initialize: vi.fn(),
    cleanup: vi.fn(),
    captureError: vi.fn(),
    captureMessage: vi.fn(),
    addBreadcrumb: vi.fn(),
    getBreadcrumbs: vi.fn(() => []),
    clearBreadcrumbs: vi.fn(),
    setUser: vi.fn(),
    clearUser: vi.fn(),
    reportWebVitals: vi.fn(),
    getContext: vi.fn(() => ({
      sessionId: 'test-session-id',
      userId: null,
      breadcrumbs: [],
    })),
  },
  captureError: vi.fn(),
  captureMessage: vi.fn(),
  addBreadcrumb: vi.fn(),
  getBreadcrumbs: vi.fn(() => []),
  clearBreadcrumbs: vi.fn(),
  initializeErrorTracking: vi.fn(),
  cleanupErrorTracking: vi.fn(),
  setUser: vi.fn(),
  clearUser: vi.fn(),
  reportWebVitals: vi.fn(),
  getMonitoringContext: vi.fn(() => ({
    sessionId: 'test-session-id',
    userId: null,
    breadcrumbs: [],
  })),
}));

// Extend Vitest's expect with Testing Library matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  disconnect = vi.fn();
  unobserve = vi.fn();
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
});

// Mock ResizeObserver
class MockResizeObserver {
  observe = vi.fn();
  disconnect = vi.fn();
  unobserve = vi.fn();
}

Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: MockResizeObserver,
});

// Mock fetch to return a resolved Promise
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
  } as Response)
);

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: localStorageMock,
});

// Mock performance
Object.defineProperty(window, 'performance', {
  value: {
    ...performance,
    now: vi.fn(() => Date.now()),
    mark: vi.fn(),
    measure: vi.fn(),
    getEntriesByType: vi.fn(() => []),
    getEntriesByName: vi.fn(() => []),
  },
});

// Console spy for tests
vi.spyOn(console, 'error').mockImplementation(() => {});
vi.spyOn(console, 'warn').mockImplementation(() => {});

// Mock TextEncoder and TextDecoder for jose library (jsdom doesn't have these)
if (typeof window !== 'undefined' && !window.TextEncoder) {
  const { TextEncoder, TextDecoder } = require('util');
  // Make TextEncoder/TextDecoder globally available
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;

  Object.defineProperty(window, 'TextEncoder', {
    writable: true,
    value: TextEncoder,
  });
  Object.defineProperty(window, 'TextDecoder', {
    writable: true,
    value: TextDecoder,
  });

  // Ensure Uint8Array is the same across contexts
  Object.defineProperty(window, 'Uint8Array', {
    writable: true,
    value: Uint8Array,
  });
}
