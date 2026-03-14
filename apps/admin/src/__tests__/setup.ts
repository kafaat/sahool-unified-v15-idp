/**
 * SAHOOL Admin Test Setup
 * إعداد الاختبارات
 */

import { expect, afterEach, vi } from "vitest";

// Only set up DOM-related mocks when running in a browser-like environment
const isBrowser = typeof window !== "undefined";

if (isBrowser) {
  // Dynamic imports for browser-only modules
  const { cleanup } = await import("@testing-library/react");
  const matchers = await import("@testing-library/jest-dom/matchers");

  // Extend Vitest's expect with Testing Library matchers
  expect.extend(matchers);

  // Cleanup after each test
  afterEach(() => {
    cleanup();
  });

  // Mock window.matchMedia
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
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

  Object.defineProperty(window, "IntersectionObserver", {
    writable: true,
    value: MockIntersectionObserver,
  });

  // Mock ResizeObserver
  class MockResizeObserver {
    observe = vi.fn();
    disconnect = vi.fn();
    unobserve = vi.fn();
  }

  Object.defineProperty(window, "ResizeObserver", {
    writable: true,
    value: MockResizeObserver,
  });

  // Mock fetch
  globalThis.fetch = vi.fn() as typeof fetch;

  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };

  Object.defineProperty(window, "localStorage", {
    value: localStorageMock,
  });

  // Mock sessionStorage
  Object.defineProperty(window, "sessionStorage", {
    value: localStorageMock,
  });

  // Mock performance
  Object.defineProperty(window, "performance", {
    value: {
      ...performance,
      now: vi.fn(() => Date.now()),
      mark: vi.fn(),
      measure: vi.fn(),
      getEntriesByType: vi.fn(() => []),
      getEntriesByName: vi.fn(() => []),
    },
  });
}

// Console spy for tests (works in both environments)
vi.spyOn(console, "error").mockImplementation(() => {});
vi.spyOn(console, "warn").mockImplementation(() => {});
